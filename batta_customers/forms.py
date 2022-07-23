from django import forms

from batta_customers.models import (
    Customer, CustomerLedgerPayment, CustomerLedger
)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class CustomerLedgerForm(forms.ModelForm):
    class Meta:
        model = CustomerLedger
        fields = '__all__'


class CustomerLedgerPaymentForm(forms.ModelForm):
    class Meta:
        model = CustomerLedgerPayment
        fields = '__all__'
