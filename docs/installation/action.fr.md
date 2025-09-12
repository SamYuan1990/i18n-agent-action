# Exécuter en tant qu'actions GitHub

## Méthode par défaut

```yaml
name: Internationalisation manuelle et création de PR

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # Permet un déclenchement manuel

jobs:
  i18n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: Vérifier le code
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}
          fetch-depth: 0

      - name: Exécuter la traduction i18n
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          workspace: ${{ github.workspace }}
          CONFIG_FILE: mkdocs.yml
          DOCS_FOLDER: docs
          RESERVED_WORD: kepler,model
          target_language: zh
          max_files: 10

      - name: Créer une demande de tirage (PR)
        uses: peter-evans/create-pull-request@v7
        with:
          title: "Traduction i18n automatique"
          body: "Cette PR contient des traductions automatisées d'internationalisation"
          branch: feature/i18n-${{ github.run_id }}
          base: main
```

## Automatique après PR

```yaml
name: Traiter les fichiers Markdown modifiés

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

      - name: Obtenir les fichiers Markdown modifiés
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          since_last_remote_commit: true
          separator: ","
          files: |
            docs/**/*.md
          files_ignore: |
            docs/**/*.*.md

      - name: Exécuter i18n sur les fichiers modifiés
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

      - name: Créer une demande de tirage (PR)
        uses: peter-evans/create-pull-request@v7
        with:
          title: "Mises à jour i18n automatiques"
          body: "Mises à jour de traduction automatisées pour les fichiers modifiés"
          branch: feature/i18n-update-${{ github.run_id }}
          base: main
```