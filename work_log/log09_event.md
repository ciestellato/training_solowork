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