from django.conf.urls import url
from . import views
from other_expense.views import (
    OtherExpenses, AddOtherExpenseFormView, OtherExpenseUpdateView, OtherExpenseDeleteView,
    DebitDieselLedgerView, CreditDieselLedgerView, DieselDetailsView, DieselUpdateView, DieselInvoicesView,
    DebitMittiLedgerView, CreditMittiLedgerView, MittiDetailsView, MittiUpdateView, MittiInvoicesView
)

urlpatterns = [
    url(r'^add/$', AddOtherExpenseFormView.as_view(), name='add'),
    url(r'^$', OtherExpenses.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/update/$', OtherExpenseUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete/$', OtherExpenseDeleteView.as_view(), name='delete'),

    url(r'^(?P<pk>\d+)/debit/$', DebitDieselLedgerView.as_view(), name='debit'),
    url(r'^(?P<pk>\d+)/credit/$', CreditDieselLedgerView.as_view(), name='credit'),
    url(r'^(?P<pk>\d+)/diesel/details/$', DieselDetailsView.as_view(), name='diesel_details'),
    url(r'^(?P<pk>\d+)/diesel/update/$', DieselUpdateView.as_view(), name='diesel_update'),
    url(r'^(?P<pk>\d+)/diesel/delete/$', views.DeleteDieselLedger, name='diesel_delete'),
    url(
        r'^(?P<other_expense_id>\d+)/invoices/$',
        DieselInvoicesView.as_view(),
        name='invoices'
    ),
    url(
        r'^(?P<other_expense_id>\d+)/invoices/'
        r'start/(?P<start>.+)/end/(?P<end>.+)/$',
        DieselInvoicesView.as_view(),
        name='invoices_filter'
    ),

    url(r'^(?P<pk>\d+)/mitti/credit/$', CreditMittiLedgerView.as_view(), name='mitti_credit'),
    url(r'^(?P<pk>\d+)/mitti/debit/$', DebitMittiLedgerView.as_view(), name='mitti_debit'),
    url(r'^(?P<pk>\d+)/mitti/details/$', MittiDetailsView.as_view(), name='mitti_details'),
    url(r'^(?P<pk>\d+)/mitti/update/$', MittiUpdateView.as_view(), name='mitti_update'),
    url(r'^(?P<pk>\d+)/mitti/delete/$', views.DeleteMittidebit, name='mitti_delete'),
    url(
        r'^(?P<other_expense_id>\d+)/mitti/invoices/$',
        MittiInvoicesView.as_view(),
        name='mitti_invoices'
    ),
    url(
        r'^(?P<other_expense_id>\d+)/mitti/invoices/'
        r'start/(?P<start>.+)/end/(?P<end>.+)/$',
        MittiInvoicesView.as_view(),
        name='mitti_invoices_filter'
    ),

]
