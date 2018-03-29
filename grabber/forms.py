from django import forms

from .models import Auction
from .models import Category
from .models import Site


class AuctionForm(forms.Form):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), empty_label=None)
    from_num = forms.IntegerField(min_value=1)
    till_num = forms.IntegerField(min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories_values = Category.objects.values_list('id', 'title')
        iquery_choices = [(cat[0], cat[1]) for cat in categories_values]
        self.fields['categories'] = forms.MultipleChoiceField(
            choices=iquery_choices, widget=forms.CheckboxSelectMultiple)

        num = self.default_num()
        self.fields['from_num'].initial = num
        self.fields['till_num'].initial = num

    def default_num(self):
        if Auction.objects.count():
            return Auction.objects.latest().number + 1
        else:
            return 1

    def clean(self):
        cleaned_data = super().clean()
        from_num = cleaned_data.get("from_num")
        till_num = cleaned_data.get("till_num")
        if from_num > till_num:
                raise forms.ValidationError(
                    "From > Till"
                )
