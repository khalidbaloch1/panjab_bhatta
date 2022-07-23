from django import forms

from other_expense.models import (
    OtherExpense, DieselLedger, MittiLedger
)


class OtherExpenseForm(forms.ModelForm):
    class Meta:
        model = OtherExpense
        fields = '__all__'


class DieselLedgerForm(forms.ModelForm):
    class Meta:
        model = DieselLedger
        fields = '__all__'


class MittiLedgerForm(forms.ModelForm):
    class Meta:
        model = MittiLedger
        fields = '__all__'
