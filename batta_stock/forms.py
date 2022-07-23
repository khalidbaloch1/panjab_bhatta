from django import forms

from batta_stock.models import Stock, StockIn, StockOut, PurchasedStock


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = "__all__"


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = "__all__"


class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockOut
        fields = "__all__"


class PurchasedItemForm(forms.ModelForm):
    class Meta:
        model = PurchasedStock
        fields = "__all__"
