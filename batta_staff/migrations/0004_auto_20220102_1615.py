# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2022-01-02 11:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batta_staff', '0003_staffothercredit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='staff_type',
            field=models.CharField(blank=True, choices=[('Salary Staff', 'Salary Staff'), ('Weekly Staff', 'Weekly Staff'), ('Other Staff', 'Other Staff'), ('Petroleum Staff', 'Petroleum Staff'), ('Multiple Staff', 'Multiple Staff')], default='Salary Staff', max_length=100, null=True),
        ),
    ]
