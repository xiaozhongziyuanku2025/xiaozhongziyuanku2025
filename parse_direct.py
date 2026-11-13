import requests
import json
import re
import os
import time
from urllib.parse import urlparse

def get_direct_link(session, share_url, pwd):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        
        # 1. 访问分享页（带上密码）
        url = f"{share_url}?pwd={pwd}" if pwd else share_url
        res = session.get(url, headers=headers, timeout=10)
        
        # 如果触发 WAF 盾
        if "acw_sc__v2" in res.text or "arg1" in res.text:
            print("    ⚠️ 触发 WAF 盾，请配置 LANZOU_COOKIE。")
            return ""

        # 2. 从页面源码中提取 ajaxfile.php 的 ID
        file_match = re.search(r"ajaxfile\.php\?file=(\d+)", res.text)
        if not file_match:
            print("    ⚠️ 页面中未找到 ajaxfile 参数。")
            return ""
            
        fid = file_match.group(1)
        domain = f"{urlparse(share_url).scheme}://{urlparse(share_url).netloc}"
        ajax_url = f"{domain}/ajaxfile.php?file={fid}"
        
        # 3. 请求 ajaxfile.php 接口
        ajax_headers = headers.copy()
        ajax_headers['X-Requested-With'] = 'XMLHttpRequest'
        ajax_headers['Referer'] = url
        
        ajax_res = session.get(ajax_url, headers=ajax_headers, timeout=10)
        data = ajax_res.json()
        
        # 4. 拼接真实直链
        if data.get('zt') == 1:
            dom = data.get('dom', '')
            path = data.get('url', '')
            if dom and path:
                return f"{dom}/file/{path}"
        return ""
    except Exception as e:
        print(f"    ❌ 解析异常: {e}")
        return ""

def main():
    print("🚀 启动极速直链解析...")
    
    # 读取 Cookie（强烈建议配置，降低被盾拦截的概率）
    cookie_str = os.environ.get('LANZOU_COOKIE', '')
    session = requests.Session()
    if cookie_str:
        session.headers.update({'Cookie': cookie_str})
        print("✅ 已注入 LANZOU_COOKIE")

    input_file = 'lanzou-cache.json'       # 你的母库
    output_file = 'lanzou-direct.json'     # 前端最终读取的直链库
    
    if not os.path.exists(input_file):
        print(f"❌ 未找到 {input_file}，请先运行前置工作流。")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        files = json.load(f)

    results = []
    for idx, item in enumerate(files):
        name = item.get('name', '未知文件')
        share_url = item.get('url', '')
        pwd = item.get('pwd', '')
        path = item.get('path', '')
        size = item.get('size', '0')

        print(f"\n[{idx+1}/{len(files)}] 解析: {name}")
        direct_url = get_direct_link(session, share_url, pwd) if share_url else ""

        if direct_url:
            print(f"  ✅ 直链成功: {direct_url[:50]}...")
        else:
            print(f"  ❌ 直链获取失败")

        # 组装新的数据结构
        results.append({
            "name": name,
            "url": share_url,          # 供前端兜底跳转
            "pwd": pwd,
            "path": path,
            "direct_url": direct_url,  # 真实下载链接
            "size": size
        })
        
        # 延迟 1 秒防封
        time.sleep(1)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 全部解析完成，已生成 {output_file}")

if __name__ == '__main__':
    main()
