# Ejecutar como GitHub Actions

## Forma predeterminada

```yaml
name: i18n manual y creación de PR

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # Permite activación manual

jobs:
  i18n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout del código
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}
          fetch-depth: 0

      - name: Ejecutar traducción i18n
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          workspace: ${{ github.workspace }}
          CONFIG_FILE: mkdocs.yml
          DOCS_FOLDER: docs
          RESERVED_WORD: kepler,model
          target_language: zh
          max_files: 10

      - name: Crear Pull Request
        uses: peter-evans/create-pull-request@v7
        with:
          title: "Traducción i18n automática"
          body: "Este PR contiene traducciones automatizadas de internacionalización"
          branch: feature/i18n-${{ github.run_id }}
          base: main
```

## Automático después de PR

```yaml
name: Procesar archivos Markdown modificados

permissions:
  contents: write
  pull-requests: write

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**/*.md'

jobs:
  process-markdown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Obtener archivos Markdown modificados
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          since_last_remote_commit: true
          separator: ","
          files: |
            docs/**/*.md
          files_ignore: |
            docs/**/*.*.md

      - name: Ejecutar i18n en archivos modificados
        if: steps.changed-files.outputs.all_changed_files != ''
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          workspace: ${{ github.workspace }}
          CONFIG_FILE: mkdocs.yml
          DOCS_FOLDER: docs
          RESERVED_WORD: i18n-agent-action
          FILE_LIST: ${{ steps.changed-files.outputs.all_changed_files }}
          dryRun: false
          usecache: true

      - name: Crear Pull Request
        uses: peter-evans/create-pull-request@v7
        with:
          title: "Actualizaciones i18n automáticas"
          body: "Actualizaciones de traducción automatizadas para archivos modificados"
          branch: feature/i18n-update-${{ github.run_id }}
          base: main
```