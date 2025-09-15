# i18n 代理操作应用容器使用指南

## 概述
这是一个基于 Flet 框架构建的国际化（i18n）代理应用容器，提供了一个用于管理和处理 i18n 相关任务的 Web 界面。

## 快速开始

### 1. 拉取镜像
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:app
```

### 2. 运行容器
```bash
docker run -d -p 8550:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### 3. 访问应用
打开浏览器并导航到：http://localhost:8550

## 配置选项

### 端口映射
默认端口为 8550。您可以将其映射到任何主机端口：
```bash
docker run -d -p 8080:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### 环境变量
您可以配置以下环境变量：

- `FLET_SECRET_KEY`：应用密钥（默认：123）
- `FLET_SERVER_PORT`：服务器端口（默认：8550）

示例：
```bash
docker run -d \
  -p 8550:8550 \
  -e FLET_SECRET_KEY=your-secret-key \
  -e FLET_SERVER_PORT=8550 \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

### 数据持久化
对于数据持久化，您可以挂载一个卷：
```bash
docker run -d \
  -p 8550:8550 \
  -v ./i18n-data:/app/data \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

## 开发模式

### 构建自定义镜像
如果您修改了代码，可以重新构建镜像：
```bash
docker build -f Dockerfile_App -t my-i18n-app .
```

### 运行开发版本
```bash
docker run -d -p 8550:8550 --name my-i18n-app my-i18n-app
```

## 常用命令

### 查看容器日志
```bash
docker logs i18n-app
```

### 访问容器 shell
```bash
docker exec -it i18n-app /bin/bash
```

### 停止容器
```bash
docker stop i18n-app
```

### 重启容器
```bash
docker restart i18n-app
```

### 移除容器
```bash
docker rm i18n-app
```

## 故障排除

1. **端口冲突**：如果端口 8550 已被使用，请使用其他端口
2. **容器启动失败**：使用 `docker logs i18n-app` 检查日志
3. **无法访问应用**：验证防火墙设置和端口映射

## 支持

如有问题，请查阅项目文档或向 GitHub 仓库提交问题。

---

**注意**：此容器仅适用于开发和测试环境。在生产环境中使用时，请确保配置适当的安全措施。