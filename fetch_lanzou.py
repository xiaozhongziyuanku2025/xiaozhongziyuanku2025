import asyncio
from playwright.async_api import async_playwright
import json, re, os, random

async def main():
    print("🚀 启动终极拟真探测爬虫...")
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
        
        # 监听所有返回的网络请求，打印出来供分析
        async def log_response(response):
            if "doupload.php" in response.url or "mydisk.php" in response.url:
                try:
                    text = await response.text()
                    print(f"  [网络监控] 捕获 URL: {response.url}")
                    print(f"  [网络监控] 响应片段: {text[:200]}")
                except: pass
        page.on("response", log_response)

        print("正在访问登录页...")
        await page.goto("https://accounts.woozooo.com/accounts.php?action=login&ref=pc.woozooo.com", timeout=30000)
        await page.wait_for_timeout(2000)

        # --- 登录流程 ---
        try:
            print("正在输入账号密码...")
            await page.fill("#username", account)
            await page.fill(".input.pwd", password)
            print("点击登录...")
            await page.click("#s3")
            await page.wait_for_timeout(4000)
        except Exception as e:
            print(f"❌ 填写表单失败: {e}")

        if "mydisk" not in page.url:
            print(f"❌ 登录失败，当前 URL: {page.url}")
            return
        print("✅ 登录成功！正在进入网盘主页...")
        
        # 访问网盘主页
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(3000)

        # --- 重点改动：从源码和页面中提取真实的 folder_id ---
        print(f"\n正在 HTML 源码中搜索【{target_folder_name}】的 folder_id...")
        html = await page.content()
        
        # 尝试匹配 onclick="show_folder('123456', ...)" 或者类似结构
        # 常见的结构可能是 onclick="show_folder('123456')" 或者 <a href="?folder_id=123456">
        match = re.search(rf"onclick=\"show_folder\('(\d+)'[^>]*>.*?{target_folder_name}", html, re.S)
        if not match:
            match = re.search(rf"{target_folder_name}.*?show_folder\('(\d+)'\)", html, re.S)
        if not match:
            # 兜底：直接找所有含数字的 folder_id 属性
            match = re.search(rf"folder_id=['\"]?(\d+)['\"]?.*?>{target_folder_name}", html, re.S)

        if match:
            target_folder_id = match.group(1)
            print(f"✅ 从源码中提取到目标 folder_id: {target_folder_id}")
        else:
            print("⚠️ 源码中未直接匹配到 folder_id，尝试去页面点击元素...")
            # 尝试通过 Playwright 点击它
            try:
                folder_element = page.get_by_text(target_folder_name, exact=True).first
                if await folder_element.count() > 0:
                    print("  [操作] 找到该文件夹文字，执行拟真点击...")
                    await folder_element.click()
                    await page.wait_for_timeout(3000)
                    # 点击后提取 URL 里的 folder_id
                    url_match = re.search(r"folder_id=(\d+)", page.url)
                    if url_match:
                        target_folder_id = url_match.group(1)
                        print(f"✅ 点击后获取到目标 folder_id: {target_folder_id}")
                    else:
                        print("❌ 点击成功但 URL 中没有 folder_id，放弃。")
                        return
                else:
                    print("❌ 页面上完全找不到这个文件夹，或者被风控隐藏了。")
                    return
            except Exception as e:
                print(f"❌ 拟真点击失败: {e}")
                return

        # --- 模拟跳转到该文件夹的 URL ---
        print(f"\n正在访问文件夹页面: https://pc.woozooo.com/mydisk.php?folder_id={target_folder_id}")
        await page.goto(f"https://pc.woozooo.com/mydisk.php?folder_id={target_folder_id}", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # --- 深度遍历（改进 Fetch 请求，带上完整伪装头） ---
        queue = [(target_folder_id, "")]
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "根目录"
            print(f"\n正在扫描: {display_path} (ID: {current_id})")
            
            # 【关键修复】带上 X-Requested-With 和 Referer，伪装成真实 AJAX
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
            print(f"  [调试] 接口原始返回: {folder_res[:300]}")
            
            try:
                folder_data = json.loads(folder_res)
            except:
                print(f"  ❌ JSON 解析失败")
                continue
                
            if folder_data.get('zt') != 1:
                print(f"  ❌ 接口返回错误 (依然被拦) : {folder_data.get('info')}")
                continue
                
            items = folder_data.get('text', [])
            print(f"  ✅ 获取到 {len(items)} 个项目")
            
            for item in items:
                item_type = str(item.get('type') or item.get('t') or '')
                item_id = item.get('id') or item.get('file_id')
                item_name = item.get('name') or item.get('name_all') or '未知文件'
                item_size = item.get('size', '0')

                if item_type == '1':  # 文件夹
                    next_path = f"{current_path}/{item_name}" if current_path else item_name
                    queue.append((item_id, next_path))
                    print(f"  > 子文件夹: {item_name} -> {next_path}")
                elif item_type == '0':  # 文件
                    print(f"  + 正在处理文件: {item_name}")
                    
                    # 获取分享链接，同样带上伪装头
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
                    print(f"    [调试] 分享接口原始返回: {share_res[:200]}")

                    try:
                        share_data = json.loads(share_res)
                        if share_data.get('zt') == 1:
                            share_url = share_data.get('info') or share_data.get('url') or ''
                            pwd = share_data.get('pwd', '')
                            
                            if share_url and not share_url.startswith("http"):
                                share_url = f"https://www.lanzouq.com/{share_url}"
                            
                            if share_url:
                                results.append({
                                    "name": item_name,
                                    "url": share_url,
                                    "pwd": pwd,
                                    "path": current_path,
                                    "size": item_size
                                })
                                print(f"    ✅ 获取分享链接成功")
                        else:
                            print(f"    ❌ 获取分享失败: {share_data.get('info')}")
                    except Exception as e:
                        print(f"    ❌ 获取分享异常: {e}")
                    await page.wait_for_timeout(500)

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
