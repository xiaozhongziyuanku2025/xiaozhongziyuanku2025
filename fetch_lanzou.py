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
        
        # 抹除自动化特征
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
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
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())

        while queue:
            current_url, current_path = queue.pop(0)
            print(f"\n正在扫描: {current_path}")
            
            try:
                try:
                    await page.goto(current_url, timeout=15000, wait_until="domcontentloaded")
                except:
                    pass
                
                await page.wait_for_timeout(1000) # 基础等待

                # 检查是否有密码框
                pwd_locator = page.locator("input[name='pwd'], input[type='password']")
                if await pwd_locator.count() > 0:
                    print("  [检测到密码框，正在输入并点击按钮...]")
                    pwd_input = pwd_locator.first
                    await pwd_input.fill(os.environ.get('GLOBAL_PWD'))
                    await page.wait_for_timeout(500) # 假装人类停顿
                    
                    # 智能寻找提交按钮
                    submit_btn = page.locator("button:has-text('确认'), button:has-text('提交'), input[type='button'], input[type='submit'], .passwd, .btn-passwd")
                    
                    if await submit_btn.count() > 0:
                        print("  [找到确认按钮，正在点击...]")
                        await submit_btn.first.click()
                    else:
                        print("  [未找到明确按钮，尝试按回车...]")
                        await pwd_input.press("Enter")
                    
                    # 等待页面响应，等待密码框消失或者文件加载出来
                    try:
                        await page.wait_for_function("() => typeof files !== 'undefined' && files.length >= 0", timeout=10000)
                        print("  [页面数据加载完毕！]")
                    except Exception:
                        print("  [等待列表加载超时，可能密码错误或网络卡顿]")
                        await page.wait_for_timeout(3000) # 再死等一会儿
                
                # 提取数据
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
                    print(f"  ❌ 提取失败，页面可能还在密码页。当前标题: {await page.title()}")
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
                        
                # 清理状态，准备进入下一个目录
                await page.goto("about:blank")
                        
            except Exception as e:
                print(f"  ❌ 页面处理异常: {e}")
                
        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
