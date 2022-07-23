# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Stock(models.Model):
    item_name = models.CharField(max_length=200)
    bhatta = models.ForeignKey(
        'common.Bhatta', related_name='stock_bhatta',
        blank=True, null=True
    )
    b_count = models.BooleanField(default=False)
    awal_count = models.BooleanField(default=False)
    duyam_count = models.BooleanField(default=False)
    rora_count = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s (%s)' % (self.item_name, self.bhatta)

    def available_stock(self, season=None):
        all_stocks = self.stock_stockin.all()
        if season:
            all_stocks = all_stocks.filter(season__season_year=season)
        try:
            all_stocks = all_stocks.aggregate(
                stock_in_quantity=Sum('stock_in'))
            all_stocks = all_stocks.get('stock_in_quantity') or 0
        except:
            all_stocks = 0

        all_out = self.stock_stockout.all()
        if season:
            all_out = all_out.filter(season__season_year=season)
        try:
            all_out = all_out.aggregate(
                stock_out_quantity=Sum('stock_out'))
            all_out = all_out.get('stock_out_quantity') or 0
        except:
            all_out = 0

        return all_stocks - all_out

    def total_stock(self, season=None):
        all_stocks = self.stock_stockin.all()
        if season:
            all_stocks = all_stocks.filter(season__season_year=season)
        try:
            all_stocks = all_stocks.aggregate(
                stock_in_quantity=Sum('stock_in'))
            all_stocks = all_stocks.get('stock_in_quantity') or 0
        except:
            all_stocks = 0

        return all_stocks

    def purchased_stock(self, season=None):
        all_out = self.stock_stockout.all()
        if season:
            all_out = all_out.filter(season__season_year=season)
        try:
            all_out = all_out.aggregate(
                stock_out_quantity=Sum('stock_out'))
            all_out = all_out.get('stock_out_quantity') or 0
        except:
            all_out = 0

        return all_out

    def purchased_stock_amount(self, season=None):
        purchased_stocks = PurchasedStock.objects.filter(stock=self)
        if season:
            purchased_stocks = purchased_stocks.filter(
                season__season_year=season)
        try:
            amount = purchased_stocks.aggregate(Sum('total_amount'))
            amount = float(amount.get('total_amount__sum'))
        except:
            amount = 0

        return amount


class StockIn(models.Model):
    season = models.ForeignKey(
        'common.Season', related_name='season_stock_in',
        blank=True, null=True
    )
    stock = models.ForeignKey(
        Stock, related_name='stock_stockin',
        blank=True, null=True, on_delete=models.SET_NULL
    )
    stock_in = models.CharField(max_length=100, blank=True, null=True)
    amount_per_item = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    total_amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    details = models.TextField(max_length=500, blank=True, null=True)
    added_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.stock.item_name if self.stock else ''


class StockOut(models.Model):
    season = models.ForeignKey(
        'common.Season', related_name='season_stock_out',
        blank=True, null=True
    )
    stock = models.ForeignKey(
        Stock, related_name='stock_stockout',
        blank=True, null=True, on_delete=models.SET_NULL
    )
    stock_out = models.CharField(max_length=100, blank=True, null=True)
    amount_per_item = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    total_amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    details = models.TextField(max_length=500, blank=True, null=True)
    added_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.stock.item_name if self.stock else ''


class PurchasedStock(models.Model):
    stock = models.ForeignKey(
        Stock, related_name='stock_purchased',
    )
    invoice = models.ForeignKey(
        'batta_sales.Invoice', related_name='stock_invoice',
        blank=True, null=True
    )
    season = models.ForeignKey(
        'common.Season', related_name='purchased_season',
        blank=True, null=True
    )
    quantity = models.DecimalField(
        max_digits=100, decimal_places=5, default=1, blank=True, null=True
    )
    price = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    total_amount = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    added_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return '%s (%s)' % (self.stock.item_name, self.id)
