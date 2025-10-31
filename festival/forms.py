from django import forms

class BulkArtistForm(forms.Form):
    """アーティスト一括登録フォーム"""
    names = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'YOASOBI, Aimer, King Gnu'}),
        label='アーティスト名（カンマ区切り）'
    )