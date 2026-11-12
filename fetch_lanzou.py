import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动「接口直连」终极稳定版爬虫...")
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

        # 监听文件夹数据
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
                            # 去重累加
                            for item in data.get('text', []):
                                if item not in captured_folder_data[fid]:
                                    captured_folder_data[fid].append(item)
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

        # ================= 获取分享链接的函数 =================
        async def get_share_link(file_id):
            try:
                # 【核心修复】只传 file_id，绝不再传 folder_id！
                res_text = await page.evaluate(f"""async () => {{
                    const formData = new URLSearchParams();
                    formData.append('task', 'file_share');
                    formData.append('file_id', '{file_id}');
                    
                    const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest'
                        }},
                        body: formData.toString()
                    }});
                    return await res.text();
                }}""")
                
                data = json.loads(res_text)
                if data.get('zt') == 1:
                    url = data.get('info') or data.get('url') or ''
                    pwd = data.get('pwd', '')
                    if url and not url.startswith("http"):
                        url = f"https://www.lanzouq.com/{url}"
                    return url, pwd
                else:
                    print(f"    ⚠️ 接口返回异常: {data.get('info')}")
                    return "", ""
            except Exception as e:
                print(f"    ❌ 获取分享异常: {e}")
                return "", ""

        # ================= 寻找目标文件夹 =================
        root_items = captured_folder_data.get('-1', [])
        target_folder_id = None

        for item in root_items:
            if 'fol_id' in item and target_folder_name in item.get('name', ''):
                target_folder_id = item.get('fol_id')
                print(f"✅ 从后台拦截数据中找到【{target_folder_name}】，ID: {target_folder_id}")
                break

        if not target_folder_id:
            print("❌ 未在根目录找到目标文件夹，退出。")
            await browser.close()
            return

        # ================= 深度遍历文件夹 =================
        queue = [(target_folder_id, "")]
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"\n📂 正在扫描目录: {display_path}")
            
            if str(current_id) in captured_folder_data:
                del captured_folder_data[str(current_id)]

            folder_url = f"https://pc.woozooo.com/mydisk.php?item=files&action=index&folder_id={current_id}"
            await page.goto(folder_url, timeout=30000)
            await page.wait_for_timeout(3000) # 等待请求截获
            
            items = []
            for _ in range(10):
                if str(current_id) in captured_folder_data:
                    items = captured_folder_data.pop(str(current_id))
                    break
                await page.wait_for_timeout(500)
                
            if not items:
                print("  ⚠️ 未截获到该目录数据")
                continue

            for item in items:
                # 如果是文件夹，加入队列
                if 'fol_id' in item:
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                    print(f"  > 发现子文件夹: {item['name']}")
                
                # 如果是文件，直接调用接口拿链接
                elif 'id' in item and 'name_all' in item:
                    item_id = str(item['id'])
                    item_name = item['name_all']
                    item_size = item.get('size', '0')
                    
                    print(f"  + 正在解析文件: {item_name}")
                    share_url, pwd = await get_share_link(item_id)
                    
                    if share_url:
                        print(f"    ✅ 获取成功: {share_url} (密码: {pwd})")
                    else:
                        print(f"    ❌ 获取失败")
                        
                    results.append({
                        "name": item_name,
                        "url": share_url,
                        "pwd": pwd,
                        "path": current_path,
                        "size": item_size
                    })
                    await page.wait_for_timeout(300) # 防封

        await browser.close()

    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
