from django.conf.urls import url

from batta_account.views import (
    AccountListView, AddAccountFormView, AccountUpdateView, AccountDeleteView,
    CreditIncomeLedgerView, DebitIncomeLedgerView, IncomeDetailsView, IncomeUpdateView,
    CreditOwnerView, DebitOwnerView, OwnerDetailsView
)

urlpatterns = [
    url(r'^add/$', AddAccountFormView.as_view(), name='add'),
    url(r'^$', AccountListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/update/$', AccountUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete/$', AccountDeleteView.as_view(), name='delete_account'),



    url(r'^(?P<pk>\d+)/credit/$', CreditIncomeLedgerView.as_view(), name='credit'),
    url(r'^(?P<pk>\d+)/debit/$', DebitIncomeLedgerView.as_view(), name='debit'),
    url(r'^(?P<income_account_id>\d+)/income/details/$', IncomeDetailsView.as_view(), name='income_details'),
    url(r'^(?P<pk>\d+)/income/update/$', IncomeUpdateView.as_view(), name='income_update'),


    url(r'^(?P<pk>\d+)/owner/credit/$', CreditOwnerView.as_view(), name='owner_credit'),
    url(r'^(?P<pk>\d+)/owner/debit/$', DebitOwnerView.as_view(), name='owner_debit'),
    url(r'^(?P<owner_account_id>\d+)/owner/details/$', OwnerDetailsView.as_view(), name='owner_details'),


]
