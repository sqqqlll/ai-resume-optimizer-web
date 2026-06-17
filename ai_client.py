"""
DeepSeek API 调用模块
复用Chrome插件中已有的Prompt模板
"""

import os
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 确保加载同目录下的 .env 文件，不依赖 CWD
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# DeepSeek 兼容 OpenAI 接口
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


# 成本统计（累计，用函数访问避免Streamlit缓存问题）
DEEPSEEK_PRICE_INPUT = 0.5   # ¥/百万token（输入）
DEEPSEEK_PRICE_OUTPUT = 2.0  # ¥/百万token（输出）
_TOTAL_STATS = {"calls": 0, "total_cost": 0.0, "total_prompt_tokens": 0, "total_completion_tokens": 0}


def get_stats():
    """获取使用统计（供app.py调用）"""
    return dict(_TOTAL_STATS)


def call_deepseek(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 4096
) -> str:
    """
    调用 DeepSeek API，返回生成文本
    每次调用会自动累计 token 和成本到 _TOTAL_STATS
    """
    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            result = response.choices[0].message.content
            if not result:
                raise Exception("AI返回内容为空")

            # 检查是否因token限制被截断（配置问题，不重试）
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "length":
                return ""  # 返回空，外层会处理

            # ---- 累计成本 ----
            usage = response.usage
            if usage:
                prompt_tk = usage.prompt_tokens or 0
                completion_tk = usage.completion_tokens or 0
                cost = (prompt_tk / 1_000_000) * DEEPSEEK_PRICE_INPUT + \
                       (completion_tk / 1_000_000) * DEEPSEEK_PRICE_OUTPUT
                _TOTAL_STATS["calls"] += 1
                _TOTAL_STATS["total_cost"] += cost
                _TOTAL_STATS["total_prompt_tokens"] += prompt_tk
                _TOTAL_STATS["total_completion_tokens"] += completion_tk

            return result

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # 指数退避：1s, 2s
                continue
            raise Exception(f"AI调用失败（重试{MAX_RETRIES}次后）: {str(e)}")


# ---- Prompt 模板（从Chrome插件 popup.js 移植） ----

# 优化强度说明
LEVEL_DESCRIPTIONS = {
    "light": "精准匹配——只替换JD关键词到简历中，不动句子结构，不增删内容",
    "medium": "润色优化——在精准匹配基础上，优化动词表达、补充量化数据，保持原结构",
    "heavy": "STAR改写——用STAR法则重写每条经历，调整结构，保留核心事实",
    "extreme": "深度重塑——全部重写，大幅调整结构和表达方式"
}

# 优化简历的System Prompt模板
OPTIMIZE_SYSTEM_TEMPLATE = """你是顶级简历顾问。用户选择了修改强度：「{level_desc}」。请严格按照这个强度操作。

输出格式（必须严格遵循）：

### 📊 JD关键词分析
✅ 命中 | ❌ 缺失 | 用表格列出

### 📈 匹配度评分：X/100
（一句话说明评分依据）

### 📝 改动清单
逐条列出具体改动，格式："原文片段" → "优化后片段"，并简要说明理由

### ✨ 优化后简历
（干净完整的简历，无任何标记符号，可直接发给面试官使用）"""

# 面试预测System Prompt
PREDICT_SYSTEM_PROMPT = """你是面试官。基于JD和用户简历，输出：

### 🎯 大概率被问的5个技术问题
（结合JD要求的硬技能，每个问题附考察意图）

### 🧠 大概率被问的3个行为问题
（STAR追问、项目深挖、冲突处理类）

### 💬 参考答案要点
（每个问题给2-3句回答框架，不要全文，给要点）"""

# 求职信System Prompt
COVER_SYSTEM_PROMPT = """写一封300字求职信/自我介绍。三段式：
1) 我对这个岗位的理解和热情
2) 我匹配的经历
3) 结语
语气专业但不假大空。"""

# HR视角System Prompt
HR_SYSTEM_PROMPT = """你是HR。6秒扫简历，输出：
1) 第一眼看到了什么
2) 第一印象（好/中性/差）
3) 哪里让你想继续看
4) 哪里让你想关掉
直接、毒舌、有用。"""

# 薪资谈判System Prompt
SALARY_SYSTEM_PROMPT = """基于JD中的薪资范围（如果有）和用户经验，给出：
1) 建议期望薪资区间
2) 谈判话术
3) 何时开口谈薪
如果JD没写薪资，给出行业参考。"""


def optimize_resume(jd_text: str, resume_text: str, level: str = "medium") -> str:
    """优化简历（无RAG版本）"""
    level_desc = LEVEL_DESCRIPTIONS.get(level, LEVEL_DESCRIPTIONS["medium"])
    system_prompt = OPTIMIZE_SYSTEM_TEMPLATE.format(level_desc=level_desc)
    user_prompt = f"""## 修改强度
{level_desc}

## 职位描述
{jd_text}

## 我的简历
{resume_text}

请按照选定的修改强度优化简历。"""
    return call_deepseek(system_prompt, user_prompt)


def optimize_resume_with_rag(
    jd_text: str,
    resume_text: str,
    rag_context: str,
    level: str = "medium"
) -> str:
    """
    优化简历（RAG增强版本）
    - 先从知识库检索相关知识
    - 把知识作为上下文注入Prompt
    - 让AI基于真实知识库建议优化，不是凭空编
    """
    level_desc = LEVEL_DESCRIPTIONS.get(level, LEVEL_DESCRIPTIONS["medium"])

    system_prompt = f"""你是顶级简历顾问。用户选择了修改强度：「{level_desc}」。请严格按照这个强度操作。

以下是从简历知识库中检索到的相关建议，请参考这些建议来优化：

{rag_context}

输出格式（必须严格遵循）：

### 📊 JD关键词分析
✅ 命中 | ❌ 缺失 | 用表格列出

### 📈 匹配度评分：X/100
（一句话说明评分依据）

### 📝 改动清单
逐条列出具体改动，格式："原文片段" → "优化后片段"，并简要说明理由

### ✨ 优化后简历
（干净完整的简历，无任何标记符号，可直接发给面试官使用）"""

    user_prompt = f"""## 修改强度
{level_desc}

## 职位描述
{jd_text}

## 我的简历
{resume_text}

请按照选定的修改强度优化简历。"""
    return call_deepseek(system_prompt, user_prompt)


def predict_interview(jd_text: str, resume_text: str) -> str:
    """面试预测"""
    user_prompt = f"""## 职位描述
{jd_text}

## 我的简历
{resume_text}

请预测面试题。"""
    return call_deepseek(PREDICT_SYSTEM_PROMPT, user_prompt)


def generate_cover_letter(jd_text: str, resume_text: str) -> str:
    """生成求职信"""
    user_prompt = f"""JD:
{jd_text}

简历:
{resume_text}"""
    return call_deepseek(COVER_SYSTEM_PROMPT, user_prompt)


def hr_review(jd_text: str, resume_text: str) -> str:
    """HR视角模拟"""
    user_prompt = f"""JD:
{jd_text}

简历:
{resume_text}"""
    return call_deepseek(HR_SYSTEM_PROMPT, user_prompt)


def salary_advice(jd_text: str, resume_text: str) -> str:
    """薪资建议"""
    user_prompt = f"""JD:
{jd_text}

简历:
{resume_text}"""
    return call_deepseek(SALARY_SYSTEM_PROMPT, user_prompt)
