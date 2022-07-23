# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView, FormView, UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.db.models import Sum

from batta_customers.forms import (
    CustomerForm, CustomerLedgerForm,
    CustomerLedgerPaymentForm
)

from batta_customers.models import Customer, CustomerLedger, CustomerLedgerPayment
from batta_sales.models import Invoice
from common.models import Bhatta


class Customers(ListView):
    template_name = 'customers/list.html'
    model = Customer
    paginate_by = 100
    # ordering = ['bhatta']
    bhatta = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                Customers, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = Customer.objects.all().order_by('bhatta', 'name')
            if self.kwargs.get('bhatta') and not self.kwargs.get('bhatta') == 'Bhattas':
                self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
                queryset = queryset.filter(bhatta__name=self.bhatta).order_by('name')

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(Customers, self).get_context_data(**kwargs)

        customers = Customer.objects.filter(customer_type=Customer.TYPE_KHATA)

        customer_remaining_balance = 0
        for customer in customers:
            customer_remaining_balance = (
                    customer_remaining_balance + customer.remaining_balance())

        customers = Customer.objects.filter(customer_type=Customer.TYPE_ADVANCE)

        customer_advance_remaining_balance = 0
        for customer in customers:
            customer_advance_remaining_balance = (
                    customer_advance_remaining_balance + customer.remaining_balance()
            )

        context.update({
            'bhattas': Bhatta.objects.all().order_by('-id'),
            'bhatta_kw': self.bhatta,
            'total_customer_balance': customer_remaining_balance,
            'customer_balance': customer_advance_remaining_balance
        })
        return context


class CustomerAddFormView(FormView):
    template_name = 'customers/add.html'
    form_class = CustomerForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CustomerAddFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

        def form_valid(self, form):
        customer = form.save(commit=False)
        try:
            customer.bhatta = Bhatta.objects.get(
                name=self.request.POST.get('bhatta_name'))
        except:
            pass
        customer.save()
        return HttpResponseRedirect(reverse('customer:list'))
    
    def form_invalid(self, form):
        return super(CustomerAddFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(CustomerAddFormView, self).get_context_data(**kwargs)
        bhatta_list = Bhatta.objects.all().order_by('name')
        context.update({
            'bhatta_list': bhatta_list,
            'customer_types': Customer.TYPES,
        })
        return context


class CustomerUpdateView(UpdateView):
    form_class = CustomerForm
    template_name = 'customers/update.html'
    model = Customer
    success_url = reverse_lazy('customer:list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CustomerUpdateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        customer = form.save(commit=False)
        customer.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name')
        )
        customer.save()
        return super(CustomerUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CustomerUpdateView, self).get_context_data(**kwargs)
        bhatta_list = Bhatta.objects.all().order_by('name')
        context.update({
            'bhatta_list': bhatta_list,
            'customer_types': Customer.TYPES,
        })
        return context


class CustomerLedgerFormView(FormView):
    template_name = 'customers/add_ledger.html'
    form_class = CustomerLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CustomerLedgerFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        customer_ledger = form.save()
        return HttpResponseRedirect(
            reverse('customer:ledger_details',
                    kwargs={'customer_id': customer_ledger.customer.id})
        )

    def get_context_data(self, **kwargs):
        context = super(
            CustomerLedgerFormView, self).get_context_data(**kwargs)
        context.update({
            'customer': Customer.objects.get(id=self.kwargs.get('pk')),
            'ledger_types': CustomerLedger.TYPES,
        })
        return context


class CustomerLedgerPaymentFormView(FormView):
    template_name = 'customers/ledger_payment.html'
    form_class = CustomerLedgerPaymentForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CustomerLedgerPaymentFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))
        
    def get(self, request, *args, **kwargs):
        messages.success(request, 'Jamah Amount Add SuccessFully')
        return self.post(request, *args, **kwargs)

    def form_valid(self, form):
        ledger_payment = form.save()
        ledger_payment.dated = ledger_payment.payment_date
        ledger_payment.save()
        return HttpResponseRedirect(
            reverse('customer:ledger_details',
                    kwargs={'customer_id': ledger_payment.customer.id})
        )

    def get_context_data(self, **kwargs):
        context = super(
            CustomerLedgerPaymentFormView, self).get_context_data(**kwargs)
        context.update({
            'customer': Customer.objects.get(id=self.kwargs.get('pk'))
        })
        return context


class CustomerLedgerDetailView(TemplateView):
    template_name = 'customers/ledger_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CustomerLedgerDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            CustomerLedgerDetailView, self).get_context_data(**kwargs)
        try:
            customer = Customer.objects.get(id=self.kwargs.get('customer_id'))
        except Customer.DoesNotExist:
            return Http404('Customer does not exists in database')

        customer_ledgers = customer.customer_ledger.all()
        customer_ledger_payments = customer.customer_ledger_payment.all()

        if customer_ledgers.exists():
            ledger_amount = customer_ledgers.aggregate(Sum('amount'))
            ledger_amount = float(ledger_amount.get('amount__sum'))
        else:
            ledger_amount = 0

        if customer_ledger_payments.exists():
            payment_amount = customer_ledger_payments.aggregate(Sum('amount'))
            payment_amount = float(payment_amount.get('amount__sum'))
        else:
            payment_amount = 0

        context.update({
            'customer': customer,
            'customer_ledgers': customer_ledgers.order_by('-date_added'),
            'customer_ledger_payments': customer_ledger_payments.order_by('-payment_date'),
            'ledger_amount': ledger_amount,
            'payment_amount': payment_amount,
            'remaining_amount': ledger_amount - payment_amount
        })
        return context


class CustomerInvoicesView(TemplateView):
    template_name = 'customers/invoices_list.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CustomerInvoicesView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            CustomerInvoicesView, self).get_context_data(**kwargs)
        invoices = Invoice.objects.filter(
            customer__id=self.kwargs.get('customer_id')
        ).order_by('invoice_date')

        start = self.kwargs.get('start')
        end = self.kwargs.get('end')
        if start and end:
            invoices = invoices.filter(
                invoice_date__range=[start, end]
            )

        if invoices.exists():
            total_quantity = invoices.aggregate(Sum('total_quantity'))
            total_quantity = total_quantity.get('total_quantity__sum')

            total_amount = invoices.aggregate(Sum('grand_total'))
            total_amount = total_amount.get('grand_total__sum')

        else:
            total_amount = 0
            total_quantity = 0

        ledgers = CustomerLedger.objects.filter(
            ledger_type=CustomerLedger.TYPE_LEDGER,
            customer__id=self.kwargs.get('customer_id')
        ).order_by('-date_added')

        if start and end:
            ledgers = ledgers.filter(
                date_added__range=[start, end]
            )

        if ledgers.exists():
            total_ledger = ledgers.aggregate(Sum('amount'))
            total_ledger = float(total_ledger.get('amount__sum'))
        else:
            total_ledger = 0

        payments = CustomerLedgerPayment.objects.filter(
            customer__id=self.kwargs.get('customer_id')
        ).order_by('-payment_date')

        if start and end:
            payments = payments.filter(
                payment_date__range=[start, end]
            )

        if payments.exists():
            total_payment = payments.aggregate(Sum('amount'))
            total_payment = float(total_payment.get('amount__sum'))
        else:
            total_payment = 0

        from itertools import chain
        query = list(chain(invoices, payments, ledgers))
        query.sort(key=lambda x: x.dated)

        context.update({
            'invoices': invoices,
            'customer': Customer.objects.get(
                id=self.kwargs.get('customer_id')),
            'total_amount': total_amount,
            'total_quantity': total_quantity,
            'start_date': start,
            'end_date': end,
            'ledgers': ledgers,
            'total_ledger': total_ledger,
            'payments': payments,
            'total_payment': total_payment,
            'query': query

        })
        return context
