import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动「点击弹窗」终极拦截+直达版爬虫...")
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

        # 监听后台请求，偷取 folder_id
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
                            captured_folder_data[fid].extend(data.get('text', []))
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
        # 去掉 networkidle，改用固定等待，防止死锁
        await page.wait_for_timeout(4000)

        # ================= 详细日志排查 =================
        print("\n🔍 [详细日志] 开始扫描页面结构...")
        page_html = await page.content()
        visible_text = await page.inner_text("body")
        print(f"👉 页面可见文字 (前 300 字): \n{visible_text[:300]}\n")

        # ================= 寻找目标文件夹 =================
        target_folder_id = None
        
        # 方案A：从后台拦截的数据里找 ID
        root_items = captured_folder_data.get('-1', [])
        for item in root_items:
            if 'fol_id' in item and target_folder_name in item.get('name', ''):
                target_folder_id = item.get('fol_id')
                print(f"✅ 从后台拦截数据中找到【{target_folder_name}】，ID: {target_folder_id}")
                break

        # 方案B：如果拦截数据没拿到，去网页上用 JS 强行找
        if not target_folder_id:
            print("⚠️ 未在后台数据中找到，尝试从网页源码提取...")
            id_match = re.search(rf"show_folder\('(\d+)'.*?{target_folder_name}", page_html, re.S)
            if id_match:
                target_folder_id = id_match.group(1)
                print(f"✅ 从网页源码中找到【{target_folder_name}】，ID: {target_folder_id}")

        if not target_folder_id:
            print("❌ 彻底找不到目标文件夹，结束。")
            await browser.close()
            return

        # ================= 进入目标文件夹 =================
        print(f"\n🚪 正在直达文件夹 ID: {target_folder_id}...")
        folder_url = f"https://pc.woozooo.com/mydisk.php?item=files&action=index&folder_id={target_folder_id}"
        await page.goto(folder_url, timeout=30000)
        await page.wait_for_timeout(4000)

        folder_text = await page.inner_text("body")
        print(f"👉 文件夹内可见文字 (前 300 字): \n{folder_text[:300]}\n")

        # ================= 点击文件弹窗 =================
        print("🔍 开始尝试点击文件并提取弹窗...")
        
        # 蓝奏云文件通常是 a 标签或者包含在表格里，我们用 JS 遍历寻找包含扩展名的元素
        file_elements = await page.locator("a, td, div").all()
        seen_files = set()

        for element in file_elements:
            try:
                file_name = await element.inner_text()
                file_name = file_name.strip()
                
                # 简单判断是不是文件名（过滤掉导航、按钮等文字）
                if not file_name or len(file_name) < 3 or file_name in seen_files:
                    continue
                if not ('.' in file_name or 'Win' in file_name or '活动' in file_name):
                    continue
                if "文件夹" in file_name or "返回" in file_name or "登录" in file_name:
                    continue
                
                # 限制长度防止点到奇奇怪怪的容器
                if len(file_name) > 50:
                    continue

                seen_files.add(file_name)
                print(f"\n📄 发现疑似文件: {file_name}")
                print(f"    🖱️ 正在点击...")
                
                # 强行点击
                await element.click(force=True)
                await page.wait_for_timeout(2500) # 等弹窗
                
                # 提取弹窗文字
                popup_text = await page.inner_text("body")
                
                # 匹配链接和密码
                url_match = re.search(r"(https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9]+)", popup_text)
                pwd_match = re.search(r"(?:密码|提取码)[:：]\s*([a-zA-Z0-9]+)", popup_text)
                
                share_url = url_match.group(1) if url_match else ""
                share_pwd = pwd_match.group(1) if pwd_match else ""

                if share_url:
                    print(f"    ✅ 成功获取: {share_url}，密码: {share_pwd}")
                    results.append({
                        "name": file_name, "url": share_url, "pwd": share_pwd, 
                        "path": "", "size": "0"
                    })
                else:
                    print(f"    ⚠️ 弹窗中未匹配到链接。弹窗文字片段: {popup_text[:100]}")

                # 关闭弹窗
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)

            except Exception as e:
                # 忽略点击失败的元素
                pass

        await browser.close()

    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
