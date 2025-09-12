# 📋 输入参数

所有执行方法都支持以下统一参数：

| 输入参数 | 必填 | 默认值 | 描述 |
|-----------------|----------|---------------|-------------|
| `apikey` | 是 | - | LLM 服务的 API 密钥 |
| `base_url` | 否 | DeepSeek | LLM 服务的端点 URL |
| `model` | 否 | DeepSeek v3 | LLM 服务的模型名称/标识符 |
| `RESERVED_WORD` | 是 | - | 从翻译中排除的保留术语/短语 |
| `DOCS_FOLDER` | 是 | - | 您的文档文件夹路径 |
| `CONFIG_FILE` | 是 | - | 项目国际化设置配置文件 |
| `FILE_LIST` | 否 | - | 要处理的特定文件列表（可选） |
| `workspace` | 是 | - | 您的代码仓库工作区路径 |
| `target_language` | 否 | `'zh'` | 翻译的目标语言代码（例如，`'zh'` 表示中文） |
| `max_files` | 否 | `'20'` | 要处理的最大文件数 |
| `dryRun` | 否 | false | 启用试运行模式（模拟执行而不进行更改） |
| `usecache` | 否 | true | 启用 LLM 请求缓存 |
| `disclaimers` | 否 | true | 在翻译结束时显示免责声明 |