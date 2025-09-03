## テストアドレス
[Mac ARM テストアドレス](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914330255)  
[Mac x86 テストアドレス](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914407540)  
[Linux テストアドレス](https://github.com/SamYuan1990/i18n-agent-action/actions/runs/17428066641/artifacts/3914313680)

## テスト目的
1. DeepSeekが翻訳でサポートできる言語の数はいくつですか？  
![](./img/screenshort20250903Test001.png)  

2. 現在のシステムプロンプトの堅牢性。  
https://github.com/SamYuan1990/i18n-agent-action/blob/main/Business/translateConfig.py#L67-L89  

3. Fletなどの開発フレームワークのプラットフォーム間（Mac、Linux）での一貫性。個人的には、将来のAIエージェントはさまざまな統合方法をサポートすると考えています。したがって、Fletのようなフレームワークが単一のコードベースからクロスプラットフォームのコンパイルとビルドを可能にし、一貫したユーザーエクスペリエンスを提供できるなら、それは素晴らしい選択肢でしょう。

## テスト手順と範囲

> 私の個人用コンピュータはMac x86なので、それを参考にします。

1. ソフトウェアをダウンロードしてインストールします。  

> 署名に関する信頼の問題が発生する可能性があります。必要に応じて数回試してください。  

2. DeepSeek APIキーを設定します。  
https://api-docs.deepseek.com/zh-cn/ を参照するか、Webプラットフォームで作成してください。  
![](./img/step1.png)  


> もちろん、既存のOpenAI形式の大規模言語モデルを使用してテスト範囲を拡大することも歓迎します。  

3. 大規模言語モデルのアクセス情報を設定して保存します。  
![](./img/step2.png)  

4. 翻訳する内容を入力し、「翻訳」をクリックして結果を待ちます（注：音声入力はデフォルトで有効です）。  
![](./img/step3.png)  

5. オプション機能：予約語。  
ステップ1に戻り、予約語を追加してステップ4を再現します。

## 技術スキルをお持ちで、音声認識を試してみたい場合は、私に連絡してください。現在、技術的な制限により、開発バージョンのみが利用可能です。