# GitHub Hacker

一个 CLI 工具，用于管理多个 GitHub 账户，执行批量操作如 star、watch、fork 等。

**官方网站**: https://ssbun.github.io/GithubHacker

## 功能特性

- **多账户管理**：登录、登出、管理多个 GitHub 账户
- **批量操作**：使用所有账户同时执行操作
- **仓库操作**：
  - Star / Unstar 仓库
  - Watch / Unwatch 仓库（订阅通知）
  - Fork 仓库
  - 查看状态（starred/watched）
  - 查看仓库信息
- **配置管理**：导入/导出账户数据（JSON 格式）

## 安装

### 方式一：使用 pip 安装（推荐）

```bash
pip install github-hacker
```

### 方式二：从源码安装（开发使用）

```bash
# 克隆仓库
git clone https://github.com/SSBun/GithubHacker.git
cd GithubHacker

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 以开发模式安装
pip install -e .
```

安装后，可以直接使用 `github-hacker` 命令：

```bash
github-hacker --help
```

## 快速开始

### 登录 GitHub 账户

```bash
github-hacker login myaccount YOUR_GITHUB_TOKEN
```

### 查看账户列表

```bash
github-hacker config list
```

### Star 仓库（所有账户）

```bash
github-hacker star owner/repo
# 或使用完整 URL
github-hacker star https://github.com/owner/repo
```

### 使用指定账户 Star

```bash
github-hacker star owner/repo -a myaccount
```

## 命令说明

### 账户管理

```bash
# 添加账户
github-hacker login <名称> <令牌>

# 移除账户
github-hacker logout <名称>

# 列出账户
github-hacker config list

# 导出账户到 JSON
github-hacker config export accounts.json

# 从 JSON 导入账户
github-hacker config import accounts.json

# 验证所有令牌
github-hacker config validate

# 显示账户信息
github-hacker config whoami
```

### 仓库操作

```bash
# Star 仓库
github-hacker star <仓库>
github-hacker star <仓库> -a <账户>

# Unstar 仓库
github-hacker unstar <仓库>

# Watch 仓库（接收通知）
github-hacker watch <仓库>

# Unwatch 仓库
github-hacker unwatch <仓库>

# Fork 仓库
github-hacker fork <仓库>

# 查看状态（starred/watched）
github-hacker status <仓库>

# 查看仓库信息
github-hacker info <仓库>
```

## 支持的仓库格式

支持以下两种格式：
- 简短格式：`owner/repo`
- 完整 URL：`https://github.com/owner/repo`

## JSON 账户格式

导入/导出账户时，使用以下格式：

```json
{
  "myaccount": {
    "token": "ghp_xxxxxxxxxxxx",
    "username": "githubuser"
  }
}
```

## 获取 GitHub 令牌

1. 访问 [GitHub 设置 > 开发者设置 > 个人访问令牌](https://github.com/settings/tokens)
2. 点击"生成新令牌（经典）"
3. 选择 `repo` 权限范围以获取完整访问权限
4. 复制生成的令牌

## 许可证

MIT
