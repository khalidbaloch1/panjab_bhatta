# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from batta_customers.models import (
    Customer, CustomerLedger, CustomerLedgerPayment
)


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta', 'mobile_no', 'address', 'customer_type', 'khata_count', 'advance_count', 'deactivate'
    )
    search_fields = (
        'bhatta__name', 'bhatta__code', 'name', 'mobile_no'
    )
    list_filter = ('customer_type', 'khata_count', 'advance_count', 'deactivate',)

    @staticmethod
    def bhatta(obj):
        return obj.bhatta.name if obj.bhatta else ''


class CustomerLedgerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta', 'amount', 'details', 'date_added', 'ledger_type'
    )
    search_fields = (
        'customer__name', 'customer__mobile_no', 'customer__bhatta__name'
    )
    raw_id_fields = (
        'customer',
    )

    @staticmethod
    def bhatta(obj):
        return obj.customer.bhatta.name


class CustomerLedgerPaymentAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta', 'amount', 'payment_type', 'payment_date'
    )
    search_fields = (
        'customer__name', 'customer__mobile_no', 'customer__bhatta__name'
    )
    raw_id_fields = (
        'customer',
    )

    @staticmethod
    def bhatta(obj):
        return obj.customer.bhatta.name


admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerLedger, CustomerLedgerAdmin)
admin.site.register(CustomerLedgerPayment, CustomerLedgerPaymentAdmin)
