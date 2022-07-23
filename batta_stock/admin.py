# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from batta_stock.models import StockOut, StockIn, Stock, PurchasedStock


class StockAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'bhatta', 'awal_count', 'duyam_count', 'rora_count')
    search_fields = ('item_name', 'bhatta__name', 'bhatta__code')
    raw_id_fields = ('bhatta',)

    @staticmethod
    def bhatta(obj):
        return obj.bhatta.name if obj.bhatta else ''


class StockInAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta', 'stock_in', 'amount_per_item',
        'total_amount', 'added_date'
    )
    search_fields = ('stock__item_name', 'stock__bhatta__name')
    list_filter = ('season',)

    @staticmethod
    def bhatta(obj):
        return obj.stock.bhatta.name if obj.stock else ''


class StockOutAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'season', 'bhatta', 'stock_out',
        'details'
    )
    search_fields = (
        'stock__item_name', 'stock__bhatta__name'
    )

    @staticmethod
    def bhatta(obj):
        return obj.stock.bhatta.name if obj.stock else ''


class PurchasedStockAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'season', 'bhatta', 'invoice', 'quantity',
        'price', 'total_amount', 'added_date'
    )
    raw_id_fields = ('stock',)
    search_fields = ('stock__item_name', 'stock__item_name', 'stock__bhatta__name')

    @staticmethod
    def bhatta(obj):
        return obj.stock.bhatta.name if obj.stock else ''


admin.site.register(Stock, StockAdmin)
admin.site.register(StockIn, StockInAdmin)
admin.site.register(StockOut, StockOutAdmin)
admin.site.register(PurchasedStock, PurchasedStockAdmin)
