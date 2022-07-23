# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from batta_expense.models import (
    SeasonalExpenditure, SeasonalIncome, ExpenditureAmount
)


class ExpenditureAmountAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'amount', 'details', 'added_date'
    )


admin.site.register(SeasonalExpenditure)
admin.site.register(SeasonalIncome)
admin.site.register(ExpenditureAmount, ExpenditureAmountAdmin)
