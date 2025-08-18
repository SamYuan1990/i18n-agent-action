# 第一阶段：构建环境
FROM python:3.13 as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 第二阶段：生产环境
FROM python:3.13.7-slim
WORKDIR /app

# 从builder阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
COPY . .

# 确保脚本可访问
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

ENV api_key=""
ENV CONFIG_FILE=""
ENV DOCS_FOLDER=""
ENV RESERVED_WORD=""
ENV FILE_LIST=""
# 启动命令（支持环境变量和参数覆盖）
CMD bash -c 'python3 main.py "${CONFIG_FILE}" "${DOCS_FOLDER}" "${RESERVED_WORD}" ${FILE_LIST:+$FILE_LIST}'