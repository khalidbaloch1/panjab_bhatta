from django.conf.urls import url

from .views import (
    AddCoalExpenseFormView, CoalExpenseListView, CoalExpenseUpdateView,
    CoalExpenseDeleteView, SeasonalExpenditureFormView,
    SeasonalExpenditureListView, SeasonalExpenditureUpdateView,
    SeasonalExpenditureDeleteView, SeasonalIncomeFormView,
    SeasonalIncomeDeleteView, SeasonalIncomeListView,
    ExpenditureAmountListView, ExpenditureAmountFormView,
    ExpenditureAmountUpdateView, SeasonalStockListView, SeasonalStockDeleteView,
    SeasonalStockFormView, KoylaAmountListView, AddKoylaAmountFormView
)


urlpatterns = [
    url(
        r'^coal/create/$', AddCoalExpenseFormView.as_view(),
        name='coal_create'
    ),
    url(
        r'^coal/list/$', CoalExpenseListView.as_view(),
        name='coal_list'
    ),
    url(
        r'^create/amount$', AddKoylaAmountFormView.as_view(),
        name='create_stock'
    ),
    url(
        r'^koyla/amount/$', KoylaAmountListView.as_view(),
        name='koyla_amount'
    ),
    url(
        r'^coal/(?P<pk>\d+)/update/$',
        CoalExpenseUpdateView.as_view(),
        name='coal_update'
    ),
    url(
        r'^coal/(?P<pk>\d+)/delete/$',
        CoalExpenseDeleteView.as_view(),
        name='coal_delete'
    ),
    url(
        r'^coal/list/(?P<season>[a-zA-Z0-9_-]+)/$',
        CoalExpenseListView.as_view(), name='coal_expense_filter'
    ),
    url(
        r'^create/$', SeasonalExpenditureFormView.as_view(),
        name='create_expense'
    ),
    url(
        r'^list/$', SeasonalExpenditureListView.as_view(),
        name='expense_list'
    ),
    url(
        r'^(?P<pk>\d+)/update/$',
        SeasonalExpenditureUpdateView.as_view(),
        name='update_expense'
    ),
    url(
        r'^(?P<pk>\d+)/delete/$',
        SeasonalExpenditureDeleteView.as_view(),
        name='delete_expense'
    ),
    url(
        r'^list/(?P<season>[a-zA-Z0-9_-]+)/$',
        SeasonalExpenditureListView.as_view(), name='expense_filter'
    ),
    url(
        r'^income/create/$', SeasonalIncomeFormView.as_view(),
        name='create_income'
    ),
    url(
        r'^income/list/$', SeasonalIncomeListView.as_view(),
        name='income_list'
    ),
    url(
        r'^income/(?P<pk>\d+)/delete/$',
        SeasonalIncomeDeleteView.as_view(),
        name='delete_income'
    ),
    url(
        r'^income/list/(?P<season>[a-zA-Z0-9_-]+)/$',
        SeasonalIncomeListView.as_view(), name='income_filter'
    ),
    url(
        r'^(?P<pk>\d+)/amount/details/$',
        ExpenditureAmountListView.as_view(),
        name='expense_amount_details'
    ),
    url(
        r'^(?P<pk>\d+)/amount/details/'
        r'start/(?P<start>.+)/end/(?P<end>.+)/$',
        ExpenditureAmountListView.as_view(),
        name='expense_amount_details_filter'
    ),
    url(
        r'^(?P<pk>\d+)/amount/add/$',
        ExpenditureAmountFormView.as_view(),
        name='expense_amount_add'
    ),
    url(
        r'^(?P<pk>\d+)/amount/update/$',
        ExpenditureAmountUpdateView.as_view(),
        name='expense_amount_update'
    ),
    url(
        r'^stock/create/$', SeasonalStockFormView.as_view(),
        name='create_stock'
    ),
    url(
        r'^stock/list/$', SeasonalStockListView.as_view(),
        name='stock_list'
    ),
    url(
        r'^stock/(?P<pk>\d+)/delete/$',
        SeasonalStockDeleteView.as_view(),
        name='delete_stock'
    ),
    url(
        r'^stock/list/(?P<season>[a-zA-Z0-9_-]+)/$',
        SeasonalStockListView.as_view(), name='income_filter'
    ),
]
