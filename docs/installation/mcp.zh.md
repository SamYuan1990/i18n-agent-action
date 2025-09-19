# i18n MCP 服务器用户指南

## 镜像信息
- **镜像名称**: `ghcr.io/samyuan1990/i18n-agent-action:mcp`
- **基础镜像**: Python 3.12
- **工作目录**: `/app`

## 描述
这是一个模型上下文协议 (MCP) 服务器，专为国际化 (i18n) 任务设计，提供翻译相关功能，并支持自定义 ONNX 模型。

## 快速开始

### 拉取镜像
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### 运行容器
```bash
docker run -p 8080:8080 -e api_key="YOUR_API_KEY" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### 环境变量配置
- `api_key`: (必需) 翻译服务 API 密钥
- `encoder`: (可选) 编码器 ONNX 模型文件路径 (默认: `/tmp/base-encoder.onnx`)
- `decoder`: (可选) 解码器 ONNX 模型文件路径 (默认: `/tmp/base-decoder.onnx`)
- `tokens`: (可选) 令牌 ONNX 模型文件路径 (默认: `/tmp/base-tokens.onnx`)

使用自定义模型示例:
```bash
docker run -p 8080:8080 \
  -e api_key="your-translation-api-key" \
  -e encoder="/app/models/custom-encoder.onnx" \
  -e decoder="/app/models/custom-decoder.onnx" \
  -e tokens="/app/models/custom-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## 挂载自定义 ONNX 模型
您可以使用 Docker 卷将您自己的 ONNX 模型文件挂载到容器中:

```bash
docker run -p 8080:8080 \
  -e api_key="your-api-key" \
  -v /path/to/your/models:/app/models \
  -e encoder="/app/models/your-encoder.onnx" \
  -e decoder="/app/models/your-decoder.onnx" \
  -e tokens="/app/models/your-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

```
{
    "method": "docker run",
    "args": [
        "-p", "8080:8080",
        "-e", "api_key=your-api-key",
        "-v", "/path/to/your/models:/app/models",
        "-e", "encoder=/app/models/your-encoder.onnx",
        "-e", "decoder=/app/models/your-decoder.onnx",
        "-e", "tokens=/app/models/your-tokens.onnx",
        "ghcr.io/samyuan1990/i18n-agent-action:mcp"
    ]
}
```

## 端口配置
- 默认暴露端口: **8080**
- 您可以调整主机端口映射:
  ```bash
  docker run -p 3000:8080 [...] # 将主机端口 3000 映射到容器端口 8080
  ```

## 项目结构
- 使用 Poetry 进行依赖管理
- 源代码位于容器内的 `/app` 目录
- 自动安装所有额外依赖（包括开发依赖）

## 自定义配置
如需额外自定义:

1. **挂载配置文件**:
   ```bash
   docker run -v /path/to/your/config.yaml:/app/config.yaml [...]
   ```

2. **使用环境变量**:
   ```bash
   docker run -e api_key="your-key" -e OTHER_VAR="value" [...]
   ```

## 开发使用
如果您需要修改代码或进行开发:

```bash
# 克隆源代码
git clone <your-repo>
cd <repo-directory>

# 使用 Docker Compose (推荐)
# 或使用 docker run 挂载本地代码
docker run -p 8080:8080 -v $(pwd):/app -e api_key="your-key" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## 健康检查
服务器启动后，您可以通过访问以下地址验证其状态:
```bash
curl http://localhost:8080/health
```

## 注意事项
1. 确保提供有效的 `api_key` 环境变量
2. 容器在启动时自动移除默认的 config.yaml 文件
3. 对于持久化配置，请挂载
外部配置文件
4. 对于自定义模型，挂载您的 ONNX 文件并设置适当的环境变量

## 支持与反馈
如果您遇到问题或需要支持，请通过项目仓库提交 Issue 或联系维护者。