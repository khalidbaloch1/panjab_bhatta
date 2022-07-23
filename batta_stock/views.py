# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, FormView, View
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt

from common.models import Bhatta
from common.models import Season

from batta_stock.models import Stock

from batta_stock.forms import StockForm, StockInForm, StockOutForm


class StockView(TemplateView):
    template_name = 'stocks/item_list.html'
    season = ''
    bhatta = ''

    def dispatch(self, request, *args, **kwargs):
        self.season = self.kwargs.get('season')
        self.bhatta = self.kwargs.get('bhatta')
        if self.request.user.is_authenticated():
            return super(
                StockView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(StockView, self).get_context_data(**kwargs)
        stocks = Stock.objects.all().order_by('bhatta__name')

        if self.kwargs.get('bhatta') and not self.kwargs.get('bhatta') == 'Bhattas':
            self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
            stocks = stocks.filter(bhatta__name=self.bhatta)

        context.update({
            'stocks': stocks,
            'bhattas': Bhatta.objects.all().order_by('name'),
            'seasons': Season.objects.all().order_by('-season_year'),
            'season_kw': self.season,
            'bhatta_kw': self.bhatta,
        })
        return context


class AddItemFormView(FormView):
    template_name = 'stocks/add_item.html'
    form_class = StockForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AddItemFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))
    
    def form_valid(self, form):
        item = form.save(commit=False)
        item.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name'))
        item.save()
        return HttpResponseRedirect(reverse('stock:item_list'))
    
    def form_invalid(self, form):
        return super(AddItemFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(AddItemFormView, self).get_context_data(**kwargs)
        context.update({
            'bhatta_list': Bhatta.objects.all().order_by('name')
        })
        return context


class AddNewStockFormView(FormView):
    template_name = 'stocks/stock_in.html'
    form_class = StockInForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AddNewStockFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(AddNewStockFormView, self).get_context_data(**kwargs)
        context.update({
            'item': Stock.objects.get(id=self.kwargs.get('pk')),
            'seasons': Season.objects.all().order_by('-id')
        })
        return context

    def form_valid(self, form):
        stock_in = form.save(commit=False)
        stock_in.season = Season.objects.get(
            season_year=self.request.POST.get('season_name'))
        stock_in.save()
        return HttpResponseRedirect(
            reverse('stock:item_stock_details', kwargs={
                'item_id': stock_in.stock.id
            })
        )
    
    def form_invalid(self, form):
        return super(AddNewStockFormView, self).form_invalid(form)


class StockOutFormView(FormView):
    template_name = 'stocks/stock_out.html'
    form_class = StockOutForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                StockOutFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(StockOutFormView, self).get_context_data(**kwargs)
        context.update({
            'item': Stock.objects.get(id=self.kwargs.get('pk')),
            'seasons': Season.objects.all().order_by('-id')
        })
        return context

    def form_valid(self, form):
        stock_out = form.save(commit=False)
        stock_out.season = Season.objects.get(
            season_year=self.request.POST.get('season_name'))
        stock_out.save()
        return HttpResponseRedirect(
            reverse('stock:item_stock_details', kwargs={
                'item_id': stock_out.stock.id
            })
        )

    def form_invalid(self, form):
        return super(StockOutFormView, self).form_invalid(form)


class ItemStockDetailsView(TemplateView):
    template_name = 'stocks/item_stock_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                ItemStockDetailsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            ItemStockDetailsView, self).get_context_data(**kwargs)
        try:
            item = Stock.objects.get(id=self.kwargs.get('item_id'))
        except Stock.DoesNotExist:
            return Http404('Item does not exists in database')

        item_stocks_in = item.stock_stockin.all()
        item_stocks_out = item.stock_stockout.all()

        if self.kwargs.get('season'):
            item_stocks_in = item.stock_stockin.filter(
                season__season_year=self.kwargs.get('season'))
            item_stocks_out = item_stocks_out.filter(
                season__season_year=self.kwargs.get('season'))

        if item_stocks_in.exists():
            total_stock_in = item_stocks_in.aggregate(Sum('stock_in'))
            total_stock_in = float(total_stock_in.get('stock_in__sum'))
        else:
            total_stock_in = 0

        if item_stocks_out.exists():
            total_stock_out = item_stocks_out.aggregate(Sum('stock_out'))
            total_stock_out = float(total_stock_out.get('stock_out__sum'))
        else:
            total_stock_out = 0

        context.update({
            'item': item,
            'item_stock_in': item_stocks_in.order_by('-added_date'),
            'item_stock_out': item_stocks_out.order_by('-added_date'),
            'total_stock_in': total_stock_in,
            'total_stock_out': total_stock_out,
            'remaining_stock': total_stock_in - total_stock_out,
            'season_kw': self.kwargs.get('season'),
            'seasons': Season.objects.all().order_by('-season_year')
        })

        return context


class AvailableStockAPIView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(
            AvailableStockAPIView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        bhatta_name = self.request.POST.get('bhatta_name')
        stock_item_name = self.request.POST.get('item_name')

        stock = Stock.objects.get(
            bhatta__name=bhatta_name, item_name=stock_item_name
        )

        return JsonResponse({
            'status': True,
            'message': 'Successfull',
            'available_items': stock.available_stock(
                season=self.request.POST.get('season'))
        })


class StockReportsView(TemplateView):
    template_name = 'stocks/reports.html'

    def get_context_data(self, **kwargs):
        context = super(StockReportsView, self).get_context_data(**kwargs)
        bhattas = Bhatta.objects.all().order_by('name')
        season = self.kwargs.get('season')
        overall_available_stock = 0
        overall_purchased_stock = 0
        overall_total_stock = 0
        overall_purchased_amount = 0
        results = []

        for bhatta in bhattas:
            stocks = bhatta.stock_bhatta.all().order_by('item_name')
            bhatta_stocks_results = []
            total_available_stock = 0
            total_purchased_stock = 0
            total_purchased_stock_amount = 0
            grand_total_stock = 0
            for stock in stocks:
                stock_results = {}
                available_stock = stock.available_stock(season=season)
                purchased_stock = stock.purchased_stock(season=season)
                total_stock = stock.total_stock(season=season)
                purchased_stock_amount = stock.purchased_stock_amount(
                        season=season)
                stock_results.update({
                    'item': stock.item_name,
                    'available_stock': available_stock,
                    'purchased_stock': purchased_stock,
                    'total_stock': total_stock,
                    'purchased_stock_amount': purchased_stock_amount
                })
                bhatta_stocks_results.append(stock_results)
                total_available_stock += available_stock
                total_purchased_stock += purchased_stock
                total_purchased_stock_amount += purchased_stock_amount
                grand_total_stock += total_stock

            results.append({
                'bhatta': bhatta.code,
                'stocks': bhatta_stocks_results,
                'grand_total_stock': grand_total_stock,
                'total_available_stock': total_available_stock,
                'total_purchased_stock': total_purchased_stock,
                'total_purchased_stock_amount': total_purchased_stock_amount
            })

            overall_available_stock += total_available_stock
            overall_purchased_stock += total_purchased_stock
            overall_purchased_amount += total_purchased_stock_amount
            overall_total_stock += grand_total_stock

        context.update({
            'seasons': Season.objects.all().order_by('season_year'),
            'season_kw': season,
            'results': results,
            'overall_available_stock': overall_available_stock,
            'overall_purchased_stock': overall_purchased_stock,
            'overall_purchased_amount': overall_purchased_amount,
            'overall_total_stock': overall_total_stock
        })
        return context
