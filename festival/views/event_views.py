from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from ..models import Event, EventDay, Performance
from ..forms import EventForm

def event_list(request):
    """イベントの一覧表示ページ"""
    events = Event.objects.all().order_by('start_date')
    return render(request, 'event_list.html', {'events': events})

def fes_event_list(request):
    """フェスイベント一覧ページ"""
    events = Event.objects.filter(event_type='FES').order_by('start_date')
    return render(request, 'event_list_fes.html', {'events': events})

def other_event_list(request):
    """フェス以外のイベント一覧ページ"""
    events = Event.objects.exclude(event_type='FES').order_by('start_date')
    return render(request, 'event_list_other.html', {'events': events})

def event_detail(request, pk):
    """イベント詳細ページ"""
    event = get_object_or_404(Event, pk=pk)
    event_days = event.eventday_set.all().order_by('date')
    day_performances = [
        (day, day.performance_set.select_related('artist').order_by('artist__name'))
        for day in event_days
    ]
    return render(request, 'event_detail.html', {
        'event': event,
        'day_performances': day_performances
    })

@staff_member_required
def create_event(request):
    """イベント登録ビュー"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('festival:fes_event_list')
    else:
        form = EventForm()
    return render(request, 'event_form.html', {'form': form, 'mode': 'create'})

@staff_member_required
def edit_event(request, event_id):
    """イベント編集ビュー"""
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('festival:event_detail', event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'event_form.html', {'form': form, 'mode': 'edit', 'event': event})

