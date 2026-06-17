# Phase 1 学习报告 - MVP

> 时间：2026.06.17
> 状态：✅ 完成（代码通过审查，等待用户验收）

---

## 一、这阶段做了什么

| 步骤 | 内容 | 时间 |
|:----:|------|:----:|
| 环境搭建 | Python venv + 装依赖（streamlit/pdfplumber/openai/dotenv） | 30min |
| PDF解析 | 用 pdfplumber 提取简历文字（中文不乱码） | 30min |
| API集成 | 用 openai 库调 DeepSeek（复用Chrome插件Prompt） | 1h |
| 页面骨架 | Streamlit 布局：侧边栏上传 + 主区JD + 按钮 + 结果展示 | 1h |
| 代码审查 | 双Agent审查，修复了5个问题（含BUG和安全） | 1h |

## 二、代码结构

```
ai-resume-optimizer-web/
├── app.py              # Streamlit主页面（~220行）
├── ai_client.py        # DeepSeek API调用 + Prompt模板
├── pdf_parser.py       # PDF解析（~30行）
├── .env                # API Key（已gitignore）
├── requirements.txt    # 依赖清单
├── CLAUDE.md           # 项目规则
└── .gitignore
```

## 三、技术选型速记（面试用）

### 为什么选 pdfplumber 而不是 PyMuPDF？
PyMuPDF 对中文PDF的字体编码支持不好，大量中文PDF提取出来是乱码。pdfplumber 基于PDF原始文本流提取，不依赖字体渲染，中文更稳定。

### 为什么选 DeepSeek 而不是 OpenAI？
- 便宜：DeepSeek API 成本是 OpenAI 的 1/10
- 中文好：DeepSeek 的中文理解能力不输 GPT-4
- 兼容 OpenAI 接口：代码几乎不用改

### 为什么不用 Flask/FastAPI 而是 Streamlit？
Streamlit 是 Python 全栈框架，写一个网页不用学 HTML/CSS/JS，适合快速出 MVP。如果要上生产，再拆成 FastAPI 后端 + React 前端。

## 四、代码审查发现的坑

| 问题 | 怎么修 | 面试怎么说 |
|------|--------|-----------|
| PDF内容更新后，用户编辑过的文本框不刷新 | `st.session_state.resume_editor = text` | 「Streamlit 的 widget 状态独立于 value 参数，需要手动同步 session_state」 |
| API失败时旧结果"复活" | 异常处理里清空 `st.session_state.result` | 「状态管理要考虑异常路径，失败时不能残留旧数据误导用户」 |
| `load_dotenv()` 依赖 CWD | 改用 `Path(__file__).parent / ".env"` | 「用相对路径加载 env 文件，不依赖当前工作目录，增加可移植性」 |
| AI输出用 `unsafe_allow_html=True` 可能有XSS风险 | 改用纯 `st.markdown()` | 「不信任AI输出的内容，防止Prompt注入」 |
| API调用没有重试 | 加了3次指数退避重试 | 「API调用要考虑网络抖动，加重试提高可用性」 |

## 五、面试会怎么问

| 问题 | 能用这个项目回答什么 |
|------|-------------------|
| 「你做过什么AI项目？」 | 一个完整的AI简历优化器，上传PDF→调DeepSeek→出结果 |
| 「为什么选Streamlit？」 | 纯Python开发效率高，MVP阶段快速验证 |
| 「有没有考虑异常情况？」 | PDF解析失败兜底、API重试、状态管理 |
| 「RAG怎么做的？」 | Phase 2加，目前Phase 1是直接调API |

## 六、文件清单

| 文件 | 行数 | 作用 |
|------|:----:|------|
| app.py | ~220 | Streamlit主页面 |
| ai_client.py | ~170 | API调用 + 6种Prompt模板 |
| pdf_parser.py | ~30 | PDF文字提取 |
| requirements.txt | 4 | 依赖 |
| .env | 1 | API Key |
| CLAUDE.md | ~60 | 项目规则 |
| .gitignore | ~15 | 忽略规则 |

## 七、下一阶段预告

**Phase 2：加 RAG**
- 用 LangChain 做文档切片
- Chroma 做向量存储
- 构建简历知识库
- 检索增强优化

**需要你确认后才能推进。**
