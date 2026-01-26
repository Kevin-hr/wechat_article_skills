import json
import requests
import os
import sys
import datetime

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
    print("=== Verifying Drafts in WeChat Official Account ===")
    token = get_access_token()
    drafts = get_draft_list(token)
    
    if "item" not in drafts:
        print("No drafts found or error occurred.")
        print(drafts)
        return

    print(f"Total drafts found: {drafts.get('total_count', 0)}")
    print("-" * 50)
    
    for item in drafts["item"]:
        update_time = datetime.datetime.fromtimestamp(item["update_time"]).strftime('%Y-%m-%d %H:%M:%S')
        article = item["content"]["news_item"][0]
        title = article["title"]
        author = article.get("author", "Unknown")
        thumb_media_id = article["thumb_media_id"]
        digest = article.get("digest", "")
        
        print(f"Title:   {title}")
        print(f"Author:  {author}")
        print(f"Time:    {update_time}")
        print(f"CoverID: {thumb_media_id}")
        print(f"Digest:  {digest[:30]}..." if digest else "Digest:  (None)")
        print("-" * 50)

if __name__ == "__main__":
    main()
