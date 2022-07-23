# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from batta_sales.models import Invoice
from batta_stock.models import StockOut


class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 'bhatta', 'season', 'challan_no', 'transport',
        'total_quantity', 'sub_total', 'paid_amount', 'remaining_payment', 'invoice_date'
    )
    list_filter = ('season',)

    @staticmethod
    def customer(obj):
        return obj.customer.name if obj.customer else ''

    @staticmethod
    def bhatta(obj):
        return obj.bhatta.name if obj.bhatta else ''

    raw_id_fields = ('bhatta', 'customer',)
    search_fields = ('challan_no', 'bhatta__name', 'customer__name',)


admin.site.register(Invoice, InvoiceAdmin)
