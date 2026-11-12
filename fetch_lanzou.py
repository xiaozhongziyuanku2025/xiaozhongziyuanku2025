import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动终极文件名点击探测版爬虫...")
    account = os.environ.get('LANZOU_ACCOUNT')
    password = os.environ.get('LANZOU_PASSWORD')

    if not account or not password:
        print("❌ 缺少账号或密码环境变量")
        return

    results = []
    seen_files = set()
    target_folder_name = "小众资源库"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        captured_folder_data = {}
        captured_share_data = {}

        async def handle_response(response):
            if "doupload.php" in response.url:
                try:
                    post_data = response.request.post_data or ""
                    data = await response.json()
                    
                    # 监听文件夹数据
                    match = re.search(r"folder_id=(-?\d+)", post_data)
                    if match and isinstance(data, dict) and data.get('zt') == 1 and isinstance(data.get('text'), list):
                        fid = match.group(1)
                        if fid not in captured_folder_data:
                            captured_folder_data[fid] = []
                        captured_folder_data[fid].extend(data.get('text', []))
                            
                    # 监听分享数据
                    if "file_share" in post_data and data.get('zt') == 1:
                        file_id_match = re.search(r"file_id=(\d+)", post_data)
                        if file_id_match:
                            fid = file_id_match.group(1)
                            url = data.get('info') or data.get('url') or ''
                            pwd = data.get('pwd', '')
                            if url and not url.startswith("http"):
                                url = f"https://www.lanzouq.com/{url}"
                            captured_share_data[fid] = {"url": url, "pwd": pwd}
                            print(f"    🟢 [网络截获] 成功获取 file_id {fid} 的分享链接！")
                except: pass
        page.on("response", handle_response)

        print("正在访问登录页...")
        await page.goto("https://accounts.woozooo.com/accounts.php?action=login&ref=pc.woozooo.com", timeout=30000)
        await page.wait_for_timeout(2000)

        try:
            await page.fill("#username", account)
            await page.fill(".input.pwd", password)
            await page.click("#s3")
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"❌ 登录异常: {e}")

        if "mydisk" not in page.url:
            print(f"❌ 登录失败，当前 URL: {page.url}")
            await browser.close()
            return
        
        print("✅ 登录成功！正在进入网盘...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(5000)

        async def get_share_url_by_clicking(file_name, file_id, current_folder_id):
            print(f"    🖱️ 尝试点击文件名获取: {file_name}")
            
            # --- 策略1：直接点击文件名 ---
            try:
                # 根据文件名精准定位元素并点击
                name_locator = page.locator(f"text='{file_name}'").first
                if await name_locator.count() > 0:
                    await name_locator.click(force=True)
                    print(f"      [UI] 已点击文件名，等待弹窗或接口响应...")
                    await page.wait_for_timeout(2500) # 等待界面反应
                    
                    # 1. 检查是否在后台直接被截获了（最理想的情况）
                    if file_id in captured_share_data:
                        res = captured_share_data.pop(file_id)
                        print(f"      ✅ 直接触发了后台分享请求！")
                        return res['url'], res['pwd']
                        
                    # 2. 如果没有直接触发，检查页面上有没有出现弹窗按钮
                    print(f"      [DOM探查] 点击后出现的按钮或文字:")
                    # 打印当前可见的按钮/链接文本，供排查
                    visible_texts = await page.evaluate("""() => {
                        const els = Array.from(document.querySelectorAll('a, button, .btn, .dialog span'));
                        return els.map(e => e.innerText.trim()).filter(t => t.length > 0 && t.length < 20);
                    }""")
                    unique_texts = list(set([t for t in visible_texts if t]))
                    print(f"      👉 页面可见文字: {unique_texts}")

                    # 尝试寻找可能含有关键字的弹窗按钮
                    for keyword in ["外链", "分享", "复制链接"]:
                        btn = page.locator(f"text={keyword}").first
                        if await btn.count() > 0:
                            print(f"      [UI] 发现包含 '{keyword}' 的按钮，尝试点击...")
                            await btn.click(force=True)
                            await page.wait_for_timeout(2000)
                            if file_id in captured_share_data:
                                res = captured_share_data.pop(file_id)
                                return res['url'], res['pwd']
                            else:
                                print(f"      [UI] 点击了 '{keyword}'，但未截获到请求。")
                else:
                    print(f"      ❌ 页面上完全找不到文件名文本")
            except Exception as e:
                print(f"      [UI异常] 点击操作失败: {e}")

            # --- 策略2：如果 UI 彻底失败，作为最后的底线，尝试直接发带 folder_id 的请求 ---
            print(f"      [兜底] 尝试发送原生请求...")
            try:
                res_text = await page.evaluate(f"""async () => {{
                    const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest',
                            'Referer': window.location.href
                        }},
                        body: 'task=file_share&file_id={file_id}&folder_id={current_folder_id}'
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
            except:
                pass
            
            return "", ""

        # 1. 处理根目录
        root_items = captured_folder_data.get('-1', [])
        target_folder_id = None
        seen_root = set()

        for item in root_items:
            unique_key = f"{item.get('name_all') or item.get('name')}_{item.get('id') or item.get('fol_id')}"
            if unique_key in seen_root: continue
            seen_root.add(unique_key)

            if 'name_all' in item: 
                item_name = item.get('name_all')
                item_id = str(item.get('id'))
                share_url, pwd = await get_share_url_by_clicking(item_name, item_id, -1)
                results.append({"name": item_name, "url": share_url, "pwd": pwd, "path": "", "size": item.get('size', '0')})
            elif 'fol_id' in item: 
                if target_folder_name in item.get('name', ''):
                    target_folder_id = item.get('fol_id')
                    print(f"✅ 找到目标文件夹【{item.get('name')}】，ID: {target_folder_id}")

        if not target_folder_id:
            print("❌ 未找到目标文件夹")
            await browser.close()
            return

        # 2. 深度遍历子文件夹
        queue = [(target_folder_id, "")]
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"\n📂 正在扫描子目录: {display_path} (ID: {current_id})")
            
            if str(current_id) in captured_folder_data:
                del captured_folder_data[str(current_id)]

            folder_url = f"https://pc.woozooo.com/mydisk.php?item=files&action=index&folder_id={current_id}"
            await page.goto(folder_url, timeout=30000)
            
            items = []
            for _ in range(20):
                if str(current_id) in captured_folder_data:
                    items = captured_folder_data.pop(str(current_id))
                    break
                await page.wait_for_timeout(500)
                
            if not items: continue
            
            seen_sub = set()
            for item in items:
                unique_key = f"{item.get('name_all') or item.get('name')}_{item.get('id') or item.get('fol_id')}"
                if unique_key in seen_sub: continue
                seen_sub.add(unique_key)

                if 'fol_id' in item: 
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                elif 'id' in item and 'name_all' in item: 
                    item_id = str(item['id'])
                    item_name = item['name_all']
                    unique_key = f"{item_name}_{current_path}"
                    if unique_key in seen_files: continue
                    seen_files.add(unique_key)
                    
                    share_url, pwd = await get_share_url_by_clicking(item_name, item_id, current_id)
                    results.append({"name": item_name, "url": share_url, "pwd": pwd, "path": current_path, "size": item.get('size', '0')})

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
