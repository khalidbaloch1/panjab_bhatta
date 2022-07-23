from __future__ import unicode_literals

from django.views.generic import TemplateView, ListView, FormView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.db import transaction
from django.db.models import Sum

from batta_account.forms import (
    AccountForm, IncomeLedgerForm, OwnerLedgerForm
)

from batta_account.models import Account, IncomeLedger
from common.models import Season, Bhatta


class AddAccountFormView(FormView):
    template_name = 'accounts/add.html'
    form_class = AccountForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AddAccountFormView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        accounts = form.save(commit=False)
        accounts.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name')
        )
        accounts.save()
        return HttpResponseRedirect(reverse('account:list'))

    def form_invalid(self, form):
        return super(AddAccountFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(AddAccountFormView, self).get_context_data(**kwargs)
        bhatta_list = Bhatta.objects.all().order_by('name')
        context.update({
            'bhatta_list': bhatta_list,
        })
        return context


class AccountListView(ListView):
    template_name = 'accounts/list.html'
    model = Account
    paginate_by = 50
    bhatta = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AccountListView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = Account.objects.all().order_by('bhatta', 'name')
            if self.kwargs.get('bhatta') and not self.kwargs.get('bhatta') == 'Bhattas':
                self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
                queryset = queryset.filter(bhatta__name=self.bhatta).order_by('name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super(AccountListView, self).get_context_data(**kwargs)

        context.update({
            'bhattas': Bhatta.objects.all().order_by('-id'),
            'bhatta_kw': self.bhatta,
        })
        return context


class AccountUpdateView(UpdateView):
    form_class = AccountForm
    template_name = 'accounts/update.html'
    model = Account
    success_url = reverse_lazy('account:list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AccountUpdateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        accounts = form.save(commit=False)
        accounts.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name')
        )
        accounts.save()
        return super(AccountUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AccountUpdateView, self).get_context_data(**kwargs)
        bhatta_list = Bhatta.objects.all().order_by('name')
        context.update({
            'bhatta_list': bhatta_list,
        })
        return context


class AccountDeleteView(DeleteView):
    model = Account
    success_url = reverse_lazy('account:list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class CreditIncomeLedgerView(FormView):
    template_name = 'accounts/income/income_credit.html'
    form_class = IncomeLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CreditIncomeLedgerView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        credit = form.save()
        return HttpResponseRedirect(
                reverse('account:income_details', kwargs={'income_account_id': credit.account.id}))

    def get_context_data(self, **kwargs):
        context = super(
            CreditIncomeLedgerView, self).get_context_data(**kwargs)

        context.update({
            'bhatta': Bhatta.objects.all(),
            'seasons': Season.objects.all().order_by('season_year'),
            'account': Account.objects.get(id=self.kwargs.get('pk')),
        })
        return context


class DebitIncomeLedgerView(FormView):
    template_name = 'accounts/income/income_debit.html'
    form_class = IncomeLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            DebitIncomeLedgerView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        debit = form.save()
        return HttpResponseRedirect(
            reverse('account:income_details', kwargs={'income_account_id': debit.account.id}))

    def get_context_data(self, **kwargs):
        context = super(
            DebitIncomeLedgerView, self).get_context_data(**kwargs)

        context.update({
            'account': Account.objects.get(id=self.kwargs.get('pk')),
        })
        return context


class IncomeDetailsView(TemplateView):
    paginate_by = 50
    template_name = 'accounts/income/income_details.html'
    ordering = '-income_date'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                IncomeDetailsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            IncomeDetailsView, self).get_context_data(**kwargs)
        try:
            income_account = Account.objects.get(id=self.kwargs.get('income_account_id'))
        except Account.DoesNotExist:
            return Http404('IncomeAccount does not exists in database')

        income_accounts = income_account.income_ledger.all()

        if income_accounts.exists():
            income_credit_amount = income_accounts.aggregate(Sum('income_credit_amount'))
            income_debit_amount = income_accounts.aggregate(Sum('income_debit_amount'))

            income_credit_amount = float(income_credit_amount.get('income_credit_amount__sum'))
            income_debit_amount = float(income_debit_amount.get('income_debit_amount__sum'))
        else:
            income_credit_amount = 0
            income_debit_amount = 0

        context.update({
            'income_account': income_account,
            'income_accounts': income_accounts.order_by('-dated'),
            'seasons': Season.objects.all().order_by('-id'),
            'income_credit_amount': income_credit_amount,
            'income_debit_amount': income_debit_amount,
            'remaining_amount': income_credit_amount - income_debit_amount,
        })
        return context


class IncomeUpdateView(UpdateView):
    template_name = 'accounts/income/income_update.html'
    form_class = IncomeLedgerForm
    model = IncomeLedger

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(IncomeUpdateView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        credit = form.save()
        return HttpResponseRedirect(
                reverse('account:income_details', kwargs={'income_account_id': credit.account.id}))

    def get_context_data(self, **kwargs):
        context = super(
            IncomeUpdateView, self).get_context_data(**kwargs)

        context.update({
            'bhatta': Bhatta.objects.all().order_by('-id'),
            'seasons': Season.objects.all().order_by('season_year'),
        })
        return context


class CreditOwnerView(FormView):
    template_name = 'accounts/owner_account/owner_credit.html'
    form_class = OwnerLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CreditOwnerView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        owner_credit = form.save()
        return HttpResponseRedirect(
            reverse('account:owner_details', kwargs={'owner_account_id': owner_credit.account.id}))

    def get_context_data(self, **kwargs):
        context = super(
            CreditOwnerView, self).get_context_data(**kwargs)

        context.update({
            'bhatta': Bhatta.objects.all(),
            'seasons': Season.objects.all().order_by('season_year'),
            'account': Account.objects.get(id=self.kwargs.get('pk')),
        })
        return context


class DebitOwnerView(FormView):
    template_name = 'accounts/owner_account/owner_debit.html'
    form_class = OwnerLedgerForm

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            DebitOwnerView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        owner_debit = form.save()
        return HttpResponseRedirect(
            reverse('account:owner_details', kwargs={'owner_account_id': owner_debit.account.id}))

    def get_context_data(self, **kwargs):
        context = super(
            DebitOwnerView, self).get_context_data(**kwargs)

        context.update({
            'account': Account.objects.get(id=self.kwargs.get('pk')),
        })
        return context


class OwnerDetailsView(TemplateView):
    paginate_by = 50
    template_name = 'accounts/owner_account/owner_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                OwnerDetailsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            OwnerDetailsView, self).get_context_data(**kwargs)
        try:
            owner_account = Account.objects.get(id=self.kwargs.get('owner_account_id'))
        except Account.DoesNotExist:
            return Http404('Account does not exists in database')

        owner_accounts = owner_account.owner_ledger.all()

        if owner_accounts.exists():
            owner_credit_amount = owner_accounts.aggregate(Sum('owner_credit_amount'))
            owner_debit_amount = owner_accounts.aggregate(Sum('owner_debit_amount'))

            owner_credit_amount = float(owner_credit_amount.get('owner_credit_amount__sum'))
            owner_debit_amount = float(owner_debit_amount.get('owner_debit_amount__sum'))
        else:
            owner_credit_amount = 0
            owner_debit_amount = 0

        context.update({
            'owner_account': owner_account,
            'owner_accounts': owner_accounts.order_by('-owner_date'),
            'seasons': Season.objects.all().order_by('-id'),
            'owner_credit_amount': owner_credit_amount,
            'owner_debit_amount': owner_debit_amount,
            'remaining_amount': owner_credit_amount - owner_debit_amount,
        })
        return context
