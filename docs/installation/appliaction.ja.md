# デスクトップアプリまたはモバイルアプリとして実行

## サポートプラットフォーム

| macOS (x86) | macOS (arm) | Windows | Linux (x86?) | iOS | Android |
| ----------- | ----------- | ------- | ------------ | --- | ------- |
| ✅      | ✅       | テスト募集 | テスト募集 | テスト募集 | テスト募集 |

## GHAからダウンロード

以下にアクセスしてください
[link](https://github.com/SamYuan1990/i18n-agent-action/actions/workflows/release.yml?query=event%3Aschedule)

最新のビルドを見つける
![](../img/install_step1.png)  

パッケージを見つける
![](../img/install_step2.png)  

## 使用方法

> 私の個人用コンピュータはMac x86なので、それを参考にします。

1. ソフトウェアをダウンロードしてインストールしてください。  

> 署名に関する信頼性の問題に遭遇するかもしれません。必要に応じて数回試してみるか、開発者の場合は `
sudo xattr -d com.apple.quarantine ~/i18n-agent-action.app 
codesign --force --deep --sign - --preserve-metadata=entitlements --options runtime ~/i18n-agent-action.app`
が役立つかもしれません。

2. DeepSeek APIキーを設定してください。  
https://api-docs.deepseek.com/zh-cn/ を参照するか、ウェブプラットフォームで作成してください。  
![](../img/step1.png)  


> もちろん、既存のOpenAI形式の大規模言語モデルを使用してテスト範囲を拡大することも歓迎します。  

3. 大規模言語モデルのアクセス情報を設定して保存してください。  
![](../img/step2.png) 

4. 翻訳する内容を入力し、「翻訳」をクリックして結果を待ちます（注：音声出力はデフォルトで有効です）。  
![](../img/step3.png) 

5. オプション機能: 予約語。  
ステップ1に戻り、予約語を追加してステップ4を再実行してください。