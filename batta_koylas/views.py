# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView, FormView, UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.db.models import Sum

from batta_koylas.forms import (
    KoylaForm, KoylaLedgerForm, KoylaLedgerPaymentForm
)

from batta_koylas.models import Koyla, KoylaLedgerPayment, KoylaLedger
from common.models import Season, Bhatta


class Koylas(ListView):
    template_name = 'koyla/list.html'
    model = Koyla
    paginate_by = 100
    bhatta = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                Koylas, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = Koyla.objects.all().order_by('bhatta', 'name')
            if self.kwargs.get('bhatta') and not self.kwargs.get('bhatta') == 'Bhattas':
                self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
                queryset = queryset.filter(bhatta__name=self.bhatta).order_by('name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super(Koylas, self).get_context_data(**kwargs)

        context.update({
            'bhattas': Bhatta.objects.all().order_by('-id'),
            'bhatta_kw': self.bhatta,
        })
        return context


class KoylaAddFormView(FormView):
    template_name = 'koyla/add.html'
    form_class = KoylaForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                KoylaAddFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        koyla = form.save(commit=False)
        koyla.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name')
        )
        koyla.save()
        return HttpResponseRedirect(reverse('koyla:list'))

    def form_invalid(self, form):
        return super(KoylaAddFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(KoylaAddFormView, self).get_context_data(**kwargs)
        bhatta_list = Bhatta.objects.all().order_by('name')
        context.update({
            'bhatta_list': bhatta_list,
            'seasons': Season.objects.all().order_by('season_year'),
        })
        return context


class KoylaUpdateView(UpdateView):
    form_class = KoylaForm
    template_name = 'koyla/update.html'
    model = Koyla
    success_url = reverse_lazy('koyla:list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                KoylaUpdateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        koyla = form.save(commit=False)
        koyla.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name')
        )
        koyla.save()
        return super(KoylaUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(KoylaUpdateView, self).get_context_data(**kwargs)
        bhatta_list = Bhatta.objects.all().order_by('name')
        context.update({
            'bhatta_list': bhatta_list,
        })
        return context


class KoylaLedgerFormView(FormView):
    template_name = 'koyla/add_ledger.html'
    form_class = KoylaLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                KoylaLedgerFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        koyla_ledger = form.save()
        koyla_ledger.season = Season.objects.get(
            season_year=self.request.POST.get('season_year'))
        koyla_ledger.save()
        return HttpResponseRedirect(
            reverse('koyla:ledger_details',
                    kwargs={'koyla_id': koyla_ledger.koyla.id})
        )

    def get_context_data(self, **kwargs):
        context = super(
            KoylaLedgerFormView, self).get_context_data(**kwargs)
        context.update({
            'koyla': Koyla.objects.get(id=self.kwargs.get('pk')),
            'seasons': Season.objects.all().order_by('-season_year')
        })
        return context


class KoylaLedgerPaymentFormView(FormView):
    template_name = 'koyla/ledger_payment.html'
    form_class = KoylaLedgerPaymentForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                KoylaLedgerPaymentFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        ledger_payment = form.save()
        ledger_payment.dated = ledger_payment.payment_date
        ledger_payment.save()
        return HttpResponseRedirect(
            reverse('koyla:ledger_details',
                    kwargs={'koyla_id': ledger_payment.koyla.id})
        )

    def get_context_data(self, **kwargs):
        context = super(
            KoylaLedgerPaymentFormView, self).get_context_data(**kwargs)
        context.update({
            'koyla': Koyla.objects.get(id=self.kwargs.get('pk'))
        })
        return context


class KoylaLedgerDetailView(TemplateView):
    template_name = 'koyla/ledger_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                KoylaLedgerDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            KoylaLedgerDetailView, self).get_context_data(**kwargs)
        try:
            koyla = Koyla.objects.get(id=self.kwargs.get('koyla_id'))
        except Koyla.DoesNotExist:
            return Http404('Koyla does not exists in database')

        koyla_ledgers = koyla.koyla_ledger.all()
        koyla_ledger_payments = koyla.koyla_ledger_payment.all()

        if koyla_ledgers.exists():
            total_carriage = koyla_ledgers.aggregate(Sum('carriage'))
            total_carriage = float(total_carriage.get('carriage__sum'))

            total_amount = koyla_ledgers.aggregate(Sum('amount'))
            total_amount = float(total_amount.get('amount__sum'))

        else:
            total_carriage = 0
            total_amount = 0

        if koyla_ledger_payments.exists():
            payment_amount = koyla_ledger_payments.aggregate(Sum('amount'))
            payment_amount = float(payment_amount.get('amount__sum'))
        else:
            payment_amount = 0

        context.update({
            'koyla': koyla,
            'koyla_ledgers': koyla_ledgers.order_by('-date_added'),
            'koyla_ledger_payments': koyla_ledger_payments.order_by('-payment_date'),
            'total_carriage': total_carriage,
            'total_amount': total_amount,
            'payment_amount': payment_amount,
            'remaining_payment': payment_amount - total_amount,
        })
        return context


class KoylaReportsView(TemplateView):
    template_name = 'koyla/koyla_reports.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                KoylaReportsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            KoylaReportsView, self).get_context_data(**kwargs)
        koyla_ledgers = KoylaLedger.objects.filter(
            koyla__id=self.kwargs.get('koyla_id')
        ).order_by('-date_added')

        start = self.kwargs.get('start')
        end = self.kwargs.get('end')
        if start and end:
            koyla_ledgers = koyla_ledgers.filter(
                date_added__range=[start, end]
            )

        if koyla_ledgers.exists():
            total_carriage = koyla_ledgers.aggregate(Sum('carriage'))
            total_carriage = float(total_carriage.get('carriage__sum'))

            total_amount = koyla_ledgers.aggregate(Sum('amount'))
            total_amount = float(total_amount.get('amount__sum'))

        else:
            total_carriage = 0
            total_amount = 0

        payments = KoylaLedgerPayment.objects.filter(
            koyla__id=self.kwargs.get('koyla_id')
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
        query = list(chain(koyla_ledgers, payments))
        query.sort(key=lambda x: x.dated)

        context.update({
            'koyla': Koyla.objects.get(
                id=self.kwargs.get('koyla_id')),
            'start_date': start,
            'end_date': end,
            'koyla_ledgers': koyla_ledgers,
            'total_carriage': total_carriage,
            'total_amount': total_amount,
            'payment_amount': total_payment,
            'remaining_payment': total_payment - total_amount,
            'payments': payments,
            'query': query
        })
        return context
