import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动「暴力拟真点击」终极全日志版...")
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
        
        # 详细网络日志
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
                            for item in data.get('text', []):
                                if item not in captured_folder_data[fid]:
                                    captured_folder_data[fid].append(item)
                            print(f"    [网络截获] 拿到文件夹 {fid} 数据，共 {len(data.get('text'))} 项")
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

        # ================= 寻找目标文件夹 =================
        root_items = captured_folder_data.get('-1', [])
        target_folder_id = None

        for item in root_items:
            if 'fol_id' in item and target_folder_name in item.get('name', ''):
                target_folder_id = item.get('fol_id')
                print(f"✅ 找到目标文件夹【{target_folder_name}】，ID: {target_folder_id}")
                break

        if not target_folder_id:
            print("❌ 未找到目标文件夹")
            await browser.close()
            return

        # ================= 深度遍历 =================
        queue = [(target_folder_id, "")]
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"\n📂 正在扫描目录: {display_path}")
            
            if str(current_id) in captured_folder_data:
                del captured_folder_data[str(current_id)]

            folder_url = f"https://pc.woozooo.com/mydisk.php?item=files&action=index&folder_id={current_id}"
            await page.goto(folder_url, timeout=30000)
            await page.wait_for_timeout(3000)
            
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
                if 'fol_id' in item: # 子文件夹
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                    print(f"  > 发现子文件夹: {item['name']}")
                
                elif 'id' in item and 'name_all' in item: # 文件
                    item_name = item['name_all']
                    item_size = item.get('size', '0')
                    
                    print(f"\n  + 开始处理文件: {item_name}")
                    
                    share_url = ""
                    share_pwd = ""
                    
                    try:
                        # 使用精确文本匹配点击
                        print(f"    🖱️ 正在精准定位文本: '{item_name}'")
                        locator = page.get_by_text(item_name, exact=True).first
                        
                        if await locator.count() == 0:
                            print(f"    ⚠️ 精确匹配失败，尝试模糊匹配...")
                            locator = page.get_by_text(item_name, exact=False).first
                            if await locator.count() == 0:
                                print(f"    ❌ 模糊匹配也失败，跳过。")
                                continue
                                
                        print(f"    🖱️ 执行强制点击...")
                        await locator.click(force=True)
                        
                        print("    ⏳ 等待 2.5 秒看弹窗...")
                        await page.wait_for_timeout(2500)
                        
                        # 抓取全屏文字
                        popup_text = await page.inner_text("body")
                        
                        url_match = re.search(r"(https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9]+)", popup_text)
                        pwd_match = re.search(r"(?:密码|提取码)[:：]\s*([a-zA-Z0-9]+)", popup_text)
                        
                        if url_match:
                            share_url = url_match.group(1)
                        if pwd_match:
                            share_pwd = pwd_match.group(1)
                            
                        if share_url:
                            print(f"    ✅ 【弹窗成功】链接: {share_url} | 密码: {share_pwd}")
                        else:
                            print(f"    ⚠️ 【弹窗失败】页面文字中未匹配到链接。弹窗快照：")
                            print(f"    ---\n{popup_text[:500]}\n    ---")
                            # 按 ESC 防止卡死
                            await page.keyboard.press("Escape")
                            await page.wait_for_timeout(500)
                            
                    except Exception as e:
                        print(f"    ❌ 点击/解析异常: {e}")
                        
                    results.append({
                        "name": item_name,
                        "url": share_url,
                        "pwd": share_pwd,
                        "path": current_path,
                        "size": item_size
                    })
                    await page.wait_for_timeout(500)

        await browser.close()

    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
