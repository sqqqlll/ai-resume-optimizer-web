# Phase 3 学习报告 - 工程化

> 时间：2026.06.17
> 状态：✅ 完成（Docker化 + CI + 成本统计 + 部署准备）

---

## 一、这阶段做了什么

| 步骤 | 内容 |
|:----:|------|
| Docker化 | Dockerfile + docker-compose.yml，slim镜像+PyTorch CPU版 |
| GitHub Actions CI | 语法检查 → Docker构建 → 启动测试 |
| 成本统计 | 每次调用显示次数和总消耗（页面展示） |
| 代码审查 | 修复了基础镜像兼容性、变量命名、缓存等问题 |

## 二、新增/修改文件

```
Dockerfile                      ← 新建
docker-compose.yml              ← 新建
.github/workflows/ci.yml        ← 新建
app.py                          ← 修改（加使用统计面板 + 每次调用累计）
ai_client.py                    ← 修改（Token统计 + finish_reason处理）
.gitignore                      ← 修改（加Docker忽略）
requirements.txt                ← 修改（加langchain等依赖）
```

## 三、面试话术速记

### Docker
> 「我用Docker容器化了项目，docker-compose一键启动，保证了环境一致性。镜像用python:3.12-slim + PyTorch CPU版，体积可控。」

面试官追问「为什么用Docker？」
> 「面试官你也能一键跑起来看我的项目，不用装依赖配环境。」

### CI
> 「用GitHub Actions做了CI，每次push自动检查Python语法 + Docker构建。」

### 成本意识
> 「我做了个使用统计面板，每次调用显示次数和成本。DeepSeek API很便宜，一次优化大概1分钱。」

## 四、部署到Streamlit Cloud（需你操作）

项目已经可以部署了。你在终端里执行：

```bash
cd F:/cc2/ai-resume-optimizer-web
git init
git add .
git commit -m "init"
```

然后推到你的GitHub，再到 https://streamlit.io/cloud 绑定仓库、设置 `DEEPSEEK_API_KEY` 环境变量即可。

---

## 五、Phase 变更日志

| Phase | 内容 | 状态 | 文件数 |
|:----:|------|:----:|:-----:|
| **Phase 1** | MVP：Streamlit+PDF+DeepSeek | ✅ | 4个.py |
| **Phase 2** | RAG：LangChain+Chroma+知识库 | ✅ | +1个.py |
| **Phase 3** | 工程化：Docker+CI+成本+部署 | ✅ | +3个文件 |
| **整体完成** | 项目已可部署面试 | ✅ | **8个核心文件** |

## 六、最终项目文件清单

```
ai-resume-optimizer-web/
├── app.py              # Streamlit主界面（~280行）
├── ai_client.py        # DeepSeek API + 6种Prompt + Token统计
├── pdf_parser.py       # PDF简历解析
├── rag_engine.py       # RAG引擎（Chroma + 知识库）
├── Dockerfile          # 容器化
├── docker-compose.yml  # 一键启动
├── .github/workflows/ci.yml  # CI流水线
├── requirements.txt    # 依赖
├── .env                # API Key（已忽视）
├── .gitignore
├── CLAUDE.md           # 项目规则
├── Phase1-学习报告.md
├── Phase2-学习报告.md
└── Phase3-学习报告.md
```
