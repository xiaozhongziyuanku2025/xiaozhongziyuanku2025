import requests
import json
import re
import os
import time
from urllib.parse import urlparse

def main():
    print("启动轻量级源码爬虫...")
    folder_url = os.environ.get('FOLDER_URL')
    pwd = os.environ.get('GLOBAL_PWD', '')
    cookie = os.environ.get('LANZOU_COOKIE', '')

    if not folder_url:
        print("❌ 缺少 FOLDER_URL")
        return

    # 提取域名和根 ID
    parsed = urlparse(folder_url)
    domain = parsed.netloc
    root_id = parsed.path.strip('/').split('/')[-1]

    # 构造请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': f'https://{domain}/'
    }
    if cookie:
        headers['Cookie'] = cookie

    session = requests.Session()
    session.headers.update(headers)

    results = []
    # 队列格式: (文件夹ID, 路径)
    queue = [(root_id, "蓝奏云专属")]

    while queue:
        current_id, current_path = queue.pop(0)
        print(f"正在扫描: {current_path} (ID: {current_id})")

        # 构造请求 URL
        if current_id == root_id:
            url = f"https://{domain}/{root_id}?pwd={pwd}"
        else:
            url = f"https://{domain}/{root_id}?folder_id={current_id}&pwd={pwd}"

        try:
            res = session.get(url, timeout=15)
            
            # 匹配源码中的文件数据
            match = re.search(r"var files = '(.*?)';", res.text, re.S)
            if not match:
                match = re.search(r"var files = (\[.*?\]);", res.text, re.S)

            if not match:
                print(f"  ❌ 提取失败。可能 Cookie 失效，或者触发了防爬盾。")
                # 打印一段源码看看是不是被拦截了
                print(f"  网页开头源码: {res.text[:100]}")
                continue

            files_data = json.loads(match.group(1))
            print(f"  ✅ 找到 {len(files_data)} 个项目")

            for item in files_data:
                item_type = str(item.get('type'))
                item_id = item.get('id')
                item_name = item.get('name_all') or item.get('name')
                item_size = item.get('size', '0')

                if item_type == '0': 
                    # 提取到文件
                    share_url = f"https://{domain}/{root_id}_{item_id}"
                    results.append({
                        "name": item_name,
                        "url": share_url,
                        "pwd": pwd,
                        "path": current_path,
                        "size": item_size
                    })
                    print(f"  + 获取文件: {item_name}")
                elif item_type == '1': 
                    # 发现子文件夹，加入队列继续遍历
                    next_path = f"{current_path}/{item_name}" if current_path != "蓝奏云专属" else f"蓝奏云专属/{item_name}"
                    queue.append((item_id, next_path))
                    print(f"  > 发现子文件夹: {item_name}")

        except Exception as e:
            print(f"  ❌ 请求发生异常: {e}")

        # 防封，停顿 1 秒
        time.sleep(1)

    # 保存结果
    with open('lanzou-cache.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 扫描完成！共提取 {len(results)} 个文件，已保存至 lanzou-cache.json")

if __name__ == "__main__":
    main()
