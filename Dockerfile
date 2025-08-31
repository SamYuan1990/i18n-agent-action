FROM python:3.12
WORKDIR /app

# 从builder阶段复制已安装的包
COPY . .
RUN pip install --no-cache-dir .

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