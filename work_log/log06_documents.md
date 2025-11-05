# ドキュメント類の作成

## README.mdの作成

現時点での成果をCopilotへ伝えて、READMEを作成した

## requirements.txtの作成

`requirements.txt` を自動生成したい場合は、以下のコマンドが便利です：

```bash
pip freeze > requirements.txt
```

これで現在の環境にインストールされているパッケージ一覧を保存できます。  
他にもセットアップスクリプトや依存管理を整えたい場合は、`pip-tools` や `Poetry` の導入も検討できますよ！

以下のように `requirements.txt` を整えておくと、他の開発者やチームメンバーが環境構築しやすくなります ✅

---

## 📦 整理済み `requirements.txt`

```txt
# Webフレームワーク
Django==5.2.7
asgiref==3.10.0
sqlparse==0.5.3
tzdata==2025.2

# API連携・通信
requests==2.32.5
urllib3==2.5.0
certifi==2025.10.5
charset-normalizer==3.4.4
idna==3.11

# 環境変数管理
python-dotenv==1.2.1
```

---

## 💡 補足

- 上記は `pip freeze` による自動生成結果を整理したものです。コメントを加えることで、依存関係の目的が明確になります。
- 今後、Bootstrapやテストツール（`pytest`, `django-debug-toolbar` など）を導入する場合は、ここに追記していくと良いです。
- `requirements.txt` を更新したら、GitHubにコミットしておくと環境の再現性が保てます。

---

ドキュメント整備はプロジェクトの理解・引き継ぎ・外部共有にとって非常に重要です。以下のように、整備すべきドキュメントを目的別に整理しました ✍️

---

## 📚 ドキュメント整備ガイド

### 1. `README.md`（✅ 完了済み）
- プロジェクト概要、技術構成、セットアップ手順、機能説明などを網羅
- 今後は英語版やスクリーンショットの追加も検討可能

---

### 2. `.env.example`
目的：環境変数のテンプレートを共有  
内容例：

```env
# Spotify API credentials
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# Django secret key
DJANGO_SECRET_KEY=your_django_secret_key_here

# その他必要な環境変数があれば追加
```

---

### 3. `docs/` フォルダの新設
目的：設計資料や仕様書を整理  
おすすめファイル：

| ファイル名 | 内容 |
|------------|------|
| `ER_diagram.png` | モデル設計のER図（Event, Artist, Performanceなど） |
| `screen_flow.md` | 画面遷移図・ページ構成の説明 |
| `api_spec.md` | Spotify API連携の仕様と使用エンドポイント |
| `feature_plan.md` | 実装予定の機能一覧と優先度 |
| `dev_notes.md` | 開発中のメモや注意点（例：バリデーションの仕様） |

---

### 4. `CONTRIBUTING.md`（任意）
目的：外部コラボレーター向けの開発ルール  
内容例：
- ブランチ運用ルール（例：`main`, `dev`, `feature/*`）
- コミットメッセージの書き方
- Issue・Pull Requestのテンプレート

---

### 5. `CHANGELOG.md`（任意）
目的：バージョンごとの変更履歴を記録  
内容例：

```md
## [0.1.0] - 2025-11-05
### Added
- アーティスト一覧・詳細ページ
- Spotify API連携による一括登録機能
- イベント登録フォーム（JSによる日付選択）

### Changed
- 管理画面の表示項目をカスタマイズ
```

---

## ✅ 次のアクション提案

1. `.env.example` を作成して `.env` を除外する `.gitignore` を確認
2. `docs/` フォルダを作成して ER図や画面構成を追加
3. `feature_plan.md` に今後の機能アイデアを整理
4. 必要に応じて `CONTRIBUTING.md` や `CHANGELOG.md` を追加

---

## screen_flow.mdの作成

[screen_flow.md](../docs/screen_flow.md)

## api_spec.mdの作成

[api_spec.md](../docs/api_spec.md)

## feature_plan.mdの作成

[feature_plan.md](../docs/feature_plan.md)

