# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from other_expense.models import (
    OtherExpense, DieselLedger, MittiLedger
)


class OtherExpenseAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta'
    )


class DieselLedgerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'season', 'amount_per_ltr', 'ltr', 'total_amount', 'diesel_debit_amount',
        'diesel_details', 'diesel_date'
    )


class MittiLedgerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'season', 'amount_per_load', 'total_load', 'total_amount', 'mitti_debit_amount',
        'mitti_details', 'mitti_date'
    )


admin.site.register(OtherExpense, OtherExpenseAdmin)
admin.site.register(DieselLedger, DieselLedgerAdmin)
admin.site.register(MittiLedger, MittiLedgerAdmin)
