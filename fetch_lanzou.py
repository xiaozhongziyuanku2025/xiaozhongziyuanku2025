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
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        cookie_str = os.environ.get('LANZOU_COOKIE', '')
        if cookie_str:
            cookies = []
            for item in cookie_str.split(';'):
                if '=' in item:
                    k, v = item.strip().split('=', 1)
                    cookies.append({'name': k, 'value': v, 'url': 'https://wwbmd.lanzout.com'})
                    cookies.append({'name': k, 'value': v, 'url': 'https://www.lanzouq.com'})
            await context.add_cookies(cookies)

        page = await context.new_page()
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())

        captured_data = None
        async def handle_response(response):
            nonlocal captured_data
            if "filemoreajax.php" in response.url:
                try:
                    text = await response.text()
                    data = json.loads(text)
                    if isinstance(data, dict) and 'text' in data and isinstance(data['text'], list):
                        captured_data = data['text']
                    elif isinstance(data, list):
                        captured_data = data
                except: pass
        page.on("response", handle_response)

        while queue:
            current_url, current_path = queue.pop(0)
            print(f"\n正在扫描: {current_path}")
            captured_data = None
            
            try:
                try:
                    await page.goto(current_url, timeout=15000, wait_until="domcontentloaded")
                except: pass
                
                await page.wait_for_timeout(2000)

                # 填密码
                pwd_filled = False
                for frame in page.frames:
                    try:
                        inputs = await frame.locator("input").all()
                        for inp in inputs:
                            itype = await inp.get_attribute('type')
                            iname = await inp.get_attribute('name')
                            if itype == 'password' or iname == 'pwd' or (await inp.get_attribute('placeholder') and '密码' in (await inp.get_attribute('placeholder'))):
                                await inp.fill(os.environ.get('GLOBAL_PWD'))
                                pwd_filled = True
                                btn = frame.locator("button:has-text('确认'), button:has-text('提交'), input[type='button'], input[type='submit'], .passwd")
                                if await btn.count() > 0:
                                    await btn.first.click()
                                else:
                                    await inp.press("Enter")
                                break
                    except: pass

                if pwd_filled:
                    await page.wait_for_timeout(4000) 
                
                if not captured_data:
                    print("  ❌ 网络没有截获到 filemoreajax.php 数据！")
                    continue

                files_data = captured_data
                print(f"  ✅ 成功截获 {len(files_data)} 个项目，开始解析层级...")
                
                for item in files_data:
                    # 【核心修复1】蓝奏云返回的是 t，而不是 type
                    item_type = str(item.get('t')) 
                    
                    # 【核心修复2】把 id 后面的乱码尾巴切掉
                    raw_id = item.get('id', '')
                    item_id = raw_id.split('?')[0] 
                    
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
                    else:
                        print(f"  ⚠️ 未知项目: {item}")

                await page.goto("about:blank")
                        
            except Exception as e:
                print(f"  ❌ 页面处理异常: {e}")
                
        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
