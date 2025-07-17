from django import forms
from .models import Portfolio

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['coin_id', 'amount', 'purchase_price']

    def clean_coin_id(self):
        return self.cleaned_data['coin_id'].lower()