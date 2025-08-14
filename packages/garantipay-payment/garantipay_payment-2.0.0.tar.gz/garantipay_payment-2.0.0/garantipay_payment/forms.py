from django import forms
from django.forms import formset_factory


class BasketItemForm(forms.Form):
    amount = forms.DecimalField(max_digits=11, decimal_places=2)
    product_kind = forms.CharField(max_length=16)


class HashForm(forms.Form):
    hash = forms.CharField(max_length=256)
    salt = forms.CharField(max_length=16)
    platform = forms.CharField(max_length=16)


BasketItemFormSet = formset_factory(BasketItemForm, extra=0)
