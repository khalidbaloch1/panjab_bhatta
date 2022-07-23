from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class Account(models.Model):
    INCOME = 'Income Account'
    OWNER = 'Owner Account'

    TYPES = (
        (INCOME, 'Income Account'),
        (OWNER, 'Owner Account'),
    )

    bhatta = models.ForeignKey('common.Bhatta', related_name='account_bhatta', blank=True, null=True)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=100, blank=True, null=True, choices=TYPES)

    def __unicode__(self):
        return self.name


class IncomeLedger(models.Model):
    TYPE_INCOME_CREDIT_AMOUNT = 'Credit Ledger Book'
    TYPE_INCOME_DEBIT_AMOUNT = 'Debit Ledger Book'

    TYPES = (
        (TYPE_INCOME_CREDIT_AMOUNT, 'Credit Ledger Book'),
        (TYPE_INCOME_DEBIT_AMOUNT, 'Debit Ledger Book'),
    )
    bhatta = models.ForeignKey('common.Bhatta', related_name='income_bhatta', blank=True, null=True)
    season = models.ForeignKey('common.Season', related_name='income_seasion', blank=True, null=True)
    account = models.ForeignKey(Account, related_name='income_ledger')
    income_payment_type = models.CharField(max_length=100, choices=TYPES, blank=True, null=True)
    income_credit_amount = models.DecimalField(max_digits=65, decimal_places=2, default=0, blank=True, null=True)
    income_debit_amount = models.DecimalField(max_digits=65, decimal_places=2, default=0, blank=True, null=True)
    income_details = models.CharField(max_length=200, blank=True, null=True)
    income_date = models.DateField(default=timezone.now, blank=True, null=True)
    dated = models.DateField(default=timezone.now, blank=True, null=True)

    def __unicode__(self):
        return self.account.name


class OwnerLedger(models.Model):
    TYPE_OWNER_CREDIT_AMOUNT = 'Credit Ledger Book'
    TYPE_OWNER_DEBIT_AMOUNT = 'Debit Ledger Book'

    OWNER_TYPES = (
        (TYPE_OWNER_CREDIT_AMOUNT, 'Credit Ledger Book'),
        (TYPE_OWNER_DEBIT_AMOUNT, 'Debit Ledger Book'),
    )
    bhatta = models.ForeignKey('common.Bhatta', related_name='owner_bhatta', blank=True, null=True)
    season = models.ForeignKey('common.Season', related_name='owner_seasion', blank=True, null=True)
    account = models.ForeignKey(Account, related_name='owner_ledger')
    owner_payment_type = models.CharField(max_length=100, choices=OWNER_TYPES, blank=True, null=True)
    owner_credit_amount = models.DecimalField(max_digits=65, decimal_places=2, default=0, blank=True, null=True)
    owner_debit_amount = models.DecimalField(max_digits=65, decimal_places=2, default=0, blank=True, null=True)
    owner_details = models.CharField(max_length=200, blank=True, null=True)
    owner_date = models.DateField(default=timezone.now, blank=True, null=True)

    def __unicode__(self):
        return self.account.name
