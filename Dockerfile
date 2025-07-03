# 使用华为云镜像源的Python 3.12-slim镜像
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-slim

# 设置工作目录
WORKDIR /app

# 使用阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 首先复制requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 单独安装spacy（使用特殊参数避免安装问题）
RUN pip install --no-cache-dir spacy --pre --no-build-isolation

# 复制其余项目文件
COPY . .

# 安装spaCy的语言模型
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download zh_core_web_sm

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口（用于Streamlit应用）
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "app.py"] 