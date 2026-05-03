<p align="center">
  <a href="#简体中文">简体中文</a> |
  <a href="#繁體中文">繁體中文</a> |
  <a href="#english">English</a>
</p>

---

<a id="简体中文"></a>

<details>
<summary><h1>🎉 WebPilot-CLI — 轻量级 AI 浏览器自动化命令行工具</h1></summary>

> 🚀 零外部依赖 · YAML 工作流驱动 · 智能内容提取 · 终端原生体验

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8%2B-green" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License">
  <img src="https://img.shields.io/badge/dependencies-zero-brightgreen" alt="Zero Dependencies">
</p>

---

## 🎉 项目介绍

**WebPilot-CLI** 是一款专为 AI Agent 和开发者打造的轻量级浏览器自动化命令行工具。它完全基于 Python 标准库构建，**零外部依赖**，开箱即用。

### 🎯 项目定位

在 AI Agent 日益普及的今天，浏览器自动化是 Agent 与 Web 世界交互的核心能力。然而，现有的自动化工具要么体积庞大（Selenium、Playwright），要么依赖复杂（需要浏览器驱动），要么功能单一（只能抓取、不能编排）。**WebPilot-CLI** 的定位是：

> **一个足够轻、足够智能、足够灵活的终端浏览器自动化瑞士军刀。**

### 💡 解决的痛点

| 痛点 | WebPilot-CLI 的方案 |
|------|-------------------|
| 现有工具依赖沉重，安装配置繁琐 | 纯 Python 标准库实现，`pip install` 即可使用 |
| 网页抓取结果充满噪声（导航栏、广告、页脚） | 智能噪声过滤引擎，自动识别并过滤无关内容 |
| 自动化操作需要写大量代码 | YAML 工作流引擎，用声明式配置替代命令式编程 |
| 缺少终端原生的可视化方案 | ASCII 艺术截图 + HTML Canvas 截图，终端也能"看到"网页 |
| 多步骤操作难以编排和复用 | 变量传递、条件分支、循环控制，完整的流程编排能力 |

### 🌟 差异化亮点

- 🪶 **极致轻量**：零外部依赖，整个工具包仅使用 Python 标准库（`urllib`、`html.parser`、`http.cookiejar`）
- 🧠 **智能提取**：内置噪声识别引擎，自动过滤导航栏、侧边栏、广告、页脚等无关内容
- 📝 **YAML 驱动**：用声明式 YAML 定义复杂的浏览器操作流程，支持变量传递与条件分支
- 🖥️ **终端友好**：ASCII 艺术截图让你在终端中也能"看到"网页布局
- 🔄 **会话管理**：内置 Cookie/Session 管理，轻松处理需要登录的场景
- 📤 **多格式输出**：支持 JSON、Markdown、纯文本三种输出格式，适配不同下游消费场景

---

## ✨ 核心特性

- 🌐 **网页浏览** — 一条命令获取网页内容，自动提取标题、正文、链接、图片
- 📸 **智能截图** — 支持 ASCII 艺术截图和 HTML Canvas 截图两种模式
- 🔍 **内容提取** — 智能过滤噪声，提取结构化内容（标题/描述/正文/链接/图片）
- ⚙️ **YAML 工作流** — 声明式定义多步骤自动化流程，支持 navigate/extract/screenshot/wait/condition/loop
- 🔄 **变量传递** — 步骤间通过 `${var}` 语法传递数据，支持条件分支和循环
- 🍪 **会话管理** — 自动管理 Cookie 和 Session，支持跨请求状态保持
- 🖥️ **交互模式** — 内置 REPL 交互式浏览器会话，实时探索网页
- 📤 **多格式输出** — JSON / Markdown / 纯文本，适配管道和脚本集成
- 🎨 **彩色终端** — 丰富的 ANSI 彩色输出，提升终端阅读体验
- 📊 **进度展示** — 工作流执行时显示实时进度条
- 🛡️ **健壮性** — 自动重试、超时控制、编码检测、错误恢复
- 🪶 **零依赖** — 完全基于 Python 标准库，无需安装任何第三方包

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- 网络连接（用于访问目标网页）
- 无需安装浏览器或浏览器驱动

### 安装

```bash
# 方式一：从 PyPI 安装（推荐）
pip install git+https://github.com/gitstq/webpilot-cli.git

# 方式二：从源码安装
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
pip install -e .
```

### 快速体验

```bash
# 浏览网页，查看结构化内容
webpilot browse https://example.com

# 以 JSON 格式输出
webpilot browse https://example.com --output json

# 截取网页 ASCII 截图
webpilot screenshot https://example.com -o screenshot.txt -f ascii

# 截取网页 HTML 截图（可在浏览器中打开）
webpilot screenshot https://example.com -o screenshot.html -f html

# 提取网页结构化内容
webpilot extract https://example.com --fields title description text

# 执行 YAML 工作流
webpilot run workflow.yaml

# 启动交互式浏览器会话
webpilot interactive
```

---

## 📖 详细使用指南

### 全局选项

所有子命令均支持以下全局选项：

| 选项 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--output` | `-o` | 输出格式：`json` / `markdown` / `text` | `markdown` |
| `--no-color` | | 禁用彩色终端输出 | 关闭 |
| `--verbose` | `-v` | 启用详细输出模式 | 关闭 |
| `--version` | `-V` | 显示版本号 | — |

### `browse` — 浏览网页

获取并展示网页的结构化内容，自动过滤噪声。

```bash
# 基本用法
webpilot browse <url>

# 指定超时时间和输出格式
webpilot browse https://example.com --timeout 60 --output json

# 启用详细模式
webpilot browse https://example.com -v
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 目标网页 URL（必填） | — |
| `--timeout` / `-t` | 请求超时时间（秒） | 30 |

### `screenshot` — 网页截图

支持两种截图模式：终端友好的 ASCII 艺术截图和可在浏览器中打开的 HTML Canvas 截图。

```bash
# HTML 截图（默认，可在浏览器中打开查看）
webpilot screenshot https://example.com -o page.html

# ASCII 截图（终端友好）
webpilot screenshot https://example.com -f ascii -o page.txt

# 自定义终端宽度
webpilot screenshot https://example.com -f ascii --width 120
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 目标网页 URL（必填） | — |
| `--output-file` / `-o` | 输出文件路径 | `screenshot.html` |
| `--format` / `-f` | 截图格式：`ascii` / `html` | `html` |
| `--width` | ASCII 截图的终端宽度（字符数） | 80 |

### `extract` — 提取结构化内容

从网页中提取结构化数据，支持按字段筛选。

```bash
# 提取所有内容
webpilot extract https://example.com

# 仅提取标题和描述
webpilot extract https://example.com --fields title description

# 仅提取链接和图片
webpilot extract https://example.com --fields links images

# JSON 格式输出，方便程序处理
webpilot extract https://example.com --output json
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 目标网页 URL（必填） | — |
| `--fields` | 提取字段：`title` / `description` / `text` / `links` / `images`（可多选） | 全部 |
| `--timeout` / `-t` | 请求超时时间（秒） | 30 |

### `run` — 执行 YAML 工作流

通过 YAML 文件定义和执行多步骤浏览器自动化流程。

```bash
# 执行工作流
webpilot run workflow.yaml

# 导出执行结果
webpilot run workflow.yaml --export result.json

# 详细模式
webpilot run workflow.yaml -v
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `workflow` | YAML 工作流文件路径（必填） | — |
| `--export` / `-e` | 将结果导出为 JSON 文件 | 不导出 |

#### YAML 工作流示例

```yaml
name: daily_news_collector
description: 每日新闻采集工作流

# 全局变量
vars:
  base_url: "https://news.example.com"
  output_dir: "output"

# 遇到错误是否停止
stop_on_error: true

steps:
  # 第一步：导航到目标页面
  - name: "打开新闻首页"
    type: navigate
    url: "${base_url}"
    save: page_info

  # 第二步：等待页面加载
  - name: "等待加载"
    type: wait
    seconds: 2

  # 第三步：提取页面内容
  - name: "提取新闻内容"
    type: extract
    fields:
      - title
      - description
      - text
      - links
    save: news_data

  # 第四步：截取页面截图
  - name: "保存截图"
    type: screenshot
    output: "${output_dir}/news_screenshot.html"
    format: html

  # 第五步：条件判断
  - name: "检查标题是否存在"
    type: condition
    variable: page_info
    operator: exists
    then:
      - name: "标题提取成功"
        type: set_variable
        value: "页面标题已成功提取"
        save: status_message
    else:
      - name: "标题提取失败"
        type: set_variable
        value: "未找到页面标题"
        save: status_message

  # 第六步：循环处理
  - name: "批量处理"
    type: loop
    count: 3
    index_var: iteration
    steps:
      - name: "处理第 ${iteration} 批"
        type: set_variable
        value: "正在处理第 ${iteration} 批数据"
        save: batch_status
```

#### 支持的步骤类型

| 步骤类型 | 说明 | 关键参数 |
|----------|------|----------|
| `navigate` | 导航到指定 URL | `url` |
| `extract` | 提取当前页面内容 | `fields`（可选） |
| `screenshot` | 截取当前页面截图 | `output`, `format` |
| `wait` | 等待指定秒数 | `seconds` |
| `condition` | 条件分支 | `variable`, `operator`, `then`, `else` |
| `loop` | 循环执行子步骤 | `count`, `index_var`, `steps` |
| `set_variable` | 设置工作流变量 | `value` |

#### 支持的条件运算符

| 运算符 | 说明 |
|--------|------|
| `exists` | 变量是否存在 |
| `equals` | 等于指定值 |
| `not_equals` | 不等于指定值 |
| `contains` | 包含指定值 |
| `greater_than` | 大于指定值 |
| `less_than` | 小于指定值 |
| `is_true` | 布尔值为真 |
| `is_false` | 布尔值为假 |

### `interactive` — 交互式浏览器会话

启动一个 REPL（读取-求值-输出循环）交互式会话，实时探索网页。

```bash
# 启动交互模式
webpilot interactive

# 带初始 URL 启动
webpilot interactive --url https://example.com
```

**交互模式内置命令：**

| 命令 | 说明 |
|------|------|
| `browse <url>` | 导航到指定 URL |
| `extract` | 提取当前页面结构化内容 |
| `screenshot [path]` | 保存截图（默认 `screenshot.html`） |
| `info` | 显示当前页面信息 |
| `ascii` | 显示 ASCII 截图 |
| `title` | 显示页面标题 |
| `links` | 列出当前页面所有链接 |
| `images` | 列出当前页面所有图片 |
| `cookies` | 显示当前 Cookie |
| `help` | 显示帮助信息 |
| `quit` / `exit` / `q` | 退出交互模式 |

---

## 💡 设计思路与迭代规划

### 设计理念

WebPilot-CLI 的设计遵循以下核心理念：

1. **极简主义（Minimalism）**：不引入任何外部依赖，用最少的代码实现最多的功能。Python 标准库已经足够强大，`urllib` 处理网络请求，`html.parser` 解析 HTML，`http.cookiejar` 管理会话——我们不需要更多。

2. **声明式优先（Declarative First）**：能用 YAML 配置表达的，就不需要写 Python 代码。工作流引擎让非程序员也能定义复杂的浏览器操作流程。

3. **终端原生（Terminal Native）**：作为命令行工具，终端就是我们的主场。ASCII 截图、彩色输出、进度条——让终端体验不逊色于 GUI。

4. **AI Agent 友好（Agent Friendly）**：结构化的 JSON 输出、可编程的工作流引擎、清晰的状态管理——每一个设计决策都考虑了 AI Agent 的集成需求。

### 技术选型原因

| 技术选择 | 原因 |
|----------|------|
| `urllib` 而非 `requests` | 零依赖，标准库自带，满足基本 HTTP 需求 |
| `html.parser` 而非 `BeautifulSoup` | 零依赖，标准库自带，性能可控 |
| `http.cookiejar` 而非 `requests.Session` | 零依赖，原生支持 Cookie 持久化 |
| YAML 工作流 而非 Python 脚本 | 声明式更易读、更易维护、更易被 AI 生成 |
| ASCII 截图 而非 PNG 截图 | 无需额外依赖（如 Pillow），终端原生展示 |

### 后续规划

- [ ] 🔌 **插件系统**：支持自定义提取器和输出格式的插件机制
- [ ] 🗄️ **结果持久化**：支持将提取结果保存到 SQLite / CSV
- [ ] 🔄 **增量抓取**：基于 ETag / Last-Modified 的增量内容更新
- [ ] 📡 **API 模式**：内置 HTTP 服务器，提供 RESTful API 接口
- [ ] 🧪 **断言引擎**：工作流中支持页面内容断言，用于监控和测试
- [ ] 📊 **报告生成**：自动生成工作流执行报告（HTML / PDF）
- [ ] 🌐 **代理支持**：内置 HTTP/SOCKS 代理配置
- [ ] 📦 **批量模式**：支持从文件读取 URL 列表进行批量处理
- [ ] 🤖 **MCP 集成**：作为 MCP（Model Context Protocol）服务器运行

---

## 📦 安装与部署指南

### 系统要求

- **操作系统**：Windows / macOS / Linux
- **Python 版本**：3.8、3.9、3.10、3.11、3.12
- **磁盘空间**：约 1 MB（源码）
- **网络**：需要能访问目标网站

### 安装方式

```bash
# 方式一：从 GitHub 直接安装（推荐）
pip install git+https://github.com/gitstq/webpilot-cli.git

# 方式二：克隆仓库后以开发模式安装
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
pip install -e .

# 方式三：克隆仓库后直接使用（无需安装）
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
python -m webpilot.cli browse https://example.com
```

### 验证安装

```bash
# 查看版本号
webpilot --version

# 查看帮助信息
webpilot --help

# 快速测试
webpilot browse https://example.com
```

### 卸载

```bash
pip uninstall webpilot-cli
```

---

## 🤝 贡献指南

我们欢迎并感谢所有形式的贡献！无论是提交 Bug 报告、改进文档，还是提交代码 Pull Request。

### 如何贡献

1. **Fork** 本仓库
2. 创建你的特性分支：`git checkout -b feature/amazing-feature`
3. 提交你的改动：`git commit -m 'Add some amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli

# 以开发模式安装
pip install -e .

# 运行测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_extractor.py -v
```

### 代码规范

- 遵循 PEP 8 编码规范
- 为所有公开函数编写文档字符串
- 确保所有测试通过后再提交 PR
- 提交信息使用清晰、描述性的语言

### 提交 Issue

在提交 Issue 之前，请：

1. 搜索已有的 Issues，避免重复提交
2. 提供复现步骤和期望行为
3. 附上运行环境信息（Python 版本、操作系统等）

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

```
MIT License

Copyright (c) 2024 WebPilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<p align="center">
  用 ❤️ 和 Python 标准库构建 · <a href="https://github.com/gitstq/webpilot-cli">GitHub</a>
</p>

</details>

---

<a id="繁體中文"></a>

<details>
<summary><h1>🎉 WebPilot-CLI — 輕量級 AI 瀏覽器自動化命令列工具</h1></summary>

> 🚀 零外部依賴 · YAML 工作流驅動 · 智慧內容擷取 · 終端原生體驗

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8%2B-green" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License">
  <img src="https://img.shields.io/badge/dependencies-zero-brightgreen" alt="Zero Dependencies">
</p>

---

## 🎉 專案介紹

**WebPilot-CLI** 是一款專為 AI Agent 與開發者打造的輕量級瀏覽器自動化命令列工具。它完全基於 Python 標準函式庫建構，**零外部依賴**，安裝即可使用。

### 🎯 專案定位

在 AI Agent 日益普及的今天，瀏覽器自動化是 Agent 與 Web 世界互動的核心能力。然而，現有的自動化工具要麼體積龐大（Selenium、Playwright），要麼依賴複雜（需要瀏覽器驅動程式），要麼功能單一（只能抓取、不能編排）。**WebPilot-CLI** 的定位是：

> **一個足夠輕、足夠智慧、足夠靈活的終端瀏覽器自動化瑞士軍刀。**

### 💡 解決的痛點

| 痛點 | WebPilot-CLI 的方案 |
|------|-------------------|
| 現有工具依賴沉重，安裝配置繁瑣 | 純 Python 標準函式庫實作，`pip install` 即可使用 |
| 網頁抓取結果充滿雜訊（導覽列、廣告、頁尾） | 智慧雜訊過濾引擎，自動識別並過濾無關內容 |
| 自動化操作需要寫大量程式碼 | YAML 工作流引擎，用宣告式配置取代命令式程式設計 |
| 缺少終端原生的視覺化方案 | ASCII 藝術截圖 + HTML Canvas 截圖，終端也能「看到」網頁 |
| 多步驟操作難以編排和重用 | 變數傳遞、條件分支、迴圈控制，完整的流程編排能力 |

### 🌟 差異化亮點

- 🪶 **極致輕量**：零外部依賴，整個工具包僅使用 Python 標準函式庫（`urllib`、`html.parser`、`http.cookiejar`）
- 🧠 **智慧擷取**：內建雜訊識別引擎，自動過濾導覽列、側邊欄、廣告、頁尾等無關內容
- 📝 **YAML 驅動**：用宣告式 YAML 定義複雜的瀏覽器操作流程，支援變數傳遞與條件分支
- 🖥️ **終端友善**：ASCII 藝術截圖讓你在終端中也能「看到」網頁版面配置
- 🔄 **工作階段管理**：內建 Cookie/Session 管理，輕鬆處理需要登入的場景
- 📤 **多格式輸出**：支援 JSON、Markdown、純文字三種輸出格式，適配不同下游消費場景

---

## ✨ 核心特性

- 🌐 **網頁瀏覽** — 一條命令取得網頁內容，自動擷取標題、正文、連結、圖片
- 📸 **智慧截圖** — 支援 ASCII 藝術截圖和 HTML Canvas 截圖兩種模式
- 🔍 **內容擷取** — 智慧過濾雜訊，擷取結構化內容（標題/描述/正文/連結/圖片）
- ⚙️ **YAML 工作流** — 宣告式定義多步驟自動化流程，支援 navigate/extract/screenshot/wait/condition/loop
- 🔄 **變數傳遞** — 步驟間透過 `${var}` 語法傳遞資料，支援條件分支和迴圈
- 🍪 **工作階段管理** — 自動管理 Cookie 和 Session，支援跨請求狀態保持
- 🖥️ **互動模式** — 內建 REPL 互動式瀏覽器工作階段，即時探索網頁
- 📤 **多格式輸出** — JSON / Markdown / 純文字，適配管線和腳本整合
- 🎨 **彩色終端** — 豐富的 ANSI 彩色輸出，提升終端閱讀體驗
- 📊 **進度展示** — 工作流執行時顯示即時進度條
- 🛡️ **穩健性** — 自動重試、逾時控制、編碼偵測、錯誤復原
- 🪶 **零依賴** — 完全基於 Python 標準函式庫，無需安裝任何第三方套件

---

## 🚀 快速開始

### 環境需求

- Python 3.8 或更高版本
- 網路連線（用於存取目標網頁）
- 無需安裝瀏覽器或瀏覽器驅動程式

### 安裝

```bash
# 方式一：從 GitHub 直接安裝（推薦）
pip install git+https://github.com/gitstq/webpilot-cli.git

# 方式二：從原始碼安裝
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
pip install -e .
```

### 快速體驗

```bash
# 瀏覽網頁，查看結構化內容
webpilot browse https://example.com

# 以 JSON 格式輸出
webpilot browse https://example.com --output json

# 截取網頁 ASCII 截圖
webpilot screenshot https://example.com -o screenshot.txt -f ascii

# 截取網頁 HTML 截圖（可在瀏覽器中開啟）
webpilot screenshot https://example.com -o screenshot.html -f html

# 擷取網頁結構化內容
webpilot extract https://example.com --fields title description text

# 執行 YAML 工作流
webpilot run workflow.yaml

# 啟動互動式瀏覽器工作階段
webpilot interactive
```

---

## 📖 詳細使用指南

### 全域選項

所有子命令均支援以下全域選項：

| 選項 | 縮寫 | 說明 | 預設值 |
|------|------|------|--------|
| `--output` | `-o` | 輸出格式：`json` / `markdown` / `text` | `markdown` |
| `--no-color` | | 停用彩色終端輸出 | 關閉 |
| `--verbose` | `-v` | 啟用詳細輸出模式 | 關閉 |
| `--version` | `-V` | 顯示版本號 | — |

### `browse` — 瀏覽網頁

取得並展示網頁的結構化內容，自動過濾雜訊。

```bash
# 基本用法
webpilot browse <url>

# 指定逾時時間和輸出格式
webpilot browse https://example.com --timeout 60 --output json

# 啟用詳細模式
webpilot browse https://example.com -v
```

**參數說明：**

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `url` | 目標網頁 URL（必填） | — |
| `--timeout` / `-t` | 請求逾時時間（秒） | 30 |

### `screenshot` — 網頁截圖

支援兩種截圖模式：終端友善的 ASCII 藝術截圖和可在瀏覽器中開啟的 HTML Canvas 截圖。

```bash
# HTML 截圖（預設，可在瀏覽器中開啟查看）
webpilot screenshot https://example.com -o page.html

# ASCII 截圖（終端友善）
webpilot screenshot https://example.com -f ascii -o page.txt

# 自訂終端寬度
webpilot screenshot https://example.com -f ascii --width 120
```

**參數說明：**

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `url` | 目標網頁 URL（必填） | — |
| `--output-file` / `-o` | 輸出檔案路徑 | `screenshot.html` |
| `--format` / `-f` | 截圖格式：`ascii` / `html` | `html` |
| `--width` | ASCII 截圖的終端寬度（字元數） | 80 |

### `extract` — 擷取結構化內容

從網頁中擷取結構化資料，支援依欄位篩選。

```bash
# 擷取所有內容
webpilot extract https://example.com

# 僅擷取標題和描述
webpilot extract https://example.com --fields title description

# 僅擷取連結和圖片
webpilot extract https://example.com --fields links images

# JSON 格式輸出，方便程式處理
webpilot extract https://example.com --output json
```

**參數說明：**

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `url` | 目標網頁 URL（必填） | — |
| `--fields` | 擷取欄位：`title` / `description` / `text` / `links` / `images`（可多選） | 全部 |
| `--timeout` / `-t` | 請求逾時時間（秒） | 30 |

### `run` — 執行 YAML 工作流

透過 YAML 檔案定義和執行多步驟瀏覽器自動化流程。

```bash
# 執行工作流
webpilot run workflow.yaml

# 匯出執行結果
webpilot run workflow.yaml --export result.json

# 詳細模式
webpilot run workflow.yaml -v
```

**參數說明：**

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `workflow` | YAML 工作流檔案路徑（必填） | — |
| `--export` / `-e` | 將結果匯出為 JSON 檔案 | 不匯出 |

#### YAML 工作流範例

```yaml
name: daily_news_collector
description: 每日新聞採集工作流

# 全域變數
vars:
  base_url: "https://news.example.com"
  output_dir: "output"

# 遇到錯誤是否停止
stop_on_error: true

steps:
  # 第一步：導航到目標頁面
  - name: "開啟新聞首頁"
    type: navigate
    url: "${base_url}"
    save: page_info

  # 第二步：等待頁面載入
  - name: "等待載入"
    type: wait
    seconds: 2

  # 第三步：擷取頁面內容
  - name: "擷取新聞內容"
    type: extract
    fields:
      - title
      - description
      - text
      - links
    save: news_data

  # 第四步：截取頁面截圖
  - name: "儲存截圖"
    type: screenshot
    output: "${output_dir}/news_screenshot.html"
    format: html

  # 第五步：條件判斷
  - name: "檢查標題是否存在"
    type: condition
    variable: page_info
    operator: exists
    then:
      - name: "標題擷取成功"
        type: set_variable
        value: "頁面標題已成功擷取"
        save: status_message
    else:
      - name: "標題擷取失敗"
        type: set_variable
        value: "未找到頁面標題"
        save: status_message

  # 第六步：迴圈處理
  - name: "批次處理"
    type: loop
    count: 3
    index_var: iteration
    steps:
      - name: "處理第 ${iteration} 批"
        type: set_variable
        value: "正在處理第 ${iteration} 批資料"
        save: batch_status
```

#### 支援的步驟類型

| 步驟類型 | 說明 | 關鍵參數 |
|----------|------|----------|
| `navigate` | 導航到指定 URL | `url` |
| `extract` | 擷取當前頁面內容 | `fields`（可選） |
| `screenshot` | 截取當前頁面截圖 | `output`, `format` |
| `wait` | 等待指定秒數 | `seconds` |
| `condition` | 條件分支 | `variable`, `operator`, `then`, `else` |
| `loop` | 迴圈執行子步驟 | `count`, `index_var`, `steps` |
| `set_variable` | 設定工作流變數 | `value` |

#### 支援的條件運算子

| 運算子 | 說明 |
|--------|------|
| `exists` | 變數是否存在 |
| `equals` | 等於指定值 |
| `not_equals` | 不等於指定值 |
| `contains` | 包含指定值 |
| `greater_than` | 大於指定值 |
| `less_than` | 小於指定值 |
| `is_true` | 布林值為真 |
| `is_false` | 布林值為假 |

### `interactive` — 互動式瀏覽器工作階段

啟動一個 REPL（讀取-求值-輸出迴圈）互動式工作階段，即時探索網頁。

```bash
# 啟動互動模式
webpilot interactive

# 帶初始 URL 啟動
webpilot interactive --url https://example.com
```

**互動模式內建命令：**

| 命令 | 說明 |
|------|------|
| `browse <url>` | 導航到指定 URL |
| `extract` | 擷取當前頁面結構化內容 |
| `screenshot [path]` | 儲存截圖（預設 `screenshot.html`） |
| `info` | 顯示當前頁面資訊 |
| `ascii` | 顯示 ASCII 截圖 |
| `title` | 顯示頁面標題 |
| `links` | 列出當前頁面所有連結 |
| `images` | 列出當前頁面所有圖片 |
| `cookies` | 顯示當前 Cookie |
| `help` | 顯示說明資訊 |
| `quit` / `exit` / `q` | 結束互動模式 |

---

## 💡 設計思路與迭代規劃

### 設計理念

WebPilot-CLI 的設計遵循以下核心理念：

1. **極簡主義（Minimalism）**：不引入任何外部依賴，用最少的程式碼實現最多的功能。Python 標準函式庫已經足夠強大，`urllib` 處理網路請求，`html.parser` 解析 HTML，`http.cookiejar` 管理工作階段——我們不需要更多。

2. **宣告式優先（Declarative First）**：能用 YAML 配置表達的，就不需要寫 Python 程式碼。工作流引擎讓非程式設計師也能定義複雜的瀏覽器操作流程。

3. **終端原生（Terminal Native）**：作為命令列工具，終端就是我們的主場。ASCII 截圖、彩色輸出、進度條——讓終端體驗不遜色於 GUI。

4. **AI Agent 友善（Agent Friendly）**：結構化的 JSON 輸出、可程式化的工作流引擎、清晰的狀態管理——每一個設計決策都考慮了 AI Agent 的整合需求。

### 技術選型原因

| 技術選擇 | 原因 |
|----------|------|
| `urllib` 而非 `requests` | 零依賴，標準函式庫自帶，滿足基本 HTTP 需求 |
| `html.parser` 而非 `BeautifulSoup` | 零依賴，標準函式庫自帶，效能可控 |
| `http.cookiejar` 而非 `requests.Session` | 零依賴，原生支援 Cookie 持久化 |
| YAML 工作流 而非 Python 腳本 | 宣告式更易讀、更易維護、更易被 AI 生成 |
| ASCII 截圖 而非 PNG 截圖 | 無需額外依賴（如 Pillow），終端原生展示 |

### 後續規劃

- [ ] 🔌 **外掛系統**：支援自訂擷取器和輸出格式的外掛機制
- [ ] 🗄️ **結果持久化**：支援將擷取結果儲存到 SQLite / CSV
- [ ] 🔄 **增量抓取**：基於 ETag / Last-Modified 的增量內容更新
- [ ] 📡 **API 模式**：內建 HTTP 伺服器，提供 RESTful API 介面
- [ ] 🧪 **斷言引擎**：工作流中支援頁面內容斷言，用於監控和測試
- [ ] 📊 **報告生成**：自動生成工作流執行報告（HTML / PDF）
- [ ] 🌐 **代理支援**：內建 HTTP/SOCKS 代理設定
- [ ] 📦 **批次模式**：支援從檔案讀取 URL 列表進行批次處理
- [ ] 🤖 **MCP 整合**：作為 MCP（Model Context Protocol）伺服器執行

---

## 📦 安裝與部署指南

### 系統需求

- **作業系統**：Windows / macOS / Linux
- **Python 版本**：3.8、3.9、3.10、3.11、3.12
- **磁碟空間**：約 1 MB（原始碼）
- **網路**：需要能存取目標網站

### 安裝方式

```bash
# 方式一：從 GitHub 直接安裝（推薦）
pip install git+https://github.com/gitstq/webpilot-cli.git

# 方式二：複製倉庫後以開發模式安裝
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
pip install -e .

# 方式三：複製倉庫後直接使用（無需安裝）
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
python -m webpilot.cli browse https://example.com
```

### 驗證安裝

```bash
# 查看版本號
webpilot --version

# 查看說明資訊
webpilot --help

# 快速測試
webpilot browse https://example.com
```

### 解除安裝

```bash
pip uninstall webpilot-cli
```

---

## 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！無論是提交 Bug 回報、改進文件，還是提交程式碼 Pull Request。

### 如何貢獻

1. **Fork** 本倉庫
2. 建立你的特性分支：`git checkout -b feature/amazing-feature`
3. 提交你的變更：`git commit -m 'Add some amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 開發環境建置

```bash
# 複製倉庫
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli

# 以開發模式安裝
pip install -e .

# 執行測試
python -m pytest tests/

# 執行特定測試
python -m pytest tests/test_extractor.py -v
```

### 程式碼規範

- 遵循 PEP 8 編碼規範
- 為所有公開函式撰寫文件字串
- 確保所有測試通過後再提交 PR
- 提交資訊使用清晰、描述性的語言

### 提交 Issue

在提交 Issue 之前，請：

1. 搜尋已有的 Issues，避免重複提交
2. 提供重現步驟和期望行為
3. 附上執行環境資訊（Python 版本、作業系統等）

---

## 📄 開源授權

本專案基於 [MIT License](LICENSE) 開源。

```
MIT License

Copyright (c) 2024 WebPilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<p align="center">
  用 ❤️ 和 Python 標準函式庫建構 · <a href="https://github.com/gitstq/webpilot-cli">GitHub</a>
</p>

</details>

---

<a id="english"></a>

<details open>
<summary><h1>🎉 WebPilot-CLI — Lightweight AI Browser Automation CLI Tool</h1></summary>

> 🚀 Zero External Dependencies · YAML Workflow Engine · Smart Content Extraction · Terminal-Native Experience

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8%2B-green" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License">
  <img src="https://img.shields.io/badge/dependencies-zero-brightgreen" alt="Zero Dependencies">
</p>

---

## 🎉 Introduction

**WebPilot-CLI** is a lightweight browser automation CLI tool designed for AI Agents and developers. Built entirely on the Python standard library, it has **zero external dependencies** and works right out of the box.

### 🎯 Project Positioning

As AI Agents become increasingly prevalent, browser automation is a core capability for Agent-Web interaction. However, existing tools are either heavyweight (Selenium, Playwright), complex to set up (requiring browser drivers), or limited in functionality (scraping-only, no orchestration). **WebPilot-CLI** aims to be:

> **A terminal-native browser automation Swiss Army knife that is lightweight, intelligent, and flexible.**

### 💡 Problems We Solve

| Pain Point | Our Solution |
|------------|-------------|
| Existing tools are heavy and complex to install | Pure Python standard library — just `pip install` and go |
| Scraped content is full of noise (navbars, ads, footers) | Smart noise filtering engine that auto-detects and removes irrelevant content |
| Automation requires writing lots of code | YAML workflow engine — declarative config over imperative programming |
| No terminal-native visualization | ASCII art screenshots + HTML Canvas screenshots — "see" web pages in your terminal |
| Multi-step operations are hard to orchestrate | Variable passing, conditional branching, loop control — full workflow orchestration |

### 🌟 Key Differentiators

- 🪶 **Ultra Lightweight**: Zero external dependencies. The entire toolkit uses only Python standard library modules (`urllib`, `html.parser`, `http.cookiejar`)
- 🧠 **Smart Extraction**: Built-in noise detection engine that automatically filters out navigation bars, sidebars, ads, footers, and other irrelevant content
- 📝 **YAML-Driven**: Define complex browser automation flows with declarative YAML, supporting variable passing and conditional branching
- 🖥️ **Terminal-Friendly**: ASCII art screenshots let you "see" web page layouts right in your terminal
- 🔄 **Session Management**: Built-in Cookie/Session management for handling login-required scenarios with ease
- 📤 **Multi-Format Output**: JSON, Markdown, and plain text output formats to fit different downstream consumption needs

---

## ✨ Core Features

- 🌐 **Web Browsing** — Fetch and display web page content with a single command; auto-extracts titles, body text, links, and images
- 📸 **Smart Screenshots** — Two screenshot modes: ASCII art (terminal-friendly) and HTML Canvas (browser-viewable)
- 🔍 **Content Extraction** — Intelligent noise filtering for structured content extraction (title/description/text/links/images)
- ⚙️ **YAML Workflows** — Declaratively define multi-step automation flows with navigate/extract/screenshot/wait/condition/loop steps
- 🔄 **Variable Passing** — Pass data between steps using `${var}` syntax, with support for conditional branching and loops
- 🍪 **Session Management** — Automatic Cookie/Session management with cross-request state persistence
- 🖥️ **Interactive Mode** — Built-in REPL interactive browser session for real-time web exploration
- 📤 **Multi-Format Output** — JSON / Markdown / Plain text, ready for pipeline and script integration
- 🎨 **Colored Terminal** — Rich ANSI colored output for an enhanced terminal reading experience
- 📊 **Progress Display** — Real-time progress bars during workflow execution
- 🛡️ **Robustness** — Auto-retry, timeout control, encoding detection, and error recovery
- 🪶 **Zero Dependencies** — Entirely based on the Python standard library; no third-party packages needed

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or later
- Network connection (to access target websites)
- No browser or browser driver installation required

### Installation

```bash
# Option 1: Install directly from GitHub (recommended)
pip install git+https://github.com/gitstq/webpilot-cli.git

# Option 2: Install from source
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
pip install -e .
```

### Try It Out

```bash
# Browse a web page and view structured content
webpilot browse https://example.com

# Output in JSON format
webpilot browse https://example.com --output json

# Take an ASCII screenshot
webpilot screenshot https://example.com -o screenshot.txt -f ascii

# Take an HTML screenshot (openable in a browser)
webpilot screenshot https://example.com -o screenshot.html -f html

# Extract structured content from a web page
webpilot extract https://example.com --fields title description text

# Run a YAML workflow
webpilot run workflow.yaml

# Start an interactive browser session
webpilot interactive
```

---

## 📖 Detailed Usage Guide

### Global Options

All subcommands support the following global options:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output format: `json` / `markdown` / `text` | `markdown` |
| `--no-color` | | Disable colored terminal output | Off |
| `--verbose` | `-v` | Enable verbose output mode | Off |
| `--version` | `-V` | Show version number | — |

### `browse` — Browse a Web Page

Fetch and display structured content from a web page, with automatic noise filtering.

```bash
# Basic usage
webpilot browse <url>

# Specify timeout and output format
webpilot browse https://example.com --timeout 60 --output json

# Enable verbose mode
webpilot browse https://example.com -v
```

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `url` | Target web page URL (required) | — |
| `--timeout` / `-t` | Request timeout in seconds | 30 |

### `screenshot` — Capture a Screenshot

Two screenshot modes are available: terminal-friendly ASCII art and browser-viewable HTML Canvas.

```bash
# HTML screenshot (default, viewable in a browser)
webpilot screenshot https://example.com -o page.html

# ASCII screenshot (terminal-friendly)
webpilot screenshot https://example.com -f ascii -o page.txt

# Custom terminal width
webpilot screenshot https://example.com -f ascii --width 120
```

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `url` | Target web page URL (required) | — |
| `--output-file` / `-o` | Output file path | `screenshot.html` |
| `--format` / `-f` | Screenshot format: `ascii` / `html` | `html` |
| `--width` | Terminal width for ASCII screenshots (characters) | 80 |

### `extract` — Extract Structured Content

Extract structured data from a web page with field-level filtering.

```bash
# Extract all content
webpilot extract https://example.com

# Extract only title and description
webpilot extract https://example.com --fields title description

# Extract only links and images
webpilot extract https://example.com --fields links images

# JSON output for programmatic processing
webpilot extract https://example.com --output json
```

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `url` | Target web page URL (required) | — |
| `--fields` | Fields to extract: `title` / `description` / `text` / `links` / `images` (multiple allowed) | All |
| `--timeout` / `-t` | Request timeout in seconds | 30 |

### `run` — Execute a YAML Workflow

Define and execute multi-step browser automation flows via YAML files.

```bash
# Run a workflow
webpilot run workflow.yaml

# Export execution results
webpilot run workflow.yaml --export result.json

# Verbose mode
webpilot run workflow.yaml -v
```

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `workflow` | Path to YAML workflow file (required) | — |
| `--export` / `-e` | Export results to a JSON file | No export |

#### YAML Workflow Example

```yaml
name: daily_news_collector
description: Daily news collection workflow

# Global variables
vars:
  base_url: "https://news.example.com"
  output_dir: "output"

# Stop on error
stop_on_error: true

steps:
  # Step 1: Navigate to the target page
  - name: "Open news homepage"
    type: navigate
    url: "${base_url}"
    save: page_info

  # Step 2: Wait for page to load
  - name: "Wait for load"
    type: wait
    seconds: 2

  # Step 3: Extract page content
  - name: "Extract news content"
    type: extract
    fields:
      - title
      - description
      - text
      - links
    save: news_data

  # Step 4: Take a screenshot
  - name: "Save screenshot"
    type: screenshot
    output: "${output_dir}/news_screenshot.html"
    format: html

  # Step 5: Conditional check
  - name: "Check if title exists"
    type: condition
    variable: page_info
    operator: exists
    then:
      - name: "Title found"
        type: set_variable
        value: "Page title was successfully extracted"
        save: status_message
    else:
      - name: "No title found"
        type: set_variable
        value: "No page title found"
        save: status_message

  # Step 6: Loop processing
  - name: "Batch processing"
    type: loop
    count: 3
    index_var: iteration
    steps:
      - name: "Process batch ${iteration}"
        type: set_variable
        value: "Processing batch ${iteration}"
        save: batch_status
```

#### Supported Step Types

| Step Type | Description | Key Parameters |
|-----------|-------------|----------------|
| `navigate` | Navigate to a URL | `url` |
| `extract` | Extract content from the current page | `fields` (optional) |
| `screenshot` | Take a screenshot of the current page | `output`, `format` |
| `wait` | Wait for a specified number of seconds | `seconds` |
| `condition` | Conditional branching | `variable`, `operator`, `then`, `else` |
| `loop` | Execute sub-steps in a loop | `count`, `index_var`, `steps` |
| `set_variable` | Set a workflow variable | `value` |

#### Supported Condition Operators

| Operator | Description |
|----------|-------------|
| `exists` | Variable exists |
| `equals` | Equals a specified value |
| `not_equals` | Does not equal a specified value |
| `contains` | Contains a specified value |
| `greater_than` | Greater than a specified value |
| `less_than` | Less than a specified value |
| `is_true` | Boolean value is true |
| `is_false` | Boolean value is false |

### `interactive` — Interactive Browser Session

Launch a REPL (Read-Eval-Print Loop) interactive session for real-time web exploration.

```bash
# Start interactive mode
webpilot interactive

# Start with an initial URL
webpilot interactive --url https://example.com
```

**Built-in Interactive Commands:**

| Command | Description |
|---------|-------------|
| `browse <url>` | Navigate to a URL |
| `extract` | Extract structured content from the current page |
| `screenshot [path]` | Save a screenshot (default: `screenshot.html`) |
| `info` | Show current page information |
| `ascii` | Display an ASCII screenshot |
| `title` | Show the page title |
| `links` | List all links on the current page |
| `images` | List all images on the current page |
| `cookies` | Show current cookies |
| `help` | Show help information |
| `quit` / `exit` / `q` | Exit interactive mode |

---

## 💡 Design Philosophy & Roadmap

### Design Principles

WebPilot-CLI is guided by the following core principles:

1. **Minimalism**: No external dependencies. Achieve maximum functionality with minimum code. The Python standard library is already powerful enough — `urllib` for HTTP, `html.parser` for HTML parsing, `http.cookiejar` for session management. We don't need anything else.

2. **Declarative First**: If it can be expressed in YAML configuration, it shouldn't require Python code. The workflow engine empowers non-programmers to define complex browser automation flows.

3. **Terminal Native**: As a CLI tool, the terminal is our home turf. ASCII screenshots, colored output, progress bars — the terminal experience should rival any GUI.

4. **Agent Friendly**: Structured JSON output, programmable workflow engine, clear state management — every design decision considers AI Agent integration needs.

### Technology Choices

| Choice | Rationale |
|--------|-----------|
| `urllib` over `requests` | Zero dependencies, included in the standard library, sufficient for basic HTTP needs |
| `html.parser` over `BeautifulSoup` | Zero dependencies, included in the standard library, controllable performance |
| `http.cookiejar` over `requests.Session` | Zero dependencies, native Cookie persistence support |
| YAML workflows over Python scripts | Declarative approach is more readable, maintainable, and AI-generable |
| ASCII screenshots over PNG screenshots | No extra dependencies (like Pillow), native terminal display |

### Roadmap

- [ ] 🔌 **Plugin System**: Support for custom extractors and output format plugins
- [ ] 🗄️ **Result Persistence**: Save extraction results to SQLite / CSV
- [ ] 🔄 **Incremental Scraping**: Content updates based on ETag / Last-Modified
- [ ] 📡 **API Mode**: Built-in HTTP server with RESTful API endpoints
- [ ] 🧪 **Assertion Engine**: Page content assertions in workflows for monitoring and testing
- [ ] 📊 **Report Generation**: Automatic workflow execution reports (HTML / PDF)
- [ ] 🌐 **Proxy Support**: Built-in HTTP/SOCKS proxy configuration
- [ ] 📦 **Batch Mode**: Process URL lists from a file in bulk
- [ ] 🤖 **MCP Integration**: Run as an MCP (Model Context Protocol) server

---

## 📦 Installation & Deployment Guide

### System Requirements

- **Operating System**: Windows / macOS / Linux
- **Python Version**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Disk Space**: ~1 MB (source code)
- **Network**: Access to target websites required

### Installation Methods

```bash
# Option 1: Install directly from GitHub (recommended)
pip install git+https://github.com/gitstq/webpilot-cli.git

# Option 2: Clone and install in development mode
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
pip install -e .

# Option 3: Clone and use directly (no installation needed)
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli
python -m webpilot.cli browse https://example.com
```

### Verify Installation

```bash
# Check version
webpilot --version

# View help
webpilot --help

# Quick test
webpilot browse https://example.com
```

### Uninstall

```bash
pip uninstall webpilot-cli
```

---

## 🤝 Contributing Guide

We welcome and appreciate contributions of all kinds — whether it's filing bug reports, improving documentation, or submitting code Pull Requests.

### How to Contribute

1. **Fork** this repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Submit a **Pull Request**

### Development Setup

```bash
# Clone the repository
git clone https://github.com/gitstq/webpilot-cli.git
cd webpilot-cli

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Run specific tests
python -m pytest tests/test_extractor.py -v
```

### Code Standards

- Follow PEP 8 coding conventions
- Write docstrings for all public functions
- Ensure all tests pass before submitting a PR
- Use clear, descriptive commit messages

### Filing Issues

Before submitting an issue, please:

1. Search existing issues to avoid duplicates
2. Provide reproduction steps and expected behavior
3. Include your environment details (Python version, OS, etc.)

---

## 📄 License

This project is released under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2024 WebPilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<p align="center">
  Built with ❤️ and the Python Standard Library · <a href="https://github.com/gitstq/webpilot-cli">GitHub</a>
</p>

</details>
