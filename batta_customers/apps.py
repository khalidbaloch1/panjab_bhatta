# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings


class BattaCustomersConfig(AppConfig):
    name = 'batta_customers'
    verbose_name = '%s Customer' % settings.COMPANY_SHORT_NAME
