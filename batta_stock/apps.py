# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings


class BattaStockConfig(AppConfig):
    name = 'batta_stock'
    verbose_name = '%s Stock' % settings.COMPANY_SHORT_NAME
