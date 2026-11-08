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
        # 拦截图片加快速度
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())

        while queue:
            current_url, current_path = queue.pop(0)
            print(f"\n正在扫描: {current_path}")
            
            try:
                try:
                    await page.goto(current_url, timeout=15000, wait_until="domcontentloaded")
                except:
                    pass
                
                await page.wait_for_timeout(2000)
                print(f"  当前页面标题: {await page.title()}")

                # 1. 在所有 iframe 中地毯式搜索密码框
                pwd_filled = False
                for frame in page.frames:
                    try:
                        inputs = await frame.locator("input").all()
                        for inp in inputs:
                            itype = await inp.get_attribute('type')
                            iname = await inp.get_attribute('name')
                            iplaceholder = await inp.get_attribute('placeholder')
                            
                            # 只要像密码框，就填
                            if itype == 'password' or iname == 'pwd' or (iplacholder and '密码' in iplacholder if iplacholder else False):
                                print(f"  [找到密码框] type={itype}, name={iname}")
                                await inp.fill(os.environ.get('GLOBAL_PWD'))
                                pwd_filled = True
                                
                                btn = frame.locator("button:has-text('确认'), button:has-text('提交'), input[type='button'], input[type='submit'], .passwd")
                                if await btn.count() > 0:
                                    print("  [点击确认按钮]")
                                    await btn.first.click()
                                else:
                                    print("  [按回车提交]")
                                    await inp.press("Enter")
                                await page.wait_for_timeout(3000)
                                break
                    except: pass

                if not pwd_filled:
                    print("  [无密码框，直接提取]")

                await page.wait_for_timeout(1500) # 给数据加载留点时间
                
                # 2. 在所有 iframe 中寻找文件列表
                files_json_str = None
                for frame in page.frames:
                    try:
                        # 方法1：读取内存
                        fj = await frame.evaluate("() => { return typeof files !== 'undefined' ? JSON.stringify(files) : null; }")
                        if fj and fj != 'null':
                            files_json_str = fj
                            print(f"  ✅ 成功从 frame 内存中抓取到数据！")
                            break
                        # 方法2：正则匹配
                        html = await frame.content()
                        match = re.search(r"var files = '(.*?)';", html, re.S) or re.search(r"var files = (\[.*?\]);", html, re.S)
                        if match:
                            files_json_str = match.group(1)
                            print(f"  ✅ 成功从 frame 源码中抓取到数据！")
                            break
                    except: pass
                
                if not files_json_str:
                    print(f"  ❌ 提取失败，所有 frame 中都没找到 files 变量。")
                    continue
                    
                files_data = json.loads(files_json_str)
                print(f"  ✅ 解析完毕！找到 {len(files_data)} 个项目")
                
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
                        
                await page.goto("about:blank")
                        
            except Exception as e:
                print(f"  ❌ 页面处理异常: {e}")
                
        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
