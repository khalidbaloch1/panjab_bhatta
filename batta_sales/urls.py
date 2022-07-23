from django.conf.urls import url
from . import views
from batta_sales.views import (
    CreateInvoiceFormView, StockItemsAPIView, CreateInvoiceAPIView,
    InvoicesListView, InvoiceDetailsView
)

urlpatterns = [
    url(r'^invoices/$', InvoicesListView.as_view(), name='invoices'),
    url(
        r'^invoices/(?P<season>[a-zA-Z0-9_-]+)/$',
        InvoicesListView.as_view(), name='invoices_filter'
    ),
    url(r'^create/$', CreateInvoiceFormView.as_view(), name='create_invoice'),
    url(r'^(?P<pk>\d+)/invoice/delete/$', views.DeleteInvoices, name='invoice_delete'),
    url(
        r'stock/items/api/$', StockItemsAPIView.as_view(),
        name='stock_items_api'
    ),
    url(
        r'create/invoice/api/$', CreateInvoiceAPIView.as_view(),
        name='create_invoice_api'
    ),
    url(
        r'^invoice/(?P<pk>\d+)/details/$',
        InvoiceDetailsView.as_view(),
        name='invoice_details'
    ),
]
