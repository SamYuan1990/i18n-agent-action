# تشغيل كإجراءات GitHub

## الطريقة الافتراضية

```yaml
name: i18n يدوي وإنشاء طلب السحب

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # يسمح بالتشغيل اليدوي

jobs:
  i18n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: التحقق من الكود
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}
          fetch-depth: 0

      - name: تشغيل ترجمة i18n
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          workspace: ${{ github.workspace }}
          CONFIG_FILE: mkdocs.yml
          DOCS_FOLDER: docs
          RESERVED_WORD: kepler,model
          target_language: zh
          max_files: 10

      - name: إنشاء طلب السحب
        uses: peter-evans/create-pull-request@v7
        with:
          title: "ترجمة i18n تلقائية"
          body: "يحتوي طلب السحب هذا على ترجمات دولية آلية"
          branch: feature/i18n-${{ github.run_id }}
          base: main
```

## تلقائي بعد طلب السحب

```yaml
name: معالجة ملفات Markdown المتغيرة

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

      - name: الحصول على ملفات Markdown المتغيرة
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          since_last_remote_commit: true
          separator: ","
          files: |
            docs/**/*.md
          files_ignore: |
            docs/**/*.*.md

      - name: تشغيل i18n على الملفات المتغيرة
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

      - name: إنشاء طلب السحب
        uses: peter-evans/create-pull-request@v7
        with:
          title: "تحديثات i18n تلقائية"
          body: "تحديثات ترجمة آلية للملفات المتغيرة"
          branch: feature/i18n-update-${{ github.run_id }}
          base: main
```