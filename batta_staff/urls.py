from django.conf.urls import url

from batta_staff.views import (
    StaffListView, CreateStaffView, StaffCreditView, StaffDebitView,
    StaffUpdateView, NormalStaffDetailsView, AdvanceStaffCreditFormView,
    AdvanceStaffDetails, AdvanceStaffCreditUpdateView, NormalStaffDetailsReportsView,
    WeeklyStaffDetailsReportsView, OtherStaffCreditFormView, OtherStaffDebitView, OtherStaffDetails
)

urlpatterns = [
    url(r'^list/$', StaffListView.as_view(), name='list'),
    url(
        r'^list/(?P<season>[a-zA-Z0-9_-]+)/$',
        StaffListView.as_view(), name='list_filter'
    ),
    url(r'^create/$', CreateStaffView.as_view(), name='create'),
    url(
        r'^(?P<pk>\d+)/update/$',
        StaffUpdateView.as_view(), name='update'
     ),
    url(
        r'^(?P<pk>\d+)/credit/$',
        StaffCreditView.as_view(), name='credit'
     ),
    url(
        r'^(?P<pk>\d+)/debit/$',
        StaffDebitView.as_view(), name='debit'
    ),
    url(
        r'^(?P<pk>\d+)/details/$',
        NormalStaffDetailsView.as_view(), name='details'
    ),
    url(
        r'^(?P<pk>\d+)/details_reports/$',
        NormalStaffDetailsReportsView.as_view(), name='details_reports'
    ),
    url(
        r'^(?P<pk>\d+)/weekly/reports/$',
        WeeklyStaffDetailsReportsView.as_view(), name='weekly_reports'
    ),
    url(
        r'^(?P<pk>\d+)/weekly/reports/(?P<season>[a-zA-Z0-9_-]+)/$',
        WeeklyStaffDetailsReportsView.as_view(), name='weekly_reports_fiter'
    ),
    url(
        r'^(?P<pk>\d+)/credit/advance/$',
        AdvanceStaffCreditFormView.as_view(), name='credit_advance'
    ),
    url(
        r'^(?P<pk>\d+)/credit/update/$',
        AdvanceStaffCreditUpdateView.as_view(), name='update_advance'
    ),
    url(
        r'^(?P<pk>\d+)/details/advance/$',
        AdvanceStaffDetails.as_view(), name='details_advance'
    ),
    url(
        r'^(?P<pk>\d+)/details/advance/(?P<season>[a-zA-Z0-9_-]+)/$',
        AdvanceStaffDetails.as_view(), name='details_advance_fiter'
    ),
    url(
        r'^(?P<pk>\d+)/credit/other/$',
        OtherStaffCreditFormView.as_view(), name='credit_other'
    ),
    url(
        r'^(?P<pk>\d+)/debit/other/$',
        OtherStaffDebitView.as_view(), name='debit_other'
    ),
    url(
        r'^(?P<pk>\d+)/details/other/$',
        OtherStaffDetails.as_view(), name='details_other'
    ),
    url(
        r'^(?P<pk>\d+)/details/other/(?P<season>[a-zA-Z0-9_-]+)/$',
        OtherStaffDetails.as_view(), name='details_other_fiter'
    ),
]
