#!/usr/bin/env python3
"""
GitHub 通知监听器 - 每分钟检查GitHub未读通知，有新通知时唤醒OpenClaw
"""
import requests
import os
import sys
import time
import json

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OPENCLAW_HOOK_URL = "http://127.0.0.1:18789/hooks/wake"
OPENCLAW_TOKEN = os.environ.get("OPENCLAW_HOOK_TOKEN", "my-secret-token")

LAST_NOTIFY_FILE = "/tmp/github_notify_last.json"

def get_unread_notifications():
    """获取未读通知"""
    r = requests.get(
        "https://api.github.com/notifications",
        headers={"Authorization": f"token {GITHUB_TOKEN}"},
        params={"all": "false", "participating": "false"},
        timeout=10
    )
    if r.status_code != 200:
        print(f"[ERROR] GitHub API: {r.status_code}")
        return []
    return r.json()

def get_last_ids():
    """获取上次已通知的通知ID"""
    try:
        with open(LAST_NOTIFY_FILE) as f:
            data = json.load(f)
            return set(data.get("ids", []))
    except:
        return set()

def save_last_ids(ids):
    """保存已通知的通知ID"""
    with open(LAST_NOTIFY_FILE, "w") as f:
        json.dump({"ids": list(ids), "time": time.time()}, f)

def wake_openclay(message):
    """唤醒OpenClaw"""
    try:
        resp = requests.post(
            OPENCLAW_HOOK_URL,
            headers={
                "Authorization": f"Bearer {OPENCLAW_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"text": message, "mode": "now"},
            timeout=10
        )
        if resp.status_code == 200:
            print(f"[OK] OpenClaw notified")
            return True
        else:
            print(f"[ERROR] OpenClaw hook: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"[ERROR] OpenClaw hook: {e}")
        return False

def main():
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN not set")
        sys.exit(1)
    
    print("[INFO] Checking GitHub notifications...")
    notifications = get_unread_notifications()
    
    if not notifications:
        print("[INFO] No unread notifications")
        return
    
    last_ids = get_last_ids()
    current_ids = {n["id"] for n in notifications}
    new_ids = current_ids - last_ids
    
    if not new_ids:
        print(f"[INFO] No new notifications ({len(notifications)} unread)")
        return
    
    # 有新通知！
    print(f"[INFO] {len(new_ids)} new notifications!")
    
    # 按仓库分组
    by_repo = {}
    for n in notifications:
        if n["id"] in new_ids:
            repo = n["repository"]["full_name"]
            if repo not in by_repo:
                by_repo[repo] = []
            by_repo[repo].append(n["subject"]["title"])
    
    # 构建消息
    msg = f"🔔 GitHub 新通知 ({len(new_ids)}条):\n\n"
    for repo, titles in by_repo.items():
        msg += f"📦 {repo}\n"
        for t in titles[:3]:  # 每个仓库最多3条
            msg += f"  • {t[:60]}\n"
        if len(titles) > 3:
            msg += f"  ... 还有{len(titles)-3}条\n"
        msg += "\n"
    
    # 唤醒OpenClaw
    wake_openclay(msg)
    
    # 保存已通知的ID
    save_last_ids(current_ids)

if __name__ == "__main__":
    main()
