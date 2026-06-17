"""
PDF简历解析模块
使用 pdfplumber 提取PDF中的文字内容
中文支持好，不乱码
"""

import pdfplumber
from typing import Optional, IO


def extract_text_from_pdf(uploaded_file: IO) -> Optional[str]:
    """
    从上传的PDF文件中提取文字

    Args:
        uploaded_file: Streamlit上传的文件对象（类文件对象）

    Returns:
        提取的文字内容，如果为空则返回 None

    Raises:
        Exception: PDF解析失败时抛出
    """
    try:
        text_parts = []

        with pdfplumber.open(uploaded_file) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(page_text.strip())

        if not text_parts:
            return None

        full_text = "\n".join(text_parts)
        return full_text

    except Exception as e:
        raise Exception(f"PDF解析失败: {str(e)}")
