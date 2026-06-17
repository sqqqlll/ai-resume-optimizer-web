# AI简历优化器 - Docker镜像
# 基于 slim 镜像 + PyTorch CPU 版

FROM python:3.12-slim

WORKDIR /app

# 先装 PyTorch（CPU版，体积可控）
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir sentence-transformers

# 再装其他依赖（利用 Docker layer 缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 最后拷源码
COPY . .

# 暴露 Streamlit 端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

# 启动
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
