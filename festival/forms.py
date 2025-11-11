from django import forms

from .models import Event, EventDay, Artist, Performance, Event

class BulkArtistForm(forms.Form):
    """アーティスト一括登録フォーム"""
    names = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'YOASOBI, Aimer, King Gnu'}),
        label='アーティスト名（カンマ区切り）'
    )

class ArtistForm(forms.ModelForm):
    """アーティスト情報編集フォーム"""
    class Meta:
        model = Artist
        fields = ['name', 'furigana', 'popularity', 'genres', 'spotify_id']
        widgets = {
            'genres': forms.Textarea(attrs={'rows': 2}),
        }

class EventDayPerformanceForm(forms.Form):
    """イベント内容・出演者入力フォーム"""
    event = forms.ModelChoiceField(queryset=Event.objects.all(), label='イベント')
    date = forms.ChoiceField(choices=[], label='開催日')  # 選択肢はJSで動的に生成
    venue = forms.CharField(max_length=255, label='会場')
    artists = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='出演アーティスト'
    )

class ArtistSchedulePasteForm(forms.Form):
    """ツアー日程登録用フォーム"""
    artist = forms.ModelChoiceField(queryset=Artist.objects.all(), label='アーティスト')
    event_name = forms.CharField(label='イベント名')
    raw_text = forms.CharField(
        label='出演日程（コピペ）',
        widget=forms.Textarea(attrs={'rows': 10}),
        help_text='例:\n2025-11-10 Zepp Tokyo\n2025-11-12 名古屋ダイアモンドホール'
    )

class EventForm(forms.ModelForm):
    """イベントの登録・編集フォーム"""
    class Meta:
        model = Event
        fields = ['name', 'event_type', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and start > end:
            raise forms.ValidationError("開始日は終了日より前である必要があります。")