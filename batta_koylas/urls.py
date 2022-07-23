from django.conf.urls import url

from batta_koylas.views import (
    Koylas, KoylaAddFormView,
    KoylaLedgerFormView, KoylaLedgerPaymentFormView, KoylaLedgerDetailView, KoylaReportsView, KoylaUpdateView
)

urlpatterns = [
    url(r'^$', Koylas.as_view(), name='list'),
    url(r'^add/$', KoylaAddFormView.as_view(), name='add'),
    url(
        r'^(?P<pk>\d+)/update/$',
        KoylaUpdateView.as_view(),
        name='update'
    ),
    url(
        r'^(?P<pk>\d+)/add/ledger/$',
        KoylaLedgerFormView.as_view(),
        name='add_ledger'
    ),
    url(
        r'^(?P<pk>\d+)/payment/ledger/$',
        KoylaLedgerPaymentFormView.as_view(),
        name='payment_ledger'
    ),
    url(
        r'^(?P<koyla_id>\d+)/ledger/details/$',
        KoylaLedgerDetailView.as_view(),
        name='ledger_details'
    ),
    url(
        r'^(?P<koyla_id>\d+)/reports/$',
        KoylaReportsView.as_view(),
        name='reports'
    ),
]
