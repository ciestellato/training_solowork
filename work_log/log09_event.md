# イベント詳細

## イベント詳細の編集

`views.py`

```
@staff_member_required
def edit_event_day_performances(request, event_day_id):
    """特定の EventDay に紐づく出演者を編集するビュー"""
    event_day = get_object_or_404(EventDay, pk=event_day_id)
    event = event_day.event
    existing_artists = event_day.performance_set.values_list('artist_id', flat=True)

    if request.method == 'POST':
        form = EventDayPerformanceForm(request.POST)
        form.fields['date'].choices = [(event_day.date.strftime('%Y-%m-%d'), event_day.date.strftime('%Y-%m-%d'))]
        if form.is_valid():
            # 既存の出演者を削除して再登録
            Performance.objects.filter(event_day=event_day).delete()
            for artist in form.cleaned_data['artists']:
                Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)
            request.session['message'] = f"{event_day} の出演者を更新しました。"
            return redirect('festival:event_detail', pk=event.id)
    else:
        form = EventDayPerformanceForm(initial={
            'event': event,
            'date': event_day.date.strftime('%Y-%m-%d'),
            'venue': event_day.venue,
            'artists': existing_artists
        })
        form.fields['date'].choices = [(event_day.date.strftime('%Y-%m-%d'), event_day.date.strftime('%Y-%m-%d'))]

    return render(request, 'edit_event_day.html', {
        'form': form,
        'event_day': event_day,
        'event': event
    })
```

`urls.py`

```
path('event_day/<int:event_day_id>/edit/', views.edit_event_day_performances, name='edit_event_day_performances'),
```

`event_detail.html`

```
{% if request.user.is_staff %}
  <a href="{% url 'festival:edit_event_day_performances' event_day.id %}" class="btn btn-sm btn-outline-secondary">
    出演者を編集
  </a>
{% endif %}
```

`edit_event_day.html`

```
<h2>{{ event.name }} - {{ event_day.date }} の出演者編集</h2>

<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit" class="btn btn-primary">更新</button>
</form>

<a href="{% url 'festival:event_detail' event.id %}" class="btn btn-secondary mt-3">← イベント詳細に戻る</a>
```

### 編集画面で開催日欄が空欄になってしまう

ありがとうございます。`event_data_json` の中身を確認するには、テンプレート内で **JavaScriptの `console.log()` を使う方法が最も簡単で確実**です。

---

## ✅ 方法：ブラウザの開発者ツールで確認する

### 🔧 ステップ 1：テンプレートに `console.log()` を追加

テンプレートの `<script>` 内に以下の1行を追加してください：

```javascript
console.log("event_data_json:", eventData);
```

追加する位置は `eventData` を定義した直後がベストです：

```javascript
const eventData = JSON.parse('{{ event_data_json|escapejs }}' || '{}');
console.log("event_data_json:", eventData);  // ← ここ！
```

---

### 🔧 ステップ 2：ブラウザで確認

1. 編集画面を開いた状態で
2. ブラウザの「開発者ツール」（DevTools）を開きます  
   - Windows: `F12` または `Ctrl+Shift+I`  
   - Mac: `Cmd+Opt+I`
3. 「Console」タブを選択
4. `event_data_json:` に続いて表示されるオブジェクトを確認

---

## ✅ 期待される構造（例）

```json
{
  "3": {
    "start": "2025-11-08",
    "end": "2025-11-10"
  },
  "4": {
    "start": "2025-12-01",
    "end": "2025-12-03"
  }
}
```

このように、イベントIDをキーとして、`start` と `end` の日付が含まれているはずです。

---

## ✅ よくある問題

- `event_data_json` が空 (`{}`) → JSで選択肢が生成されない
- `selectedEventId` が `eventData` に存在しない → 該当イベントの日付が生成されない
- `event_day.date` が `start`〜`end` の範囲外 → 初期選択されない

---

## ✅ 次のステップ

`console.log()` で中身を確認したら、以下をチェックしてください：

- `eventData[selectedEventId]` が存在するか
- `event_day.date` がその `start`〜`end` の範囲に含まれているか

もし `event_data_json` が空だった場合は、ビュー側で `event_data_json = json.dumps(...)` の生成処理を確認する必要があります。必要ならそちらも一緒に見ていきましょう！
