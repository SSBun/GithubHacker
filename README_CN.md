# GitHub Hacker

一个 CLI 工具，用于管理多个 GitHub 账户，执行批量操作如 star、watch、fork 等。

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

```bash
# 克隆仓库
git clone https://github.com/yourusername/GithubHacker.git
cd GithubHacker

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 登录 GitHub 账户

```bash
python main.py login myaccount YOUR_GITHUB_TOKEN
```

### 查看账户列表

```bash
python main.py config list
```

### Star 仓库（所有账户）

```bash
python main.py star owner/repo
# 或使用完整 URL
python main.py star https://github.com/owner/repo
```

### 使用指定账户 Star

```bash
python main.py star owner/repo -a myaccount
```

## 命令说明

### 账户管理

```bash
# 添加账户
python main.py login <名称> <令牌>

# 移除账户
python main.py logout <名称>

# 列出账户
python main.py config list

# 导出账户到 JSON
python main.py config export accounts.json

# 从 JSON 导入账户
python main.py config import accounts.json

# 验证所有令牌
python main.py config validate

# 显示账户信息
python main.py config whoami
```

### 仓库操作

```bash
# Star 仓库
python main.py star <仓库>
python main.py star <仓库> -a <账户>

# Unstar 仓库
python main.py unstar <仓库>

# Watch 仓库（接收通知）
python main.py watch <仓库>

# Unwatch 仓库
python main.py unwatch <仓库>

# Fork 仓库
python main.py fork <仓库>

# 查看状态（starred/watched）
python main.py status <仓库>

# 查看仓库信息
python main.py info <仓库>
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
