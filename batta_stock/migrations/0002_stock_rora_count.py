# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2022-03-06 08:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batta_stock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='rora_count',
            field=models.BooleanField(default=False),
        ),
    ]
