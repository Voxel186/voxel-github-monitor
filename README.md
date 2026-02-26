# GitHub Notification Monitor

监控GitHub未读通知，有新通知时通过OpenClaw Hook唤醒Agent。

## 使用方法

```bash
# 1. 配置环境变量
export GITHUB_TOKEN=your_github_pat
export OPENCLAW_HOOK_TOKEN=your_openclaw_hook_token

# 2. 运行脚本
python3 github-monitor.py

# 3. 或配置cron每分钟运行
* * * * * cd /path/to && GITHUB_TOKEN=xxx OPENCLAW_HOOK_TOKEN=xxx python3 github-monitor.py >> /tmp/monitor.log 2>&1
```

## 功能

- 每分钟检查GitHub未读通知
- 对比上次已通知的ID，发现新通知时唤醒OpenClaw
- 支持所有GitHub通知类型（issues、PRs、@mentions等）

## OpenClaw Hook配置

在`~/.openclaw/openclaw.json`中添加：

```json
{
  "hooks": {
    "enabled": true,
    "token": "your-hook-token",
    "path": "/hooks"
  }
}
```

然后`openclaw gateway restart`
