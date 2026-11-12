import asyncio
from playwright.async_api import async_playwright
import requests
import json, re, os

# ================= 配置区 =================
TARGET_FOLDER_NAME = "小众资源库"
# ==========================================

async def main():
    print("🚀 启动【终极混合架构】爬虫...")
    account = os.environ.get('LANZOU_ACCOUNT')
    password = os.environ.get('LANZOU_PASSWORD')

    if not account or not password:
        print("❌ 缺少账号或密码环境变量")
        return

    results = []
    seen_files = set()

    async with async_playwright() as p:
        # ---------------- 阶段一：Playwright 拟真登录 ----------------
        print("\n[阶段一] 启动无头浏览器进行拟真登录...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

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
        
        print("✅ 登录成功！")
        await page.goto("https://pc.woozooo.com/mydisk.php", timeout=30000)
        await page.wait_for_timeout(3000)

        # ---------------- 阶段二：提取 Cookie 交接给 requests ----------------
        print("\n[阶段二] 提取最新 Cookie，交接给轻量级 HTTP 引擎...")
        cookies = await context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        
        session = requests.Session()
        for k, v in cookie_dict.items():
            session.cookies.set(k, v)
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://pc.woozooo.com/mydisk.php'
        })

        def api_post(task, folder_id=None, file_id=None):
            """使用 requests 发送后台请求"""
            url = "https://pc.woozooo.com/doupload.php"
            data = {'task': task}
            if folder_id is not None:
                data['folder_id'] = folder_id
            if file_id is not None:
                data['file_id'] = file_id
            
            res = session.post(url, data=data, timeout=10)
            return res.json() if res.status_code == 200 else {"zt": 0}

        # ---------------- 阶段三：requests 高速递归 ----------------
        print("\n[阶段三] HTTP 引擎高速递归解析层级...")
        
        # 1. 找根目录里的“小众资源库”
        root_res = api_post('task_list', folder_id=-1)
        target_folder_id = None
        root_items = root_res.get('text', [])
        if not isinstance(root_items, list): root_items = []

        for item in root_items:
            if 'name_all' in item: # 根目录文件
                unique_key = f"{item.get('name_all')}_"
                if unique_key not in seen_files:
                    seen_files.add(unique_key)
                    share_url, pwd = get_share_url(item.get('id'), page, session)
                    results.append({
                        "name": item.get('name_all'), "url": share_url, "pwd": pwd,
                        "path": "", "size": item.get('size', '0')
                    })
                    print(f"  + 根目录文件: {item.get('name_all')}")
            elif 'fol_id' in item:
                if TARGET_FOLDER_NAME in item.get('name', ''):
                    target_folder_id = item.get('fol_id')
                    print(f"✅ 找到目标文件夹【{item.get('name')}】，ID: {target_folder_id}")

        if not target_folder_id:
            print("❌ 未找到目标文件夹，退出。")
            await browser.close()
            return

        # 2. 广度优先遍历子目录
        queue = [(target_folder_id, "")]
        while queue:
            current_id, current_path = queue.pop(0)
            display_path = current_path if current_path else "小众资源库(根)"
            print(f"  正在扫描: {display_path}")
            
            folder_res = api_post('task_list', folder_id=current_id)
            if folder_res.get('zt') != 1:
                print(f"    ❌ 接口被拦截或出错: {folder_res}")
                continue
                
            items = folder_res.get('text', [])
            if not isinstance(items, list):
                continue

            for item in items:
                if 'fol_id' in item: # 子文件夹
                    next_path = f"{current_path}/{item['name']}" if current_path else item['name']
                    queue.append((item['fol_id'], next_path))
                elif 'id' in item and 'name_all' in item: # 子文件
                    item_name = item['name_all']
                    unique_key = f"{item_name}_{current_path}"
                    if unique_key in seen_files: continue
                    seen_files.add(unique_key)

                    share_url, pwd = get_share_url(item.get('id'), page, session)
                    results.append({
                        "name": item_name, "url": share_url, "pwd": pwd,
                        "path": current_path, "size": item.get('size', '0')
                    })
                    print(f"    + {item_name}")

        await browser.close()

    # --- 写入 JSON ---
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 全部完成！共提取 {len(results)} 个文件。")


async def get_share_url(file_id, page, session):
    """
    获取分享链接：先尝试纯 HTTP 请求，失败则降级为 Playwright 拟真点击。
    """
    # 策略 A：Requests 高速请求
    url = "https://pc.woozooo.com/doupload.php"
    data = {'task': 'file_share', 'file_id': file_id}
    try:
        res = session.post(url, data=data, timeout=5)
        data_json = res.json()
        if data_json.get('zt') == 1:
            share_url = data_json.get('info') or data_json.get('url') or ''
            pwd = data_json.get('pwd', '')
            if share_url and not share_url.startswith("http"):
                share_url = f"https://www.lanzouq.com/{share_url}"
            return share_url, pwd
    except:
        pass

    # 策略 B：降级为 Playwright 模拟点击（终极兜底）
    print(f"      ⚠️ 接口被拦截，启动浏览器兜底提取 file_id: {file_id}")
    try:
        # 在浏览器上下文中，直接注入脚本去点分享（模拟真实环境）
        # 蓝奏云前端的分享逻辑通常会发请求并弹窗
        res_text = await page.evaluate(f"""async () => {{
            const fd = new FormData();
            fd.append('task', 'file_share');
            fd.append('file_id', '{file_id}');
            // 加上完整的请求头，尤其是 Referer
            const res = await fetch('https://pc.woozooo.com/doupload.php', {{
                method: 'POST',
                body: fd,
                headers: {{ 'X-Requested-With': 'XMLHttpRequest' }}
            }});
            return await res.text();
        }}""")
        
        # 尝试解析兜底请求的返回
        try:
            data = json.loads(res_text)
            if data.get('zt') == 1:
                share_url = data.get('info') or ''
                pwd = data.get('pwd', '')
                if share_url and not share_url.startswith("http"):
                    share_url = f"https://www.lanzouq.com/{share_url}"
                return share_url, pwd
        except:
            pass
    except Exception as e:
        print(f"      ❌ 兜底提取异常: {e}")

    return "", ""


if __name__ == "__main__":
    asyncio.run(main())
