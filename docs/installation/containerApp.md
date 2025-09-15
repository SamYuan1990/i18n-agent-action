# i18n Agent Action App Container Usage Guide

## Overview
This is an internationalization (i18n) agent application container built on the Flet framework, providing a web interface for managing and processing i18n-related tasks.

## Quick Start

### 1. Pull the Image
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:app
```

### 2. Run the Container
```bash
docker run -d -p 8550:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### 3. Access the Application
Open your browser and navigate to: http://localhost:8550

## Configuration Options

### Port Mapping
Default port is 8550. You can map it to any host port:
```bash
docker run -d -p 8080:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### Environment Variables
You can configure the following environment variables:

- `FLET_SECRET_KEY`: Application secret key (default: 123)
- `FLET_SERVER_PORT`: Server port (default: 8550)

Example:
```bash
docker run -d \
  -p 8550:8550 \
  -e FLET_SECRET_KEY=your-secret-key \
  -e FLET_SERVER_PORT=8550 \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

### Data Persistence
For data persistence, you can mount a volume:
```bash
docker run -d \
  -p 8550:8550 \
  -v ./i18n-data:/app/data \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

## Development Mode

### Build Custom Image
If you modify the code, you can rebuild the image:
```bash
docker build -f Dockerfile_App -t my-i18n-app .
```

### Run Development Version
```bash
docker run -d -p 8550:8550 --name my-i18n-app my-i18n-app
```

## Common Commands

### View Container Logs
```bash
docker logs i18n-app
```

### Access Container Shell
```bash
docker exec -it i18n-app /bin/bash
```

### Stop Container
```bash
docker stop i18n-app
```

### Restart Container
```bash
docker restart i18n-app
```

### Remove Container
```bash
docker rm i18n-app
```

## Troubleshooting

1. **Port Conflict**: If port 8550 is already in use, use a different port
2. **Container Startup Failure**: Check logs with `docker logs i18n-app`
3. **Cannot Access Application**: Verify firewall settings and port mapping

## Support

For issues, please check the project documentation or submit an issue to the GitHub repository.

---

**Note**: This container is intended for development and testing environments only. For production use, ensure appropriate security measures are configured.