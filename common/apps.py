# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings


class CommonConfig(AppConfig):
    name = 'common'
    verbose_name = '%s Main' % settings.COMPANY_SHORT_NAME
