from __future__ import unicode_literals
from django.contrib import admin

from batta_account.models import (
    Account, IncomeLedger
)


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta'
    )
    list_filter = ('account_type',)


class IncomeLedgerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'season', 'income_credit_amount', 'income_debit_amount',
        'income_details', 'income_date'
    )
    list_filter = ('income_payment_type', 'season',)


admin.site.register(Account, AccountAdmin)
admin.site.register(IncomeLedger, IncomeLedgerAdmin)
