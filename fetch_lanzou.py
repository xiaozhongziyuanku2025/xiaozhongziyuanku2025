import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动终极 UI 拟真点击版爬虫...")
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
        captured_share_data = {} # 用于截获点击分享后生成的链接

        async def handle_response(response):
            if "doupload.php" in response.url:
                try:
                    post_data = response.request.post_data or ""
                    data = await response.json()
                    
                    # 监听文件夹数据
                    match = re.search(r"folder_id=(-?\d+)", post_data)
                    if match and "task=task_list" in post_data:
                        fid = match.group(1)
                        if data.get('zt') == 1 and isinstance(data.get('text'), list):
                            if fid not in captured_folder_data:
                                captured_folder_data[fid] = []
                            captured_folder_data[fid].extend(data.get('text', []))
                            
                    # 监听分享数据
                    if "task=file_share" in post_data and data.get('zt') == 1:
                        file_id_match = re.search(r"file_id=(\d+)", post_data)
                        if file_id_match:
                            fid = file_id_match.group(1)
                            url = data.get('info') or data.get('url') or ''
                            pwd = data.get('pwd', '')
                            if url and not url.startswith("http"):
                                url = f"https://www.lanzouq.com/{url}"
                            captured_share_data[fid] = {"url": url, "pwd": pwd}
                            print(f"    [网络截获] 成功获取到 file_id {fid} 的分享链接！")
                except: pass
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
            await browser.close()
            return
        
        print("✅ 登录成功！正在进入网盘...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(5000)

        # UI 拟真获取分享链接的函数
        async def get_share_url_by_ui(file_name, file_id):
            try:
                # 1. 定位包含该文件名的表格行 (tr)
                row = page.locator(f"tr:has-text('{file_name}')").first
                if await row.count() == 0:
                    return "", ""
                
                # 2. 找该行内的“更多/三个点”按钮 (通常有 title="更多" 或包含相关图标)
                # 蓝奏云的三个点按钮通常带 onclick="show_menu(...)" 或是个 <a> 标签
                more_btn = row.locator("a[onclick*='show_menu'], a[title='更多'], .file_menus, i.fa-ellipsis-h").first
                if await more_btn.count() == 0:
                    # 如果找不到，尝试定位该行最后一个 a 标签（通常是操作菜单）
                    more_btn = row.locator("a").last
                
                await more_btn.hover() # 鼠标悬停
                await page.wait_for_timeout(500)
                await more_btn.click(force=True) # 强制点击，防止被遮挡
                await page.wait_for_timeout(1000)
                
                # 3. 在弹出的菜单中找“外链分享”按钮
                share_btn = page.locator("text='外链分享', a:has-text('分享')").first
                if await share_btn.count() > 0:
                    await share_btn.click()
                    print(f"    [UI操作] 点击了外链分享，等待弹窗...")
                    await page.wait_for_timeout(3000) # 等待接口返回并被 handle_response 截获
                else:
                    print(f"    ❌ 未找到外链分享按钮")
                    return "", ""
                
                # 检查是否截获成功
                if file_id in captured_share_data:
                    res = captured_share_data.pop(file_id)
                    return res['url'], res['pwd']
                else:
                    print(f"    ❌ 等待分享数据截获超时")
                    return "", ""
                    
            except Exception as e:
                print(f"    ❌ UI 操作异常: {e}")
                return "", ""

        # 1. 处理根目录
        root_items = captured_folder_data.get('-1', [])
        target_folder_id = None
        seen_root = set()

        for item in root_items:
            unique_key = f"{item.get('name_all') or item.get('name')}_{item.get('id') or item.get('fol_id')}"
            if unique_key in seen_root: continue
            seen_root.add(unique_key)

            if 'name_all' in item: 
                item_name = item.get('name_all')
                item_id = str(item.get('id'))
                print(f"  + 正在处理根目录文件: {item_name}")
                share_url, pwd = await get_share_url_by_ui(item_name, item_id)
                results.append({
                    "name": item_name,
                    "url": share_url,
                    "pwd": pwd,
                    "path": "", 
                    "size": item.get('size', '0')
                })
            elif 'fol_id' in item: 
                if target_folder_name in item.get('name', ''):
                    target_folder_id = item.get('fol_id')
                    print(f"✅ 找到目标文件夹【{item.get('name')}】，ID: {target_folder_id}")

        if not target_folder_id:
            print("❌ 未找到目标文件夹")
            await browser.close()
            return

        # 2. 深度遍历子文件夹
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
                continue
            
            seen_sub = set()
            for item in items:
                unique_key = f"{item.get('name_all') or item.get('name')}_{item.get('id') or item.get('fol_id')}"
                if unique_key in seen_sub: continue
                seen_sub.add(unique_key)

                if 'fol_id' in item: 
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                    print(f"  > 子文件夹: {item['name']}")
                elif 'id' in item and 'name_all' in item: 
                    item_id = str(item['id'])
                    item_name = item['name_all']
                    unique_key = f"{item_name}_{current_path}"
                    
                    if unique_key in seen_files: continue
                    seen_files.add(unique_key)
                    
                    print(f"  + 正在处理文件: {item_name}")
                    share_url, pwd = await get_share_url_by_ui(item_name, item_id)
                    
                    results.append({
                        "name": item_name,
                        "url": share_url,
                        "pwd": pwd,
                        "path": current_path,
                        "size": item.get('size', '0')
                    })
                    await page.wait_for_timeout(500)

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
