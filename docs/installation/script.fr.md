# Exécuter en tant que script

## Installer les dépendances

```bash
uv sync
# ou utiliser pip
pip install --no-cache-dir .
```

## Définir la clé API

```bash
export api_key={your_key}
```

## Exécuter

```bash
python3 run main.py {i18n_config_file} {docs_directory} {reserved_words,comma_separated} {optional_file_list}
```

## Exemple

```bash
# Traduire toute la documentation du projet (kepler en tant que mot réservé)
python3 run main.py mkdocs.yml docs kepler

# Utiliser plusieurs mots-clés réservés pour traduire des fichiers spécifiques
python3 run main.py mkdocs.yml docs kepler,kepler-model-server,pod /workspace/docs/index.md

# Exemple de commande Python spécifique
python3 main.py /Users/yuanyi/OpenSource/kepler-doc/mkdocs.yml /Users/yuanyi/OpenSource/kepler-doc/docs kepler,kepler-model-server,pod
```