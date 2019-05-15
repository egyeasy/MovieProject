from dal import autocomplete
from django import forms
from .models import SearchQuery


class SearchForm(forms.ModelForm):
    class Meta:
        model = SearchQuery
        fields = ('__all__')
        widgets = {
            'search_query': autocomplete.ModelSelect2(url='watch:movie-autocomplete'),
        }