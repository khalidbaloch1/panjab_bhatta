from django import forms

from .models import (
    Staff, StaffLedger, StaffLedgerPayment, StaffAdvanceCredit, StaffOtherCredit, StaffOtherDebit
)


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'


class StaffLedgerForm(forms.ModelForm):
    class Meta:
        model = StaffLedger
        fields = '__all__'


class StaffLedgerPaymentForm(forms.ModelForm):
    class Meta:
        model = StaffLedgerPayment
        fields = '__all__'


class StaffAdvanceCreditForm(forms.ModelForm):
    class Meta:
        model = StaffAdvanceCredit
        fields = '__all__'


class StaffOtherCreditForm(forms.ModelForm):
    class Meta:
        model = StaffOtherCredit
        fields = '__all__'


class StaffOtherDebitForm(forms.ModelForm):
    class Meta:
        model = StaffOtherDebit
        fields = '__all__'
