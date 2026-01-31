import json
import requests
import os
import sys
import datetime
from pathlib import Path

# 加载配置
try:
    config_path = os.path.join(os.path.expanduser("~"), ".wechat-publisher", "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    APPID = config["appid"]
    APPSECRET = config["appsecret"]
except Exception as e:
    print(f"Error loading config: {e}")
    sys.exit(1)

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    resp = requests.get(url).json()
    if "access_token" in resp:
        return resp["access_token"]
    else:
        print(f"Error getting token: {resp}")
        sys.exit(1)

def get_draft_list(token):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}"
    data = {
        "offset": 0,
        "count": 5,
        "no_content": 0
    }
    resp = requests.post(url, json=data).json()
    return resp

def main():
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "verify.log"
    lines = []
    lines.append("=== Verifying Drafts in WeChat Official Account ===")
    token = get_access_token()
    drafts = get_draft_list(token)
    if "item" not in drafts:
        msg = "No drafts found or error occurred."
        print(msg)
        print(drafts)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} {msg}\n")
            f.write(json.dumps(drafts, ensure_ascii=False) + "\n")
        return
    total = drafts.get("total_count", 0)
    lines.append(f"Total drafts found: {total}")
    lines.append("-" * 50)
    for item in drafts["item"]:
        update_time = datetime.datetime.fromtimestamp(item["update_time"]).strftime('%Y-%m-%d %H:%M:%S')
        article = item["content"]["news_item"][0]
        title = article["title"]
        author = article.get("author", "Unknown")
        thumb_media_id = article["thumb_media_id"]
        digest = article.get("digest", "")
        lines.append(f"Title:   {title}")
        lines.append(f"Author:  {author}")
        lines.append(f"Time:    {update_time}")
        lines.append(f"CoverID: {thumb_media_id}")
        lines.append(f"Digest:  {digest[:30]}..." if digest else "Digest:  (None)")
        lines.append("-" * 50)
    for s in lines:
        print(s)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat()} Verify Summary\n")
        for s in lines:
            f.write(s + "\n")

if __name__ == "__main__":
    main()
