# i18n Agent Action App コンテナ使用ガイド

## 概要
これはFletフレームワーク上に構築された国際化（i18n）エージェントアプリケーションコンテナで、i18n関連のタスクを管理および処理するためのウェブインターフェースを提供します。

## クイックスタート

### 1. イメージをプルする
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:app
```

### 2. コンテナを実行する
```bash
docker run -d -p 8550:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### 3. アプリケーションにアクセスする
ブラウザを開き、次のURLに移動してください: http://localhost:8550

## 設定オプション

### ポートマッピング
デフォルトポートは8550です。任意のホストポートにマッピングできます:
```bash
docker run -d -p 8080:8550 --name i18n-app ghcr.io/samyuan1990/i18n-agent-action:app
```

### 環境変数
以下の環境変数を設定できます:

- `FLET_SECRET_KEY`: アプリケーションのシークレットキー（デフォルト: 123）
- `FLET_SERVER_PORT`: サーバーポート（デフォルト: 8550）

例:
```bash
docker run -d \
  -p 8550:8550 \
  -e FLET_SECRET_KEY=your-secret-key \
  -e FLET_SERVER_PORT=8550 \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

### データ永続化
データ永続化のために、ボリュームをマウントできます:
```bash
docker run -d \
  -p 8550:8550 \
  -v ./i18n-data:/app/data \
  --name i18n-app \
  ghcr.io/samyuan1990/i18n-agent-action:app
```

## 開発モード

### カスタムイメージをビルドする
コードを変更した場合、イメージをリビルドできます:
```bash
docker build -f Dockerfile_App -t my-i18n-app .
```

### 開発バージョンを実行する
```bash
docker run -d -p 8550:8550 --name my-i18n-app my-i18n-app
```

## 一般的なコマンド

### コンテナログを表示する
```bash
docker logs i18n-app
```

### コンテナシェルにアクセスする
```bash
docker exec -it i18n-app /bin/bash
```

### コンテナを停止する
```bash
docker stop i18n-app
```

### コンテナを再起動する
```bash
docker restart i18n-app
```

### コンテナを削除する
```bash
docker rm i18n-app
```

## トラブルシューティング

1. **ポート競合**: ポート8550が既に使用中の場合は、別のポートを使用してください
2. **コンテナ起動失敗**: `docker logs i18n-app` でログを確認してください
3. **アプリケーションにアクセスできない**: ファイアウォール設定とポートマッピングを確認してください

## サポート

問題がある場合は、プロジェクトのドキュメントを確認するか、GitHubリポジトリにイシューを提出してください。

---

**注記**: このコンテナは開発およびテスト環境のみを対象としています。本番環境で使用する場合は、適切なセキュリティ対策を設定してください。