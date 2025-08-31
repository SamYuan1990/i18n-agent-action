# I am an i18n AI Agent

To promote knowledge sharing and make our technology and projects more accessible to global audiences, we permit the use of large language models (LLMs) or generative AI for translating our documentation and community meeting notes.

Prioritize resource efficiency: Rather than having readers repeatedly translate our content via LLMs for their own needs, we believe it is more sustainable for us, as maintainers, to provide unified translated versions.

However, since we rely on cutting-edge AI translation technologies, we cannot guarantee absolute accuracy. If you encounter inconsistencies, please refer to the original English documentation and report any issues to the community for improvement.

## How it works

### 📋 Input Parameters

All execution methods support the following unified parameters:

| Input Parameter | Required | Default Value | Description |
|-----------------|----------|---------------|-------------|
| `apikey`        | Yes      | -             | API key for the LLM service |
| `base_url`      | No       | DeepSeek             | Endpoint URL of the LLM service |
| `model`         | No       | DeepSeek v3            | Model name/identifier for the LLM service |
| `RESERVED_WORD` | Yes      | -             | Reserved terms/phrases to exclude from translation |
| `DOCS_FOLDER`   | Yes      | -             | Path to your documentation folder |
| `CONFIG_FILE`   | Yes      | -             | Configuration file for project i18n settings |
| `FILE_LIST`     | No       | -             | Specific list of files to process (optional) |
| `workspace`     | Yes      | -             | Path to your code repository workspace |
| `target_language` | No     | `'zh'`        | Target language code for translation (e.g., `'zh'` for Chinese) |
| `max_files`     | No       | `'20'`        | Maximum number of files to process |
| `dryRun`        | No       | false             | Enable dry-run mode (simulates execution without making changes) |
| `usecache`      | No       | true             | Enable cache for LLM request |
| `disclaimers`   | No       | true             | Show disclaimers at end of translate |

<details>
<summary><h2>📋 Manual Execution</h2></summary>

### Install Dependencies
```bash
uv sync
# or using pip
pip install --no-cache-dir .
```

### Set API Key
```bash
export api_key={your_key}
```

### Run Command
```bash
python3 run main.py {i18n_config_file} {docs_directory} {reserved_words,comma_separated} {optional_file_list}
```

### Examples
```bash
# Translate entire project docs (kepler as reserved word)
python3 run main.py mkdocs.yml docs kepler

# Translate specific files with multiple reserved keywords
python3 run main.py mkdocs.yml docs kepler,kepler-model-server,pod /workspace/docs/index.md

# Specific Python command example
python3 main.py /Users/yuanyi/OpenSource/kepler-doc/mkdocs.yml /Users/yuanyi/OpenSource/kepler-doc/docs kepler,kepler-model-server,pod
```

</details>

<details>
<summary><h2>🐳 Container Execution</h2></summary>

### Basic Command
```bash
docker run -it \
  -v path_to_your_repo:/workspace \
  -e api_key="your_api_key_here" \
  -e CONFIG_FILE="/workspace/mkdocs.yml" \
  -e DOCS_FOLDER="/workspace/docs" \
  -e RESERVED_WORD="your-reserved-words" \
  ghcr.io/samyuan1990/i18n-agent-action:latest
```

### Complete Example
```bash
docker run -it \
  -v /Users/yuanyi/OpenSource/kepler-doc:/workspace \
  -e api_key="sk-your-deepseek-key" \
  -e model="deepseek-chat" \
  -e base_url="https://api.deepseek.com" \
  -e dryRun="false" \
  -e target_language="zh" \
  -e max_files="20" \
  -e usecache="true" \
  -e disclaimers="true" \
  -e CONFIG_FILE="/workspace/mkdocs.yml" \
  -e DOCS_FOLDER="/workspace/docs" \
  -e RESERVED_WORD="kepler,kepler-model-server,pod" \
  -e FILE_LIST="/workspace/docs/index.md" \
  ghcr.io/samyuan1990/i18n-agent-action:latest
```

</details>

<details>
<summary><h2>⚡ GitHub Actions Execution</h2></summary>

### Initial Setup Workflow
```yaml
name: Manual i18n and PR Creation

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # Allow manual triggering

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

### Post-PR Incremental Translation Workflow
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

</details>

## Tested communtiy/project

- [My Own](https://github.com/SamYuan1990/i18n-agent-action/pull/15)
- HAMi
- Huggingface Diffuser
  - [PR](https://github.com/huggingface/diffusers/pull/12032)
  - [PR](https://github.com/huggingface/diffusers/pull/12179)
