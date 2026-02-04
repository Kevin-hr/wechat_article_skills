# 错误码参考

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 40164 | IP 不在白名单 | 微信后台添加 IP |
| 40001 | 凭证无效 | 检查 config.json |
| 42001 | 令牌过期 | 删除 token_cache.json |
| 45009 | API 频率限制 | 等待次日 |

## 排查步骤

1. 检查 `~/.wechat-publisher/config.json` 配置正确
2. 确认微信公众平台已添加 IP 到白名单
3. 如遇 42001，删除 `token_cache.json` 重新获取 token
