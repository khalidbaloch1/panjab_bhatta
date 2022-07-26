# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2021-12-26 08:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('batta_sales', '0001_initial'),
        ('common', '0001_initial'),
        ('batta_stock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='purchased_stock',
            field=models.ManyToManyField(related_name='purchased_stock_invoice', to='batta_stock.PurchasedStock'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='season',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='seasion_invoice', to='common.Season'),
        ),
    ]
