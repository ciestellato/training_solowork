# 配色変更

**「Blast the Music」カラーをベースに、ページ全体の配色を調整するには、staticフォルダに custom.css を作成して、主要色を反映させるのが最適です。**  
Bootstrapの構造を活かしつつ、以下のように色を割り当てることで、フェスらしい鮮やかで統一感のあるUIが実現できます。

---

## 🎨 カラーパレット（Blast the Music）

| 色名               | HEXコード   | 用途の提案 |
|--------------------|-------------|------------|
| Cadmium Violet     | `#832C99`   | ナビバー背景、ボタン |
| Medium Sea Green   | `#38BD67`   | 成功系メッセージ、チェック済み表示 |
| Champagne          | `#F6E2CB`   | 背景色、カード内背景 |
| Spanish Crimson    | `#E9184E`   | アクションボタン、リンクホバー |
| American Purple    | `#3F1E59`   | フッター、タイトル文字色 |

出典: 

---

## 🛠️ custom.css の例

```css
body {
    background-color: #F6E2CB; /* Champagne */
    color: #3F1E59; /* American Purple */
    font-family: 'Helvetica Neue', sans-serif;
}

.navbar {
    background-color: #832C99; /* Cadmium Violet */
}

.navbar-brand, .nav-link {
    color: #F6E2CB !important;
}

.nav-link:hover {
    color: #E9184E !important; /* Spanish Crimson */
}

.btn-primary {
    background-color: #E9184E;
    border-color: #E9184E;
}

.btn-primary:hover {
    background-color: #832C99;
    border-color: #832C99;
}

.card {
    background-color: #F6E2CB;
    border: none;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

footer {
    background-color: #3F1E59;
    color: #F6E2CB;
    padding: 10px;
    text-align: center;
}
```

---

## 📦 static フォルダに配置

1. `static/css/custom.css` を作成
2. `base.html` の `<head>` に以下を追加：

```html
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/custom.css' %}">
{% endblock %}
```

---

## ✨ 補足アイデア

- ステージカラーを `Stage.color_code` に基づいてインラインスタイルで反映する場合、テンプレート内で `style="background-color: {{ stage.color_code }};"` を使うと柔軟です。
- Bootstrapの `btn`, `card`, `alert` などの構造を活かしつつ、色だけを上書きすることで、保守性と一貫性を両立できます。

---

このエラーの原因は明確で、テンプレート内で `{% static '...' %}` を使っているにもかかわらず、**`{% load static %}` をテンプレートの先頭で読み込んでいない**ことが原因です。

---

## ✅ 解決方法

テンプレートファイル（例：`base.html`）の冒頭に、以下の1行を追加してください：

```django
{% load static %}
```

### 修正後の例（`base.html`）

```html
{% load static %}
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}音楽フェスティバル管理{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    {% block extra_css %}
        <link rel="stylesheet" href="{% static 'css/color.css' %}">
    {% endblock %}
    <style>
        body {
            padding-top: 50px;
        }
    </style>
</head>
<body>
    ...
```

---

## 🔍 なぜ必要？

- `{% static %}` は Django のテンプレートタグで、静的ファイルのURLを解決するために使います。
- これを使うには、テンプレート内で `{% load static %}` を宣言して、テンプレートタグを有効にする必要があります。
- これを忘れると、Djangoは `{% static %}` を「知らないタグ」として扱い、`TemplateSyntaxError` を出します。

---

## ✅ 補足チェックポイント

- `color.css` のパスが `static/css/color.css` であることを再確認
- 開発環境であれば、`python manage.py runserver` で `STATICFILES_DIRS` の設定が効いているか確認
- ブラウザのキャッシュをクリアして、CSSの変更が反映されているか確認

---

これでエラーは解消されるはずです！  
もし他のテンプレートでも `{% static %}` を使っている場合は、それぞれのテンプレートにも `{% load static %}` を忘れずに追加してくださいね。

次は `color.css` の中身を一緒に整えて、ページ全体の雰囲気をフェスっぽく仕上げていきましょうか？
