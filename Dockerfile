# 使用华为云镜像源的Python 3.12-slim镜像
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-slim

# 设置工作目录
WORKDIR /app

# 配置apt镜像源
RUN echo "deb https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bookworm-updates main non-free non-free-firmware contrib" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bookworm-backports main non-free non-free-firmware contrib" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security bookworm-security main non-free non-free-firmware contrib" >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 配置pip镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

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