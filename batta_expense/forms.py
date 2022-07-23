from django import forms

from batta_expense.models import (
    CoalExpense, SeasonalExpenditure, SeasonalIncome, ExpenditureAmount, SeasonalStock
)


class CoalExpenseForm(forms.ModelForm):
    class Meta:
        model = CoalExpense
        fields = '__all__'


class SeasonalExpenditureForm(forms.ModelForm):
    class Meta:
        model = SeasonalExpenditure
        fields = '__all__'


class SeasonalIncomeForm(forms.ModelForm):
    class Meta:
        model = SeasonalIncome
        fields = '__all__'


class ExpenditureAmountForm(forms.ModelForm):
    class Meta:
        model = ExpenditureAmount
        fields = '__all__'


class SeasonalStockForm(forms.ModelForm):
    class Meta:
        model = SeasonalStock
        fields = '__all__'
