# Outbound Guide 自动更新系统

每天自动监测 Steam 官方补丁、Reddit 社区讨论、Steam 评价变化，发现新内容后自动生成攻略页面并部署。

## 功能特性

| 监测源 | 监测内容 | 自动操作 |
|--------|----------|----------|
| Steam 官方 | 补丁日志、新闻公告 | 检测到新版本 → 自动生成 patch-notes 页面 |
| Reddit r/Outbound | 热门帖子、攻略分享 | 高赞/详细帖子 → 自动生成攻略页面 |
| Steam 评价 | 评价数、好评率 | 变化超过阈值 → 更新首页数据 |

## 项目结构

```
outbound-auto-update/
├── main.py                 # 主程序入口
├── config.py              # 配置参数
├── state_manager.py       # 状态管理（记录上次监测结果）
├── steam_monitor.py       # Steam 监测模块
├── reddit_monitor.py      # Reddit 监测模块
├── page_generator.py      # 页面生成器
├── requirements.txt       # Python 依赖
├── setup_windows_task.ps1 # Windows 定时任务设置脚本
├── .github/workflows/     # GitHub Actions 配置
│   └── auto-update.yml
└── data/                  # 数据存储（自动创建）
    ├── monitor_state.json # 监测状态
    └── report_*.txt       # 执行报告
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置网站路径

编辑 `config.py`，确保 `SITE_REPO_PATH` 指向你的网站仓库：

```python
SITE_REPO_PATH = r"C:\Users\...\outbound-site"
```

### 3. 测试运行

```bash
python main.py
```

### 4. 设置定时任务（二选一）

#### 方案 A: Windows 任务计划程序（推荐本地运行）

以管理员身份运行 PowerShell：

```powershell
.\setup_windows_task.ps1
```

这会创建一个每天 09:00 运行的定时任务。

#### 方案 B: GitHub Actions（云端运行）

1. 将此项目推送到 GitHub 仓库
2. 在仓库 Settings → Secrets 中添加 `GH_PAT`（GitHub Personal Access Token，需要有 outbound-guide 仓库的写权限）
3. GitHub Actions 会自动每天运行

## 配置说明

### 监测阈值（config.py）

```python
MIN_UPVOTES_FOR_GUIDE = 10   # Reddit 帖子最少 upvotes 才生成攻略
MIN_REVIEWS_CHANGE = 50      # 评价数变化超过此值才更新首页
```

### 内容分类关键词（config.py）

系统会根据关键词自动分类生成的攻略：

- `starter` - 新手开荒
- `crafting` - 合成配方
- `energy` - 电力能源
- `van` - 房车升级
- `multiplayer` - 多人联机
- `collectibles` - 收集品
- `progression` - 科技树
- `items` - 物品资源
- `fixes` - 问题修复
- `achievements` - 成就

## 运行报告

每次运行后会生成报告文件：`data/report_YYYYMMDD_HHMMSS.txt`

报告包含：
- 检查时间戳
- 发现的 Steam 补丁
- Reddit 帖子处理情况
- 生成的页面列表
- Git 提交状态

## 手动触发

```bash
# 立即运行一次
python main.py

# Windows 上手动启动定时任务
Start-ScheduledTask -TaskName "OutboundGuideAutoUpdate"
```

## 注意事项

1. **Reddit 速率限制**：Reddit API 有速率限制，频繁运行可能导致暂时被封
2. **Git 权限**：确保脚本有 outbound-site 仓库的写权限
3. **状态文件**：`data/monitor_state.json` 记录上次状态，删除后会重新处理所有历史内容
4. **备份**：建议定期备份 `data/` 目录

## 扩展开发

### 添加新的监测源

1. 创建新的监测模块（如 `discord_monitor.py`）
2. 在 `main.py` 的 `run()` 方法中添加调用
3. 在 `page_generator.py` 中添加对应的页面生成方法

### 自定义页面模板

修改 `page_generator.py` 中的 `BASE_TEMPLATE` 变量即可更改生成页面的样式。

## License

MIT
