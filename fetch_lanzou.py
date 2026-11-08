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

        # 核心：监听所有响应，捕获 filemoreajax.php 的返回数据
        captured_files = None
        async def handle_response(response):
            nonlocal captured_files
            if "filemoreajax.php" in response.url:
                try:
                    text = await response.text()
                    print(f"  [网络捕获] 截获 filemoreajax.php，响应长度: {len(text)}")
                    # 蓝奏云此接口返回的通常是 JSON
                    data = json.loads(text)
                    # 兼容不同版本的返回结构
                    if isinstance(data, dict):
                        if 'text' in data and isinstance(data['text'], list):
                            captured_files = data['text']
                        elif 'data' in data and isinstance(data['data'], list):
                            captured_files = data['data']
                        elif isinstance(data, list):
                            captured_files = data
                    elif isinstance(data, list):
                        captured_files = data
                    if captured_files:
                        print(f"  [网络捕获] 成功解析到 {len(captured_files)} 个项目！")
                except Exception as e:
                    print(f"  [网络捕获] 解析响应失败: {e}")
        page.on("response", handle_response)

        while queue:
            current_url, current_path = queue.pop(0)
            print(f"\n{'='*40}\n正在扫描: {current_path}")
            captured_files = None # 重置
            
            try:
                try:
                    await page.goto(current_url, timeout=15000, wait_until="domcontentloaded")
                except:
                    pass
                
                await page.wait_for_timeout(2000)
                title = await page.title()
                print(f"  页面标题: {title}")

                # 尝试填入密码
                pwd_filled = False
                for frame in page.frames:
                    try:
                        inputs = await frame.locator("input").all()
                        for inp in inputs:
                            itype = await inp.get_attribute('type')
                            iname = await inp.get_attribute('name')
                            # 放宽条件
                            if itype == 'password' or iname == 'pwd' or (await inp.get_attribute('placeholder') and '密码' in (await inp.get_attribute('placeholder'))):
                                print(f"  [密码框] 在 frame 中发现: type={itype}, name={iname}")
                                await inp.fill(os.environ.get('GLOBAL_PWD'))
                                pwd_filled = True
                                btn = frame.locator("button:has-text('确认'), button:has-text('提交'), input[type='button'], input[type='submit'], .passwd")
                                if await btn.count() > 0:
                                    print("  [提交] 点击确认按钮")
                                    await btn.first.click()
                                else:
                                    print("  [提交] 按下回车键")
                                    await inp.press("Enter")
                                break
                    except: pass

                if pwd_filled:
                    # 提交后等待网络请求或页面变化
                    await page.wait_for_timeout(4000) 
                
                # 如果网络捕获成功，直接用
                if captured_files:
                    files_data = captured_files
                else:
                    # 否则，深度遍历所有 frame，寻找 var files 或直接的文件元素
                    print("  [回退] 网络未捕获，开始遍历所有 frame 查找数据...")
                    files_json_str = None
                    for idx, frame in enumerate(page.frames):
                        try:
                            f_url = frame.url
                            print(f"    - Frame [{idx}]: {f_url[:80]}...")
                            
                            # 打印部分源码片段用于分析
                            html = await frame.content()
                            snippet = html[:200].replace('\n', ' ')
                            print(f"      源码片段: {snippet}...")
                            
                            fj = await frame.evaluate("() => { return typeof files !== 'undefined' ? JSON.stringify(files) : null; }")
                            if fj and fj != 'null':
                                files_json_str = fj
                                print(f"      ✅ 在 Frame [{idx}] 内存中找到 files")
                                break
                            
                            match = re.search(r"var files = '(.*?)';", html, re.S) or re.search(r"var files = (\[.*?\]);", html, re.S)
                            if match:
                                files_json_str = match.group(1)
                                print(f"      ✅ 在 Frame [{idx}] 源码中找到 files")
                                break
                        except Exception as e:
                            print(f"      Frame [{idx}] 检查失败: {e}")

                    if files_json_str:
                        try:
                            files_data = json.loads(files_json_str)
                        except:
                            print("  ❌ JSON 解析失败，可能不是标准 JSON 格式。")
                            continue
                    else:
                        print("  ❌ 所有 frame 均未找到 files 变量。")
                        # 保存完整页面源码以便分析
                        html = await page.content()
                        with open("debug_full.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        print("  已保存完整页面源码至 debug_full.html")
                        # 如果页面提示密码错误
                        if "密码错误" in html or "密码不正确" in html:
                            print("  ⚠️ 页面提示密码错误，请检查 GLOBAL_PWD 是否正确。")
                        continue

                print(f"  ✅ 最终解析到 {len(files_data)} 个项目")
                
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
                        print(f"  + 文件: {item_name}")
                    elif item_type == '1': 
                        base_url = "https://" + page.url.split('/')[2]
                        folder_url = f"{base_url}/b011mmapdg?folder_id={item_id}&pwd={os.environ.get('GLOBAL_PWD')}"
                        next_path = f"{current_path}/{item_name}" if current_path != "蓝奏云专属" else f"蓝奏云专属/{item_name}"
                        queue.append((folder_url, next_path))
                        print(f"  > 文件夹: {item_name}")
                        
                await page.goto("about:blank")
                        
            except Exception as e:
                print(f"  ❌ 页面处理异常: {e}")
                
        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
