"""
RAG 引擎 - 简历知识库检索增强
使用 LangChain + Chroma + sentence-transformers

知识库预置内容（面试重点）：
- STAR法则写经历模板
- 弱动词替换表（量化表达）
- 行业关键词库
- 简历结构模板
- 常见简历错误

面试话术：
「我预置了一个简历知识库，优化前先从知识库检索相关建议作为上下文，
再发给DeepSeek。这样AI不是凭空编，而是有行业最佳实践作为依据。」
"""

import os
from pathlib import Path
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 知识库持久化目录
CHROMA_PERSIST_DIR = str(Path(__file__).parent / "chroma_db")

# ============================================================
# 预置知识库数据
# ============================================================
KNOWLEDGE_BASE = [
    {
        "content": """STAR法则写经历的标准化模板

S (Situation - 背景): 在什么情况下？团队规模多大？业务目标是什么？
"所在电商平台日活50万，负责核心交易链路的前端开发，团队8人"

T (Task - 任务): 你具体负责什么？责任边界在哪？
"独立负责购物车模块重构，目标将页面加载时间缩短至1.5秒以内"

A (Action - 行动): 你做了什么？用了什么技术/方法？
"采用Vue3 + TypeScript重构，引入虚拟列表优化长列表渲染，
使用Web Worker处理复杂计算，关键接口加Redis缓存"

R (Result - 结果): 结果怎样？用数据说话！
"首屏加载从3.2s降至1.2s，用户跳出率下降18%，
双十一期间承载峰值10万QPS，零故障"

注意事项：
1. 每条经历都要有S+T+A+R，缺一不可
2. R必须有量化数据（百分比、时间、金额）
3. A要具体（用了什么技术，不要只说"优化"）""",
        "metadata": {"category": "模板", "tag": "STAR"}
    },
    {
        "content": """弱动词替换表（简历专用）

❌ 负责    → ✅ 主导 / 独立负责 / 全面负责
❌ 参与    → ✅ 核心参与 / 深度参与 / 主要贡献
❌ 协助    → ✅ 配合 / 支持 / 协同推进
❌ 进行    → ✅ 实施 / 执行 / 落地
❌ 做了    → ✅ 完成 / 实现 / 交付
❌ 了解    → ✅ 掌握 / 熟悉 / 精通
❌ 接触    → ✅ 实践 / 运用 / 操作
❌ 帮忙    → ✅ 协助解决 / 支持

核心原则：
1. 用具体动词替代模糊动词
2. 每个动词后接量化结果
3. 避免"负责xxx"开头，改为"通过xxx，实现xxx"

示例：
❌ "负责公司官网开发"
✅ "主导公司官网重构，使用React + TypeScript，
首屏加载时间从3s降至0.8s"

改写口诀：
"不要说你做了什么，要说你做到了什么"
"不要说你参与了，要说你贡献了什么" """,
        "metadata": {"category": "技巧", "tag": "弱动词"}
    },
    {
        "content": """量化表达示例库

没有数据时用这些方式体现成果：

【效率提升】
- "开发效率提升约40%"（前后对比）
- "手动流程改为自动化，耗时从2小时缩短至10分钟"
- "日处理量从100条提升至1000条"

【质量改进】
- "Bug率降低约60%"（引入代码审查后）
- "线上故障减少80%"（加监控告警后）
- "代码覆盖率从20%提升至85%"

【规模体现】
- "支撑日活用户50万+"
- "处理日均100万+请求"
- "管理总价值500万的项目预算"
- "服务团队人数100+"

【业务结果】
- "带来约30万/月的营收增长"
- "客户满意度从3.2提升至4.7（满分5）"
- "用户留存率提升12个百分点"

注意：
1. 即使无法精确量化，用估算值也比没有好
2. 加上对比更有效："从X到Y"
3. 单位用具体数字，不要用"大量""很多""显著" """,
        "metadata": {"category": "技巧", "tag": "量化"}
    },
    {
        "content": """AI/互联网行业核心技能关键词

【编程语言】
Python, Java, C++, C#, Go, Rust, TypeScript, JavaScript

【AI/机器学习】
大模型应用, Prompt Engineering, RAG, LangChain, Agent, Fine-tuning
TensorFlow, PyTorch, DeepSeek, OpenAI API, 向量数据库

【数据处理】
SQL, MySQL, PostgreSQL, MongoDB, Redis
ETL, 数据清洗, 数据分析, Pandas, Spark

【开发工具】
Git, Docker, K8s, CI/CD, Linux, RESTful API, GraphQL

【云平台】
阿里云, 腾讯云, AWS, Azure,  Serverless

【软技能突出点】
跨部门协作, 项目管理, 需求分析, 技术方案设计, 独立负责

【写简历技巧】
1. 把JD中的关键词自然地放在简历经历中
2. 不要堆砌，每条经历搭配2-3个关键词即可
3. 关键词要跟实际工作相关，不要为了凑而凑 """,
        "metadata": {"category": "词库", "tag": "AI行业关键词"}
    },
    {
        "content": """优秀简历结构模板

【基本信息】（顶部）
- 姓名 | 求职意向 | 联系方式（电话/邮箱）
- GitHub/个人博客/作品链接（加分）
- 简洁，不超过3行

【个人简介】（1-2句话）
- 核心定位 + 主要成就 + 目标方向
- 示例："3年后端开发经验，主导过日活50万的电商系统重构，
精通Python/Go，追求高可用高性能架构"

【工作/项目经历】（占简历70%）
- 按时间倒序排列
- 每条经历用STAR法则写（3-5条）
- 每条重点写2-4个关键点
- 必须量化！每个点都要有数据支撑

【专业技能】（列表式，简洁）
- 分类列出：语言/框架/工具/领域
- 不要自评等级（精通/熟练/了解等主观词）

【教育背景】（底部）
- 学校 | 专业 | 学位 | 时间
- 如果成绩好可以写GPA
- 如果相关课程有特色可以列课程

简历一页为佳，不超过两页
格式用PDF，不要用Word """,
        "metadata": {"category": "模板", "tag": "简历结构"}
    },
    {
        "content": """常见简历错误与修正

1. 经历写成岗位JD
❌ "负责公司产品的需求分析、开发和维护"
✅ "主导用户增长系统从0到1搭建，上线3个月带来2万新增用户"

2. 只有职责没有成果
❌ "负责数据库的日常维护"
✅ "优化慢查询100+条，数据库响应时间从2s降至200ms"

3. 没有关键词
❌ "做过后端开发，用的Java"
✅ "基于Spring Boot + MyBatis开发高并发交易系统，
日处理订单10万+"

4. 篇幅太满
❌ 写满两页纸，没有重点
✅ 一页纸，挑最重要的3-5个项目/经历

5. 排版混乱
❌ 字体大小不统一、格式不一致
✅ 统一字体、对齐、留白合理

6. 照片/个人信息过多
❌ 放照片、身高体重、籍贯等无关信息
✅ 只放必要信息：姓名、电话、邮箱、意向岗位

7. 自我评价假大空
❌ "性格开朗、工作认真、吃苦耐劳"
✅ 不写自我评价或换成1-2句核心定位 """,
        "metadata": {"category": "技巧", "tag": "常见错误"}
    },
]


class ResumeKnowledgeBase:
    """简历知识库 - 基于Chroma的向量检索"""

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", "。", " ", ""]
        )
        self.vector_store = self._load_or_create()

    def _load_or_create(self):
        """加载已有向量库，不存在则创建"""
        try:
            if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
                return Chroma(
                    persist_directory=CHROMA_PERSIST_DIR,
                    embedding_function=self.embeddings
                )
        except Exception:
            pass
        return self._build_knowledge_base()

    def _build_knowledge_base(self):
        """用预置知识库数据构建向量库"""
        docs = []
        for item in KNOWLEDGE_BASE:
            doc = Document(
                page_content=item["content"],
                metadata=item["metadata"]
            )
            docs.append(doc)

        # 长文本切片
        split_docs = self.text_splitter.split_documents(docs)

        vector_store = Chroma.from_documents(
            split_docs,
            self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )
        return vector_store

    def search(self, query: str, k: int = 3) -> List[Document]:
        """
        MMR检索，保证结果多样性
        MMR = 既相关又不重复
        """
        try:
            results = self.vector_store.max_marginal_relevance_search(
                query, k=k, fetch_k=15
            )
            return results
        except Exception as e:
            return []

    def get_context(self, query: str, k: int = 3) -> str:
        """检索相关知识并拼接成上下文文本"""
        docs = self.search(query, k)
        if not docs:
            return ""
        return "\n\n---\n".join(
            [f"[{doc.metadata.get('tag', '知识')}]\n{doc.page_content}" for doc in docs]
        )

    @property
    def count(self) -> int:
        """知识库中的文档块总数"""
        try:
            return len(self.vector_store.get()["ids"])
        except Exception:
            return 0

    def add_document(self, content: str, metadata: Optional[dict] = None):
        """向知识库添加新文档"""
        if metadata is None:
            metadata = {"category": "用户上传", "tag": "自定义"}
        doc = Document(page_content=content, metadata=metadata)
        self.vector_store.add_documents([doc])

    def rebuild(self):
        """重建知识库（用于调试）"""
        import shutil
        if os.path.exists(CHROMA_PERSIST_DIR):
            shutil.rmtree(CHROMA_PERSIST_DIR)
        self.vector_store = self._build_knowledge_base()
