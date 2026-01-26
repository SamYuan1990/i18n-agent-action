FROM python:3.14
WORKDIR /app

# 定义构建参数，默认值为 main
ARG SERVICE_TYPE=main

# 安装 poetry
RUN pip install poetry

# 先复制依赖配置文件
COPY pyproject.toml poetry.lock* ./

# 配置 poetry 并安装依赖
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# 复制项目文件
COPY . .

# 复制启动脚本并赋予执行权限
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 确保脚本可访问
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# 设置环境变量（可以从构建参数继承，也可以在运行时覆盖）
ENV SERVICE_TYPE=${SERVICE_TYPE}
ENV api_key=""
ENV CONFIG_FILE=""
ENV DOCS_FOLDER=""
ENV RESERVED_WORD=""
ENV FILE_LIST=""

# 使用启动脚本作为入口点
CMD ["/app/start.sh"]