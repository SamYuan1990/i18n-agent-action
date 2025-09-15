# Run as Contaienr

This is backend of github action not desktop app.

## basic

```bash
docker run -it \
  -v path_to_your_repo:/workspace \
  -e api_key="your_api_key_here" \
  -e CONFIG_FILE="/workspace/mkdocs.yml" \
  -e DOCS_FOLDER="/workspace/docs" \
  -e RESERVED_WORD="your-reserved-words" \
  ghcr.io/samyuan1990/i18n-agent-action:latest
```

## full

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