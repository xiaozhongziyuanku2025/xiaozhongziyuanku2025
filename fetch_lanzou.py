import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动「点击弹窗」终极探测版爬虫...")
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

        print("✅ 登录成功！等待 1 秒...")
        await page.wait_for_timeout(1000)
        
        # 强制等待页面网络请求空闲
        print("正在进入网盘主页...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_load_state("networkidle") # 等待网络请求彻底结束
        await page.wait_for_timeout(3000)

        # ================= 详细日志排查 =================
        print("\n🔍 [详细日志] 开始扫描页面结构...")
        page_html = await page.content()
        print(f"页面 HTML 长度: {len(page_html)} 字符")
        
        # 打印页面上所有可见的文字
        visible_text = await page.inner_text("body")
        print(f"👉 页面可见文字 (前 500 字): \n{visible_text[:500]}\n")
        
        print(f"👉 页面 HTML 片段 (前 500 字): \n{page_html[:500]}\n")
        
        # 检查是否有 iframe，有时候内容在内嵌框架里
        print(f"👉 发现 {len(page.frames)} 个 iframe 框架")
        for idx, frame in enumerate(page.frames):
            print(f"   - 框架 {idx}: {frame.url}")
        # ================================================

        print(f"\n正在尝试寻找文件夹【{target_folder_name}】...")
        # 使用宽松匹配，只要包含这几个字即可
        folder_locator = page.locator(f"text={target_folder_name}").first
        
        if await folder_locator.count() == 0:
            print(f"❌ 依然找不到。尝试用 JS 强行查找是否有这个文本...")
            has_text = await page.evaluate(f"document.body.innerText.includes('{target_folder_name}')")
            print(f"   JS 检查结果: 页面文本中是否包含该名字: {has_text}")
            
            if has_text:
                print("   ⚠️ 文本存在，但 Playwright 选择器找不到。可能是被隐藏了，尝试用 JS 强行点击...")
                await page.evaluate(f"""() => {{
                    const els = Array.from(document.querySelectorAll('*'));
                    for (let el of els) {{
                        if (el.innerText && el.innerText.trim() === '{target_folder_name}') {{
                            el.click();
                            return true;
                        }}
                    }}
                }}""")
                await page.wait_for_timeout(3000)
            else:
                await browser.close()
                return
        else:
            print("✅ 找到了文件夹元素，正在执行鼠标拟真点击...")
            await folder_locator.click(force=True)
            await page.wait_for_timeout(3000)

        # ================= 进入文件夹后，打印文件结构 =================
        print("\n🔍 [详细日志] 进入文件夹后，分析文件列表...")
        visible_text_folder = await page.inner_text("body")
        print(f"👉 文件夹内可见文字: \n{visible_text_folder[:500]}\n")

        # 尝试广泛捕获文件元素
        file_elements = await page.locator("a, td").all()
        valid_files = []
        for el in file_elements:
            try:
                txt = await el.inner_text()
                if txt and len(txt) > 2 and ".exe" in txt or ".apk" in txt or ".jpg" in txt or ".txt" in txt or "Win" in txt:
                    valid_files.append(el)
            except:
                pass

        print(f"👉 捕获到疑似文件元素 {len(valid_files)} 个")
        
        for element in valid_files:
            try:
                file_name = await element.inner_text()
                file_name = file_name.strip()
                print(f"\n📄 尝试点击文件: {file_name}")
                
                await element.click(force=True)
                await page.wait_for_timeout(2500) # 等待弹窗
                
                # 提取弹窗内容
                popup_text = await page.inner_text("body")
                
                # 打印弹窗新增的文字，方便排错
                print(f"   [弹窗探测] 页面文字增量：...")

                # 匹配链接
                url_match = re.search(r"(https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9]+)", popup_text)
                pwd_match = re.search(r"(?:密码|提取码)[:：]\s*([a-zA-Z0-9]+)", popup_text)
                
                share_url = url_match.group(1) if url_match else ""
                share_pwd = pwd_match.group(1) if pwd_match else ""

                if share_url:
                    print(f"   ✅ 弹窗提取成功: {share_url}，密码: {share_pwd}")
                    results.append({"name": file_name, "url": share_url, "pwd": share_pwd, "path": "", "size": "0"})
                else:
                    print(f"   ❌ 弹窗未包含链接，可能点击没触发弹窗，或者需要按 ESC 关闭旧弹窗。")
                
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
            except Exception as e:
                print(f"   ❌ 点击文件异常: {e}")

        await browser.close()

    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
