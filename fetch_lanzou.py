import asyncio
from playwright.async_api import async_playwright
import json, re, os

async def main():
    print("🚀 启动「点击弹窗」终极版爬虫...")
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # --- 监听网络请求（兜底：以防弹窗内的链接是通过接口动态获取的）---
        captured_share_data = {}
        async def handle_response(response):
            if "doupload.php" in response.url:
                try:
                    post_data = response.request.post_data or ""
                    data = await response.json()
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

        print("✅ 登录成功！")
        print("等待 1 秒...")
        await page.wait_for_timeout(1000)
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(3000)

        # ================= 点击文件夹 =================
        print(f"正在寻找并点击文件夹【{target_folder_name}】...")
        folder_locator = page.locator(f"text='{target_folder_name}'").first
        if await folder_locator.count() == 0:
            print(f"❌ 页面上找不到文件夹【{target_folder_name}】")
            await browser.close()
            return

        await folder_locator.click(force=True)
        print("已点击文件夹，等待内容加载...")
        await page.wait_for_timeout(3000)

        # ================= 遍历文件并点击 =================
        # 获取当前文件夹页面上的所有文件名
        # 蓝奏云的文件名通常在 a 标签或 span 标签中，这里用一种相对宽泛的方式捕获
        file_elements = await page.locator("a[href*='javascript:'], .file-name, td:first-child").all()
        
        for element in file_elements:
            try:
                file_name = await element.inner_text()
                file_name = file_name.strip()
                if not file_name or file_name in seen_files:
                    continue
                # 简单的过滤，排除非文件名
                if len(file_name) < 2 or "文件夹" in file_name or "返回" in file_name:
                    continue
                    
                seen_files.add(file_name)
                print(f"\n📄 发现文件: {file_name}")
                print(f"    🖱️ 正在点击文件名...")
                
                await element.click(force=True)
                # 等待弹窗出现
                await page.wait_for_timeout(2000)
                
                # --- 从弹窗中提取链接和密码 ---
                share_url = ""
                share_pwd = ""
                
                # 策略1：在整个页面文本中搜索弹窗内容
                page_text = await page.inner_text("body")
                
                # 匹配类似 https://wwbmd.lanzn.com/xxxx 的链接
                url_match = re.search(r"(https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9]+)", page_text)
                # 匹配 "密码: xxxx" 或 "提取码: xxxx"
                pwd_match = re.search(r"(?:密码|提取码)[:：]\s*([a-zA-Z0-9]+)", page_text)
                
                if url_match:
                    share_url = url_match.group(1)
                if pwd_match:
                    share_pwd = pwd_match.group(1)

                if share_url:
                    print(f"    ✅ 从弹窗中提取到链接: {share_url}，密码: {share_pwd}")
                    results.append({
                        "name": file_name,
                        "url": share_url,
                        "pwd": share_pwd,
                        "path": "",
                        "size": "0"
                    })
                else:
                    print(f"    ⚠️ 弹窗中未直接找到链接文本，检查网络截获...")
                    # 如果弹窗文本没找到，检查是否触发了后台请求
                    # 由于不知道 file_id，这里简单检查 captured_share_data 是否有新增
                    if captured_share_data:
                        # 取最新的一条
                        latest_id = list(captured_share_data.keys())[-1]
                        res = captured_share_data.pop(latest_id)
                        print(f"    ✅ 从网络截获到链接: {res['url']}，密码: {res['pwd']}")
                        results.append({
                            "name": file_name,
                            "url": res['url'],
                            "pwd": res['pwd'],
                            "path": "",
                            "size": "0"
                        })
                    else:
                        print(f"    ❌ 未能获取到分享链接。")
                
                # 关闭弹窗，准备处理下一个文件
                # 尝试按 ESC 或点击关闭按钮
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)

            except Exception as e:
                print(f"    ❌ 处理文件时异常: {e}")

        await browser.close()

    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
