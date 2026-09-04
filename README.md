# OceanEye 巨量行情 V0.1

OceanEye 是一个运行在 Windows 11 本机的“广告投放行情终端”。当前版本使用动态 Mock 数据，不需要巨量引擎账号或 Access Token。

> 当前所有数据都是演示数据，不代表真实业务数据。系统只做分析和提醒，不会暂停广告、修改预算或修改出价。

## 第一次运行

### 1. 确认基础环境

需要安装：

- Node.js LTS（当前电脑已检测到）
- Python 3.11 或更高版本

如果没有 Python：打开 [Python Windows 下载页](https://www.python.org/downloads/windows/)，下载安装程序。安装时务必勾选 **Add python.exe to PATH**。

### 2. 安装 OceanEye

在项目根目录双击：

```text
setup.bat
```

它会自动安装前后端依赖，并初始化 SQLite 与 Mock 数据。已有数据库不会被清空或覆盖。

## 平时运行

双击：

```text
start.bat
```

系统会自动启动后端、前端并打开浏览器。

默认网址：

```text
http://localhost:5173
```

## 停止

双击：

```text
stop.bat
```

停止程序不会删除 SQLite 数据。

## 当前包含的功能

- 艺恒、鼎远两个 Mock 账户，六个不同表现的计划
- 每 10 秒生成消耗、展示、点击、转化数据并写入 SQLite
- 今日消耗、转化、CPA、点击、展示、CTR、CVR、余额和预算使用率
- 最近 30 分钟与上一 30 分钟的涨跌对比，CPA 下降按改善显示
- ECharts 分时走势图、Tooltip、十字线、滚轮缩放、平滑更新
- 5 分钟、15 分钟、30 分钟、1 小时时间粒度
- 计划排序、状态判断、计划详情、账户排行
- 实时异动、页面内 Toast、可选浏览器通知
- 可配置预警阈值，保存在 SQLite
- 本地规则式 AI 看盘（只读）
- 导入、日报、素材检测的后续入口

## 数据保存位置

```text
data/oceaneye.db
```

Mock 引擎只追加指标快照，不会在启动时清空已有数据。CTR、CVR、CPA 由后端根据原始指标计算，避免 Infinity 和 NaN。

## 如何切换真实巨量数据

V0.1 已建立独立 Provider 接口，但没有编造或写死巨量 API。正式接入前：

1. 复制 `.env.example` 为 `.env`。
2. 获得真实的 App ID、Secret、Access Token 和广告主 ID。
3. 根据巨量引擎开放平台当时的官方文档实现 `backend/app/providers/oceanengine_provider.py`。
4. 完成只读接口验证后，再把 `.env` 中的 `DATA_SOURCE` 改为 `oceanengine`。

`.env` 已被 Git 忽略。不要把 Token 或 Secret 发到聊天、提交到 Git，或写进前端代码。

## 开发命令（可选）

后端测试：

```powershell
$env:PYTHONPATH = (Get-Location)
.\.venv\Scripts\python.exe -m pytest backend\tests
```

如果项目使用内置运行时，则执行：

```powershell
$env:PYTHONPATH = (Get-Location)
.\runtime\python\python.exe -m pytest backend\tests
```

前端构建：

```powershell
npm run build --prefix frontend
```

接口文档（运行后）：

```text
http://localhost:8000/docs
```

## 端口占用

OceanEye 使用：

- 前端：5173
- 后端：8000

如果端口被占用，`start.bat` 会直接告诉你具体端口。关闭占用该端口的软件后，再双击 `start.bat`。
