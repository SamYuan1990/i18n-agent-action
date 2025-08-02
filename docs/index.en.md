# Why we have this
After discussions at KCD 2025 Beijing and Community Over Code 2025 China, we finally decided to create an agent to handle the community's i18n work.
For me, I can't work simultaneously on [https://github.com/sustainable-computing-io/kepler-doc/issues/175](https://github.com/sustainable-computing-io/kepler-doc/issues/175) and the Community Over Code 2025 meeting.

## Trying my own agent development principles

#### Corollary 1: If the task is relatively fixed and has a reliable solution, there's no need to call a large model to take the risk.

#### Corollary 2: The task is not fixed, adapting one by one is too complex. Large models have a certain generality, we need to make good use of this generality and delegate it to the large model.

#### Corollary 3: The task is not fixed, it can be adapted one by one according to the actual situation. If a large model is used, the possibility of the large model responding incorrectly must be considered and the error handled accordingly.

#### Corollary 4: The task is fixed but does not have a reliable solution. If a large model is used to attempt creative solutions, human intervention is needed.

# Because it's an AI agent
## How it works
### Manual (suitable for development, or you should take the security responsibility yourself, since it doesn't run in a sandbox)
```
pip3 install -r ./requirements.txt
export api_key={your_key}
//python3 main.py {your config file} {your docs folder} {Reserved Word} {optional if you have a file list}
python3 main.py {full_path_to_your_repo}/mkdocs.yml {full_path_to_your_repo}/docs kepler {optional if you have a file list}
```
And you should run the linting yourself.

### Container (runs in a sandbox)
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
I suggest you enable PR creation in the project settings so that PR is automatically returned.

#### First initialization
```
name: i8n manual and PR creation

permissions:
  contents: write
  pull-requests: write

on:
  workflow_dispatch:  # Allows manual triggering

jobs:
  i8n-and-create-pr:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref || 'main' }}  # Uses the current branch or the main branch
          fetch-depth: 0  # Gets the entire history to create a branch

      - name: Use this Action
        id: use-action
        uses: SamYuan1990/i18n-agent-action@main
        with:
          apikey: ${{ secrets.API_KEY }}
          RESERVED_WORD: i18n-agent-action
          DOCS_FOLDE
R: /workspace/docs
      CONFIG_FILE: /workspace/mkdocs.yml
      workspace: /home/runner/work/i18n-agent-action/i18n-agent-action

  - name: Create Pull Request
    uses: peter-evans/create-pull-request@v7
    with:
      title:
Use GHA for automatic i18n
      body: "This PR completes internationalization for you"
      branch: feature/i18n-${{ github.run_id }}
      base: main  # Target branch
      draft: false
```
#### After each PR
```
name: Process changed Markdown files

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
            docs/**/*.*.md  # Matches all language variants

      - name: Print and use changed files
        if: steps.changed-files.outputs.all_changed_files != ''
        run: |
          echo
Changed markdown files (excluding all i18n variants):
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
          title: "Use GHA for automatic internationalization"
          body: "This PR completes internationalization for you"
          branch: feature/i18n-${{ github.run_id }}
          base: main  # Target branch
          draft: false

## Input
| Input Parameter | Required | Default Value | Description |
|-----------------|----------|---------------|-------------|
| `apikey`        | Yes      | -             | LLM service API key |
| `base_url`      | No       | DeepSeek             | LLM service endpoint URL |
| `model`         | No       | DeepSeek v3            | LLM service model name/identifier |
| `RESERVED_WORD` | Yes      | -             | Reserved term/phrase to exclude from translation |
| `DOCS_FOLDER`   | Yes      | -             | Path to your documents folder |
| `CONFIG_FILE`   | Yes      | -             | Configuration file for project internationalization |
| `FILE_LIST`     | No       | -
| Specific list of files to process (optional) |
| `workspace`     | Yes      | -             | Path to your code repository's workspace |
| `target_language` | No     | `'zh'`        | Target language code for translation (e.g., `'zh'` for Chinese) |
| `max_files`     | No       | `'20'`        | Maximum number of files to process |
| `dryRun`        | No       | false             | Enable dry-run mode (simulate execution without making changes) |

## Test completed
muntiy/project
- Own(https://github.com/SamYuan1990/i18n-agent-action/pull/15)
- HAMi

## Out of scope
- lint
 Disclaimer: This content is powered by i18n-agent-action with the LLM service https://api.deepseek.com with the model deepseek-chat, for some reason, (for example, we are not native speakers) we use LLM to provide this translation for you. If you find any corrections, please open an issue or submit a PR back to GitHub, and switch back to the default language.
 Disclaimers: This content is powered by i18n-agent-action with LLM service https://api.deepseek.com with model deepseek-chat, for some reason, (for example, we are not native speaker) we use LLM to provide this translate for you. If you find any corrections, please file an issue or raise a PR back to github, and switch back to default language.
 Disclaimers: This content is powered by i18n-agent-action with LLM service https://api.deepseek.com with model deepseek-chat, for some reason, (for example, we are not native speaker) we use LLM to provide this translate for you. If you find any corrections, please file an issue or raise a PR back to github, and switch back to default language.