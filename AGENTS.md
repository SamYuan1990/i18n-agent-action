# AGENTS.md for i18n-agent-action

## Dev environment setup

- Create a Python virtual environment: `python -m venv venv`
- Activate the virtual environment:
  - Windows: `venv\Scripts\activate`
  - Unix/MacOS: `source venv/bin/activate`
- Install dependencies: `pip install -e .`
- Install optional dependencies as needed:
  - For app functionality: `pip install -e ".[app]"`
  - For documentation: `pip install -e ".[docs]"`
- For package management: `poetry`

## Development tips

- The project contains two main packages: `Business` and `AgentUtils`
- Use `import Business` or `import AgentUtils` to access package functionality
- The project requires Python 3.12+ (specified in pyproject.toml)

## Testing instructions

- Run tests using pytest (assuming tests are configured): `pytest`
- Run tests for specific modules: `poetry run pytest`
- To run with coverage: `poetry run pytest --cov=my_project -v`
- To run local dev UI: `poetry run flet run -d ./App` or `export FLET_SECRET_KEY=123 && poetry run flet run -wd ./App`
- Ensure all tests pass before committing changes
- Lint `docker run --rm \
  -e RUN_LOCAL=true \
  -e VALIDATE_PYTHON=true \
  -e VALIDATE_PYTHON_BLACK=true \
  -e VALIDATE_PYTHON_RUFF=true \
  -e VALIDATE_PYTHON_ISORT=true \
  -e VALIDATE_PYTHON_PYLINT=true \
  -e DEFAULT_BRANCH=main \
  -e VALIDATE_GITHUB_ACTIONS=true \
  -e FIX_PYTHON_RUFF=true \
  -e FIX_PYTHON_ISORT=true \
  -e FIX_PYTHON_BLACK=true \
  -v "$PWD:/tmp/lint" \
  ghcr.io/super-linter/super-linter:latest
`
- To test build result on mac `
sudo xattr -d com.apple.quarantine ~/i18n-agent-action.app 
codesign --force --deep --sign - --preserve-metadata=entitlements --options runtime ~/i18n-agent-action.app`
may help.

## Documentation

- Documentation is built with MkDocs and related plugins
- To serve documentation locally: `mkdocs serve`
- To build documentation: `mkdocs build`

## PR instructions

- Title format: `[i18n-agent-action] <Title>`
- Ensure Python type checking passes (if using mypy)
- Run all tests before committing
- Update documentation if functionality changes
- Add tests for new features

## Deployment notes

### GitHub Action Deployment
This project is deployed as a GitHub Action with the following configuration:

**Required Inputs:**
- `apikey`: API key to LLM service (required)
- `RESERVED_WORD`: Words to keep untranslated (required)
- `DOCS_FOLDER`: Documentation folder path (required)
- `CONFIG_FILE`: Configuration file for i18n settings (required)
- `workspace`: Workspace to your code repository (required)

**Optional Inputs:**
- `base_url`: LLM service endpoint
- `model`: LLM service model
- `FILE_LIST`: Specific files to process
- `target_language`: Target language (default: 'support')
- `max_files`: Maximum file numbers (default: '20')
- `dryRun`: Dry run option
- `usecache`: Cache LLM responses or not
- `disclaimers`: Show disclaimers or not

**Docker Deployment:**
The action runs in a Docker container with the following volume mapping:
- Workspace directory mounted to `/workspace`
- Environment variables for all configuration parameters

**Usage Example:**
```yaml
- uses: SamYuan1990/i18n-agent-action@v1
  with:
    apikey: ${{ secrets.API_KEY }}
    RESERVED_WORD: "technical terms"
    DOCS_FOLDER: "docs"
    CONFIG_FILE: "i18n-config.json"
    workspace: ${{ github.workspace }}
    target_language: "zh-CN"
```

### Package Deployment
- The package is built with setuptools and wheel
- Build package: `python -m build`
- The project includes Prometheus client for monitoring

## Dependencies

- Core dependencies: openai, transformers, prometheus-client, python-defer
- App dependencies: flet (with all extras)
- Docs dependencies: mkdocs and related plugins

## Project URLs

- **Homepage**: https://github.com/SamYuan1990/i18n-agent-action
- **Documentation**: https://samyuan1990.github.io/i18n-agent-action/
- **Repository**: https://github.com/SamYuan1990/i18n-agent-action
- **Issues**: https://github.com/SamYuan1990/i18n-agent-action/issues