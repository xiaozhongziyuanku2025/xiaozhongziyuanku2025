import asyncio
from playwright.async_api import async_playwright
import json
import os
import re

async def main():
    print("🚀 启动 Playwright 无头浏览器（直链极速解析版）...")
    cookie_str = os.environ.get('LANZOU_COOKIE', '')
    
    input_file = 'lanzou-cache.json'
    output_file = 'lanzou-direct.json'
    
    if not os.path.exists(input_file):
        print(f"❌ 未找到 {input_file}，请先运行前置工作流。")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        files = json.load(f)

    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 如果配置了 Cookie 就注入
        if cookie_str:
            print("✅ 已注入 LANZOU_COOKIE")
            cookies = []
            for item in cookie_str.split(';'):
                if '=' in item:
                    k, v = item.strip().split('=', 1)
                    cookies.append({'name': k, 'value': v, 'domain': '.lanzn.com', 'path': '/'})
            await context.add_cookies(cookies)

        page = await context.new_page()

        # 拦截 ajaxfile.php 响应
        captured_data = None
        async def handle_response(response):
            nonlocal captured_data
            if "ajaxfile.php" in response.url:
                try:
                    data = await response.json()
                    if data.get('zt') == 1 and data.get('dom') and data.get('url'):
                        captured_data = f"{data['dom']}/file/{data['url']}"
                except: pass
        page.on("response", handle_response)

        for idx, item in enumerate(files):
            name = item.get('name', '未知文件')
            share_url = item.get('url', '')
            pwd = item.get('pwd', '')
            path = item.get('path', '')
            size = item.get('size', '0')

            print(f"\n[{idx+1}/{len(files)}] 解析: {name}")
            
            if not share_url:
                print("  ⚠️ 缺少分享链接，跳过")
                results.append({**item, "direct_url": ""})
                continue

            captured_data = None # 清空
            try:
                # 打开分享链接
                await page.goto(share_url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(1000)
                
                # 检查是否有密码框
                if pwd and await page.locator("input[type='password'], input[name='pwd'], input[placeholder*='密码']").count() > 0:
                    print("  [检测到密码框，正在输入...]")
                    await page.fill("input[type='password'], input[name='pwd'], input[placeholder*='密码']", pwd)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(2000)
                
                # 等待截获 ajaxfile 数据（最多等 8 秒）
                for _ in range(16):
                    if captured_data:
                        break
                    await page.wait_for_timeout(500)
                    
                if captured_data:
                    print(f"  ✅ 直链成功: {captured_data[:50]}...")
                else:
                    print("  ❌ 未截获到 ajaxfile 数据")
                    
            except Exception as e:
                print(f"  ❌ 页面异常: {e}")
                captured_data = ""

            # 组装结果
            results.append({
                "name": name,
                "url": share_url,       # 分享页，供兜底跳转
                "pwd": pwd,             # 密码
                "path": path,           # 层级
                "direct_url": captured_data or "",  # 直链
                "size": size
            })
            await page.wait_for_timeout(500) # 防封延迟

        await browser.close()

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 全部解析完成，已生成 {output_file}")

if __name__ == '__main__':
    asyncio.run(main())
