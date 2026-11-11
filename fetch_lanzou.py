import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动守株待兔版终极爬虫...")
    account = os.environ.get('LANZOU_ACCOUNT')
    password = os.environ.get('LANZOU_PASSWORD')

    if not account or not password:
        print("❌ 缺少账号或密码环境变量")
        return

    results = []
    # ⚠️ 这里已改回精准的名字：小众资源库
    target_folder_name = "小众资源库" 

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # 准备用于保存网络截获的数据
        captured_folders = None
        captured_root_files = None

        async def handle_response(response):
            nonlocal captured_folders, captured_root_files
            if "doupload.php" in response.url:
                try:
                    data = await response.json()
                    if data.get('zt') == 1 and isinstance(data.get('text'), list):
                        items = data['text']
                        # 如果列表里有 fol_id，说明这是文件夹列表
                        if len(items) > 0 and 'fol_id' in items[0]:
                            captured_folders = items
                            print(f"  [网络截获] 拿到根目录文件夹列表！共 {len(items)} 个文件夹")
                        # 如果列表里有 id 和 name_all，说明这是文件列表
                        elif len(items) > 0 and 'name_all' in items[0]:
                            captured_root_files = items
                            print(f"  [网络截获] 拿到根目录文件列表！共 {len(items)} 个文件")
                except:
                    pass
        page.on("response", handle_response)

        print("正在访问登录页...")
        await page.goto("https://accounts.woozooo.com/accounts.php?action=login&ref=pc.woozooo.com", timeout=30000)
        await page.wait_for_timeout(2000)

        # 登录
        try:
            print("正在输入账号密码...")
            await page.fill("#username", account)
            await page.fill(".input.pwd", password)
            await page.click("#s3")
            await page.wait_for_timeout(5000) # 等待登录并触发页面加载
        except Exception as e:
            print(f"❌ 填写表单失败: {e}")

        if "mydisk" not in page.url:
            print(f"❌ 登录失败，当前 URL: {page.url}")
            return
        
        print("✅ 登录成功！等待网盘数据加载完毕...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(5000) # 给浏览器充足的时间去发请求

        # --- 1. 解析根目录文件 ---
        if captured_root_files:
            for item in captured_root_files:
                results.append({
                    "name": item.get('name_all'),
                    "url": "", 
                    "pwd": "",
                    "path": "", # 根目录文件路径为空
                    "size": item.get('size', '0')
                })
                print(f"  + 发现根目录文件: {item.get('name_all')}")
        else:
            print("⚠️ 未截获到根目录文件列表")

        # --- 2. 查找目标文件夹 ID ---
        target_folder_id = None
        if captured_folders:
            for folder in captured_folders:
                # 精准匹配“小众资源库”
                if folder.get('name') == target_folder_name:
                    target_folder_id = folder.get('fol_id')
                    print(f"✅ 在文件夹列表中找到【{target_folder_name}】，ID: {target_folder_id}")
                    break
            
            if not target_folder_id:
                print(f"❌ 没找到名为【{target_folder_name}】的文件夹。")
                print(f"   >>> 你账号里截获到的文件夹有: {[f.get('name') for f in captured_folders]}")
                return
        else:
            print("❌ 未截获到任何文件夹列表！")
            return

        # --- 3. 深度遍历子文件夹 ---
        queue = [(target_folder_id, "")] # path 默认为空
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"\n正在扫描子目录: {display_path} (ID: {current_id})")
            
            folder_res = await page.evaluate(f"""async () => {{
                const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': 'https://pc.woozooo.com/mydisk.php'
                    }},
                    body: 'task=task_list&folder_id={current_id}'
                }});
                return await res.text();
            }}""")
            
            try:
                folder_data = json.loads(folder_res)
            except:
                print(f"  ❌ JSON 解析失败: {folder_res[:100]}")
                continue
                
            if folder_data.get('zt') != 1:
                print(f"  ❌ 接口返回错误，可能请求头被拦截: {folder_data}")
                continue
                
            items = folder_data.get('text', [])
            if not isinstance(items, list):
                print(f"  ✅ 目录为空")
                continue
                
            print(f"  ✅ 获取到 {len(items)} 个项目")
            
            for item in items:
                if 'fol_id' in item: 
                    # 是文件夹
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                    print(f"  > 子文件夹: {item['name']}")
                elif 'id' in item and 'name_all' in item:
                    # 是文件
                    item_id = item['id']
                    item_name = item['name_all']
                    item_size = item.get('size', '0')
                    
                    print(f"  + 正在处理文件: {item_name}")
                    # 获取分享链接
                    share_res = await page.evaluate(f"""async () => {{
                        const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'X-Requested-With': 'XMLHttpRequest',
                                'Referer': 'https://pc.woozooo.com/mydisk.php'
                            }},
                            body: 'task=file_share&file_id={item_id}'
                        }});
                        return await res.text();
                    }}""")
                    
                    try:
                        share_data = json.loads(share_res)
                        if share_data.get('zt') == 1:
                            share_url = share_data.get('info') or share_data.get('url') or ''
                            pwd = share_data.get('pwd', '')
                            
                            if share_url and not share_url.startswith("http"):
                                share_url = f"https://www.lanzouq.com/{share_url}"
                            
                            results.append({
                                "name": item_name,
                                "url": share_url,
                                "pwd": pwd,
                                "path": current_path,
                                "size": item_size
                            })
                            print(f"    ✅ 获取分享链接: {share_url}")
                        else:
                            print(f"    ❌ 分享失败: {share_data}")
                    except:
                        pass
                    await page.wait_for_timeout(500)

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
