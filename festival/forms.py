from django import forms

from .models import Event, EventDay, Artist, Performance

class BulkArtistForm(forms.Form):
    """アーティスト一括登録フォーム"""
    names = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'YOASOBI, Aimer, King Gnu'}),
        label='アーティスト名（カンマ区切り）'
    )

class EventDayPerformanceForm(forms.Form):
    """イベント内容・出演者入力フォーム"""
    event = forms.ModelChoiceField(queryset=Event.objects.all(), label='イベント')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='開催日')
    venue = forms.CharField(max_length=255, label='会場')
    artists = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='出演アーティスト'
    )
