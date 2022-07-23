from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.db.models import Sum

from common.models import Bhatta, Season


class CoalExpense(models.Model):
    owner = models.CharField(
        max_length=200
    )
    city = models.CharField(
        max_length=200, blank=True, null=True
    )
    bhatta = models.ForeignKey(
        'common.Bhatta', related_name='bhatta_expense',
        blank=True, null=True
    )
    season = models.ForeignKey(
        'common.Season', related_name='season_expense',
        blank=True, null=True
    )
    transport = models.CharField(
        max_length=50, blank=True, null=True
    )
    carriage = models.DecimalField(
        max_digits=100, decimal_places=3, default=0, blank=True, null=True
    )
    amount_per_carriage = models.DecimalField(
        max_digits=65, decimal_places=3, default=0, blank=True, null=True
    )
    amount = models.DecimalField(
        max_digits=100, decimal_places=3, default=0, blank=True, null=True
    )
    total_amount = models.DecimalField(
        max_digits=100, decimal_places=3, default=0, blank=True, null=True
    )
    total_payment = models.DecimalField(
        max_digits=100, decimal_places=3, default=0, blank=True, null=True
    )
    received_amount = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    added_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.owner


class SeasonalExpenditure(models.Model):
    expense_name = models.CharField(max_length=200)
    expense_amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    expense_item_quantities = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    bhatta = models.ForeignKey(
        'common.Bhatta', related_name='bhatta_expenditures',
        blank=True, null=True
    )
    season = models.ForeignKey(
        'common.Season', related_name='season_expenditure',
        blank=True, null=True
    )

    def __unicode__(self):
        return self.expense_name

    def total_expense(self):
        expense_amount = self.seasonal_expense.all()
        if expense_amount.exists():
            amount = expense_amount.aggregate(Sum('amount'))
            amount = amount.get('amount__sum')
        else:
            amount = 0

        return amount


class ExpenditureAmount(models.Model):
    expense = models.ForeignKey(
        SeasonalExpenditure, related_name='seasonal_expense',
        blank=True, null=True
    )
    amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    item_quantities = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    details = models.TextField(
        max_length=500, blank=True, null=True
    )
    added_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.expense.expense_name if self.expense else ''


class SeasonalIncome(models.Model):
    INSIDE = 'Inside'
    OUTSIDE = 'Outside'

    AVAILABILITY_TYPES = (
        (INSIDE, 'Inside'),
        (OUTSIDE, 'Outside'),
    )

    stock = models.ForeignKey('batta_stock.Stock', related_name='income_stock', blank=True, null=True)
    availability_type = models.CharField(
        choices=AVAILABILITY_TYPES, default=INSIDE,
        blank=True, null=True, max_length=100
    )
    stock_quantity = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True,
        help_text='should be filled automatically if '
                  'availability type is outside'
    )
    estimate_price = models.DecimalField(max_digits=100, decimal_places=2, default=0, blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True,
        help_text='Multiplication of stock quantity and estimate price'
    )
    bhatta = models.ForeignKey('common.Bhatta', related_name='bhatta_income', blank=True, null=True)
    season = models.ForeignKey('common.Season', related_name='season_income', blank=True, null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.stock.item_name, self.availability_type)


class SeasonalStock(models.Model):
    stock_amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True,
    )
    season = models.ForeignKey(
        'common.Season', related_name='season_stock', blank=True, null=True
    )

    def __unicode__(self):
        return self.stock_quantity

