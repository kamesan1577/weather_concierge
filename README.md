# Weather Concierge
Weather Conciergeは、AI駆動の分析を使用して天気情報と推奨事項を提供するFastAPIベースのアプリケーションです。

## 前提条件

Docker  
Docker Compose  
Messaging APIが使えるLINE BOTのアカウント([LINE Developers](https://developers.line.biz/console/)から登録)  
ngrok(ローカルでデバッグしたい場合)  
## 環境セットアップ

1. リポジトリをクローンします：
```bash
git clone https://github.com/kamesan1577/weather_concierge.git
cd weather_concierge
```

2. ルートディレクトリに.envファイルを作成します：
```bash
cp .env.sample .env
```

3. .envファイルを編集し、必要な環境変数を設定します：
```
CHANNEL_ACCESS_TOKEN="LINEのチャンネルアクセストークン"
CHANNEL_SECRET="LINEのチャンネルシークレット"
QDRANT_HOST="http://qdrant:6333"
OPENAI_API_KEY="OpenAIのAPIキー"
OPENAI_API_BASE="https://api.openai.iniad.org/api/v1"
```


4. アプリケーションの実行

Dockerコンテナをビルドして起動します：
```bash
docker-compose up --build
```
FastAPIアプリケーションは http://localhost:8000 で利用可能になります。
アプリケーションを停止するには、docker-composeを実行しているターミナルでCtrl+Cを押すか、以下のコマンドを実行します：
```bash
docker-compose down
```

5. ngrokを使ったデバッグ  
ngrokを使ってLINEのサーバーとアプリの通信ができるようにします：
```bash
ngrok http 8000
```
実行するとフォワーディングされたURLがターミナルに表示されるので、  
LINE Developersのコンソールのプロバイダー→{作成したチャネル}→Messaging API設定→Webhook設定→Webhook URLに
```
https://表示されたURL/callback
```
と入力します。


