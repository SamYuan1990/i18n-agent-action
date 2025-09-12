# Run as script

## install dep

```bash
uv sync
# 或使用 pip
pip install --no-cache-dir .
```

## Set api key

```bash
export api_key={your_key}
```

## run

```bash
python3 run main.py {i18n_config_file} {docs_directory} {reserved_words,comma_separated} {optional_file_list}
```

## example

```bash
# 翻译整个项目文档（kepler 作为保留词）
python3 run main.py mkdocs.yml docs kepler

# 使用多个保留关键字翻译特定文件
python3 run main.py mkdocs.yml docs kepler,kepler-model-server,pod /workspace/docs/index.md

# 特定 Python 命令示例
python3 main.py /Users/yuanyi/OpenSource/kepler-doc/mkdocs.yml /Users/yuanyi/OpenSource/kepler-doc/docs kepler,kepler-model-server,pod
```