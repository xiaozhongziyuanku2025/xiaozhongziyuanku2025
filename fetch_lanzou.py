import asyncio
from playwright.async_api import async_playwright
import json, re, os, random

# --- 拟人化鼠标工具类（略，沿用你之前的代码）---
class HumanCursor:
    async def drag_slider(self, page, slider_selector, distance):
        # ... 你的拟人化拖动逻辑 ...
        pass

async def main():
    print("🚀 启动拟人化+AI视觉无头浏览器...")
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
        cursor = HumanCursor()

        print("正在访问登录页...")
        await page.goto("https://accounts.woozooo.com/accounts.php?action=login&ref=pc.woozooo.com", timeout=30000)
        await page.wait_for_timeout(2000)

        # 1. 登录（同之前）
        try:
            print("正在输入账号密码...")
            await page.fill("#username", account)
            await page.fill(".input.pwd", password)
            print("点击登录...")
            await page.click("#s3")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"❌ 填写表单失败: {e}")

        # 2. 滑块（同之前）
        # ... 你的滑块处理逻辑 ...

        # 3. 验证登录成功
        await page.wait_for_timeout(3000)
        if "mydisk" not in page.url:
            print(f"❌ 登录失败，当前 URL: {page.url}")
            await page.screenshot(path="login_failed.png", full_page=True)
            with open("login_failed.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
            return
        print("✅ 登录成功！正在进入网盘...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(2000)

        # 4. 查找目标文件夹 ID（增加详细日志）
        print(f"\n正在查找根目录下的【{target_folder_name}】...")
        api_res = await page.evaluate("""async () => {
            const res = await fetch('https://pc.woozooo.com/doupload.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'task=task_list&folder_id=-1'
            });
            return await res.text();
        }""")
        print(f"  [调试] 根目录 task_list 原始响应: {api_res[:500]}")  # 打印前500字符

        target_id = None
        try:
            data = json.loads(api_res)
            if data.get('zt') == 1:
                for item in data.get('text', []):
                    # 动态查找文件夹：尝试常见字段名
                    item_type = str(item.get('type') or item.get('t') or '')
                    item_name = item.get('name') or item.get('name_all') or ''
                    if item_type == '1' and item_name == target_folder_name:
                        target_id = item.get('id') or item.get('folder_id')
                        print(f"  [调试] 找到文件夹，ID: {target_id}")
                        break
                    # 如果 type 字段不存在，尝试直接匹配名称
                    if item_name == target_folder_name:
                        target_id = item.get('id') or item.get('folder_id')
                        print(f"  [调试] 通过名称匹配找到文件夹，ID: {target_id}")
                        break
        except Exception as e:
            print(f"❌ 解析根目录数据失败: {e}")

        if not target_id:
            print(f"❌ 根目录找不到名为【{target_folder_name}】的文件夹！")
            await page.screenshot(path="folder_not_found.png", full_page=True)
            return

        print(f"✅ 找到目标文件夹，ID: {target_id}")

        # 5. 深度遍历（增加详细日志）
        queue = [(target_id, "")]
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "根目录"
            print(f"\n正在扫描: {display_path} (ID: {current_id})")
            
            folder_res = await page.evaluate(f"""async () => {{
                const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                    body: 'task=task_list&folder_id={current_id}'
                }});
                return await res.text();
            }}""")
            print(f"  [调试] 文件夹 {current_id} 原始响应: {folder_res[:500]}")
            
            try:
                folder_data = json.loads(folder_res)
            except:
                print(f"  ❌ JSON 解析失败，原始返回: {folder_res[:200]}")
                continue
                
            if folder_data.get('zt') != 1:
                print(f"  ❌ 接口返回错误: {folder_data.get('info')}")
                continue
                
            items = folder_data.get('text', [])
            print(f"  ✅ 获取到 {len(items)} 个项目")
            
            for item in items:
                # 动态适配字段名
                item_type = str(item.get('type') or item.get('t') or '')
                item_id = item.get('id') or item.get('file_id')
                item_name = item.get('name') or item.get('name_all') or '未知文件'
                item_size = item.get('size', '0')
                
                print(f"    [调试] 项目: name={item_name}, type={item_type}, id={item_id}")

                if item_type == '1':  # 文件夹
                    next_path = f"{current_path}/{item_name}" if current_path else item_name
                    queue.append((item_id, next_path))
                    print(f"  > 子文件夹: {item_name} -> {next_path}")
                elif item_type == '0':  # 文件
                    print(f"  + 正在处理文件: {item_name}")
                    # 请求分享链接
                    share_res = await page.evaluate(f"""async () => {{
                        const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                            body: 'task=file_share&file_id={item_id}'
                        }});
                        return await res.text();
                    }}""")
                    print(f"    [调试] 分享接口原始响应: {share_res[:200]}")  # 打印分享接口响应

                    try:
                        share_data = json.loads(share_res)
                        if share_data.get('zt') == 1:
                            # 动态适配分享链接字段
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
                                print(f"    ✅ 获取分享链接: {share_url}")
                            else:
                                print(f"    ❌ 分享链接为空，原始响应: {share_res[:200]}")
                        else:
                            print(f"    ❌ 获取分享失败: {share_data.get('info')}")
                    except Exception as e:
                        print(f"    ❌ 获取分享异常: {e}, 原始: {share_res[:200]}")
                    await page.wait_for_timeout(500)

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件，已保存至 lanzou-cache.json。")

if __name__ == "__main__":
    asyncio.run(main())
