# 我是一个 i18n AI 代理

为了促进知识共享，并使我们的技术和项目更容易被全球受众访问，我们允许使用大型语言模型（LLMs）或生成式 AI 来翻译我们的文档和社区会议记录。

优先考虑资源效率：与其让读者反复通过 LLMs 翻译我们的内容以满足自己的需求，我们认为作为维护者，提供统一的翻译版本更加可持续。

然而，由于我们依赖前沿的 AI 翻译技术，我们无法保证绝对准确性。如果您遇到不一致之处，请参考原始英文文档，并向社区报告任何问题以进行改进。

## 工作原理

### 手动方式（用于开发，或者您应该自行负责安全，因为它不在沙箱中运行）

```
uv sync
export api_key={your_key}
// uv run main.py {i18n rule of your project} {your docs folder} {Reserved Word, separated by comma} {optional if you have a file list}
// 下面是一个翻译此项目文档的示例（kepler 是一个保留词）
uv rn main.py mkdocs.yml docs kepler
```

并且您应该自行运行 linting。

### 容器方式（在沙箱中运行）

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

我建议您在项目设置中启用 PR 创建，以便自动创建 PR 返回。

#### 首次初始化

```
name: 手动 i8n 和 PR 创建

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # 允许手动触发

jobs:
  i8n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: 检出代码
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}  # 使用当前分支或 main 分支
          fetch-depth: 0  # 获取所有历史记录以便创建分支

      - name: 使用此 Action
        id: use-action
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          RESERVED_WORD: i18n-agent-action
          DOCS_FOLDER: /workspace/docs
          CONFIG_FILE: /workspace/mkdocs.yml
          workspace: /home/runner/work/i18n-agent-action/i18n-agent-action

      - name: 创建 Pull Request
        uses: peter-evans/create-pull-request@v7
        with:
          title: "使用 GHA 自动 i18n"
          body: "此 PR 为您执行 i18n"
          branch: feature/i18n-${{ github.run_id }}
          base: main  # 目标分支
          draft: false
```

#### 在每个 PR 之后

```
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
        w
```
ith:
  fetch-depth: 0

- name: 获取更改的 Markdown 文件（排除所有 i18n 变体）
  id: changed-files
  uses: tj-actions/changed-files@v40
  with:
    since_last_remote_commit: true
    separator: ","
    files: |
      docs/**/*.md
    files_ignore: |
      docs/**/*.*.md  # 匹配所有语言变体

- name: 打印并使用更改的文件
  if: steps.changed-files.outputs.all_changed_files != ''
  run: |
    echo "Changed markdown files (excluding all i18n variants):"
    echo "${{ steps.changed-files.outputs.all_changed_files }}"

- name: 使用此 Action
  id: use-action
  uses: SamYuan1990/i18n-agent-action@main
  with:
    apikey: ${{ secrets.API_KEY }}
    RESERVED_WORD: i18n-agent-action
    DOCS_FOLDER: /workspace/docs
    CONFIG_FILE: /workspace/mkdocs.yml
    workspace: /home/runner/work/i18n-agent-action/i18n-agent-action
    FILE_LIST: ${{ steps.changed-files.outputs.all_changed_files }}

- name: 创建拉取请求
  uses: peter-evans/create-pull-request@v7
  with:
    title: "auto i18n with GHA"
    body: "This PR do i18n for you"
    branch: feature/i18n-${{ github.run_id }}
    base: main  # 目标分支
    draft: false

## 输入参数

| 输入参数 | 是否必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `apikey` | 是 | - | LLM 服务的 API 密钥 |
| `base_url` | 否 | DeepSeek | LLM 服务的端点 URL |
| `model` | 否 | DeepSeek v3 | LLM 服务的模型名称/标识符 |
| `RESERVED_WORD` | 是 | - | 要排除翻译的保留术语/短语 |
| `DOCS_FOLDER` | 是 | - | 文档文件夹的路径 |
| `CONFIG_FILE` | 是 | - | 项目 i18n 设置的配置文件 |
| `FILE_LIST` | 否 | - | 要处理的特定文件列表（可选） |
| `workspace` | 是 | - | 代码仓库工作空间的路径 |
| `target_language` | 否 | `'zh'` | 翻译的目标语言代码（例如，`'zh'` 表示中文） |
| `max_files` | 否 | `'20'` | 要处理的最大文件数 |
| `dryRun` | 否 | false | 启用干运行模式（模拟执行而不做更改） |
| `usecache` | 否 | true | 启用 LLM 请求的缓存 |
| `disclaimers` | 否 | true | 在翻译结束时显示免责声明 |

## 测试过的社区/项目

- [我自己的](https://github.com/SamYuan1990/i18n-agent-action/pull/15)
- HAMi
- Huggingface Diffuser
  - [PR](https://github.com/huggingface/diffusers/pull/12032)
  - [PR](https://github.com/huggingface/diffusers/pull/12179)