# Guía de Uso del Contenedor de Aplicación de Acción del Agente i18n

## Resumen
Esta es una aplicación de contenedor de agente de internacionalización (i18n) construida sobre el framework Flet, que proporciona una interfaz web para gestionar y procesar tareas relacionadas con i18n.

## Inicio Rápido

### 1. Extraer la Imagen
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:app
```

### 2. Ejecutar el Contenedor
```bash
docker run -d -p 8550:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### 3. Acceder a la Aplicación
Abra su navegador y vaya a: http://localhost:8550

## Opciones de Configuración

### Mapeo de Puertos
El puerto predeterminado es 8550. Puede mapearlo a cualquier puerto del host:
```bash
docker run -d -p 8080:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### Variables de Entorno
Puede configurar las siguientes variables de entorno:

- `FLET_SECRET_KEY`: Clave secreta de la aplicación (predeterminada: 123)
- `FLET_SERVER_PORT`: Puerto del servidor (predeterminado: 8550)

Ejemplo:
```bash
docker run -d \
  -p 8550:8550 \
  -e FLET_SECRET_KEY=your-secret-key \
  -e FLET_SERVER_PORT=8550 \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

### Persistencia de Datos
Para la persistencia de datos, puede montar un volumen:
```bash
docker run -d \
  -p 8550:8550 \
  -v ./i18n-data:/app/data \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

## Modo de Desarrollo

### Construir Imagen Personalizada
Si modifica el código, puede reconstruir la imagen:
```bash
docker build -f Dockerfile_App -t my-i18n-app .
```

### Ejecutar Versión de Desarrollo
```bash
docker run -d -p 8550:8550 --name my-i18n-app my-i18n-app
```

## Comandos Comunes

### Ver Registros del Contenedor
```bash
docker logs i18n-app
```

### Acceder a la Shell del Contenedor
```bash
docker exec -it i18n-app /bin/bash
```

### Detener el Contenedor
```bash
docker stop i18n-app
```

### Reiniciar el Contenedor
```bash
docker restart i18n-app
```

### Eliminar el Contenedor
```bash
docker rm i18n-app
```

## Resolución de Problemas

1. **Conflicto de Puerto**: Si el puerto 8550 ya está en uso, utilice un puerto diferente
2. **Fallo de Inicio del Contenedor**: Verifique los registros con `docker logs i18n-app`
3. **No Se Puede Acceder a la Aplicación**: Verifique la configuración del firewall y el mapeo de puertos

## Soporte
Para problemas, consulte la documentación del proyecto o envíe un problema al repositorio de GitHub.

---

**Nota**: Este contenedor está destinado únicamente para entornos de desarrollo y pruebas. Para uso en producción, asegúrese de configurar las medidas de seguridad apropiadas.