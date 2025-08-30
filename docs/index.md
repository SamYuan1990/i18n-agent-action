# I am an i18n AI Agent

To promote knowledge sharing and make our technology and projects more accessible to global audiences, we permit the use of large language models (LLMs) or generative AI for translating our documentation and community meeting notes.

Prioritize resource efficiency: Rather than having readers repeatedly translate our content via LLMs for their own needs, we believe it is more sustainable for us, as maintainers, to provide unified translated versions.

However, since we rely on cutting-edge AI translation technologies, we cannot guarantee absolute accuracy. If you encounter inconsistencies, please refer to the original English documentation and report any issues to the community for improvement.

## How it works

### Manual(for dev, or you should take your own security as it not running in sandbox)

```
uv sync
export api_key={your_key}
// uv run main.py {i18n rule of your project} {your docs folder} {Reserved Word, separated by comma} {optional if you have a file list}
// Below is an example that translate this project's docs (kepler is a resesrved word)
uv rn main.py mkdocs.yml docs kepler
```

and you shoud run linting by yourself.

### Container(running in sandbox)

```
docker run -it \
  -v path_to_your_repo:/workspace \
  -e model="deepseek-chat" \
  -e base_url="https://api.deepseek.com" \
  -e api_key="..." \
  -e CONFIG_FILE="/workspace/mkdocs.yml" \
  -e DOCS_FOLDER="/workspace/docs" \
  -e RESERVED_WORD="i18n-agent-action" \
  -e FILE_LIST="/workspace/docs/index.md" \
  ghcr.io/samyuan1990/i18n-agent-action:latest
```

### GHA

I suggest you enable PR creation in project settng to make auto PR back.

#### 1st init

```
name: Manual i8n and PR Creation

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # 允许手动触发

jobs:
  i8n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}  # 使用当前分支或main分支
          fetch-depth: 0  # 获取所有历史记录以便创建分支

      - name: Use this Action
        id: use-action
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          RESERVED_WORD: i18n-agent-action
          DOCS_FOLDER: /workspace/docs
          CONFIG_FILE: /workspace/mkdocs.yml
          workspace: /home/runner/work/i18n-agent-action/i18n-agent-action

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v7
        with:
          title: "auto i18n with GHA"
          body: "This PR do i18n for you"
          branch: feature/i18n-${{ github.run_id }}
          base: main  # 目标分支
          draft: false
```

#### after each PR

```
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

      - name: Get changed markdown files (excluding all i18n variants)
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          since_last_remote_commit: true
          separator: ","
          files: |
            docs/**/*.md
          files_ignore: |
            docs/**/*.*.md  # 匹配所有语言变体

      - name: Print and use changed files
        if: steps.changed-files.outputs.all_changed_files != ''
        run: |
          echo "Changed markdown files (excluding all i18n variants):"
          echo "${{ steps.changed-files.outputs.all_changed_files }}"

      - name: Use this Action
        id: use-action
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          RESERVED_WORD: i18n-agent-action
          DOCS_FOLDER: /workspace/docs
          CONFIG_FILE: /workspace/mkdocs.yml
          workspace: /home/runner/work/i18n-agent-action/i18n-agent-action
          FILE_LIST: ${{ steps.changed-files.outputs.all_changed_files }}

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v7
        with:
          title: "auto i18n with GHA"
          body: "This PR do i18n for you"
          branch: feature/i18n-${{ github.run_id }}
          base: main  # 目标分支
          draft: false
```  

## Inputs

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

## Tested communtiy/project

- [My Own](https://github.com/SamYuan1990/i18n-agent-action/pull/15)
- HAMi
- Huggingface Diffuser
  - [PR](https://github.com/huggingface/diffusers/pull/12032)
  - [PR](https://github.com/huggingface/diffusers/pull/12179)
