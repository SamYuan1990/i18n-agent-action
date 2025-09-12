# Run as GitHub Actions

## Default way

```yaml
name: Manual i18n and PR Creation

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # 允许手动触发

jobs:
  i18n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}
          fetch-depth: 0

      - name: Run i18n Translation
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          workspace: ${{ github.workspace }}
          CONFIG_FILE: mkdocs.yml
          DOCS_FOLDER: docs
          RESERVED_WORD: kepler,model
          target_language: zh
          max_files: 10

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v7
        with:
          title: "Auto i18n Translation"
          body: "This PR contains automated internationalization translations"
          branch: feature/i18n-${{ github.run_id }}
          base: main
```

## Auto after PR

```yaml
name: Process Changed Markdown Files

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

      - name: Get changed markdown files
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          since_last_remote_commit: true
          separator: ","
          files: |
            docs/**/*.md
          files_ignore: |
            docs/**/*.*.md

      - name: Run i18n on changed files
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

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v7
        with:
          title: "Auto i18n Updates"
          body: "Automated translation updates for changed files"
          branch: feature/i18n-update-${{ github.run_id }}
          base: main
```