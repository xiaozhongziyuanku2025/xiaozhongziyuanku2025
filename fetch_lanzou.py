import asyncio
from playwright.async_api import async_playwright
import json, re, os, random, time, base64
import ddddocr

# --- 拟人化鼠标工具类 ---
class HumanCursor:
    def __init__(self, page):
        self.page = page

    async def _bezier_track(self, distance):
        """生成贝塞尔曲线轨迹（先快后慢，带抖动）"""
        track = []
        current = 0
        mid = distance * 4 / 5
        t = 0.2
        v = 0
        while current < distance:
            if current < mid:
                a = 2  # 前期加速
            else:
                a = -3 # 后期减速
            v0 = v
            v = v0 + a * t
            move = v0 * t + 0.5 * a * t * t
            current += move
            # 加入Y轴抖动和微小回拉
            track.append(round(move))
        # 模拟手抖校准
        track.append(-random.randint(2, 6))
        track.append(random.randint(2, 6))
        return track

    async def drag_slider(self, slider_selector, distance):
        """模拟真人拖动滑块"""
        try:
            slider = self.page.locator(slider_selector).first
            box = await slider.bounding_box()
            if not box:
                print("❌ 未找到滑块元素")
                return False

            start_x = box['x'] + box['width'] / 2
            start_y = box['y'] + box['height'] / 2
            
            # 1. 移动到滑块位置
            await self.page.mouse.move(start_x, start_y)
            await asyncio.sleep(random.uniform(0.1, 0.3)) # 随机停顿
            
            # 2. 按下并等待
            await self.page.mouse.down()
            await asyncio.sleep(random.uniform(0.08, 0.2)) # 确认抓稳
            
            # 3. 生成轨迹并移动
            track = await self._bezier_track(distance)
            for x in track:
                # Y轴加入随机抖动
                y_jitter = random.randint(-2, 2)
                await self.page.mouse.move(start_x + x, start_y + y_jitter)
                await asyncio.sleep(random.uniform(0.01, 0.05)) # 随机延迟
            
            # 4. 松开前停顿
            await asyncio.sleep(random.uniform(0.06, 0.15))
            await self.page.mouse.up()
            print("✅ 拖动完成")
            return True
        except Exception as e:
            print(f"❌ 拖动滑块失败: {e}")
            return False

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
        cursor = HumanCursor(page)

        print("正在访问登录页...")
        await page.goto("https://accounts.woozooo.com/accounts.php?action=login&ref=pc.woozooo.com", timeout=30000)
        await page.wait_for_timeout(2000)

        # 1. 填写账号密码（使用更稳健的选择器）
        try:
            print("正在输入账号密码...")
            await page.fill("#username", account)
            await page.fill(".input.pwd", password)
            print("点击登录...")
            await page.click("#s3")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"❌ 填写表单失败: {e}")

        # 2. 检测并处理滑块验证
        page_content = await page.content()
        if "滑动" in page_content or "验证" in page_content:
            print("⚠️ 检测到滑块验证，启动AI视觉识别...")
            
            # 使用 ddddocr 识别缺口
            ocr = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
            
            # 提取背景图和滑块图（需要根据实际页面结构调整选择器）
            # 这里是一个通用示例，实际选择器可能不同
            bg_selector = ".geetest_bg" 
            slice_selector = ".geetest_slice_bg"
            slider_btn_selector = ".geetest_btn"
            
            try:
                # 获取图片base64数据
                bg_b64 = await page.locator(bg_selector).get_attribute("src")
                slice_b64 = await page.locator(slice_selector).get_attribute("src")
                
                if bg_b64 and slice_b64:
                    bg_bytes = base64.b64decode(bg_b64.split(",")[1])
                    slice_bytes = base64.b64decode(slice_b64.split(",")[1])
                    
                    # 识别缺口位置
                    res = ocr.slide_match(slice_bytes, bg_bytes, simple_target=True)
                    distance = res['target'][0]
                    print(f"✅ AI识别到缺口距离: {distance}px")
                    
                    # 执行拟人化拖动
                    await cursor.drag_slider(slider_btn_selector, distance)
                    await page.wait_for_timeout(4000)
                else:
                    print("❌ 未能获取验证码图片")
            except Exception as e:
                print(f"❌ AI识别或拖动过程异常: {e}")

        # 3. 验证是否登录成功
        await page.wait_for_timeout(3000)
        current_url = page.url
        print(f"当前页面 URL: {current_url}")
        
        if "mydisk" not in current_url:
            print("❌ 登录失败！保存截图和HTML供排查。")
            await page.screenshot(path="login_failed.png", full_page=True)
            with open("login_failed.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
            print("已保存 login_failed.png 和 login_failed.html")
            return

        print("✅ 登录成功！正在进入网盘...")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(2000)

        # 4. 查找目标文件夹ID (逻辑不变)
        # ... (此处省略查找文件夹ID的代码，与之前版本相同) ...

        # 5. 深度遍历文件夹 (逻辑不变)
        # ... (此处省略遍历代码，与之前版本相同) ...

        await browser.close()
        
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件。")

if __name__ == "__main__":
    asyncio.run(main())
