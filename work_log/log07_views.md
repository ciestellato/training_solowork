# 修正ポイント

## GET / POSTの処理をわかりやすく

```
    # POST処理：フォーム送信された場合
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['event'] = selected_event.id  # hiddenで送ったeventを強制セット
        form = EventDayPerformanceForm(post_data)
        form.fields['date'].choices = date_choices  # 日付選択肢を設定

        if form.is_valid():
            # EventDay と Performance を登録
            event_day = EventDay.objects.create(
                event=form.cleaned_data['event'],
                date=form.cleaned_data['date'],
                venue=form.cleaned_data['venue']
            )
            for artist in form.cleaned_data['artists']:
                Performance.objects.create(event_day=event_day, artist=artist, is_confirmed=True)

            # 成功メッセージをセッションに保存してリダイレクト（PRG）
            request.session['message'] = f"{event_day} に {form.cleaned_data['artists'].count()} 組の出演者を登録しました。"
            return redirect(f"{request.path}?event_id={selected_event.id}")

    else:
        # GET処理：フォーム初期表示
        form = EventDayPerformanceForm(initial={'event': selected_event})
        form.fields['date'].choices = date_choices  # 日付選択肢を設定
```

## register_event_day_and_performancesをPRGパターンに対応させた

これでフォーム送信後に更新しても再送信されないようになった。
