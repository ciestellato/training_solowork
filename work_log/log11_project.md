Spotifyの仕様変更に柔軟に対応し、プレイリスト作成機能にフォーカスを移すのはとても良い判断です。以下に、**2025年11月12日（水）〜11月21日（金）**の新しいスケジュール表を「段階的な開発ステップ」に沿ってご提案します。

---

## 🗓️ プレイリスト作成機能に向けた開発スケジュール（2025年11月12日〜11月21日）

| 日付       | タスク内容 | 使用技術・ファイル | 備考 |
|------------|------------|---------------------|------|
| **11/12 (水)** | 🔍 要件定義・画面設計 | `feature_plan.md`, `screen_flow.md` | プレイリスト作成の流れを明確化（選択→生成→表示） |
| **11/13 (木)** | 🎨 UIモック作成・テンプレート設計 | `playlist_create.html`, Bootstrap | 出演者選択画面・生成ボタン・結果表示エリア |
| **11/14 (金)** | 🧠 プレイリスト生成ロジック設計 | `playlist.py`（新規） | Spotify APIの `/tracks` or `/search` を活用 |
| **11/17 (月)** | 🛠️ プレイリスト作成ビュー実装 | `views.py`, `playlist.py` | 選択されたアーティストから曲を取得し、リスト生成 |
| **11/18 (火)** | 🧪 テンプレート連携・動作確認 | `playlist_create.html`, `urls.py` | アーティスト選択→プレイリスト表示までの一連の流れ |
| **11/19 (水)** | 🎯 UI改善・検索バー・選択補助 | JavaScript, CSS | アーティスト検索・チェックボックス・選択数表示など |
| **11/20 (木)** | 🧪 テスト・バグ修正 | `test_views.py`, `test_playlist.py` | Spotify APIのエラー処理・選択漏れ対応など |
| **11/21 (金)** | 📦 最終調整・ドキュメント更新・発表準備 | `README.md`, `docs/playlist_spec.md` | スクリーンショット・デモ・スライド作成 |

---

## 🔮 補足：将来的な拡張に向けて

- **ログイン機能**：`django.contrib.auth` によるユーザー管理
- **お気に入りアーティスト保存**：`UserProfile` モデル＋`ManyToManyField`
- **個別プレイリスト生成**：ユーザーごとの選択状態をセッションまたはDBに保存

---

このスケジュールであれば、**11/18までに基本機能を完成させ、残り3日でUI改善・テスト・発表準備に集中**できます。必要であれば、Spotify APIのプレイリスト生成に関する仕様確認や、テンプレート構成の提案もできますよ。

次は、画面設計やプレイリスト生成ロジックの詳細を一緒に詰めていきましょうか？
ありがとうございます！イベント一覧のテンプレートがとても丁寧に作られていて、Bootstrapによる整ったUIがすでに活用されていますね。このスタイルを踏襲しつつ、**プレイリスト作成画面の設計**を以下のように提案します。

---

## 🎨 プレイリスト作成画面の構成案（`playlist_create.html`）

### 🧭 画面の目的
- ユーザーがイベント日程を選択し、出演アーティストをチェックボックスで選択
- 「プレイリストを作成」ボタンでSpotify APIから代表曲を取得
- 結果を画面下部に表示（曲名・アーティスト名・Spotifyリンク）

---

### 🖼️ UI構成（Bootstrapベース）

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>プレイリスト作成</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-4">
    <h1>🎧 プレイリスト作成</h1>

    <form method="POST">
        {% csrf_token %}

        <!-- イベント日程選択 -->
        <div class="mb-3">
            <label for="event_day" class="form-label">イベント日程を選択</label>
            <select name="event_day" id="event_day" class="form-select">
                {% for day in event_days %}
                    <option value="{{ day.id }}">{{ day.date }} @ {{ day.venue }}</option>
                {% endfor %}
            </select>
        </div>

        <!-- 出演アーティスト選択 -->
        <div class="mb-3">
            <label class="form-label">出演アーティストを選択</label>
            <input type="text" class="form-control mb-2" placeholder="アーティスト名で絞り込み" id="artistSearch">
            <div class="border p-3" style="max-height: 300px; overflow-y: scroll;">
                {% for artist in artists %}
                    <div class="form-check">
                        <input class="form-check-input artist-checkbox" type="checkbox" name="artists" value="{{ artist.id }}" id="artist{{ artist.id }}">
                        <label class="form-check-label" for="artist{{ artist.id }}">{{ artist.name }}（{{ artist.furigana }}）</label>
                    </div>
                {% endfor %}
            </div>
        </div>

        <!-- 作成ボタン -->
        <button type="submit" class="btn btn-primary">プレイリストを作成する</button>
    </form>

    <!-- 結果表示 -->
    {% if playlist %}
        <hr>
        <h2 class="mt-4">🎶 プレイリスト</h2>
        <ul class="list-group">
            {% for track in playlist %}
                <li class="list-group-item">
                    {{ track.name }} - {{ track.artist }}
                    <a href="{{ track.spotify_url }}" target="_blank" class="btn btn-sm btn-outline-success float-end">Spotifyで聴く</a>
                </li>
            {% endfor %}
        </ul>
    {% endif %}

    <a href="{% url 'festival:event_list' %}" class="btn btn-secondary mt-4">イベント一覧へ戻る</a>

    <!-- JS: アーティスト検索フィルター -->
    <script>
        document.getElementById('artistSearch').addEventListener('input', function () {
            const keyword = this.value.toLowerCase();
            document.querySelectorAll('.artist-checkbox').forEach(cb => {
                const label = cb.nextElementSibling.textContent.toLowerCase();
                cb.parentElement.style.display = label.includes(keyword) ? 'block' : 'none';
            });
        });
    </script>
</body>
</html>
```

---

## ✅ 補足ポイント

- `event_days` と `artists` はビュー側で渡す必要があります（`context`に含める）
- `playlist` はプレイリスト生成後に渡される曲情報のリスト（曲名・アーティスト名・Spotify URL）
- JavaScriptによる検索バーは、リアルタイムでチェックボックスの表示を絞り込みます

---

このテンプレートをベースに、次はビュー関数とSpotify API連携のロジック設計に進むとスムーズです。必要なら、フォームクラスやユーティリティ関数の設計も一緒に進められますよ。どこから着手しましょう？
