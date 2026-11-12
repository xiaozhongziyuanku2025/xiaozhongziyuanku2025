import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动「网络劫持+无脑点击」终极版...")
    account = os.environ.get('LANZOU_ACCOUNT')
    password = os.environ.get('LANZOU_PASSWORD')

    if not account or not password:
        print("❌ 缺少账号或密码环境变量")
        return

    results = []
    target_folder_name = "小众资源库"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        captured_folder_data = {}
        captured_share_info = None

        # 深度监听所有网络响应
        async def handle_response(response):
            nonlocal captured_share_info
            if "doupload.php" in response.url:
                try:
                    data = await response.json()
                    if not isinstance(data, dict): return
                    
                    # 1. 捕获文件夹列表
                    post_data = response.request.post_data or ""
                    match = re.search(r"folder_id=(-?\d+)", post_data)
                    if match and data.get('zt') == 1 and isinstance(data.get('text'), list):
                        fid = match.group(1)
                        if fid not in captured_folder_data:
                            captured_folder_data[fid] = []
                        captured_folder_data[fid].extend(data.get('text', []))
                        print(f"    [网络截获] 拿到目录 {fid} 数据，共 {len(data.get('text'))} 项")

                    # 2. 捕获分享信息 (你提供的关键数据结构)
                    if data.get('zt') == 1 and isinstance(data.get('info'), dict) and 'f_id' in data['info']:
                        captured_share_info = data['info']
                        print(f"    🟢 [网络劫持] 截获分享信息！f_id: {captured_share_info['f_id']}, pwd: {captured_share_info.get('pwd', '')}")
                except: pass
        page.on("response", handle_response)

        # ================= 登录 =================
        print("正在访问登录页...")
        await page.goto("https://accounts.woozooo.com/accounts.php?action=login&ref=pc.woozooo.com", timeout=30000)
        await page.wait_for_timeout(2000)

        try:
            await page.fill("#username", account)
            await page.fill(".input.pwd", password)
            await page.click("#s3")
            print("等待登录完成...")
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"❌ 登录异常: {e}")

        if "mydisk" not in page.url:
            print(f"❌ 登录失败，当前 URL: {page.url}")
            await browser.close()
            return

        print("✅ 登录成功！正在进入网盘主页...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(4000)

        # 寻找目标文件夹
        root_items = captured_folder_data.get('-1', [])
        target_folder_id = None
        for item in root_items:
            if 'fol_id' in item and target_folder_name in item.get('name', ''):
                target_folder_id = item.get('fol_id')
                print(f"✅ 找到目标文件夹【{target_folder_name}】，ID: {target_folder_id}")
                break

        if not target_folder_id:
            print("❌ 未找到目标文件夹")
            await browser.close()
            return

        # ================= 深度遍历 =================
        queue = [(target_folder_id, "")]
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"\n📂 正在扫描目录: {display_path}")
            
            if str(current_id) in captured_folder_data:
                del captured_folder_data[str(current_id)]

            folder_url = f"https://pc.woozooo.com/mydisk.php?item=files&action=index&folder_id={current_id}"
            await page.goto(folder_url, timeout=30000)
            await page.wait_for_timeout(3000)
            
            items = []
            for _ in range(10):
                if str(current_id) in captured_folder_data:
                    items = captured_folder_data.pop(str(current_id))
                    break
                await page.wait_for_timeout(500)
                
            if not items:
                print("  ⚠️ 未截获到该目录文件数据")
                continue

            for item in items:
                # 处理子文件夹
                if 'fol_id' in item:
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                    print(f"  > 发现子文件夹: {item['name']}")
                
                # 处理文件：点击并截获
                elif 'id' in item and 'name_all' in item:
                    item_name = item['name_all']
                    item_size = item.get('size', '0')
                    
                    print(f"\n  + 正在点击文件: {item_name}")
                    captured_share_info = None # 每次点击前清空上次的数据
                    
                    try:
                        # 使用模糊匹配点击，应对文件名过长被截断的问题
                        # 截取文件名前10个字符去定位元素，确保能点到
                        search_text = item_name[:10] if len(item_name) > 10 else item_name
                        locator = page.get_by_text(search_text).first
                        
                        if await locator.count() > 0:
                            await locator.click(force=True)
                            print("    🖱️ 已点击，等待网络响应...")
                            
                            # 等待网络劫持
                            for _ in range(10):
                                if captured_share_info:
                                    break
                                await page.wait_for_timeout(300)
                                
                            if captured_share_info:
                                domain = captured_share_info.get('is_newd', 'https://wwbmd.lanzn.com')
                                f_id = captured_share_info.get('f_id', '')
                                pwd = captured_share_info.get('pwd', '')
                                full_url = f"{domain}/{f_id}"
                                
                                print(f"    ✅ 拼接链接成功: {full_url} | 密码: {pwd}")
                                
                                # 去重并添加
                                if not any(r['name'] == item_name and r['path'] == current_path for r in results):
                                    results.append({
                                        "name": item_name,
                                        "url": full_url,
                                        "pwd": pwd,
                                        "path": current_path,
                                        "size": item_size
                                    })
                            else:
                                print(f"    ❌ 超时：未截获到该文件的分享数据。")
                        else:
                            print(f"    ❌ 页面上找不到文件名 '{search_text}'")
                            
                    except Exception as e:
                        print(f"    ❌ 点击或处理异常: {e}")

        await browser.close()

    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
