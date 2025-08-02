# 为什么我们拥有这个
在KCD 2025北京和Community Over Code 2025中国的讨论之后，我们最终决定创建一个代理来处理社区的i18n工作。
对我来说，我无法同时处理[https://github.com/sustainable-computing-io/kepler-doc/issues/175](https://github.com/sustainable-computing-io/kepler-doc/issues/175)和参加Community Over Code 2025会议。

## 我的代理开发原则体验

#### 结论1：如果任务相对固定且有可靠的解决方案，则无需调用大型模型冒险。

#### 结论2：任务不固定，适应每种情况非常复杂。大型模型具有一定的通用性，我们需要很好地利用这种通用性并将其委托给大型模型。

#### 结论3：任务不固定，可以根据实际情况适应每种情况。如果使用大型模型，应考虑大型模型回答错误的情况，并相应地处理错误。

#### 结论4：任务固定但没有可靠的解决方案。如果使用大型模型尝试创造性解决，需要人工干预。

# 因为它是AI代理
## 它是如何工作的
### 手动（适合开发，或者你必须自己承担安全责任，因为它不在隔离环境中运行）
```
pip3 install -r ./requirements.txt
export api_key={your_key}
//python3 main.py {your config file} {your docs folder} {Reserved Word} {optional if you have a file list}
python3 main.py {full_path_to_your_repo}/mkdocs.yml {full_path_to_your_repo}/docs kepler {optional if you have a file list}
```
你必须自己运行linting。

### 容器（在隔离环境中运行）
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
我建议在项目设置中启用PR创建以自动创建PR。

#### 初始配置
```
name: i8n手动和创建PR

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # 允许手动运行

jobs:
  i8n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: 检出代码
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}  # 使用当前分支或主分支
          fetch-depth: 0  # 获取全部历史以创建分支

      - name: 使用此动作
        id: use-action
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          RESERVED_WORD: i18n-agent-action
          DOCS_FOLDER: /workspace/docs
          CONFIG_FILE: /workspace/mkdocs.yml
          workspace: /home/runner/work/i18n-agent-action/i18n-agent-action

      - name: 创建拉取请求
        uses: peter-evans/create-pull-request@v7
        with:
          title:
使用GHA自动化i18n
          body: "此PR为您完成i18n"
          branch: feature/i18n-${{ github.run_id }}
          base: main  # 目标分支
   
           draft: false
```
#### 每次PR后
```
name: 处理变更的Markdown文件

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

      - name: 获取变更的markdown文件（不包括所有i18n变体）
        id: changed-files
        uses: tj-actions/changed-files@v40
        with:
          since_last_remote_commit: true
          separator: ","
          files: |
            docs/**/*.md
          files_ignore: |
            docs/**/*.*.md  # 匹配所有语言变体

      - name: 打印并使用变更的文件
        if: steps.changed-files.outputs.all_changed_files != ''
        run: |
          echo
变更的markdown文件（不包括所有i18n变体）：
          echo "${{ steps.changed-files.outputs.all_changed_files }}"

      - name: 使用此动作
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
          title: "使用GHA进行自动化国际化"
          body: "此PR为您完成国际化过程"
          branch: feature/i18n-${{ github.run_id }}
          base: main  # 目标分支
          draft: false

## 输入
| 输入参数 | 必需 | 默认值 | 描述 |
|-----------------|----------|---------------|-------------|
| `apikey`        | 是      | -             | LLM服务的API密钥 |
| `base_url`      | 否       | DeepSeek             | LLM服务端点的URL |
| `model`         | 否       | DeepSeek v3            | LLM服务的模型名称/标识 |
| `RESERVED_WORD` | 是      | -             | 从翻译中排除的保留术语/短语 |
| `DOCS_FOLDER`   | 是      | -             | 您的文档文件夹路径 |
| `CONFIG_FILE`   | 是      | -             | 项目国际化设置的配置文件 |
| `FILE_LIST`     | 否       | -             | 要处理的特定文件列表（可选） |
| `workspace`     | 是      | -             | 您的代码仓库的工作空间路径 |
| `target_language` | 否     | `'zh'`        | 翻译的目标语言代码（例如，`'zh'`为中文） |
| `max_files`     | 否       | `'20'`        | 要处理的文件的最大数量 |
| `dryRun`        | 否       | false             | 启用dry-run模式（模拟执行而不做任何更改） |

## 测试完成
muntiy/项目
- 自己(https://github.com/SamYuan1990/i18n-agent-action/pull/15)
- HAMi

## 超出范围
- lint
 免责声明：此内容由i18n-agent-action与LLM服务https://api支持
.deepseek.com 使用deepseek-chat模型，出于某种原因（例如，我们不是母语者），我们使用LLM为您提供此翻译。如果您发现任何需要更正的地方，请提交问题或向github提出PR，并切换回默认语言。免责声明：此内容由i18n-agent-action与LLM服务https://api.deepseek.com和模型deepseek-chat提供，出于某种原因（例如，我们不是母语者），我们使用LLM为您提供此翻译。如果您发现任何需要更正的地方，请提交问题或向github提出PR，并切换回默认语言。
 Disclaimers: This content is powered by i18n-agent-action with LLM service https://api.deepseek.com with model deepseek-chat, for some reason, (for example, we are not native speaker) we use LLM to provide this translate for you. If you find any corrections, please file an issue or raise a PR back to github, and switch back to default language.