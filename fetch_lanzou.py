import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动终极拦截版爬虫...")
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

        # 截获的数据池
        captured_folder_data = {}

        async def handle_response(response):
            if "doupload.php" in response.url:
                try:
                    post_data = response.request.post_data or ""
                    # 只要请求里带了 folder_id，就截获
                    match = re.search(r"folder_id=(-?\d+)", post_data)
                    if match:
                        fid = match.group(1)
                        data = await response.json()
                        if data.get('zt') == 1:
                            items = data.get('text', [])
                            if isinstance(items, list):
                                if fid not in captured_folder_data:
                                    captured_folder_data[fid] = []
                                # 【核心修复】使用 extend 追加数据，绝不让后面的文件列表覆盖前面的文件夹列表
                                captured_folder_data[fid].extend(items)
                                print(f"  [网络截获] 拿到文件夹 {fid} 的数据，新增 {len(items)} 个项目")
                except Exception as e:
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
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"❌ 填写表单失败: {e}")

        if "mydisk" not in page.url:
            print(f"❌ 登录失败，当前 URL: {page.url}")
            return
        
        print("✅ 登录成功！等待网盘数据加载完毕...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(5000)

        # --- 1. 处理根目录 ---
        # 把 -1 和 0 的数据都合并起来
        root_items = []
        root_items.extend(captured_folder_data.get('-1', []))
        root_items.extend(captured_folder_data.get('0', []))
        
        target_folder_id = None
        if root_items:
            for item in root_items:
                if 'name_all' in item: # 是文件
                    results.append({
                        "name": item.get('name_all'),
                        "url": "",
                        "pwd": "",
                        "path": "", # 根目录为空
                        "size": item.get('size', '0')
                    })
                    print(f"  + 发现根目录文件: {item.get('name_all')}")
                elif 'fol_id' in item: # 是文件夹
                    if item.get('name') == target_folder_name:
                        target_folder_id = item.get('fol_id')
                        print(f"✅ 在根目录中找到【{target_folder_name}】，ID: {target_folder_id}")
        else:
            print("⚠️ 未截获到根目录数据")
            return

        if not target_folder_id:
            print(f"❌ 未找到名为【{target_folder_name}】的文件夹。")
            return

        # --- 2. 深度遍历子文件夹 ---
        queue = [(target_folder_id, "")]
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"\n正在扫描子目录: {display_path} (ID: {current_id})")
            
            # 每次进入新文件夹前，先清空一下之前的截获记录，防止混淆
            if str(current_id) in captured_folder_data:
                del captured_folder_data[str(current_id)]

            # 直接让浏览器跳转到该文件夹
            folder_url = f"https://pc.woozooo.com/mydisk.php?item=files&action=index&folder_id={current_id}"
            await page.goto(folder_url, timeout=30000)
            
            # 等待拦截器拿到数据
            items = []
            for _ in range(15):
                if str(current_id) in captured_folder_data:
                    items = captured_folder_data.pop(str(current_id))
                    break
                await page.wait_for_timeout(500)
                
            if not items:
                print(f"  ⚠️ 等待超时，未截获到 {current_id} 的数据")
                continue
                
            for item in items:
                if 'fol_id' in item: # 是文件夹
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                    print(f"  > 子文件夹: {item['name']}")
                elif 'id' in item and 'name_all' in item: # 是文件
                    item_id = item['id']
                    item_name = item['name_all']
                    item_size = item.get('size', '0')
                    print(f"  + 正在处理文件: {item_name}")
                    
                    # 文件分享链接
                    share_res = await page.evaluate(f"""async () => {{
                        const res = await fetch('https://pc.woozooo.com/doupload.php?uid={account}', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'X-Requested-With': 'XMLHttpRequest',
                                'Referer': window.location.href
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
                    except Exception as e:
                        print(f"    ❌ 解析分享响应异常: {e}")
                    await page.wait_for_timeout(300)

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
