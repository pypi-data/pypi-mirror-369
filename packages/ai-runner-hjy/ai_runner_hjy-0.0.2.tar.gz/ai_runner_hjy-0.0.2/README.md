# AI Runner Hjy · 用户手册（V0.0.2）

用“配置驱动”的方式稳定调用 AI，强约束日志与审计。四大核心场景开箱即用：
- 场景1：项目+接口昵称直接调用
- 场景2：本地沙盒（Run 可视化）
- 场景3：文件上传并备案（返回 URL）
- 场景4：全栈 YAML + 一键挂路由（不碰 DB）

---

## 1 分钟快速开始

```bash
# 体检（只查环境/DB，零副作用）
ai-runner-hjy init --env-only --dev-port 8899   # 环境就绪 + 自动找可用端口并写入 basic.env
ai-runner-hjy init --db-only                    # 仅查数据库连通（SELECT 1）
```

---

## 四大核心场景（最少命令）

### 场景1｜项目+接口昵称直接调用
```bash
ai-runner-hjy route -p dogvoice -r dogvocal_test -d '{"IMAGE_URL":"https://..."}'
```
输出：一份结构化结果（status/trace_id/usage/response），并写一条 `ai_call_logs`。

### 场景2｜本地沙盒（Run）
```bash
ai-runner-hjy dev --host 127.0.0.1 --port ${DEV_SERVER_PORT:-8899}
# 浏览器打开： http://127.0.0.1:${DEV_SERVER_PORT:-8899}
```
页面只需填 `project/route/variables(JSON)`，点击 Run 即可。

### 场景3｜文件上传并备案（返回 URL）
```bash
python -c 'from backend.ai_runner_hjy.core.oss import upload_file; print(upload_file("backend/tmp/1.mp3"))'
```
输出：一个可访问的文件 URL；RDS 备案到 `<OSS_DATABASE>.<OSS_TABLENAME>`。

### 场景4｜全栈 YAML + 一键挂路由（不碰 DB）
```bash
ai-runner-hjy cfg gen -f backend/tmp/exp-live-test/fullstack.yaml
ai-runner-hjy cfg route-pool -f backend/tmp/exp-live-test/members.yaml   # 独占对齐（默认），支持 --append/--dry-run
```
输出：upsert 汇总与成员对齐结果；随后直接跑“场景1”。

---

## 常用命令速查
```bash
ai-runner-hjy init [--env-only|--db-only] [--dev-port 8899]
ai-runner-hjy cfg gen -f <configs.yaml>
ai-runner-hjy cfg route-pool -f <members.yaml> [--append] [--dry-run]
ai-runner-hjy route -p <project> -r <route> -d '<json>'
ai-runner-hjy dev --host 127.0.0.1 --port 8899
```

---

## 环境变量模板
```bash
cp env_example/basic.env.example basic.env
cp env_example/mysql.env.example mysql.env
cp env_example/oss.env.example oss.env
cp env_example/ai.env.example ai.env
```

## 安装依赖（清华源）
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

## 运行测试
```bash
pytest
```

---

## 详细文档（docs/）
- 初始化与体检: `docs/manual/init.md`
- 场景1：`docs/manual/scenario-1.md`
- 场景2：`docs/manual/scenario-2.md`
- 场景3：`docs/manual/scenario-3.md`
- 场景4：`docs/manual/scenario-4.md`
- CLI 详解：`docs/manual/cli.md`
- 故障排查：`docs/manual/troubleshooting.md`

> 其余细节文档：`backend/ai_runner_hjy/docs/`（路由策略、配置开关、表结构）。
