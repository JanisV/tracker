from django import forms

from .models import Site
from .models import Category


class AuctionForm(forms.Form):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), empty_label=None)
    categories = Category.objects.values_list('id', 'title').distinct()
    iquery_choices = [(cat[0], cat[1]) for cat in categories]
    categories = forms.MultipleChoiceField(choices=iquery_choices, widget=forms.CheckboxSelectMultiple)
    from_num = forms.IntegerField(min_value=1)
    till_num = forms.IntegerField(min_value=1)

    def clean(self):
        cleaned_data = super().clean()
        from_num = cleaned_data.get("from_num")
        till_num = cleaned_data.get("till_num")
        if from_num > till_num:
                raise forms.ValidationError(
                    "From > Till"
                )
