# i18n MCP サーバー ユーザーガイド

## イメージ情報
- **イメージ名**: `ghcr.io/samyuan1990/i18n-agent-action:mcp`
- **ベースイメージ**: Python 3.12
- **作業ディレクトリ**: `/app`

## 説明
これは、国際化（i18n）タスク用に設計されたモデルコンテキストプロトコル（MCP）サーバーで、カスタム ONNX モデルをサポートした翻訳関連の機能を提供します。

## クイックスタート

### イメージのプル
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### コンテナの実行
```bash
docker run -p 8080:8080 -e api_key="YOUR_API_KEY" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### 環境変数の設定
- `api_key`: (必須) 翻訳サービスの API キー
- `encoder`: (オプション) エンコーダ ONNX モデルファイルのパス (デフォルト: `/tmp/base-encoder.onnx`)
- `decoder`: (オプション) デコーダ ONNX モデルファイルのパス (デフォルト: `/tmp/base-decoder.onnx`)
- `tokens`: (オプション) トークン ONNX モデルファイルのパス (デフォルト: `/tmp/base-tokens.onnx`)

カスタムモデルの例:
```bash
docker run -p 8080:8080 \
  -e api_key="your-translation-api-key" \
  -e encoder="/app/models/custom-encoder.onnx" \
  -e decoder="/app/models/custom-decoder.onnx" \
  -e tokens="/app/models/custom-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## カスタム ONNX モデルのマウント
Docker ボリュームを使用して、独自の ONNX モデルファイルをコンテナにマウントできます:

```bash
docker run -p 8080:8080 \
  -e api_key="your-api-key" \
  -v /path/to/your/models:/app/models \
  -e encoder="/app/models/your-encoder.onnx" \
  -e decoder="/app/models/your-decoder.onnx" \
  -e tokens="/app/models/your-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## ポート設定
- デフォルトの公開ポート: **8080**
- ホストポートのマッピングを調整できます:
  ```bash
  docker run -p 3000:8080 [...] # ホストポート 3000 をコンテナポート 8080 にマッピング
  ```

## プロジェクト構造
- 依存関係管理に Poetry を使用
- ソースコードはコンテナ内の `/app` ディレクトリに配置
- すべての追加依存関係（開発依存関係を含む）を自動的にインストール

## カスタム設定
追加のカスタマイズには:

1. **設定ファイルのマウント**:
   ```bash
   docker run -v /path/to/your/config.yaml:/app/config.yaml [...]
   ```

2. **環境変数の使用**:
   ```bash
   docker run -e api_key="your-key" -e OTHER_VAR="value" [...]
   ```

## 開発用途
コードの変更や開発が必要な場合:

```bash
# ソースコードのクローン
git clone <your-repo>
cd <repo-directory>

# Docker Compose の使用（推奨）
# または、ローカルコードをマウントして docker run を使用
docker run -p 8080:8080 -v $(pwd):/app -e api_key="your-key" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## ヘルスチェック
サーバー起動後、ステータスを確認するには:
```bash
curl http://localhost:8080/health
```

## 注意事項
1. 有効な `api_key` 環境変数を必ず提供してください
2. コンテナは起動時にデフォルトの config.yaml ファイルを自動的に削除します
3. 永続的な設定には、マウント
外部設定ファイル
4. カスタムモデルの場合、ONNXファイルをマウントし、適切な環境変数を設定してください

## サポートとフィードバック
問題が発生した場合やサポートが必要な場合は、プロジェクトリポジトリを通じてIssueを提出するか、メンテナーに連絡してください。