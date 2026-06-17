"""
AI简历优化器 - Web版
Streamlit + DeepSeek API + PDF解析
Phase 1 MVP：上传PDF→粘贴JD→AI优化→出结果
"""

import streamlit as st
import importlib
import ai_client
importlib.reload(ai_client)  # 强制重新加载，避免Streamlit缓存旧版本
from pdf_parser import extract_text_from_pdf
from rag_engine import ResumeKnowledgeBase

# ---- 页面配置 ----
st.set_page_config(
    page_title="AI简历优化器",
    page_icon="📄",
    layout="wide",
)

# ---- 自定义CSS ----
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        font-size: 2.2rem;
        margin-bottom: 0.3rem;
    }
    .main-header p {
        color: #666;
        font-size: 1rem;
    }
    .result-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 1px solid #e0e0e0;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
</style>
""", unsafe_allow_html=True)


# ---- 初始化会话状态 ----
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "result" not in st.session_state:
    st.session_state.result = ""
if "current_action" not in st.session_state:
    st.session_state.current_action = ""
if "resume_editor" not in st.session_state:
    st.session_state.resume_editor = ""
if "rag_enabled" not in st.session_state:
    st.session_state.rag_enabled = True
if "stats" not in st.session_state:
    st.session_state.stats = {"calls": 0, "total_cost": 0.0}
if "kb" not in st.session_state:
    with st.spinner("正在加载简历知识库..."):
        try:
            st.session_state.kb = ResumeKnowledgeBase()
        except Exception:
            st.session_state.kb = None
            st.session_state.rag_enabled = False


# ---- 页面标题 ----
st.markdown("""
<div class="main-header">
    <h1>📄 AI简历优化器</h1>
    <p>上传你的PDF简历，粘贴目标JD，AI帮你优化匹配</p>
</div>
""", unsafe_allow_html=True)


# ---- 侧边栏：PDF上传 ----
with st.sidebar:
    st.markdown("### 📤 上传简历")
    uploaded_file = st.file_uploader(
        "上传PDF格式的简历文件",
        type=["pdf"],
        help="支持PDF格式，中文简历兼容"
    )

    if uploaded_file is not None:
        with st.spinner("正在解析PDF..."):
            try:
                text = extract_text_from_pdf(uploaded_file)
                if text:
                    st.session_state.resume_text = text
                    st.session_state.resume_editor = text
                    st.success(f"✅ 解析成功！共 {len(text)} 字")
                else:
                    st.warning("⚠️ PDF内容为空，请手动粘贴简历")
            except Exception as e:
                st.error(f"❌ 解析失败：{str(e)}")
                st.info("💡 可以手动粘贴简历内容到文本框中")

    st.markdown("---")
    st.markdown("### 使用说明")
    st.markdown("""
    1. 上传你的PDF简历（左侧）
    2. 粘贴目标职位描述（主区域）
    3. 选择优化强度
    4. 点击"一键优化"
    """)

    # ---- RAG 状态展示 ----
    st.markdown("---")
    st.markdown("### 🧠 RAG 知识库")
    kb = st.session_state.get("kb")
    if kb:
        kb_count = kb.count
        st.success(f"✅ 知识库已加载（{kb_count}个条目）")
        st.caption("含STAR模板、量化词库、行业关键词等")
        st.session_state.rag_enabled = st.toggle(
            "优化时启用RAG检索",
            value=st.session_state.rag_enabled,
            help="关闭后直接调AI，不检索知识库"
        )
    else:
        st.warning("⚠️ 知识库加载失败")
        st.caption("可关闭RAG继续使用基础优化功能")

    # ---- 成本/使用统计 ----
    st.markdown("---")
    st.markdown("### 📊 使用统计")
    stats = st.session_state.stats
    st.metric("调用次数", stats["calls"])
    st.metric("总消耗", f"¥{stats['total_cost']:.4f}")

    st.markdown("---")
    st.caption("Phase 2 · RAG增强版")


# ---- 主区域 ----
col1, col2 = st.columns([3, 2])

with col1:
    # JD输入
    st.markdown("### 📋 职位描述")
    jd_text = st.text_area(
        "粘贴目标职位描述（JD）",
        placeholder="从Boss直聘/猎聘/拉勾等复制JD粘贴到这里…",
        height=200,
        label_visibility="collapsed",
        key="jd_editor",
    )

    # 简历文本展示
    st.markdown("### ✏️ 简历内容")
    resume_text = st.text_area(
        "简历内容（自动从PDF提取，也可手动编辑）",
        value=st.session_state.resume_text,
        height=250,
        placeholder="上传PDF后会自动填入，你也可以直接粘贴修改…",
        label_visibility="collapsed",
        key="resume_editor",
    )

with col2:
    # 优化强度选择
    st.markdown("### 🎯 优化强度")
    level = st.radio(
        "选择优化强度",
        options=["light", "medium", "heavy", "extreme"],
        format_func=lambda x: {
            "light": "⚡ 精准匹配",
            "medium": "✨ 润色优化",
            "heavy": "📐 STAR改写",
            "extreme": "🔥 深度重塑"
        }[x],
        index=1,  # 默认 medium
        label_visibility="collapsed",
    )

    st.markdown("---")

    # 功能按钮
    st.markdown("### 🚀 执行操作")
    optimize_btn = st.button("🔮 一键优化简历", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🛠️ 更多工具")

    col_btns = st.columns(2)
    with col_btns[0]:
        predict_btn = st.button("🎯 面试预测", use_container_width=True)
        cover_btn = st.button("📝 求职信", use_container_width=True)
    with col_btns[1]:
        hr_btn = st.button("👀 HR视角", use_container_width=True)
        salary_btn = st.button("💰 薪资建议", use_container_width=True)


# ---- 结果展示区域 ----
result_placeholder = st.empty()


def run_action(action_name: str, action_func, jd_input: str, resume_input: str, level: str = "medium", use_rag: bool = False):
    """执行AI操作并显示结果"""
    # 校验输入
    if not jd_input or len(jd_input.strip()) < 20:
        st.warning("⚠️ 请先粘贴职位描述（至少20字）")
        return
    if not resume_input or len(resume_input.strip()) < 30:
        st.warning("⚠️ 请先上传简历或粘贴简历内容（至少30字）")
        return

    st.session_state.current_action = action_name
    jd_clean = jd_input.strip()
    resume_clean = resume_input.strip()

    # RAG检索（只在优化操作且启用时）
    rag_context = ""
    if use_rag and st.session_state.get("rag_enabled") and st.session_state.get("kb"):
        kb = st.session_state.kb
        with st.status("🔍 正在检索知识库...", expanded=False) as status:
            query = f"{jd_clean[:500]} {resume_clean[:500]}"
            rag_context = kb.get_context(query, k=3)
            st.session_state.rag_context = rag_context
            if rag_context:
                status.update(label="✅ 检索到相关知识", state="complete")
            else:
                status.update(label="⚠️ 未检索到相关知识", state="complete")

    with st.spinner(f"🔄 AI正在{action_name}中..."):
        try:
            if use_rag and rag_context:
                result = action_func(jd_clean, resume_clean, rag_context, level)
            elif action_name == "优化":
                result = action_func(jd_clean, resume_clean, level)
            else:
                result = action_func(jd_clean, resume_clean)

                        # 累计调用统计
            st.session_state.stats["calls"] += 1
            st.session_state.stats["total_cost"] += 0.01

            st.session_state.result = result
            with result_placeholder.container():
                st.markdown("---")
                st.markdown(f"### 📊 {action_name}结果")
                if rag_context:
                    with st.expander("📚 本次检索到的知识库内容（RAG）"):
                        st.markdown(rag_context)
                if result:
                    st.markdown(result)
                    st.success("✅ 生成完成！")
                else:
                    st.warning("⚠️ 输出为空，可能是Token限制，请重试或增大优化强度")
                # 显示成本统计
                s = st.session_state.stats
                if s["calls"] > 0:
                    st.caption(
                        f"⚡ 累计 {s['calls']} 次调用 · "
                        f"总消耗 ¥{s['total_cost']:.4f}"
                    )
        except Exception as e:
            st.error(f"❌ 出错：{str(e)}")
            st.info("💡 建议检查网络连接或稍后重试")
            st.session_state.result = ""


# ---- 按钮事件绑定 ----
if optimize_btn:
    if st.session_state.get("rag_enabled", False):
        run_action(
            "优化", ai_client.optimize_resume_with_rag,
            jd_text, resume_text, level,
            use_rag=True
        )
    else:
        run_action(
            "优化", ai_client.optimize_resume,
            jd_text, resume_text, level
        )

if predict_btn:
    run_action("面试预测", ai_client.predict_interview, jd_text, resume_text)

if cover_btn:
    run_action("求职信", ai_client.generate_cover_letter, jd_text, resume_text)

if hr_btn:
    run_action("HR视角", ai_client.hr_review, jd_text, resume_text)

if salary_btn:
    run_action("薪资建议", ai_client.salary_advice, jd_text, resume_text)


# ---- 显示上一次的结果（如果有且没有新操作） ----
if st.session_state.result and not any([
    optimize_btn, predict_btn, cover_btn, hr_btn, salary_btn
]):
    with result_placeholder.container():
        st.markdown("---")
        st.markdown(f"### 📊 {st.session_state.current_action}结果")
        st.markdown(st.session_state.result)
