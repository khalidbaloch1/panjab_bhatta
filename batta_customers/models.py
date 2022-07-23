# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Customer(models.Model):
    TYPE_KHATA = 'Khata'
    TYPE_ADVANCE = 'Advance'
    TYPE_CASH = 'Cash'

    TYPES = (
        (TYPE_KHATA, 'Khata'),
        (TYPE_ADVANCE, 'Advance'),
        (TYPE_CASH, 'Cash')
    )

    TYPE_ACTIVATE = 'Activate'
    TYPE_DEACTIVATE = 'Deactivate'

    ACTION = (
        (TYPE_ACTIVATE, 'Activate'),
        (TYPE_DEACTIVATE, 'Deactivate'),
    )

    bhatta = models.ForeignKey('common.Bhatta', related_name='customer_bhatta', null=True, blank=True)
    name = models.CharField(max_length=200)
    customer_type = models.CharField(max_length=100, choices=TYPES, blank=True, null=True)
    customer_status = models.CharField(max_length=100, choices=ACTION, blank=True, null=True)
    mobile_no = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    khata_count = models.BooleanField(default=False)
    advance_count = models.BooleanField(default=False)
    deactivate = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def ledger_balance(self):
        customer_ledgers = self.customer_ledger.all()
        if customer_ledgers.exists():
            ledger_amount = customer_ledgers.aggregate(Sum('amount'))
            ledger_amount = float(ledger_amount.get('amount__sum'))
        else:
            ledger_amount = 0

        return ledger_amount

    def ledger_payment_balance(self):
        customer_ledger_payments = self.customer_ledger_payment.all()
        if customer_ledger_payments.exists():
            payment_amount = customer_ledger_payments.aggregate(Sum('amount'))
            payment_amount = float(payment_amount.get('amount__sum'))
        else:
            payment_amount = 0

        return payment_amount

    def total_payment(self):
        invoices = self.customer_invoice.all()
        if invoices.exists():
            total_payments = invoices.aggregate(Sum('paid_amount'))
            total_paid_amount = float(total_payments.get('paid_amount__sum'))
        return self.ledger_payment_balance() + total_paid_amount

    def remaining_balance(self):
        return self.ledger_balance() - self.ledger_payment_balance()


class CustomerLedger(models.Model):
    TYPE_LEDGER = 'Ledger Book'

    TYPES = (
        (TYPE_LEDGER, 'Ledger Book'),
    )
    customer = models.ForeignKey(Customer, related_name='customer_ledger')
    ledger_type = models.CharField(max_length=100, choices=TYPES, blank=True, null=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2, default=0, blank=True, null=True)
    details = models.CharField(max_length=200, blank=True, null=True)
    date_added = models.DateField(default=timezone.now, blank=True, null=True)
    dated = models.DateField(default=timezone.now, blank=True, null=True)

    def __unicode__(self):
        return self.customer.name if self.customer else ''


class CustomerLedgerPayment(models.Model):
    customer = models.ForeignKey(Customer, related_name='customer_ledger_payment')
    amount = models.DecimalField(max_digits=100, decimal_places=2, default=0, blank=True, null=True)
    payment_type = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField(max_length=200, blank=True, null=True)
    payment_date = models.DateField(default=timezone.now, blank=True, null=True)
    dated = models.DateField(default=timezone.now, blank=True, null=True)

    def __unicode__(self):
        return self.customer.name if self.customer else ''
