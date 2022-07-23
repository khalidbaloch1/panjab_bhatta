from django.conf.urls import url

from batta_stock.views import (
    StockView, AddItemFormView, AddNewStockFormView, StockOutFormView,
    ItemStockDetailsView, AvailableStockAPIView, StockReportsView
)


urlpatterns = [
    url(r'^items/$', StockView.as_view(), name='item_list'),
    url(
        r'^items/(?P<season>[a-zA-Z0-9_-]+)/$',
        StockView.as_view(), name='item_list_filter'
    ),
    url(r'^item/add/$', AddItemFormView.as_view(), name='item_add'),
    url(
        r'^item/(?P<pk>\d+)/stock-in/$',
        AddNewStockFormView.as_view(), name='stock_in'
    ),
    url(
        r'^item/(?P<pk>\d+)/stock-out/$',
        StockOutFormView.as_view(), name='stock_out'
    ),
    url(
        r'^item/(?P<item_id>\d+)/details/$',
        ItemStockDetailsView.as_view(), name='item_stock_details'
    ),
    url(
        r'^item/(?P<item_id>\d+)/details/(?P<season>[a-zA-Z0-9_-]+)/$',
        ItemStockDetailsView.as_view(), name='item_stock_details_filter'
    ),
    url(
        r'^item/available/api/', AvailableStockAPIView.as_view(),
        name='available_item_api'
    ),
    url(r'^reports/$', StockReportsView.as_view(), name='stock_reports'),
    url(
        r'^reports/(?P<season>[a-zA-Z0-9_-]+)/$', StockReportsView.as_view(),
        name='stock_reports_filter'
    ),
]
