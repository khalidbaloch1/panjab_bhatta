from django import forms

from batta_account.models import (
    Account, IncomeLedger, OwnerLedger
)


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'


class IncomeLedgerForm(forms.ModelForm):
    class Meta:
        model = IncomeLedger
        fields = '__all__'


class OwnerLedgerForm(forms.ModelForm):
    class Meta:
        model = OwnerLedger
        fields = '__all__'
