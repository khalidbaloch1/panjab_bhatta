from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class OtherExpense(models.Model):
    EXPENSE_DIESEL = 'diesel'
    EXPENSE_MITTI = 'Mitti'

    EXPENSE_TYPES = (
        (EXPENSE_DIESEL, 'diesel'),
        (EXPENSE_MITTI, 'Mitti'),
    )

    bhatta = models.ForeignKey('common.Bhatta', related_name='worker_bhatta', blank=True, null=True)
    name = models.CharField(max_length=200)
    expense_type = models.CharField(max_length=100, blank=True, null=True, choices=EXPENSE_TYPES)
    mobile_no = models.CharField(max_length=100, blank=True, null=True)
    page_no = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name


class DieselLedger(models.Model):
    TYPE_DIESEL_CREDIT_AMOUNT = 'Credit Ledger Book'
    TYPE_DIESEL_DEBIT_AMOUNT = 'Debit Ledger Book'

    TYPES = (
        (TYPE_DIESEL_CREDIT_AMOUNT, 'Credit Ledger Book'),
        (TYPE_DIESEL_DEBIT_AMOUNT, 'Debit Ledger Book'),
    )
    bhatta = models.ForeignKey('common.Bhatta', related_name='diesel_bhatta', blank=True, null=True)
    season = models.ForeignKey('common.Season', related_name='diesel_seasion', blank=True, null=True)
    other_expense = models.ForeignKey(OtherExpense, related_name='diesel_ledger')
    diesel_payment_type = models.CharField(max_length=100, choices=TYPES, blank=True, null=True)
    diesel_debit_amount = models.DecimalField(max_digits=65, decimal_places=2, default=0, blank=True, null=True)
    amount_per_ltr = models.DecimalField(max_digits=65, decimal_places=3, default=0, blank=True, null=True)
    ltr = models.DecimalField(max_digits=100, decimal_places=3, default=0, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=100, decimal_places=3, default=0, blank=True, null=True)
    diesel_details = models.CharField(max_length=200, blank=True, null=True)
    diesel_date = models.DateField(default=timezone.now, blank=True, null=True)
    dated = models.DateField(default=timezone.now, blank=True, null=True)

    def __unicode__(self):
        return self.other_expense.name


class MittiLedger(models.Model):
    TYPE_MITTI_CREDIT_AMOUNT = 'Credit Ledger Book'
    TYPE_MITTI_DEBIT_AMOUNT = 'Debit Ledger Book'

    TYPES = (
        (TYPE_MITTI_CREDIT_AMOUNT, 'Credit Ledger Book'),
        (TYPE_MITTI_DEBIT_AMOUNT, 'Debit Ledger Book'),
    )
    bhatta = models.ForeignKey('common.Bhatta', related_name='mitti_bhatta', blank=True, null=True)
    season = models.ForeignKey('common.Season', related_name='mitti_seasion', blank=True, null=True)
    other_expense = models.ForeignKey(OtherExpense, related_name='mitti_ledger')
    mitti_payment_type = models.CharField(max_length=100, choices=TYPES, blank=True, null=True)
    mitti_debit_amount = models.DecimalField(max_digits=65, decimal_places=2, default=0, blank=True, null=True)
    amount_per_load = models.DecimalField(max_digits=65, decimal_places=2, default=0, blank=True, null=True)
    total_load = models.DecimalField(max_digits=100, decimal_places=3, default=0, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=100, decimal_places=3, default=0, blank=True, null=True)
    mitti_details = models.CharField(max_length=200, blank=True, null=True)
    mitti_date = models.DateField(default=timezone.now, blank=True, null=True)

    def __unicode__(self):
        return self.other_expense.name
