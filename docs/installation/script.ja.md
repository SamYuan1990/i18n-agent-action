# スクリプトとして実行

## 依存関係のインストール

```bash
uv sync
# または pip を使用
pip install --no-cache-dir .
```

## API キーの設定

```bash
export api_key={your_key}
```

## 実行

```bash
python3 run main.py {i18n_config_file} {docs_directory} {reserved_words,comma_separated} {optional_file_list}
```

## 例

```bash
# プロジェクト全体のドキュメントを翻訳（kepler を予約語として）
python3 run main.py mkdocs.yml docs kepler

# 複数の予約キーワードを使用して特定のファイルを翻訳
python3 run main.py mkdocs.yml docs kepler,kepler-model-server,pod /workspace/docs/index.md

# 特定の Python コマンド例
python3 main.py /Users/yuanyi/OpenSource/kepler-doc/mkdocs.yml /Users/yuanyi/OpenSource/kepler-doc/docs kepler,kepler-model-server,pod
```