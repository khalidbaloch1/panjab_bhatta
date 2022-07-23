# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView, FormView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.db import transaction
from django.contrib import messages
from django.db.models import Sum

from other_expense.forms import (
    OtherExpenseForm, DieselLedgerForm, MittiLedgerForm
)

from other_expense.models import OtherExpense, DieselLedger, MittiLedger
from common.models import Season, Bhatta


class AddOtherExpenseFormView(FormView):
    template_name = 'other_expenses/add.html'
    form_class = OtherExpenseForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AddOtherExpenseFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        other_expense = form.save(commit=False)
        other_expense.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name')
        )
        other_expense.save()
        return HttpResponseRedirect(reverse('other_expense:list'))

    def form_invalid(self, form):
        return super(AddOtherExpenseFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(AddOtherExpenseFormView, self).get_context_data(**kwargs)
        bhatta_list = Bhatta.objects.all().order_by('name')
        context.update({
            'bhatta_list': bhatta_list,
        })
        return context


class OtherExpenses(ListView):
    template_name = 'other_expenses/list.html'
    model = OtherExpense
    paginate_by = 100
    bhatta = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                OtherExpenses, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = OtherExpense.objects.all().order_by('bhatta', 'name')
            if self.kwargs.get('bhatta') and not self.kwargs.get('bhatta') == 'Bhattas':
                self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
                queryset = queryset.filter(bhatta__name=self.bhatta).order_by('name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super(OtherExpenses, self).get_context_data(**kwargs)

        context.update({
            'bhattas': Bhatta.objects.all().order_by('-id'),
            'bhatta_kw': self.bhatta,
        })
        return context


class OtherExpenseUpdateView(UpdateView):
    form_class = OtherExpenseForm
    template_name = 'other_expenses/update.html'
    model = OtherExpense
    success_url = reverse_lazy('other_expense:list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                OtherExpenseUpdateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        other_expenses = form.save(commit=False)
        other_expenses.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name')
        )
        other_expenses.save()
        return super(OtherExpenseUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(OtherExpenseUpdateView, self).get_context_data(**kwargs)
        bhatta_list = Bhatta.objects.all().order_by('name')
        context.update({
            'bhatta_list': bhatta_list,
        })
        return context


class OtherExpenseDeleteView(DeleteView):
    model = OtherExpense
    success_url = reverse_lazy('other_expense:list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class DebitDieselLedgerView(FormView):
    template_name = 'other_expenses/diesel/diesel_debit.html'
    form_class = DieselLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            DebitDieselLedgerView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        debit = form.save()
        return HttpResponseRedirect(
            reverse('other_expense:diesel_details', kwargs={'pk': debit.other_expense.id}))

    def get_context_data(self, **kwargs):
        context = super(
            DebitDieselLedgerView, self).get_context_data(**kwargs)

        context.update({
            'other_expense': OtherExpense.objects.get(id=self.kwargs.get('pk')),
        })
        return context


class CreditDieselLedgerView(FormView):
    template_name = 'other_expenses/diesel/diesel_credit.html'
    form_class = DieselLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CreditDieselLedgerView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
            credit = form.save()
            return HttpResponseRedirect(
                reverse('other_expense:diesel_details', kwargs={'pk': credit.other_expense.id}))

    def get_context_data(self, **kwargs):
        context = super(
            CreditDieselLedgerView, self).get_context_data(**kwargs)

        context.update({
            'bhatta': Bhatta.objects.all(),
            'seasons': Season.objects.all().order_by('season_year'),
            'other_expense': OtherExpense.objects.get(id=self.kwargs.get('pk')),
        })
        return context


class DieselDetailsView(TemplateView):
    paginate_by = 50
    template_name = 'other_expenses/diesel/diesel_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                DieselDetailsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            DieselDetailsView, self).get_context_data(**kwargs)
        try:
            other_expense = OtherExpense.objects.get(id=self.kwargs.get('pk'))
        except OtherExpense.DoesNotExist:
            return Http404('OtherExpense does not exists in database')

        diesels = other_expense.diesel_ledger.all()

        if diesels.exists():
            amount_per_ltr = diesels.aggregate(Sum('amount_per_ltr'))
            total_amount = diesels.aggregate(Sum('total_amount'))
            ltr = diesels.aggregate(Sum('ltr'))
            diesel_debit_amount = diesels.aggregate(Sum('diesel_debit_amount'))

            amount_per_ltr = float(amount_per_ltr.get('amount_per_ltr__sum'))
            total_amount = float(total_amount.get('total_amount__sum'))
            ltr = float(ltr.get('ltr__sum'))
            diesel_debit_amount = float(diesel_debit_amount.get('diesel_debit_amount__sum'))
        else:
            amount_per_ltr = 0
            total_amount = 0
            ltr = 0
            diesel_debit_amount = 0

        context.update({
            'other_expense': other_expense,
            'diesels': diesels.order_by('-diesel_date'),
            'seasons': Season.objects.all().order_by('-id'),
            'amount_per_ltr': amount_per_ltr,
            'total_amount': total_amount,
            'diesel_debit_amount': diesel_debit_amount,
            'ltr': ltr,
            'remaining_amount': total_amount - diesel_debit_amount,
        })
        return context


class DieselUpdateView(UpdateView):
    template_name = 'other_expenses/diesel/diesel_update.html'
    form_class = DieselLedgerForm
    model = DieselLedger

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(DieselUpdateView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        with transaction.atomic():
            credit = form.save(commit=False)
            credit.season = Season.objects.get(
                season_year=self.request.POST.get('season_name'))
            credit.bhatta = Bhatta.objects.get(
                name=self.request.POST.get('bhatta_name'))
            credit.save()
            return HttpResponseRedirect(
                reverse('other_expense:diesel_details', kwargs={'pk': credit.other_expense.id}))

    def get_context_data(self, **kwargs):
        context = super(DieselUpdateView, self).get_context_data(**kwargs)

        context.update({
            'bhattas': Bhatta.objects.all().order_by('-id'),
            'seasons': Season.objects.all().order_by('id'),
        })
        return context


def DeleteDieselLedger(request, pk):

    DieselLedger.objects.get(pk=pk).delete()

    messages.success(request, 'Success Fully Deleted')
    return HttpResponseRedirect(reverse('other_expense:list'))


class DieselInvoicesView(TemplateView):
    template_name = 'other_expenses/diesel/diesel_reports.html'

    def get_context_data(self, **kwargs):
        context = super(DieselInvoicesView, self).get_context_data(**kwargs)

        start = self.kwargs.get('start')
        end = self.kwargs.get('end')

        diesel = DieselLedger.objects.filter(
            other_expense__id=self.kwargs.get('other_expense_id')
        ).order_by('-diesel_date')

        if start and end:
            diesel = diesel.filter(
                diesel_date__range=[start, end]
            )

        if diesel.exists():
            amount_per_ltr = diesel.aggregate(Sum('amount_per_ltr'))
            total_amount = diesel.aggregate(Sum('total_amount'))
            ltr = diesel.aggregate(Sum('ltr'))
            diesel_debit_amount = diesel.aggregate(Sum('diesel_debit_amount'))

            amount_per_ltr = float(amount_per_ltr.get('amount_per_ltr__sum'))
            total_amount = float(total_amount.get('total_amount__sum'))
            ltr = float(ltr.get('ltr__sum'))
            diesel_debit_amount = float(diesel_debit_amount.get('diesel_debit_amount__sum'))
        else:
            amount_per_ltr = 0
            total_amount = 0
            ltr = 0
            diesel_debit_amount = 0

        context.update({
            'other_expense': OtherExpense.objects.get(
                id=self.kwargs.get('other_expense_id')),
            'diesel': diesel,
            'start_date': start,
            'end_date': end,
            'amount_per_ltr': amount_per_ltr,
            'total_amount': total_amount,
            'diesel_debit_amount': diesel_debit_amount,
            'ltr': ltr,
            'remaining_amount': total_amount - diesel_debit_amount,
        })
        return context


class DebitMittiLedgerView(FormView):
    template_name = 'other_expenses/mitti/mitti_debit.html'
    form_class = MittiLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            DebitMittiLedgerView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        debit = form.save()
        return HttpResponseRedirect(
            reverse('other_expense:mitti_details', kwargs={'pk': debit.other_expense.id}))

    def get_context_data(self, **kwargs):
        context = super(
            DebitMittiLedgerView, self).get_context_data(**kwargs)

        context.update({
            'other_expense': OtherExpense.objects.get(id=self.kwargs.get('pk')),
        })
        return context


class CreditMittiLedgerView(FormView):
    template_name = 'other_expenses/mitti/mitti_credit.html'
    form_class = MittiLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CreditMittiLedgerView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
            mitti_credit = form.save()
            return HttpResponseRedirect(
                reverse('other_expense:mitti_details', kwargs={'pk': mitti_credit.other_expense.id}))

    def get_context_data(self, **kwargs):
        context = super(
            CreditMittiLedgerView, self).get_context_data(**kwargs)

        context.update({
            'bhatta': Bhatta.objects.all(),
            'seasons': Season.objects.all().order_by('season_year'),
            'other_expense': OtherExpense.objects.get(id=self.kwargs.get('pk')),
        })
        return context


class MittiDetailsView(TemplateView):
    paginate_by = 50
    template_name = 'other_expenses/mitti/mitti_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                MittiDetailsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            MittiDetailsView, self).get_context_data(**kwargs)
        try:
            other_expense = OtherExpense.objects.get(id=self.kwargs.get('pk'))
        except OtherExpense.DoesNotExist:
            return Http404('OtherExpense does not exists in database')

        mittis = other_expense.mitti_ledger.all()

        if mittis.exists():
            amount_per_load = mittis.aggregate(Sum('amount_per_load'))
            total_amount = mittis.aggregate(Sum('total_amount'))
            total_load = mittis.aggregate(Sum('total_load'))
            mitti_debit_amount = mittis.aggregate(Sum('mitti_debit_amount'))

            amount_per_load = float(amount_per_load.get('amount_per_load__sum'))
            total_amount = float(total_amount.get('total_amount__sum'))
            total_load = float(total_load.get('total_load__sum'))
            mitti_debit_amount = float(mitti_debit_amount.get('mitti_debit_amount__sum'))
        else:
            amount_per_load = 0
            total_amount = 0
            total_load = 0
            mitti_debit_amount = 0

        context.update({
            'other_expense': other_expense,
            'mittis': mittis.order_by('-mitti_date'),
            'seasons': Season.objects.all().order_by('-id'),
            'amount_per_load': amount_per_load,
            'total_amount': total_amount,
            'mitti_debit_amount': mitti_debit_amount,
            'total_load': total_load,
            'remaining_amount': total_amount - mitti_debit_amount,
        })
        return context


class MittiUpdateView(UpdateView):
    template_name = 'other_expenses/mitti/mitti_update.html'
    form_class = MittiLedgerForm
    model = MittiLedger

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(MittiUpdateView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        with transaction.atomic():
            mitti_credit = form.save(commit=False)
            mitti_credit.season = Season.objects.get(
                season_year=self.request.POST.get('season_name'))
            mitti_credit.bhatta = Bhatta.objects.get(
                name=self.request.POST.get('bhatta_name'))
            mitti_credit.save()
            return HttpResponseRedirect(
                reverse(
                    'other_expense:mitti_details', kwargs={'pk': mitti_credit.other_expense.id}
                )
            )

    def get_context_data(self, **kwargs):
        context = super(MittiUpdateView, self).get_context_data(**kwargs)

        context.update({
            'bhattas': Bhatta.objects.all().order_by('-id'),
            'seasons': Season.objects.all().order_by('id'),
        })
        return context


def DeleteMittidebit(request, pk):

    MittiLedger.objects.get(pk=pk).delete()

    messages.success(request, 'Success Fully Deleted')
    return HttpResponseRedirect(reverse('other_expense:list'))


class MittiInvoicesView(TemplateView):
    template_name = 'other_expenses/mitti/mitti_reports.html'

    def get_context_data(self, **kwargs):
        context = super(MittiInvoicesView, self).get_context_data(**kwargs)

        start = self.kwargs.get('start')
        end = self.kwargs.get('end')

        mitti = MittiLedger.objects.filter(
            other_expense__id=self.kwargs.get('other_expense_id')
        ).order_by('-mitti_date')

        if start and end:
            mitti = mitti.filter(
                mitti_date__range=[start, end]
            )

        if mitti.exists():
            amount_per_load = mitti.aggregate(Sum('amount_per_load'))
            total_amount = mitti.aggregate(Sum('total_amount'))
            total_load = mitti.aggregate(Sum('total_load'))
            mitti_debit_amount = mitti.aggregate(Sum('mitti_debit_amount'))

            amount_per_load = float(amount_per_load.get('amount_per_load__sum'))
            total_amount = float(total_amount.get('total_amount__sum'))
            total_load = float(total_load.get('total_load__sum'))
            mitti_debit_amount = float(mitti_debit_amount.get('mitti_debit_amount__sum'))
        else:
            amount_per_load = 0
            total_amount = 0
            total_load = 0
            mitti_debit_amount = 0

        context.update({
            'other_expense': OtherExpense.objects.get(
                id=self.kwargs.get('other_expense_id')),
            'mitti': mitti,
            'start_date': start,
            'end_date': end,
            'amount_per_load': amount_per_load,
            'total_amount': total_amount,
            'mitti_debit_amount': mitti_debit_amount,
            'total_load': total_load,
            'remaining_amount': total_amount - mitti_debit_amount,
        })
        return context
