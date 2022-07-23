# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2021-12-26 08:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('customer_type', models.CharField(blank=True, choices=[('Khata', 'Khata'), ('Advance', 'Advance'), ('Cash', 'Cash')], max_length=100, null=True)),
                ('mobile_no', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('bhatta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_bhatta', to='common.Bhatta')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerLedger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=100, null=True)),
                ('details', models.CharField(blank=True, max_length=200, null=True)),
                ('date_added', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_ledger', to='batta_customers.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerLedgerPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=100, null=True)),
                ('payment_type', models.CharField(blank=True, max_length=200, null=True)),
                ('details', models.TextField(blank=True, max_length=200, null=True)),
                ('payment_date', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('dated', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_ledger_payment', to='batta_customers.Customer')),
            ],
        ),
    ]
