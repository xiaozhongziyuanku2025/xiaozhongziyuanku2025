import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动全拟真点击版爬虫...")
    account = os.environ.get('LANZOU_ACCOUNT')
    password = os.environ.get('LANZOU_PASSWORD')

    if not account or not password:
        print("❌ 缺少账号或密码环境变量")
        return

    results = []
    seen_files = set()
    target_folder_name = "小众资源库"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        captured_folder_data = {}

        # 全程拦截浏览器自己发出的 AJAX 请求
        async def handle_response(response):
            if "doupload.php" in response.url:
                try:
                    post_data = response.request.post_data or ""
                    match = re.search(r"folder_id=(-?\d+)", post_data)
                    if match:
                        fid = match.group(1)
                        data = await response.json()
                        if data.get('zt') == 1 and isinstance(data.get('text'), list):
                            if fid not in captured_folder_data:
                                captured_folder_data[fid] = []
                            # 累加数据，绝不覆盖
                            captured_folder_data[fid].extend(data.get('text', []))
                except:
                    pass
        page.on("response", handle_response)

        print("正在访问登录页...")
        await page.goto("https://accounts.woozooo.com/accounts.php?action=login&ref=pc.woozooo.com", timeout=30000)
        await page.wait_for_timeout(2000)

        try:
            await page.fill("#username", account)
            await page.fill(".input.pwd", password)
            await page.click("#s3")
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"❌ 登录异常: {e}")

        if "mydisk" not in page.url:
            print(f"❌ 登录失败，当前 URL: {page.url}")
            return
        
        print("✅ 登录成功！正在进入网盘...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(5000)

        # 1. 提取并处理根目录
        root_items = captured_folder_data.get('-1', [])
        target_folder_id = None
        seen_root = set()

        for item in root_items:
            unique_key = f"{item.get('name_all') or item.get('name')}_{item.get('id') or item.get('fol_id')}"
            if unique_key in seen_root: continue
            seen_root.add(unique_key)

            if 'name_all' in item: # 根目录文件
                # 根目录文件直接使用 duan 拼链接，或者不需要链接
                share_url = f"https://www.lanzouq.com/{item.get('duan')}" if item.get('duan') else ""
                results.append({
                    "name": item.get('name_all'),
                    "url": share_url,
                    "pwd": "",
                    "path": "", 
                    "size": item.get('size', '0')
                })
                print(f"  + 根目录文件: {item.get('name_all')}")
            elif 'fol_id' in item: # 根目录文件夹
                # 模糊匹配“小众资源库”
                if target_folder_name in item.get('name', ''):
                    target_folder_id = item.get('fol_id')
                    print(f"✅ 找到目标文件夹【{item.get('name')}】，ID: {target_folder_id}")

        # 如果根目录请求没截获，或者没找到，直接用鼠标点击页面试试！
        if not target_folder_id:
            print(f"⚠️ 接口未找到，尝试用鼠标在页面上点击【{target_folder_name}】...")
            try:
                # 尝试点击包含该名字的文字
                folder_link = page.locator(f"text={target_folder_name}").first
                if await folder_link.count() > 0:
                    await folder_link.click()
                    await page.wait_for_timeout(4000)
                    # 点击后，URL 会变，或者发出请求
                    match = re.search(r"folder_id=(\d+)", page.url)
                    if match:
                        target_folder_id = match.group(1)
                        print(f"✅ 点击后从 URL 获取到 ID: {target_folder_id}")
                    else:
                        print("❌ 点击了，但没拿到 ID。")
            except Exception as e:
                print(f"❌ 拟真点击失败: {e}")

        if not target_folder_id:
            print("❌ 彻底未找到目标文件夹，结束。")
            return

        # 2. 深度遍历（全程用 page.goto 触发网页自身请求）
        queue = [(target_folder_id, "")]
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"\n正在扫描子目录: {display_path} (ID: {current_id})")
            
            # 清空旧缓存
            if str(current_id) in captured_folder_data:
                del captured_folder_data[str(current_id)]

            # 构造文件夹直达 URL，让浏览器自己打开并加载数据
            folder_url = f"https://pc.woozooo.com/mydisk.php?item=files&action=index&folder_id={current_id}"
            await page.goto(folder_url, timeout=30000)
            
            # 等待拦截器抓到数据（最多等 10 秒）
            items = []
            for _ in range(20):
                if str(current_id) in captured_folder_data:
                    items = captured_folder_data.pop(str(current_id))
                    break
                await page.wait_for_timeout(500)
                
            if not items:
                print(f"  ⚠️ 等待超时，未截获数据")
                continue
            
            seen_sub = set()
            for item in items:
                unique_key = f"{item.get('name_all') or item.get('name')}_{item.get('id') or item.get('fol_id')}"
                if unique_key in seen_sub: continue
                seen_sub.add(unique_key)

                if 'fol_id' in item: # 子文件夹
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                    print(f"  > 子文件夹: {item['name']}")
                elif 'id' in item and 'name_all' in item: # 子文件
                    item_id = item['id']
                    item_name = item['name_all']
                    unique_key = f"{item_name}_{current_path}"
                    
                    if unique_key in seen_files: continue
                    seen_files.add(unique_key)
                    
                    # 【重点】既然不调用接口，我们直接使用响应里的 duan 短链！
                    share_url = ""
                    if item.get('duan'):
                        share_url = f"https://www.lanzouq.com/{item['duan']}"
                    
                    results.append({
                        "name": item_name,
                        "url": share_url,
                        "pwd": "",
                        "path": current_path,
                        "size": item.get('size', '0')
                    })
                    print(f"  + 文件: {item_name} (短链: {share_url})")

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
