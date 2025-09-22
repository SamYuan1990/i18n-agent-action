#!/bin/bash

# 根据 SERVICE_TYPE 环境变量决定启动哪个服务
echo "SERVICE_TYPE: ${SERVICE_TYPE:-main}"

case "${SERVICE_TYPE}" in
    "mcp")
        echo "启动 MCP 服务器..."
        exec python3 ./mcp/mcp_server.py
        ;;
    "flet")
        echo "启动 Flet 应用..."
        exec poetry run flet run -wd ./App
        ;;
    "main"|"")
        echo "启动主应用..."
        exec python3 main.py "${CONFIG_FILE}" "${DOCS_FOLDER}" "${RESERVED_WORD}" ${FILE_LIST:+$FILE_LIST}
        ;;
    *)
        echo "错误: 未知的 SERVICE_TYPE: $SERVICE_TYPE"
        echo "可用选项: mcp, flet, main, all"
        exit 1
        ;;
esac