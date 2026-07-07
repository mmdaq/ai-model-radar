# 🚀 AI 模型雷达日报

> **每日自动抓取 AIbase 最新模型发布信息，定时推送到你的邮箱**

## ✨ 功能

- 🔍 **智能抓取** — 从 [AI News Radar](https://learnprompt.github.io/ai-news-radar/) 实时数据中提取 AIbase 内容
- 🎯 **精准筛选** — 自动识别 `model_release` 标签，只给你看模型发布/技术更新
- 📧 **精美邮件** — 带数据看板的 HTML 排版邮件，一目了然
- ⏰ **自动运行** — 通过 GitHub Actions 每天 09:00 / 21:00 自动推送
- 🆓 **零成本** — 纯 Python 标准库，无需额外付费 API

## 📂 项目结构

```
ai-model-radar/
├── src/
│   ├── __init__.py
│   ├── fetcher.py       # 🎣 数据抓取：从 GitHub 获取 AIbase 数据
│   ├── formatter.py     # 🎨 邮件排版：生成精美 HTML
│   └── mailer.py        # 📬 邮件发送：SMTP 推送
├── config/
│   └── config.example.yaml   # 配置模板
├── .github/workflows/
│   └── daily-email.yml       # GitHub Actions 自动工作流
├── output/                   # 运行输出（HTML/JSON/日志）
├── main.py              # 🎯 主入口
├── requirements.txt     # 依赖（纯标准库，可选安装）
├── README.md            # 📖 本文件
└── .gitignore
```

## 🚀 快速开始：三步部署

### 第一步：Fork 本项目

点击 GitHub 右上角的 **Fork** 按钮，将本项目复制到你的仓库。

### 第二步：配置邮箱 Secrets

在你的仓库 **Settings → Secrets and variables → Actions → New repository secret** 中添加以下机密：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `MAIL_USERNAME` | 发件邮箱地址 | `your_email@qq.com` |
| `MAIL_PASSWORD` | **QQ邮箱授权码**（⚠️ 不是登录密码） | `xxxxxxxxxxxxx` |
| `MAIL_TO` | 收件邮箱地址 | `385096659@qq.com` |
| `MAIL_SMTP_SERVER` | SMTP 服务器（可选） | `smtp.qq.com` |
| `MAIL_SMTP_PORT` | SMTP 端口（可选） | `465` |

> **💡 QQ邮箱授权码获取方式：**
> 1. 登录 QQ邮箱 → 设置 → 账户
> 2. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
> 3. 开启服务并生成**授权码**（就是16位字母）
> 4. 把这个授权码填入 `MAIL_PASSWORD`

### 第三步：启动工作流

- ⏰ **自动运行**：每天 **09:00** 和 **21:00**（北京时间）自动执行
- 👆 **手动触发**：进入 Actions → 选择 "🚀 AI 模型雷达日报" → Run workflow

---

## 🧪 本地测试

```bash
# 克隆仓库
git clone https://github.com/你的用户名/ai-model-radar.git
cd ai-model-radar

# 设置环境变量（Linux/Mac）
export MAIL_USERNAME="your_email@qq.com"
export MAIL_PASSWORD="你的授权码"
export MAIL_TO="385096659@qq.com"

# 运行（纯 Python 标准库，无需 pip install）
python main.py
```

## 📊 数据流说明

```
AI News Radar (每30分钟自动更新)
        │
        ▼
   GitHub 数据仓库
   (data/latest-24h.json)
        │
        ▼
   AI Model Radar (每日抓取)
        │
        ├── 提取 AIbase 条目
        ├── 筛选 model_release 标签
        └── 生成 HTML 邮件 → 发送
```

## 🤝 数据来源

- [AI News Radar](https://learnprompt.github.io/ai-news-radar/) — 自动整理的 24 小时 AI 更新雷达
- [GitHub 仓库](https://github.com/LearnPrompt/ai-news-radar) — 开源数据管道

## 📜 License

MIT



## 🔧 首次设置（1 分钟搞定）

### 第一步：把 workflow 文件移到正确位置

由于 GitHub API 安全机制，workflow 文件目前放在 `.github/workflow-file.yml`。
你只需要在本地执行：

```bash
# 克隆项目
git clone https://github.com/mmdaq/ai-model-radar.git
cd ai-model-radar

# 移动文件到正确位置
mkdir -p .github/workflows
mv .github/workflow-file.yml .github/workflows/daily-email.yml

# 提交并推送
git add -A
git commit -m "setup: move workflow to correct path"
git push
```

### 第二步：配置邮箱 Secrets

去仓库 **Settings → Secrets and variables → Actions → New repository secret** 添加：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `MAIL_USERNAME` | 发件QQ邮箱 | `你的QQ号@qq.com` |
| `MAIL_PASSWORD` | QQ邮箱授权码 🔑 | 16位字母（不是登录密码） |
| `MAIL_TO` | 收件邮箱 | `385096659@qq.com` |

> **💡 获取 QQ邮箱授权码：** 登录 QQ邮箱 → 设置 → 账户 → 开启 POP3/SMTP → 生成授权码

### 第三步：启动自动推送

配置好 Secrets 后，workflow 就会自动按 **每天 09:00 和 21:00（北京时间）** 运行。
也可以去 [Actions 页面](https://github.com/mmdaq/ai-model-radar/actions) 点 **Run workflow** 手动测试。

---

## ⚡ 快速验证

配置完成后，进入 Actions 手动触发一次，检查你的 **385096659@qq.com** 邮箱就能收到日报了！

