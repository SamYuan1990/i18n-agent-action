# Guía del Usuario del Servidor MCP de i18n

## Información de la Imagen
- **Nombre de la Imagen**: `ghcr.io/samyuan1990/i18n-agent-action:mcp`
- **Imagen Base**: Python 3.12
- **Directorio de Trabajo**: `/app`

## Descripción
Este es un servidor del Protocolo de Contexto de Modelo (MCP) diseñado para tareas de internacionalización (i18n), que proporciona funcionalidad relacionada con la traducción con soporte para modelos ONNX personalizados.

## Inicio Rápido

### Extraer la Imagen
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### Ejecutar el Contenedor
```bash
docker run -p 8080:8080 -e api_key="TU_CLAVE_API" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### Configuración de Variables de Entorno
- `api_key`: (Obligatorio) Clave API del servicio de traducción
- `encoder`: (Opcional) Ruta al archivo del modelo ONNX del codificador (predeterminado: `/tmp/base-encoder.onnx`)
- `decoder`: (Opcional) Ruta al archivo del modelo ONNX del decodificador (predeterminado: `/tmp/base-decoder.onnx`)
- `tokens`: (Opcional) Ruta al archivo del modelo ONNX de tokens (predeterminado: `/tmp/base-tokens.onnx`)

Ejemplo con modelos personalizados:
```bash
docker run -p 8080:8080 \
  -e api_key="tu-clave-api-de-traduccion" \
  -e encoder="/app/models/custom-encoder.onnx" \
  -e decoder="/app/models/custom-decoder.onnx" \
  -e tokens="/app/models/custom-tokens.onnx" \
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

## Montar Modelos ONNX Personalizados
Puedes montar tus propios archivos de modelo ONNX en el contenedor usando volúmenes de Docker:

```bash
docker run -p 8080:8080 \
  -e api_key="tu-clave-api" \
  -v /ruta/a/tus/modelos:/app/models \
  -e encoder="/app/models/tu-encoder.onnx" \
  -e decoder="/app/models/tu-decoder.onnx" \
  -e tokens="/app/models/tu-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## Configuración de Puerto
- Puerto expuesto predeterminado: **8080**
- Puedes ajustar el mapeo de puertos del host:
  ```bash
  docker run -p 3000:8080 [...] # Mapea el puerto del host 3000 al puerto del contenedor 8080
  ```

## Estructura del Proyecto
- Usa Poetry para la gestión de dependencias
- Código fuente ubicado en el directorio `/app` dentro del contenedor
- Instala automáticamente todas las dependencias adicionales (incluyendo dependencias de desarrollo)

## Configuración Personalizada
Para personalización adicional:

1. **Montar archivos de configuración**:
   ```bash
   docker run -v /ruta/a/tu/config.yaml:/app/config.yaml [...]
   ```

2. **Usar variables de entorno**:
   ```bash
   docker run -e api_key="tu-clave" -e OTRA_VAR="valor" [...]
   ```

## Uso en Desarrollo
Si necesitas modificar el código o desarrollar:

```bash
# Clonar el código fuente
git clone <tu-repositorio>
cd <directorio-del-repositorio>

# Usar Docker Compose (recomendado)
# O usar docker run con el código local montado
docker run -p 8080:8080 -v $(pwd):/app -e api_key="tu-clave" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## Comprobación de Salud
Después de que el servidor se inicie, puedes verificar su estado accediendo a:
```bash
curl http://localhost:8080/health
```

## Notas
1. Asegúrate de proporcionar una variable de entorno `api_key` válida
2. El contenedor elimina automáticamente el archivo config.yaml predeterminado al inicio
3. Para configuración persistente, montar
archivos de configuración externos
4. Para modelos personalizados, monte sus archivos ONNX y configure las variables de entorno apropiadas

## Soporte y Comentarios
Si encuentra problemas o necesita soporte, envíe un Issue a través del repositorio del proyecto o contacte al mantenedor.