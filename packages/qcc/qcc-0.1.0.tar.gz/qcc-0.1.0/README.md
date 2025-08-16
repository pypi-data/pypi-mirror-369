# FastCC - Fast Claude Config Manager

FastCC 是一个快速管理 Claude Code 配置的命令行工具，支持多配置档案管理、云端同步和快速切换。

## 特性

- 🚀 **快速启动**: 使用 `nv` 命令一键启动 Claude Code
- 🔐 **安全存储**: 配置加密存储在用户自己的 GitHub Gist 中
- ☁️ **云端同步**: 多设备之间自动同步配置
- 📋 **多配置管理**: 支持工作、家庭等多个环境配置
- 🎯 **简单易用**: 直观的命令行界面

## 安装

只需要安装 `uv`，然后直接运行：

```bash
# 安装 uv（如果还没安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 直接使用 FastCC（无需安装）
uvx fastcc
```

## 🚀 一键使用

### 智能启动（推荐）

```bash
# 在任何新电脑上，只需要一条命令：
uvx fastcc
```

首次运行会自动：
1. 下载最新版本的 FastCC
2. 安装所有依赖 
3. 引导 GitHub OAuth 认证
4. 创建安全的云端存储空间
5. 同步您的配置档案
6. 智能选择配置（3秒超时自动选择默认）
7. 启动 Claude Code

### 手动操作

```bash
# 添加新配置
uvx fastcc add work "工作环境配置"

# 查看所有配置
uvx fastcc list

# 使用特定配置
uvx fastcc use work

# 查看状态
uvx fastcc status
```

## 智能启动特性

`uvx fastcc` 提供最流畅的使用体验：

1. **零安装** - 使用 uvx 自动下载和运行最新版本
2. **自动检测登录状态** - 如果未登录会自动引导GitHub认证
3. **智能配置选择** - 显示配置列表，3秒内自动选择默认配置
4. **一键直达** - 回车键或超时自动使用默认配置
5. **完全自动化** - 新电脑只需 `uvx fastcc` 即可开始使用

## 命令参考

### 基本命令

- `uvx fastcc` - 🚀 智能快速启动 Claude Code（推荐）
- `uvx fastcc --smart` - 显式智能启动模式
- `uvx fastcc status` - 显示 FastCC 状态信息

### 配置管理

- `uvx fastcc add <名称> [-d 描述]` - 添加新配置档案
- `uvx fastcc list` - 列出所有配置档案
- `uvx fastcc use <名称>` - 使用指定配置启动 Claude Code
- `uvx fastcc default <名称>` - 设置默认配置档案
- `uvx fastcc remove <名称>` - 删除配置档案

### 同步管理

- `uvx fastcc sync` - 手动同步配置

## 配置文件位置

- **本地缓存**: `~/.fastcc/cache.json`
- **GitHub令牌**: `~/.fastcc/github_token.json`
- **Claude配置**: `~/.claude/settings.json`

## 安全性

- 所有 API 密钥均加密存储
- 使用用户自己的 GitHub 账号存储配置
- 支持端到端加密，确保数据安全
- 本地文件权限设置为仅所有者可读写

## 依赖项

- Python 3.7+
- click - 命令行界面
- requests - HTTP 客户端
- cryptography - 加密功能

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如有问题，请在 GitHub 上创建 Issue。