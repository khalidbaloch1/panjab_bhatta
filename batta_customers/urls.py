from django.conf.urls import url

from batta_customers.views import (
    Customers, CustomerAddFormView, CustomerUpdateView,
    CustomerLedgerFormView, CustomerLedgerPaymentFormView,
    CustomerLedgerDetailView, CustomerInvoicesView
)

urlpatterns = [
    url(r'^$', Customers.as_view(), name='list'),
    url(r'^add/$', CustomerAddFormView.as_view(), name='add'),
    url(
        r'^(?P<pk>\d+)/update/$',
        CustomerUpdateView.as_view(),
        name='update'
    ),
    url(
        r'^(?P<pk>\d+)/add/ledger/$',
        CustomerLedgerFormView.as_view(),
        name='add_ledger'
    ),
    url(
        r'^(?P<pk>\d+)/payment/ledger/$',
        CustomerLedgerPaymentFormView.as_view(),
        name='payment_ledger'
    ),
    url(
        r'^(?P<customer_id>\d+)/ledger/details/$',
        CustomerLedgerDetailView.as_view(),
        name='ledger_details'
    ),
    url(
        r'^(?P<customer_id>\d+)/invoices/$',
        CustomerInvoicesView.as_view(),
        name='invoices'
    ),
    url(
        r'^(?P<customer_id>\d+)/invoices/'
        r'start/(?P<start>.+)/end/(?P<end>.+)/$',
        CustomerInvoicesView.as_view(),
        name='invoices_filter'
    ),
    url(r'^(?P<bhatta>.+)/$', Customers.as_view(), name='list_filter'),
]
