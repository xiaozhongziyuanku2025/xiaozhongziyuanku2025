import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动全拟真混合架构爬虫 (纯浏览器拦截版)...")
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

        # 【核心】只拦截浏览器发出的原生请求，绝不自己发
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
                            captured_folder_data[fid].extend(data.get('text', []))
                            print(f"  [网络截获] 文件夹 {fid} 数据，新增 {len(data.get('text', []))} 项")
                        else:
                            print(f"  [网络截获] 文件夹 {fid} 数据返回异常: {data}")
                except Exception as e:
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
            print(f"❌ 登录操作异常: {e}")

        if "mydisk" not in page.url:
            print(f"❌ 登录失败，当前 URL: {page.url}")
            return
        
        print("✅ 登录成功！正在进入网盘...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(5000)

        # --- 1. 从拦截到的数据里找“小众资源库” ---
        print("\n[阶段一] 解析根目录...")
        # 蓝奏云可能会发 -1 或 0 的请求
        root_items = captured_folder_data.get('-1', []) or captured_folder_data.get('0', [])
        
        if not root_items:
            print("⚠️ 未截获到根目录的任何数据。网页可能还没加载完。")
            
        target_folder_id = None
        seen_root = set()

        for item in root_items:
            item_name = item.get('name_all') or item.get('name')
            unique_key = f"{item_name}_{item.get('id') or item.get('fol_id')}"
            if unique_key in seen_root: continue
            seen_root.add(unique_key)

            if 'name_all' in item: # 根目录文件
                results.append({
                    "name": item_name, "url": f"https://www.lanzouq.com/{item.get('duan')}" if item.get('duan') else "",
                    "pwd": "", "path": "", "size": item.get('size', '0')
                })
                print(f"  + 根目录文件: {item_name}")
            elif 'fol_id' in item: # 根目录文件夹
                print(f"  > 发现文件夹: {item_name}")
                if target_folder_name in item_name:
                    target_folder_id = item.get('fol_id')
                    print(f"✅ 找到目标文件夹【{item_name}】，ID: {target_folder_id}")

        if not target_folder_id:
            print("❌ 未找到目标文件夹，退出。")
            return

        # --- 2. 深度遍历 ---
        print("\n[阶段二] 开始深度遍历...")
        queue = [(target_folder_id, "")]
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"\n正在扫描子目录: {display_path} (ID: {current_id})")
            
            if str(current_id) in captured_folder_data:
                del captured_folder_data[str(current_id)]

            folder_url = f"https://pc.woozooo.com/mydisk.php?item=files&action=index&folder_id={current_id}"
            await page.goto(folder_url, timeout=30000)
            
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
                item_name = item.get('name_all') or item.get('name')
                unique_key = f"{item_name}_{item.get('id') or item.get('fol_id')}"
                if unique_key in seen_sub: continue
                seen_sub.add(unique_key)

                if 'fol_id' in item: 
                    next_path = f"{current_path}/{item_name}" if current_path else item_name
                    queue.append((item['fol_id'], next_path))
                    print(f"  > 子文件夹: {item_name}")
                elif 'id' in item and 'name_all' in item: 
                    item_name = item['name_all']
                    unique_key = f"{item_name}_{current_path}"
                    if unique_key in seen_files: continue
                    seen_files.add(unique_key)
                    
                    # 纯用 duan 短链，不发额外请求
                    share_url = f"https://www.lanzouq.com/{item['duan']}" if item.get('duan') else ""

                    results.append({
                        "name": item_name, "url": share_url, "pwd": "",
                        "path": current_path, "size": item.get('size', '0')
                    })
                    print(f"  + 文件: {item_name} (短链: {share_url})")

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
