# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Koyla(models.Model):
    name = models.CharField(max_length=200)
    department = models.CharField(
        max_length=100, blank=True, null=True
    )
    bhatta = models.ForeignKey(
        'common.Bhatta', related_name='koyla_bhatta',
        null=True, blank=True
    )

    def __unicode__(self):
        return self.name


class KoylaLedger(models.Model):
    koyla = models.ForeignKey(Koyla, related_name='koyla_ledger')
    city = models.CharField(
        max_length=200, blank=True, null=True
    )
    season = models.ForeignKey(
        'common.Season', related_name='koyla_season',
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
    date_added = models.DateField(
        default=timezone.now, blank=True, null=True
    )
    dated = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.koyla.name if self.koyla else ''


class KoylaLedgerPayment(models.Model):
    koyla = models.ForeignKey(
        Koyla, related_name='koyla_ledger_payment'
    )
    amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    payment_type = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField(max_length=200, blank=True, null=True)
    payment_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )
    dated = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.koyla.name if self.koyla else ''
