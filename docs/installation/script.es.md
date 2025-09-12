# Ejecutar como script

## Instalar dependencias

```bash
uv sync
# o usar pip
pip install --no-cache-dir .
```

## Configurar clave API

```bash
export api_key={your_key}
```

## Ejecutar

```bash
python3 run main.py {i18n_config_file} {docs_directory} {reserved_words,comma_separated} {optional_file_list}
```

## Ejemplo

```bash
# Traducir toda la documentación del proyecto (kepler como palabra reservada)
python3 run main.py mkdocs.yml docs kepler

# Usar múltiples palabras clave reservadas para traducir archivos específicos
python3 run main.py mkdocs.yml docs kepler,kepler-model-server,pod /workspace/docs/index.md

# Ejemplo específico de comando Python
python3 main.py /Users/yuanyi/OpenSource/kepler-doc/mkdocs.yml /Users/yuanyi/OpenSource/kepler-doc/docs kepler,kepler-model-server,pod
```