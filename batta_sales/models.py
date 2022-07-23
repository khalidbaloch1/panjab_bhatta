# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

from django.utils import timezone
from django.db.models.signals import pre_delete


class Invoice(models.Model):
    bhatta = models.ForeignKey(
        'common.Bhatta', related_name='bhatta_invoice'
    )
    season = models.ForeignKey(
        'common.Season', related_name='seasion_invoice',
        blank=True, null=True
    )
    customer = models.ForeignKey(
        'batta_customers.Customer', related_name='customer_invoice',
        blank=True, null=True
    )
    invoice_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )
    challan_no = models.CharField(
        blank=True, null=True, max_length=200,
    )
    purchased_stock = models.ManyToManyField(
        'batta_stock.PurchasedStock', related_name='purchased_stock_invoice'
    )

    transport = models.CharField(
        max_length=200, blank=True, null=True
    )
    total_quantity = models.CharField(
        max_length=10, blank=True, null=True, default=1)

    sub_total = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    paid_amount = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    remaining_payment = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    discount = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    shipping = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    grand_total = models.DecimalField(
        max_digits=100, decimal_places=5, default=0, blank=True, null=True
    )
    dated = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.challan_no or ''


# Signal Functions
def delete_all_details(instance, **kwargs):
    """
    The functions used to check if user profile is not created
    and created the user profile without saving role and hospital
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    # if created and not UserProfile.objects.filter(user=instance):
    #     return UserProfile.objects.create(
    #         user=instance,
    #         user_type=UserProfile.USER_TYPE_OWNER
    #     )
    from batta_stock.models import StockOut
    for purchased_stock in instance.purchased_stock.all():
        StockOut.objects.filter(
            details='purchased ID is %d' % purchased_stock.id
        ).delete()

    from batta_customers.models import CustomerLedger
    CustomerLedger.objects.filter(
        details='Remaining Payment for Challan No. %s and'
                ' Invoice %d.' % (instance.challan_no, instance.id)
    ).delete()


# Signals
pre_delete.connect(delete_all_details, sender=Invoice)
