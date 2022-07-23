# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from batta_koylas.models import (
    Koyla, KoylaLedger, KoylaLedgerPayment
)


class KoylaAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta'
    )


class KoylaLedgerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'season', 'transport', 'carriage', 'amount_per_carriage', 'amount', 'date_added'
    )


class KoylaLedgerPaymentAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'amount', 'payment_type', 'payment_date'
    )


admin.site.register(Koyla, KoylaAdmin)
admin.site.register(KoylaLedger, KoylaLedgerAdmin)
admin.site.register(KoylaLedgerPayment, KoylaLedgerPaymentAdmin)
