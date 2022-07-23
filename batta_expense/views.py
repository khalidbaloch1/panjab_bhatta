# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import (
    TemplateView, FormView, ListView, UpdateView, DeleteView
)
from django.http import HttpResponseRedirect
from django.db.models import Sum
from django.core.urlresolvers import reverse, reverse_lazy

from common.models import Bhatta, Season
from batta_stock.models import Stock

from .forms import (
    CoalExpenseForm, SeasonalExpenditureForm, SeasonalIncomeForm, SeasonalStockForm,
    ExpenditureAmountForm
)
from .models import (
    CoalExpense, SeasonalExpenditure, SeasonalIncome, ExpenditureAmount, SeasonalStock
)


class AddCoalExpenseFormView(FormView):
    template_name = 'expense/create_coal_expense.html'
    form_class = CoalExpenseForm
    success_url = reverse_lazy('expense:coal_list')

    def get_context_data(self, **kwargs):
        context = super(
            AddCoalExpenseFormView, self).get_context_data(**kwargs)
        context.update({
            'bhattas': Bhatta.objects.all().order_by('-id'),
            'seasons': Season.objects.all().order_by('-season_year')
        })
        return context

    def form_valid(self, form):
        coal_expense = form.save(commit=False)
        coal_expense.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name'))
        coal_expense.season = Season.objects.get(
            season_year=self.request.POST.get('season_year')
        )
        coal_expense.save()
        return super(AddCoalExpenseFormView, self).form_valid(form)
    
    def form_invalid(self, form):
        return super(AddCoalExpenseFormView, self).form_invalid(form)


class CoalExpenseListView(ListView):
    template_name = 'expense/coal_expense_list.html'
    model = CoalExpense
    paginate_by = 200
    ordering = '-added_date'
    season = ''
    bhatta = ''

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = CoalExpense.objects.all()

        if self.kwargs.get('season') and not self.kwargs.get(
                'season') == 'Seasons':
            self.season = self.kwargs.get('season')
            queryset = queryset.filter(
                season__season_year=self.kwargs.get('season'))

        if self.kwargs.get('bhatta') and not self.kwargs.get(
                'bhatta') == 'Bhattas':
            self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
            queryset = queryset.filter(bhatta__name=self.bhatta)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CoalExpenseListView, self).get_context_data(**kwargs)
        coal_expense = self.get_queryset()

        if coal_expense.exists():
            total_carriage = coal_expense.aggregate(Sum('carriage'))
            total_carriage = float(total_carriage.get('carriage__sum'))

            jamah_kiraya = coal_expense.aggregate(Sum('total_payment'))
            jamah_kiraya = float(jamah_kiraya.get('total_payment__sum'))

            wasol_kiraya = coal_expense.aggregate(Sum('received_amount'))
            wasol_kiraya = float(wasol_kiraya.get('received_amount__sum'))

            total_amount = coal_expense.aggregate(Sum('amount'))
            total_amount = float(total_amount.get('amount__sum'))

            grand_total = coal_expense.aggregate(Sum('total_amount'))
            grand_total = float(grand_total.get('total_amount__sum'))

        else:
            total_carriage = 0
            jamah_kiraya = 0
            wasol_kiraya = 0
            total_amount = 0
            grand_total = 0

        context.update({
            'total_carriage': total_carriage,
            'jamah_kiraya': jamah_kiraya,
            'wasol_kiraya': wasol_kiraya,
            'total_amount': total_amount,
            'grand_total': grand_total,
            'total_kiraya': jamah_kiraya + wasol_kiraya,
            'bhattas': Bhatta.objects.all().order_by('-name'),
            'seasons': Season.objects.all().order_by('-season_year'),
            'season_kw': self.season,
            'bhatta_kw': self.bhatta,
        })
        return context


class CoalExpenseUpdateView(UpdateView):
    template_name = 'expense/update_coal_expense.html'
    form_class = CoalExpenseForm
    model = CoalExpense
    success_url = reverse_lazy('expense:coal_list')

    def form_valid(self, form):
        coal_expense = form.save(commit=False)
        coal_expense.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name'))
        coal_expense.season = Season.objects.get(
            season_year=self.request.POST.get('season_year')
        )
        coal_expense.total_amount = self.request.POST.get('total_amount')
        coal_expense.save()
        return super(CoalExpenseUpdateView, self).form_valid(form)


class CoalExpenseDeleteView(DeleteView):
    model = CoalExpense
    success_url = reverse_lazy('expense:coal_list')


class AddKoylaAmountFormView(FormView):
    form_class = SeasonalStockForm
    template_name = 'expense/add_amount.html'
    success_url = reverse_lazy('expense:koyla_amount_list')

    def form_invalid(self, form):
        return super(AddKoylaAmountFormView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.season = Season.objects.get(
            season_year=self.request.POST.get('season_name')
        )
        obj.save()

        return super(AddKoylaAmountFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            AddKoylaAmountFormView, self).get_context_data(**kwargs)
        context.update({
            'bhattas': Bhatta.objects.all().order_by('name'),
            'seasons': Season.objects.all().order_by('-season_year'),
        })
        return context


class KoylaAmountListView(TemplateView):
    template_name = 'expense/koyla_amount_list.html'

    def get_context_data(self, **kwargs):
        context = super(
            KoylaAmountListView, self).get_context_data(**kwargs)


        context.update({

        })

        return context


class SeasonalExpenditureFormView(FormView):
    form_class = SeasonalExpenditureForm
    template_name = 'seasonal_reports/add_expenditures.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name'))
        obj.season = Season.objects.get(
            season_year=self.request.POST.get('season_name'))
        obj.save()
        return HttpResponseRedirect(reverse('expense:expense_list'))

    def form_invalid(self, form):
        return super(SeasonalExpenditureFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(
            SeasonalExpenditureFormView, self).get_context_data(**kwargs)
        context.update({
            'bhattas': Bhatta.objects.all().order_by('name'),
            'seasons': Season.objects.all().order_by('season_year'),
        })
        return context


class SeasonalExpenditureUpdateView(UpdateView):
    form_class = SeasonalExpenditureForm
    model = SeasonalExpenditure
    template_name = 'seasonal_reports/update_expenditures.html'
    success_url = reverse_lazy('expense:expense_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name'))
        obj.season = Season.objects.get(
            season_year=self.request.POST.get('season_name'))
        obj.save()
        return super(SeasonalExpenditureUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SeasonalExpenditureUpdateView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(
            SeasonalExpenditureUpdateView, self).get_context_data(**kwargs)
        context.update({
            'bhattas': Bhatta.objects.all().order_by('name'),
            'seasons': Season.objects.all().order_by('season_year'),
        })
        return context


class SeasonalExpenditureListView(ListView):
    model = SeasonalExpenditure
    template_name = 'seasonal_reports/expenditure_list.html'
    paginate_by = 200
    season = ''
    bhatta = ''

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = SeasonalExpenditure.objects.all()

        if self.kwargs.get('season') and not self.kwargs.get('season') == 'Seasons':
            self.season = self.kwargs.get('season')
            queryset = queryset.filter(season__season_year=self.kwargs.get('season'))

        if self.kwargs.get('bhatta') and not self.kwargs.get('bhatta') == 'Bhattas':
            self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
            queryset = queryset.filter(bhatta__name=self.bhatta)

        if not self.kwargs.get('bhatta') and not self.kwargs.get('season'):
            self.bhatta = Bhatta.objects.all().latest('id')

            self.bhatta = self.bhatta.name

        return queryset

    def get_context_data(self, **kwargs):
        context = super(
            SeasonalExpenditureListView, self).get_context_data(**kwargs)
        expense = self.get_queryset()
        expense_amount_list = ExpenditureAmount.objects.filter(
            expense=expense)

        if expense_amount_list.exists():
            total_amount = expense_amount_list.aggregate(Sum('amount'))
            total_amount = float(total_amount.get('amount__sum'))

        else:
            total_amount = 0

        context.update({
            'seasons': Season.objects.all().order_by('-season_year'),
            'bhattas': Bhatta.objects.all().order_by('-name'),
            'season_kw': self.season,
            'bhatta_kw': self.bhatta,
            'total_amount': total_amount,
        })
        return context


class SeasonalExpenditureDeleteView(DeleteView):
    model = SeasonalExpenditure
    success_url = reverse_lazy('expense:expense_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class SeasonalIncomeFormView(FormView):
    form_class = SeasonalIncomeForm
    template_name = 'seasonal_reports/add_income.html'
    success_url = reverse_lazy('expense:income_list')

    def form_invalid(self, form):
        return super(SeasonalIncomeFormView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name'))
        obj.season = Season.objects.get(
            season_year=self.request.POST.get('season_name')
        )
        obj.stock = Stock.objects.get(
            item_name=self.request.POST.get('stock_name'),
            bhatta__name=self.request.POST.get('bhatta_name')
        )
        obj.save()

        return super(SeasonalIncomeFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            SeasonalIncomeFormView, self).get_context_data(**kwargs)
        context.update({
            'bhattas': Bhatta.objects.all().order_by('name'),
            'seasons': Season.objects.all().order_by('season_year'),
            'stocks': Stock.objects.values_list(
                'item_name', flat=True).distinct()
        })
        return context


class SeasonalIncomeListView(ListView):
    model = SeasonalIncome
    template_name = 'seasonal_reports/income_list.html'
    paginate_by = 200
    season = ''
    bhatta = ''

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = SeasonalIncome.objects.all()

        if self.kwargs.get('season') and not self.kwargs.get(
                'season') == 'Seasons':
            self.season = self.kwargs.get('season')
            queryset = queryset.filter(
                season__season_year=self.kwargs.get('season'))

        if self.kwargs.get('bhatta') and not self.kwargs.get(
                'bhatta') == 'Bhattas':
            self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
            queryset = queryset.filter(bhatta__name=self.bhatta)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(
            SeasonalIncomeListView, self).get_context_data(**kwargs)

        context.update({
            'seasons': Season.objects.all().order_by('-season_year'),
            'bhattas': Bhatta.objects.all().order_by('-name'),
            'season_kw': self.season,
            'bhatta_kw': self.bhatta,
        })
        return context


class SeasonalIncomeDeleteView(DeleteView):
    model = SeasonalIncome
    success_url = reverse_lazy('expense:income_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ExpenditureAmountListView(TemplateView):
    template_name = 'seasonal_reports/expense_amount_list.html'

    def get_context_data(self, **kwargs):
        context = super(ExpenditureAmountListView, self).get_context_data(**kwargs)

        start = self.kwargs.get('start')
        end = self.kwargs.get('end')

        expense = SeasonalExpenditure.objects.get(pk=self.kwargs.get('pk'))
        expense_amount_list = ExpenditureAmount.objects.filter(
            expense=expense)

        if start and end:
            expense_amount_list = expense_amount_list.filter(
                added_date__range=[start, end]
            )

        if expense_amount_list.exists():
            total_amount = expense_amount_list.aggregate(Sum('amount'))
            total_amount = float(total_amount.get('amount__sum'))

        else:
            total_amount = 0

        context.update({
            'start_date': start,
            'end_date': end,
            'expense': expense,
            'total_amount': total_amount,
            'expense_amount_list': expense_amount_list
        })

        return context


class ExpenditureAmountFormView(FormView):
    template_name = 'seasonal_reports/expense_amount_add.html'
    form_class = ExpenditureAmountForm

    def form_valid(self, form):
        obj = form.save()
        return HttpResponseRedirect(
            reverse(
                'expense:expense_amount_details',
                kwargs={'pk': obj.expense.id}
            )
        )

    def get_context_data(self, **kwargs):
        context = super(
            ExpenditureAmountFormView, self).get_context_data(**kwargs)
        expense = SeasonalExpenditure.objects.get(pk=self.kwargs.get('pk'))
        context.update({
            'expense': expense,
        })
        return context


class ExpenditureAmountUpdateView(UpdateView):
    template_name = 'seasonal_reports/expense_amount_update.html'
    form_class = ExpenditureAmountForm
    model = ExpenditureAmount
    success_url = reverse_lazy('expense:expense_list')

    def form_valid(self, form):
        obj = form.save()
        return HttpResponseRedirect(
            reverse(
                'expense:expense_amount_details',
                kwargs={'pk': obj.expense.id}
            )
        )


class SeasonalStockFormView(FormView):
    form_class = SeasonalStockForm
    template_name = 'seasonal_reports/old_remaining_stock_add.html'
    success_url = reverse_lazy('expense:stock_list')

    def form_invalid(self, form):
        return super(SeasonalStockFormView, self).form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.season = Season.objects.get(
            season_year=self.request.POST.get('season_name')
        )
        obj.save()

        return super(SeasonalStockFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            SeasonalStockFormView, self).get_context_data(**kwargs)
        context.update({
            'bhattas': Bhatta.objects.all().order_by('name'),
            'seasons': Season.objects.all().order_by('-season_year'),
        })
        return context


class SeasonalStockDeleteView(DeleteView):
    model = SeasonalStock
    success_url = reverse_lazy('expense:stock_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class SeasonalStockListView(ListView):
    model = SeasonalStock
    template_name = 'seasonal_reports/stock_list.html'
    paginate_by = 200
    season = ''
    bhatta = ''

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = SeasonalStock.objects.all()

        if self.kwargs.get('season') and not self.kwargs.get(
                'season') == 'Seasons':
            self.season = self.kwargs.get('season')
            queryset = queryset.filter(
                season__season_year=self.kwargs.get('season'))

        if self.kwargs.get('bhatta') and not self.kwargs.get(
                'bhatta') == 'Bhattas':
            self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
            queryset = queryset.filter(bhatta__name=self.bhatta)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(
            SeasonalStockListView, self).get_context_data(**kwargs)

        context.update({
            'seasons': Season.objects.all().order_by('season_year'),
            'bhattas': Bhatta.objects.all().order_by('name'),
            'season_kw': self.season,
            'bhatta_kw': self.bhatta,
        })
        return context
