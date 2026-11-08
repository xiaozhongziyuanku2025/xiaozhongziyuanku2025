import os
import requests

print("1. Python 脚本已成功启动！")
url = os.environ.get('FOLDER_URL')
cookie = os.environ.get('LANZOU_COOKIE', '')

print("2. 读取到的链接:", url)
print("3. 读取到的 Cookie 长度:", len(cookie))
if len(cookie) > 0:
    print("   Cookie 前 10 个字符:", cookie[:10])
else:
    print("   ⚠️ 警告: 没拿到 Cookie，请检查 GitHub Secrets")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Cookie': cookie
}

print("4. 准备发送请求...")
try:
    # 尝试访问蓝奏云
    res = requests.get(f"{url}?pwd=1234", headers=headers, timeout=10)
    print("5. 请求成功！HTTP状态码:", res.status_code)
    print("6. 网页内容长度:", len(res.text))
    
    if "var files" in res.text:
        print("✅ 7. 检测到 'var files' 字段，说明 Cookie 有效，成功穿透！")
    else:
        print("❌ 7. 网页里没有找到 'var files'，说明被拦截或者 Cookie 失效了。")
        print("网页前 200 个字符:", res.text[:200])
        
except Exception as e:
    print("❌ 请求发生异常:", e)
