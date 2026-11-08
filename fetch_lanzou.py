import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print(f"启动隐形浏览器，开始解析: {os.environ.get('FOLDER_URL')}")
    results = []
    
    start_url = f"{os.environ.get('FOLDER_URL')}?pwd={os.environ.get('GLOBAL_PWD')}"
    queue = [(start_url, "蓝奏云专属")]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 抹除 webdriver 自动化特征
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
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
        
        # 【绝招】拦截图片和字体，防止页面卡死
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())

        while queue:
            current_url, current_path = queue.pop(0)
            print(f"\n正在扫描: {current_path}")
            
            try:
                # 只要有网页框架就行，不强求网络完全空闲
                try:
                    await page.goto(current_url, timeout=15000, wait_until="domcontentloaded")
                except:
                    print(f"  [警告] 页面加载稍慢，强行尝试提取数据...")
                    
                await page.wait_for_timeout(2000) # 给 JS 留 2 秒执行时间
                
                title = await page.title()
                print(f"  当前页面标题: {title}")

                # 如果弹出了密码框
                if await page.locator("input[type='password'], input[name='pwd']").count() > 0:
                    print("  [检测到密码框，正在自动填写...]")
                    await page.fill("input[type='password'], input[name='pwd']", os.environ.get('GLOBAL_PWD'))
                    await page.press("input[type='password'], input[name='pwd']", "Enter")
                    await page.wait_for_timeout(3000) # 等待验证跳转
                    
                files_json_str = None
                
                # 方式一：直接从浏览器内存变量拿
                try:
                    files_json_str = await page.evaluate("() => { return typeof files !== 'undefined' ? JSON.stringify(files) : null; }")
                except: pass
                
                # 方式二：从网页源码正则匹配
                if not files_json_str:
                    html = await page.content()
                    match = re.search(r"var files = '(.*?)';", html, re.S) or re.search(r"var files = (\[.*?\]);", html, re.S)
                    if match:
                        files_json_str = match.group(1)
                
                if not files_json_str:
                    print(f"  ❌ 提取失败。页面内容可能不包含文件列表。")
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
