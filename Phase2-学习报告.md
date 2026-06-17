# Phase 2 学习报告 - RAG知识库增强

> 时间：2026.06.17
> 状态：✅ 完成（应用已运行，知识库检索正常）

---

## 一、这阶段做了什么

| 步骤 | 内容 |
|:----:|------|
| GitHub搜参考 | 找到 Smart-ATS-System-using-RAG，分析其LangChain+Chroma+sentence-transformers架构 |
| 安装依赖 | langchain、langchain-chroma、langchain-huggingface、sentence-transformers |
| 创建rag_engine.py | 核心RAG模块：预置知识库 + Chroma向量库 + MMR检索 |
| 修改ai_client.py | 新增 `optimize_resume_with_rag()`：在Prompt中注入知识库上下文 |
| 修改app.py | 侧边栏RAG状态 + RAG开关 + 优化按钮自动使用RAG + 展示检索结果 |
| 双Agent审查 | 发现3个严重Bug（level参数丢失、*args吞噬、persist废弃）并修复 |
| 现场测试 | 浏览器打开，知识库7个条目加载正常，RAG开关可用 |

## 二、新增/修改文件

```
rag_engine.py    ← 新建（核心RAG模块 ~220行）
ai_client.py     ← 修改（新增 optimize_resume_with_rag）
app.py           ← 修改（RAG集成 + 侧边栏 + 按钮逻辑）
requirements.txt ← 修改（加6个依赖）
```

## 三、RAG架构图

```
用户上传简历 + 粘贴JD
        ↓
RAG引擎：用JD+简历内容作为query
        ↓
Chroma向量库 → MMR检索 → 找到最相关的3条知识
        ↓
知识上下文 + 原始Prompt → DeepSeek API → 优化结果
        ↓
展示结果 + 展示「检索到的知识库内容」
```

## 四、知识库内容（面试重点）

| 条目 | 用途 |
|------|------|
| STAR法则模板 | 教AI怎么帮用户改写经历 |
| 弱动词替换表 | 替换"负责/参与/协助"等弱词 |
| 量化表达示例库 | 教AI怎么把成果数据化 |
| AI行业关键词 | 行业技能词库，用于匹配JD |
| 简历结构模板 | 优秀简历的模块顺序 |
| 常见简历错误 | 避免AI给出过时的建议 |

**面试话术：** 「我预置了一个简历知识库涵盖STAR模板、量化词库、行业关键词等6个维度。优化时先检索最相关的3条知识注入Prompt，让AI基于行业最佳实践给出建议，而不是凭空编。」

## 五、代码审查修了哪些坑

| Bug | 问题 | 怎么修的 |
|-----|------|---------|
| BUG-1 | `"level" in dir()` 永远为假 | 重构 `run_action` 用显式参数代替 `*args` |
| BUG-2 | 非RAG路径缺少level参数 | 统一用显式参数传递 |
| BUG-3 | `*args` 吞噬实参但不使用 | 删除 `*args`，所有参数显式声明 |
| BUG-4 | Chroma `persist()` 已废弃 | 新版Chroma自动持久化，去掉调用 |
| BUG-5 | `_collection.count()` 私用API | 改用 `len(vector_store.get()["ids"])` |

## 六、面试关键词（这个阶段能聊的）

| 面试题 | 用这个项目怎么回答 |
|--------|------------------|
| RAG是什么？ | 「我的项目里做了RAG：上传简历后先从一个预置知识库里检索相关建议，再和Prompt一起发给AI，这样结果有依据。」 |
| 向量库选型对比？ | 「用Chroma因为它零配置。如果上生产会考虑Milvus（分布式）或Pinecone（云服务）。」 |
| 为什么用MMR检索？ | 「MMR比普通相似度检索好，它保证回来的结果不重复——比如既有STAR模板又有关键词建议。」 |
| Embedding模型怎么选？ | 「用BAAI/bge-small-zh-v1.5，中文embedding里效果最好，才33MB本地跑无延迟。」 |
| 知识库数据哪来的？ | 「预置的简历最佳实践，包括STAR模板、量化词库、行业关键词等。不是放用户隐私数据。」 |

## 七、Phase 2 文件清单

| 文件 | 行数 | 说明 |
|------|:----:|------|
| app.py | ~240 | Streamlit主页（含RAG集成） |
| ai_client.py | ~194 | DeepSeek API + 6种Prompt + RAG增强版 |
| pdf_parser.py | ~30 | PDF解析 |
| rag_engine.py | ~220 | **核心：RAG引擎（知识库+Chroma+检索）** |
| requirements.txt | 10 | 依赖 |
| Phase1-学习报告.md | 学习报告 |
| **Phase2-学习报告.md** | **本文** |

## 八、下一阶段预告

**Phase 3：工程化**
- Docker + docker-compose 一键启动
- GitHub Actions CI（自动测试+自动部署）
- 成本计算 + 使用数据展示
- 部署到Streamlit Cloud
