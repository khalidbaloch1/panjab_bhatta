from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings


class StaffDriverConfig(AppConfig):
    name = 'batta_staff'
    verbose_name = '%s Staff' % settings.COMPANY_SHORT_NAME
