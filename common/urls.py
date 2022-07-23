from django.conf.urls import url
from django.contrib import admin

from common.views import IndexView, LoginView, LogoutView, ReportsView, StaffJamahReportsView, QualityReportsView, TotalExpenseReportsView, KhattaReportsView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(
        r'^index/(?P<season>[a-zA-Z0-9_-]+)/$',
        IndexView.as_view(), name='index_filter'
    ),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^reports/$', ReportsView.as_view(), name='reports'),
    url(r'^expense/reports/$', TotalExpenseReportsView.as_view(), name='expense_reports'),
    url(
        r'^reports/(?P<season>[a-zA-Z0-9_-]+)/$',
        ReportsView.as_view(), name='reports_filter'
    ),
    url(
        r'^khatta/reports/$', KhattaReportsView.as_view(), name='khatta_reports'
    ),
    url(
        r'^expense/reports/(?P<season>[a-zA-Z0-9_-]+)/$',
        TotalExpenseReportsView.as_view(), name='expense/reports/_filter'
    ),
    url(
        r'^quality/reports/$', QualityReportsView.as_view(),
        name='quality_reports'
    ),
    url(
        r'^staff/jamah/reports/$', StaffJamahReportsView.as_view(),
        name='staff_jamah_reports'
    ),
]
