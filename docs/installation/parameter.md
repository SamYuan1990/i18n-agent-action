# 📋 Input Parameters

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