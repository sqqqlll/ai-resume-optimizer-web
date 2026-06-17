# AI简历优化器 - Web版

## 项目定位
Python + Streamlit + RAG 简历优化器。跟Chrome插件（`F:\cc2\ai-resume-optimizer`）互补：插件抓JD，Web版做AI分析+RAG。

## 权限
此项目下所有基本操作（读文件、写文件、安装依赖、运行脚本、终端命令、Git操作、网络请求等）均自动授权，无需每次确认。

## 技术栈
- Python 3.11+
- Streamlit（前端）
- LangChain（RAG编排）
- Chroma（向量数据库）
- DeepSeek API（LLM）
- pdfplumber（PDF解析）
- Docker（可选，工程化阶段加）

## 项目规则（重要）

### 工作流程
1. **每天开工前**：搜GitHub参考同类项目，评估是否引入
2. **写代码前**：先出Plan，我确认后再动手
3. **分阶段交付**：每阶段做完停，不自行推进下一阶段
4. **双Agent**：一个写代码，一个检查代码
5. **阶段报告**：每阶段出学习报告

### 分阶段规划

#### Phase 1：MVP（第1-2周）
- Python环境 + Streamlit骨架
- PDF上传 + 文字提取（pdfplumber）
- DeepSeek API调用（复用Chrome插件Prompt）
- 基础结果展示

#### Phase 2：RAG（第3-4周）
- LangChain集成
- Chroma向量库
- 简历知识库构建
- RAG增强优化

#### Phase 3：工程化（第5-6周）
- Docker化
- GitHub Actions CI
- 部署到Streamlit Cloud
- 成本计算 + 使用数据展示

## 面试价值点
- RAG全流程理解
- Prompt Engineering
- Streamlit + Python后端
- 技术选型论证
- 踩坑记录

## 关联
- Chrome插件版：`F:\cc2\ai-resume-optimizer`
- 个人规划：`F:\cc2\我的大脑\职业规划\`
