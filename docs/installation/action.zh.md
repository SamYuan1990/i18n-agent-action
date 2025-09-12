# 作为 GitHub Actions 运行

## 默认方式

```yaml
name: 手动 i18n 和 PR 创建

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # 允许手动触发

jobs:
  i18n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: 检出代码
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}
          fetch-depth: 0

      - name: 运行 i18n 翻译
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          workspace: ${{ github.workspace }}
          CONFIG_FILE: mkdocs.yml
          DOCS_FOLDER: docs
          RESERVED_WORD: kepler,model
          target_language: zh
          max_files: 10

      - name: 创建拉取请求
        uses: peter-evans/create-pull-request@v7
        with:
          title: "自动 i18n 翻译"
          body: "此 PR 包含自动化国际化翻译"
          branch: feature/i18n-${{ github.run_id }}
          base: main
```

## PR 后自动运行

```yaml
name: 处理更改的 Markdown 文件

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

      - name: 获取更改的 Markdown 文件
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          since_last_remote_commit: true
          separator: ","
          files: |
            docs/**/*.md
          files_ignore: |
            docs/**/*.*.md

      - name: 在更改的文件上运行 i18n
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

      - name: 创建拉取请求
        uses: peter-evans/create-pull-request@v7
        with:
          title: "自动 i18n 更新"
          body: "针对更改文件的自动化翻译更新"
          branch: feature/i18n-update-${{ github.run_id }}
          base: main
```