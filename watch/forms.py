from dal import autocomplete
from django import forms
from .models import QueryModel, Comment, Movie


class SearchForm(forms.ModelForm):
    content = forms.ModelChoiceField(
        Movie.objects.all(),
        widget=autocomplete.ModelSelect2(url='watch:movie-autocomplete')
        )
        
    class Meta:
        model = QueryModel
        fields = ('__all__')
    # 이전 버전
    # class Meta:
    #     model = QueryModel
    #     fields = ('__all__')
    #     widgets = {
    #         'content': autocomplete.ModelSelect2(url='watch:movie-autocomplete'),
    #     }
        
    #     birth_country = forms.ModelChoiceField(
    #     queryset=Country.objects.all(),
    #     widget=autocomplete.ModelSelect2(url='country-autocomplete')
    # )

    # class Meta:
    #     model = Person
    #     fields = ('__all__')
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', 'score')