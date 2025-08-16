# Python singbox

一个用于网络代理管理的Python项目。

## 功能特性

- 支持多种代理协议（VLESS、VMess、Trojan、Hysteria2、TUIC、Reality）
- 自动节点管理和上传
- 支持哪吒面板监控
- Argo隧道支持
- Telegram机器人推送

## 安装

```bash
pip install singbox
```

## 使用方法

### 命令行使用

```bash
singbox
```

### 环境变量配置

```bash
# 节点上传地址
export UPLOAD_URL="https://your-domain.com"

# 项目URL（用于自动保活）
export PROJECT_URL="https://your-project.com"
# 自动保活开关
export AUTO_ACCESS="true"

# 哪吒面板配置
export NEZHA_SERVER="nz.xxx.com:8008"
export NEZHA_KEY="your-secret-key"

# Argo隧道配置
export ARGO_DOMAIN="your-domain.com"
export ARGO_AUTH="your-auth-token"
export ARGO_PORT="your-auth-token"

# Telegram配置
export CHAT_ID="your-chat-id"
export BOT_TOKEN="your-bot-token"
```
