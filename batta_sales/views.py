# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.views.generic import FormView, TemplateView, View, ListView
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Sum

from django.contrib import messages

from batta_customers.models import Customer
from batta_stock.models import Stock, StockOut
from common.models import Bhatta, Season
from batta_sales.models import Invoice

from batta_sales.forms import InvoiceForm
from batta_stock.forms import PurchasedItemForm, StockOutForm
from batta_customers.forms import CustomerLedgerForm


class CreateInvoiceFormView(FormView):
    template_name = 'sales/create_invoice.html'
    form_class = InvoiceForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CreateInvoiceFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            CreateInvoiceFormView, self).get_context_data(**kwargs)
        context.update({
            'customers': Customer.objects.filter(customer_status=Customer.TYPE_ACTIVATE),
            'bhatta_list': Bhatta.objects.all().order_by('name'),
            'seasons': Season.objects.filter(season_status=Season.TYPE_ACTIVATE).order_by('-season_year')
        })
        return context


def DeleteInvoices(request, pk):

    Invoice.objects.get(pk=pk).delete()

    messages.success(request, 'Success Full Deleted')
    return HttpResponseRedirect(reverse('sales:invoices'))


class StockItemsAPIView(View):
    def get(self, request, *args, **kwargs):

        stocks = Stock.objects.values('item_name').distinct()
        result = []
        for stock in stocks:
            result.append({
                'item_name': stock.get('item_name'),
            })

        return JsonResponse({'result': result})


class CreateInvoiceAPIView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(
            CreateInvoiceAPIView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        added_date = self.request.POST.get('added_date')
        customer_id = self.request.POST.get('customer_id')
        season = self.request.POST.get('season')
        bhatta = self.request.POST.get('bhatta')
        sub_total = self.request.POST.get('sub_total')
        discount = self.request.POST.get('discount')
        shipping = self.request.POST.get('shipping')
        grand_total = self.request.POST.get('grand_total')
        totalQty = self.request.POST.get('totalQty')
        remaining_payment = self.request.POST.get('remaining_amount')
        paid_amount = self.request.POST.get('paid_amount')
        challan_no = self.request.POST.get('challan_no')
        transport = self.request.POST.get('transport')
        items = json.loads(self.request.POST.get('items'))

        purchased_items_id = []
        with transaction.atomic():
            season_obj = Season.objects.get(season_year=season)
            bhatta_obj = Bhatta.objects.get(name=bhatta)
            purchased_item = ''

            for item in items:
                item_name = item.get('item_name')

                item_obj = Stock.objects.get(
                    item_name=item_name, bhatta__name=bhatta)

                form_kwargs = {
                    'season': season_obj.id,
                    'stock': item_obj.id,
                    'quantity': item.get('qty'),
                    'price': item.get('price'),
                    'total_amount': item.get('total')
                }

                item_purchased_form = PurchasedItemForm(form_kwargs)

                if item_purchased_form.is_valid():
                    purchased_item = item_purchased_form.save()
                    purchased_items_id.append(purchased_item.id)

                    stock_out_kwargs = {
                        'season': season_obj.id,
                        'stock': item_obj.id,
                        'stock_out': item.get('qty'),
                        'details': 'purchased ID is %d' % purchased_item.id,
                        'added_date': added_date
                    }

                    stock_out_form = StockOutForm(stock_out_kwargs)
                    if stock_out_form.is_valid():
                        stock_out_obj = stock_out_form.save()

            invoice_form_kwargs = {
                'bhatta': bhatta_obj.id,
                'season': season_obj.id,
                'customer': customer_id,
                'invoice_date': added_date,
                'dated': added_date,
                'challan_no': challan_no,
                'purchased_stock': purchased_items_id,
                'transport': transport,
                'total_quantity': totalQty,
                'sub_total': sub_total,
                'paid_amount': paid_amount,
                'remaining_payment': remaining_payment,
                'discount': discount,
                'shipping': shipping,
                'grand_total': grand_total,
            }

            invoice_form = InvoiceForm(invoice_form_kwargs)

            invoice = None
            if invoice_form.is_valid():
                invoice = invoice_form.save()
                purchased_item.invoice = invoice
                purchased_item.save()

            if remaining_payment:
                ledger_form_kwargs = {
                    'customer': customer_id,
                    'amount': remaining_payment,
                    'details': (
                        'Remaining Payment for Challan No. %s'
                        ' and Invoice %s.' % (invoice.challan_no, invoice.id)
                    ),
                    'date_added': added_date,
                }
                customer_ledger_form = CustomerLedgerForm(ledger_form_kwargs)
                if customer_ledger_form.is_valid():
                    customer_ledger_form.save()

        return JsonResponse({
            'success_url': reverse(
                'sales:invoice_details', kwargs={'pk': invoice.id}
            )
        })


class InvoicesListView(ListView):
    model = Invoice
    paginate_by = 200
    template_name = 'sales/invoices.html'
    ordering = '-id'
    season = ''
    bhatta = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                InvoicesListView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = Invoice.objects.all()

        if self.kwargs.get('season') and not self.kwargs.get('season') == 'Seasons':
            self.season = self.kwargs.get('season')
            queryset = queryset.filter(season__season_year=self.kwargs.get('season'))

        if self.kwargs.get('bhatta') and not self.kwargs.get('bhatta') == 'Bhattas':
            self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
            queryset = queryset.filter(bhatta__name=self.bhatta)

        if not self.kwargs.get('bhatta') and not self.kwargs.get('season'):
            self.season = Season.objects.all().latest('id')
            self.bhatta = Bhatta.objects.all().latest('id')
            self.season = self.season.season_year
            self.bhatta = self.bhatta.name

        if self.request.GET.get('challan'):
            queryset = queryset.filter(
                challan_no=self.request.GET.get('challan'))

        return queryset.order_by('-invoice_date')

    def get_context_data(self, **kwargs):
        context = super(InvoicesListView, self).get_context_data(**kwargs)

        if self.get_queryset().exists():
            grand_total = self.get_queryset().aggregate(Sum('grand_total'))
            grand_total = float(grand_total.get('grand_total__sum'))

            total_quantity = self.get_queryset().aggregate(Sum('total_quantity'))
            total_quantity = float(total_quantity.get('total_quantity__sum'))
        else:
            grand_total = 0
            total_quantity = 0

        context.update({
            'seasons': Season.objects.all().order_by('-season_year'),
            'bhattas': Bhatta.objects.all().order_by('-name'),
            'season_kw': self.season,
            'bhatta_kw': self.bhatta,
            'grand_total': grand_total,
            'total_quantity': total_quantity,
        })
        return context


class InvoiceDetailsView(TemplateView):
    template_name = 'sales/invoice_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                InvoiceDetailsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailsView, self).get_context_data(**kwargs)

        try:
            invoice = Invoice.objects.get(id=self.kwargs.get('pk'))
        except Invoice.DoesNotExist:
            return Http404('Invoice does not exists in database')

        context.update({
            'invoice': invoice,
            'items': invoice.purchased_stock,
        })

        return context
