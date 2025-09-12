# GitHub Actionsとして実行

## デフォルトの方法

```yaml
name: 手動i18nとPR作成

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # 手動トリガーを許可

jobs:
  i18n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: コードをチェックアウト
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}
          fetch-depth: 0

      - name: i18n翻訳を実行
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          workspace: ${{ github.workspace }}
          CONFIG_FILE: mkdocs.yml
          DOCS_FOLDER: docs
          RESERVED_WORD: kepler,model
          target_language: zh
          max_files: 10

      - name: プルリクエストを作成
        uses: peter-evans/create-pull-request@v7
        with:
          title: "自動i18n翻訳"
          body: "このPRには自動化された国際化翻訳が含まれています"
          branch: feature/i18n-${{ github.run_id }}
          base: main
```

## PR後の自動実行

```yaml
name: 変更されたMarkdownファイルを処理

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

      - name: 変更されたMarkdownファイルを取得
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          since_last_remote_commit: true
          separator: ","
          files: |
            docs/**/*.md
          files_ignore: |
            docs/**/*.*.md

      - name: 変更されたファイルでi18nを実行
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

      - name: プルリクエストを作成
        uses: peter-evans/create-pull-request@v7
        with:
          title: "自動i18n更新"
          body: "変更されたファイルの自動翻訳更新"
          branch: feature/i18n-update-${{ github.run_id }}
          base: main
```