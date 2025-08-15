# AI Runner Hjy（中文文档）

[![PyPI 版本](https://badge.fury.io/py/ai-runner-hjy.svg)](https://badge.fury.io/py/ai-runner-hjy)
[![Python CI](https://github.com/your-username/ai-runner-hjy/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/ai-runner-hjy/actions/workflows/ci.yml)
[![Python Versions](https://img.shields.io/pypi/pyversions/ai-runner-hjy.svg)](https://pypi.org/project/ai-runner-hjy/)
[![Coverage](https://img.shields.io/badge/coverage-70%2B%25-brightgreen.svg)](#)
[![Downloads](https://img.shields.io/pypi/dm/ai-runner-hjy.svg)](https://pypi.org/project/ai-runner-hjy/)
[![许可证: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 一句话：数据库驱动的 AI 调用与审计引擎 —— 你只需改“配置”，无需改代码。

### Hello, World（最小可运行示例）
```python
from ai_runner_hjy import init, run_once

config = init({
    "PROJECT_NAME": "demo",
    "MYSQL_HOST": "<你的RDS>",
    "MYSQL_USER": "<user>",
    "MYSQL_PASSWORD": "<pass>",
    "MYSQL_AI_DATABASE": "ai_config",
    "AI_PEPPER": "<强pepper>"
})

run_once(config_key="<your_config_key>", config=config)
```

```mermaid
flowchart LR
    A[Install] --> B[Configure]
    B --> C[Quickstart]
    C --> D[Run Once]
```

一个面向云原生环境的、模块化与可配置的 AI 调用运行器（OpenAI Chat Completions 兼容）。

`ai-runner-hjy` 通过数据库驱动的方式集中管理“模型/参数/提示词”，在运行期注入配置，保证高内聚、低耦合与可审计，适合在多项目/多环境中复用与扩展。

## 功能特性
- **数据库驱动**：在 MySQL 中集中管理模型、提示词与参数，改配置即可生效，无需重新部署。
- **云原生友好**：完全依赖注入，模块本身无状态；与容器/DevOps 流程天然兼容。
- **安全合规**：API Key 采用 AES-256-GCM 加密存储，仅在内存中解密使用。
- **可观测/可审计**：自动入库调用指标、用量与错误，便于追踪与审计。
- **双用法**：同时支持命令行（CLI）与 Python 代码方式调用。

## 快速开始

### 1. 安装
```bash
pip install ai-runner-hjy
```

### 2. 配置
本包使用 Pydantic Settings 读取环境变量（支持 `.env` 文件），建议在项目根目录创建：

`basic.env`
```env
PROJECT_NAME="my_awesome_project"
```

`mysql.env`
```env
MYSQL_HOST="your_rds_host"
MYSQL_USER="your_db_user"
MYSQL_PASSWORD="your_db_password"
MYSQL_PORT="3306"
MYSQL_AI_DATABASE="your_ai_config_db"
AI_PEPPER="a_strong_secret_pepper_for_encryption"
```

> 完整字段见源码 `ai_runner_hjy/core/config.py: AppConfig`。

#### 配置字段表（关键项）

| 字段 | 类型 | 环境变量 | 是否必填 | 说明 |
| :-- | :-- | :-- | :--: | :-- |
| `project_name` | `str` | `PROJECT_NAME` | 否 | 项目标识，仅用于日志标注 |
| `mysql_host` | `str` | `MYSQL_HOST` | 是 | MySQL 主机名/IP |
| `mysql_user` | `str` | `MYSQL_USER` | 是 | MySQL 用户名 |
| `mysql_password` | `str` | `MYSQL_PASSWORD` | 是 | MySQL 密码 |
| `mysql_port` | `int` | `MYSQL_PORT` | 否(默认`3306`) | MySQL 端口 |
| `mysql_ai_database` | `str` | `MYSQL_AI_DATABASE` | 是 | 存放 AI 配置与日志的数据库名 |
| `ai_pepper` | `str` | `AI_PEPPER` | 是 | 解密 API Key 的 Pepper（严禁泄露） |
| `json_schema_enforce` | `bool` | `JSON_SCHEMA_ENFORCE` | 否(默认`true`) | 是否强制 JSON 输出校验 |
| `enforce_no_english` | `bool` | `ENFORCE_NO_ENGLISH` | 否(默认`true`) | 是否校验 JSON 值不含英文字符 |
| `enable_oss_spillover` | `bool` | `ENABLE_OSS_SPILLOVER` | 否(默认`false`) | 大 JSON 外溢 OSS 并在日志写链接 |

### 3. 数据库准备
在您已有的 MySQL 中创建相应表（连接/模型/参数/提示词/配置/调用日志等）。如需参考，您可以在企业内部文档或示例 SQL 中获取表结构（本包不强制创建/改表，避免越权）。

## 使用方法

### CLI 调用
```bash
ai-runner run-once your_config_key
```

### 以 Python 库方式
```python
from ai_runner_hjy import get_config, run_once

def main():
    # 1) 载入配置
    config = get_config()
    # 2) 运行数据库中的某个 config_key
    run_once(config_key="your_config_key", config=config)

if __name__ == "__main__":
    main()
```
> 设计要点：配置一次性加载并注入到需要的函数（“云原生公民”原则）。

## 5 分钟上手（从安装到一次成功调用）

1) 安装（建议虚拟环境）
```bash
/usr/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e ".[test]"
```

2) 准备配置（两选一）
- A：字典注入（推荐）
```python
from ai_runner_hjy import init, run_once
config = init({
  "PROJECT_NAME":"demo",
  "MYSQL_HOST":"<你的RDS>","MYSQL_USER":"<user>","MYSQL_PASSWORD":"<pass>",
  "MYSQL_AI_DATABASE":"ai_config","AI_PEPPER":"<强pepper>"
})
run_once("<your_config_key>", config)
```
- B：.env 文件（`basic.env`/`mysql.env`）后用 `get_config()`

3) （可选）只读导出你的 RDS 表结构
```bash
set -a; source mysql.env; set +a
ai-runner cfg dump-schema --db "$MYSQL_AI_DATABASE" --prefix ai_ \
  --out docs/SCHEMA_AUTO.md --json docs/schema_dump.json
```

4) 生成 YAML 模板并校验
```bash
ai-runner cfg sample --provider openrouter --out tmp/configs_full.yaml
ai-runner cfg verify -f tmp/configs_full.yaml   # 可加 --db-check 做只读存在性检查
```

5) （可选）导入 YAML 到 RDS
```bash
ai-runner cfg gen -f tmp/configs_full.yaml
```

6) 运行一次
```bash
ai-runner run-once <your_config_key>
```

## 60 秒演示（Demo，一键生成/上传/调用/保存结果）

```bash
source .venv/bin/activate
ai-runner quickstart --mode demo --media-path ../2.mp3
# 结果文件：tmp/demo_result.json（已脱敏，content 为“仅供展示”的结构）
```

输入参数（Demo 模式）

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | :--: | --- |
| project | string | 是 | 固定 `demo_project` |
| route_key | string | 是 | 固定 `demo_route` |
| MEDIA_URL | string | 是 | 通过 OSS 上传得到的公开 URL（命令会自动上传） |

输出（Demo 模式，结构化，敏感信息已脱敏）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| status | number | HTTP 状态码（例如 200） |
| response.id | string | 响应 ID |
| response.object | string | 固定 `chat.completion`（演示） |
| response.model | string | 模型名（演示） |
| response.choices[0].message.content | string | 文本为 `{"result":"【仅供展示】示例输出结构"...}` |
| response.usage.total_tokens | number | token 统计 |

更详细的 Demo 说明见 `QUICKSTART_DEMO.md`。

#### 字典注入（可选，更易测试/更显式）
```python
from ai_runner_hjy import init, run_once

config = init({
    "PROJECT_NAME": "my_awesome_project",
    "MYSQL_HOST": "your_rds_host",
    "MYSQL_USER": "your_db_user",
    "MYSQL_PASSWORD": "your_db_password",
    "MYSQL_AI_DATABASE": "your_ai_config_db",
    "AI_PEPPER": "a_strong_secret_pepper_for_encryption",
})

run_once(config_key="your_config_key", config=config)
```

## API 速查
- `get_config() -> AppConfig`：加载全局配置（来自 `.env`/环境变量）
- `init(config: dict) -> AppConfig`：以字典注入方式创建并校验配置（推荐在服务内调用）
- `validate_required_fields(config: AppConfig) -> None`：严格校验必填项，缺失直接抛出 `ValueError`
- `run_once(config_key: str, config: AppConfig)`：执行单个配置项
- `run_route(project: str, route_key: str, config: AppConfig)`：执行路由（按路由成员策略选择配置）

## 最佳实践与建议
- 将密钥/连接信息放入 `.env`（不入库），本地/CI 通过环境注入。
- 数据库及表结构由平台侧治理，运行器仅“读取/写入记录”，不做 DDL。
- 生产环境建议开启只读账号+专用日志库，区分业务库与日志库权限。

---
如需维护者指南、架构说明与贡献流程，请参阅《开发者文档》（`DEVELOPER.md`）。

## 常见错误对照表（FAQ）

- 缺少必填配置
  - 现象：启动时报 `Error loading configuration: Missing required configuration: ...`
  - 处理：补齐 `MYSQL_HOST/USER/PASSWORD/MYSQL_AI_DATABASE/AI_PEPPER`

- 找不到 config_key
  - 现象：Python 调用抛 `CONFIG_NOT_FOUND`
  - 处理：确认 `ai_config` 中存在该 key；可用 `cfg sample` 生成模板，`cfg gen` 导入

- 无法连接 RDS / 权限不足
  - 现象：连接失败或 `dump-schema` 报权限错误
  - 处理：网络白名单、端口、只读账号 `SELECT`/`SHOW VIEW` 权限

- 下游 429/5xx 或网络错误
  - 说明：内置退避重试；仍失败会记录错误码 `HTTP_429_RATE_LIMIT/HTTP_5XX_SERVER_ERROR/NETWORK_*`
  - 处理：降低速率/检查提供商状态/网络配置

- JSON 不合规 / 出现英文字符
  - 现象：错误码 `SCHEMA_INVALID` 或 `LETTER_DETECTED`
  - 处理：在 Prompt 里确保 `response_format` 为 `{type:json_object}`，或在参数白名单启用 `JSON_SCHEMA_ENFORCE=true`；调整模型输出


## RDS 表结构（自动导出）

- 本项目支持“只读导出 RDS 表结构”，导出结果以你的实际数据库为准：
  - 数据库：`ai_config`
  - 前缀：`ai_`
  - 最近导出时间（UTC）：`2025-08-14T07:16:59.941293Z`
  - 查看全文：`docs/SCHEMA_AUTO.md`（DDL + 列信息），原始 JSON：`docs/schema_dump.json`

### 一键重新导出（只读）

```bash
source .venv/bin/activate
set -a; source mysql.env; set +a  # 或在环境里注入五个必填项
ai-runner cfg dump-schema \
  --db "$MYSQL_AI_DATABASE" \
  --prefix ai_ \
  --out docs/SCHEMA_AUTO.md \
  --json docs/schema_dump.json
```

说明：导出仅执行 `SHOW TABLES` / `SHOW CREATE TABLE` / `SHOW FULL COLUMNS`，不会做任何 DDL/DML。数据库账号建议使用“只读权限”，至少需要能读取目标库中表的元数据（常见为对库/表的 `SELECT` 权限；如包含视图，可能需要 `SHOW VIEW`）。

## 本地快速试用（无 RDS 场景）

### 启动本地 MySQL（端口 3307）
```bash
docker compose up -d
# 首次会自动执行 scripts/mysql/init.sql 初始化最小表与一条 config_key
```

### 准备最小环境变量（写入 mysql.env）
```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=ai
MYSQL_PASSWORD=ai123
MYSQL_AI_DATABASE=ai_config
AI_PEPPER=dev_only_pepper
```

### 生成 YAML 模板与校验
```bash
source .venv/bin/activate
ai-runner cfg sample --provider openrouter --out tmp/configs_full.yaml
ai-runner cfg verify -f tmp/configs_full.yaml   # 仅静态校验
```

### （可选）导入 YAML（会写库）
```bash
ai-runner cfg gen -f tmp/configs_full.yaml
```

### 运行一次
```bash
ai-runner run-once gemini25_single_chat
```

