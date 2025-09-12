# 📋 Parámetros de Entrada

Todos los métodos de ejecución admiten los siguientes parámetros unificados:

| Parámetro de Entrada | Obligatorio | Valor Predeterminado | Descripción |
|----------------------|-------------|----------------------|-------------|
| `apikey`             | Sí          | -                    | Clave API para el servicio LLM |
| `base_url`           | No          | DeepSeek             | URL del endpoint del servicio LLM |
| `model`              | No          | DeepSeek v3          | Nombre/identificador del modelo para el servicio LLM |
| `RESERVED_WORD`      | Sí          | -                    | Términos/frases reservados para excluir de la traducción |
| `DOCS_FOLDER`        | Sí          | -                    | Ruta a tu carpeta de documentación |
| `CONFIG_FILE`        | Sí          | -                    | Archivo de configuración para los ajustes de i18n del proyecto |
| `FILE_LIST`          | No          | -                    | Lista específica de archivos a procesar (opcional) |
| `workspace`          | Sí          | -                    | Ruta a tu espacio de trabajo del repositorio de código |
| `target_language`    | No          | `'zh'`               | Código de idioma objetivo para la traducción (por ejemplo, `'zh'` para chino) |
| `max_files`          | No          | `'20'`               | Número máximo de archivos a procesar |
| `dryRun`             | No          | false                | Habilitar modo de simulación (ejecuta sin hacer cambios) |
| `usecache`           | No          | true                 | Habilitar caché para solicitudes LLM |
| `disclaimers`        | No          | true                 | Mostrar descargos de responsabilidad al final de la traducción |