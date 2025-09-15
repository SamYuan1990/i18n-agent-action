# i18n MCP Server User Guide

## Image Information
- **Image Name**: `ghcr.io/samyuan1990/i18n-agent-action:mcp`
- **Base Image**: Python 3.12
- **Working Directory**: `/app`

## Description
This is a Model Context Protocol (MCP) server designed for internationalization (i18n) tasks, providing translation-related functionality with support for custom ONNX models.

## Quick Start

### Pull the Image
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### Run the Container
```bash
docker run -p 8080:8080 -e api_key="YOUR_API_KEY" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### Environment Variables Configuration
- `api_key`: (Required) Translation service API key
- `encoder`: (Optional) Path to the encoder ONNX model file (default: `/tmp/base-encoder.onnx`)
- `decoder`: (Optional) Path to the decoder ONNX model file (default: `/tmp/base-decoder.onnx`)
- `tokens`: (Optional) Path to the tokens ONNX model file (default: `/tmp/base-tokens.onnx`)

Example with custom models:
```bash
docker run -p 8080:8080 \
  -e api_key="your-translation-api-key" \
  -e encoder="/app/models/custom-encoder.onnx" \
  -e decoder="/app/models/custom-decoder.onnx" \
  -e tokens="/app/models/custom-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## Mounting Custom ONNX Models
You can mount your own ONNX model files into the container using Docker volumes:

```bash
docker run -p 8080:8080 \
  -e api_key="your-api-key" \
  -v /path/to/your/models:/app/models \
  -e encoder="/app/models/your-encoder.onnx" \
  -e decoder="/app/models/your-decoder.onnx" \
  -e tokens="/app/models/your-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## Port Configuration
- Default exposed port: **8080**
- You can adjust the host port mapping:
  ```bash
  docker run -p 3000:8080 [...] # Maps host port 3000 to container port 8080
  ```

## Project Structure
- Uses Poetry for dependency management
- Source code located in `/app` directory inside the container
- Automatically installs all extra dependencies (including development dependencies)

## Custom Configuration
For additional customization:

1. **Mount configuration files**:
   ```bash
   docker run -v /path/to/your/config.yaml:/app/config.yaml [...]
   ```

2. **Use environment variables**:
   ```bash
   docker run -e api_key="your-key" -e OTHER_VAR="value" [...]
   ```

## Development Usage
If you need to modify code or develop:

```bash
# Clone source code
git clone <your-repo>
cd <repo-directory>

# Use Docker Compose (recommended)
# Or use docker run with local code mounted
docker run -p 8080:8080 -v $(pwd):/app -e api_key="your-key" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## Health Check
After the server starts, you can verify its status by accessing:
```bash
curl http://localhost:8080/health
```

## Notes
1. Ensure you provide a valid `api_key` environment variable
2. The container automatically removes the default config.yaml file on startup
3. For persistent configuration, mount external configuration files
4. For custom models, mount your ONNX files and set the appropriate environment variables

## Support and Feedback
If you encounter issues or need support, please submit an Issue through the project repository or contact the maintainer.