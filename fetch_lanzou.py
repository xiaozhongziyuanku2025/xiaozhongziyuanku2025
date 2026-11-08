import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import json, re, os, random

async def main():
    print(f"启动拟真浏览器，开始解析: {os.environ.get('FOLDER_URL')}")
    results = []
    
    start_url = f"{os.environ.get('FOLDER_URL')}?pwd={os.environ.get('GLOBAL_PWD')}"
    queue = [(start_url, "蓝奏云专属")]
    
    async with async_playwright() as p:
        # headless=False 在本地可以看到浏览器弹出来，服务器上必须用 True
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": random.randint(1200, 1400), "height": random.randint(800, 900)},
            device_scale_factor=1,
            has_touch=False
        )
        
        # 注入 Cookie
        cookie_str = os.environ.get('LANZOU_COOKIE', '')
        if cookie_str:
            print("✅ 检测到 Cookie，正在注入...")
            cookies = []
            for item in cookie_str.split(';'):
                if '=' in item:
                    k, v = item.strip().split('=', 1)
                    cookies.append({'name': k, 'value': v, 'url': 'https://wwbmd.lanzout.com'})
                    cookies.append({'name': k, 'value': v, 'url': 'https://www.lanzouq.com'})
            await context.add_cookies(cookies)

        page = await context.new_page()
        
        # 【核心】开启隐身模式，抹除 webdriver、Chrome 自动化特征
        await stealth_async(page)
        
        # 拦截多余资源，加快速度
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())

        while queue:
            current_url, current_path = queue.pop(0)
            print(f"\n正在扫描: {current_path}")
            
            try:
                # 模拟真人随机延迟后再打开网页
                await asyncio.sleep(random.uniform(1.0, 2.5))
                
                try:
                    await page.goto(current_url, timeout=20000, wait_until="domcontentloaded")
                except Exception:
                    print(f"  [警告] 页面加载超时，尝试强行提取...")
                    
                await page.wait_for_timeout(random.randint(2000, 4000))
                
                # 模拟真人输入密码
                if await page.locator("input[type='password'], input[name='pwd']").count() > 0:
                    print("  [检测到密码框，开始模拟真人输入...]")
                    pwd_input = page.locator("input[type='password'], input[name='pwd']").first
                    await pwd_input.click()
                    await pwd_input.type(os.environ.get('GLOBAL_PWD'), delay=random.randint(100, 250))
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(random.randint(3000, 5000))
                    
                files_json_str = None
                try:
                    files_json_str = await page.evaluate("() => { return typeof files !== 'undefined' ? JSON.stringify(files) : null; }")
                except: pass
                
                if not files_json_str:
                    html = await page.content()
                    match = re.search(r"var files = '(.*?)';", html, re.S) or re.search(r"var files = (\[.*?\]);", html, re.S)
                    if match:
                        files_json_str = match.group(1)
                
                if not files_json_str:
                    print(f"  ❌ 提取失败，页面可能触发了验证码。")
                    continue
                    
                files_data = json.loads(files_json_str)
                print(f"  ✅ 成功提取！找到 {len(files_data)} 个项目")
                
                for item in files_data:
                    item_type = str(item.get('type'))
                    item_id = item.get('id')
                    item_name = item.get('name_all') or item.get('name')
                    item_size = item.get('size', '0')
                    
                    if item_type == '0': 
                        base_url = "https://" + page.url.split('/')[2]
                        results.append({
                            "name": item_name,
                            "url": f"{base_url}/b011mmapdg_{item_id}",
                            "pwd": os.environ.get('GLOBAL_PWD'),
                            "path": current_path,
                            "size": item_size
                        })
                        print(f"  + 获取文件: {item_name}")
                    elif item_type == '1': 
                        base_url = "https://" + page.url.split('/')[2]
                        folder_url = f"{base_url}/b011mmapdg?folder_id={item_id}&pwd={os.environ.get('GLOBAL_PWD')}"
                        next_path = f"{current_path}/{item_name}" if current_path != "蓝奏云专属" else f"蓝奏云专属/{item_name}"
                        queue.append((folder_url, next_path))
                        print(f"  > 发现子文件夹: {item_name}")
            except Exception as e:
                print(f"  ❌ 页面处理异常: {e}")
                
        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
