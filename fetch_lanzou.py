import asyncio
from playwright.async_api import async_playwright
import json, re, os, random, time

# 模拟真人轨迹生成函数（用于滑块）
def get_track(distance):
    track = []
    current = 0
    mid = distance * 4 / 5
    t = 0.2
    v = 0
    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        v = v0 + a * t
        move = v0 * t + 0.5 * a * t * t
        current += move
        track.append(round(move))
    # 产生一点误差，稍微回退一点点再弹回，模拟真人手抖
    track.append(-random.randint(2, 6))
    track.append(random.randint(2, 6))
    return track

async def main():
    print("🚀 启动隐形浏览器，准备登录蓝奏云...")
    account = os.environ.get('LANZOU_ACCOUNT')
    password = os.environ.get('LANZOU_PASSWORD')
    
    if not account or not password:
        print("❌ 缺少 LANZOU_ACCOUNT 或 LANZOU_PASSWORD 环境变量！")
        return

    results = []
    target_folder_name = "小众资源库"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        # 抹除自动化特征
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        print("正在访问蓝奏云登录页...")
        await page.goto("https://up.woozooo.com/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # 1. 填写账号密码
        try:
            print("正在输入账号密码...")
            await page.fill("input[name='username']", account)
            await page.wait_for_timeout(500)
            await page.fill("input[name='password']", password)
            await page.wait_for_timeout(500)
            
            print("点击登录按钮...")
            await page.press("input[name='password']", "Enter")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"❌ 填写登录表单失败: {e}")

        # 2. 检测并处理滑块验证
        page_content = await page.content()
        if "滑动" in page_content or "验证" in page_content or "nc_" in page_content:
            print("⚠️ 检测到可能出现滑块验证，尝试模拟真人滑动...")
            try:
                # 寻找滑块元素 (不同版本可能不同，查找常见特征)
                slider_btn = page.locator(".nc_iconfont.btn_slide, .slider-btn, .btn_slide")
                if await slider_btn.count() > 0:
                    box = await slider_btn.first.bounding_box()
                    if box:
                        print(f"找到滑块，开始拖动，起点: {box['x']}, {box['y']}")
                        await page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                        await page.mouse.down()
                        # 假设滑动距离为 300 像素
                        distance = 300
                        track = get_track(distance)
                        for x in track:
                            await page.mouse.move(box["x"] + box["width"]/2 + x, box["y"] + box["height"]/2, steps=1)
                            await asyncio.sleep(random.uniform(0.01, 0.05))
                        await page.mouse.up()
                        print("滑动结束，等待验证结果...")
                        await page.wait_for_timeout(4000)
                else:
                    print("未找到标准滑块元素，可能在 iframe 中或使用了其他验证码。")
            except Exception as e:
                print(f"❌ 滑块操作异常: {e}")

        # 3. 验证是否登录成功
        await page.wait_for_timeout(3000)
        current_url = page.url
        print(f"当前页面 URL: {current_url}")
        
        if "mydisk" not in current_url and "disk" not in current_url:
            print("❌ 登录失败！保存截图供排查。")
            await page.screenshot(path="login_failed.png", full_page=True)
            with open("login_failed.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
            print("已保存 login_failed.png 和 login_failed.html")
            return

        print("✅ 登录成功！正在进入网盘...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(2000)

        # 4. 查找目标文件夹 ID
        print(f"正在查找根目录下的【{target_folder_name}】...")
        # 蓝奏云网盘通过接口返回文件夹数据，这里我们在浏览器上下文执行 fetch 获取
        api_res = await page.evaluate("""async () => {
            const res = await fetch('https://pc.woozooo.com/doupload.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'task=task_list&folder_id=-1'
            });
            return await res.text();
        }""")
        
        target_id = None
        try:
            data = json.loads(api_res)
            if data.get('zt') == 1:
                for item in data.get('text', []):
                    if item.get('type') == '1' and item.get('name') == target_folder_name:
                        target_id = item.get('id')
                        break
        except Exception as e:
            print(f"❌ 解析根目录数据失败: {e}, 原始返回: {api_res[:200]}")
            
        if not target_id:
            print(f"❌ 根目录找不到名为【{target_folder_name}】的文件夹！")
            await page.screenshot(path="folder_not_found.png", full_page=True)
            return
            
        print(f"✅ 找到目标文件夹，ID: {target_id}")

        # 5. 深度遍历文件夹
        queue = [(target_id, "")] # (folder_id, current_path)，根目录路径为空
        
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "根目录"
            print(f"\n正在扫描: {display_path} (ID: {current_id})")
            
            # 获取文件夹内容
            folder_res = await page.evaluate(f"""async () => {{
                const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                    body: 'task=task_list&folder_id={current_id}'
                }});
                return await res.text();
            }}""")
            
            try:
                folder_data = json.loads(folder_res)
            except:
                print(f"  ❌ 解析数据失败，原始返回: {folder_res[:100]}")
                continue
                
            if folder_data.get('zt') != 1:
                print(f"  ❌ 接口返回错误: {folder_data.get('info')}")
                continue
                
            items = folder_data.get('text', [])
            print(f"  ✅ 获取到 {len(items)} 个项目")
            
            for item in items:
                item_type = str(item.get('type'))
                item_id = item.get('id')
                item_name = item.get('name_all') or item.get('name')
                item_size = item.get('size', '0')
                
                if item_type == '1': # 是文件夹
                    next_path = f"{current_path}/{item_name}" if current_path else item_name
                    queue.append((item_id, next_path))
                    print(f"  > 子文件夹: {item_name} -> {next_path}")
                elif item_type == '0': # 是文件
                    print(f"  + 正在处理文件: {item_name}")
                    # 调用 API 生成分享链接
                    share_res = await page.evaluate(f"""async () => {{
                        const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                            body: 'task=file_share&file_id={item_id}'
                        }});
                        return await res.text();
                    }}""")
                    
                    try:
                        share_data = json.loads(share_res)
                        if share_data.get('zt') == 1:
                            # 蓝奏云新版的分享链接通常在 info 里，密码在 pwd 里
                            share_url = share_data.get('info', '')
                            pwd = share_data.get('pwd', '')
                            
                            # 兼容性处理，如果 info 不是完整的 url
                            if share_url and not share_url.startswith("http"):
                                share_url = f"https://www.lanzouq.com/{share_url}"
                            
                            results.append({
                                "name": item_name,
                                "url": share_url,
                                "pwd": pwd,
                                "path": current_path, # 根目录即为空字符串
                                "size": item_size
                            })
                            print(f"    ✅ 获取分享链接成功: {share_url}")
                        else:
                            print(f"    ❌ 获取分享失败: {share_data.get('info')}")
                    except Exception as e:
                        print(f"    ❌ 获取分享异常: {e}, 原始: {share_res[:100]}")
                    await page.wait_for_timeout(500) # 防止请求过快

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件，已保存至 lanzou-cache.json。")

if __name__ == "__main__":
    asyncio.run(main())
