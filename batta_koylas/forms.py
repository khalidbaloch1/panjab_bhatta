from django import forms

from batta_koylas.models import (
    Koyla, KoylaLedgerPayment, KoylaLedger
)


class KoylaForm(forms.ModelForm):
    class Meta:
        model = Koyla
        fields = '__all__'


class KoylaLedgerForm(forms.ModelForm):
    class Meta:
        model = KoylaLedger
        fields = '__all__'


class KoylaLedgerPaymentForm(forms.ModelForm):
    class Meta:
        model = KoylaLedgerPayment
        fields = '__all__'
