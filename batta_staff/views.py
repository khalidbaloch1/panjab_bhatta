# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import ListView, FormView, UpdateView, TemplateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.db.models import Sum
from django.db import transaction

from common.models import Bhatta, Season

from .models import Staff, StaffLedger, StaffLedgerPayment, StaffAdvanceCredit
from .forms import (
    StaffForm, StaffLedgerForm,
    StaffLedgerPaymentForm, StaffAdvanceCreditForm, StaffOtherCreditForm, StaffOtherDebitForm
)


class StaffListView(ListView):
    model = Staff
    template_name = 'staff/staff_list.html'
    ordering = 'name'
    season = ''
    bhatta = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                StaffListView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = Staff.objects.all()

        if self.kwargs.get('season') and not self.kwargs.get('season') == 'Seasons':
            self.season = self.kwargs.get('season')

        if self.kwargs.get('bhatta') and not self.kwargs.get('bhatta') == 'Bhattas':
            self.bhatta = self.kwargs.get('bhatta').replace('%', ' ')
            queryset = queryset.filter(bhatta__name=self.bhatta)

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super(StaffListView, self).get_context_data(**kwargs)

        staffs = Staff.objects.filter(staff_type=Staff.STAFF_SALARY)

        staff_remaining_balance = 0
        for staff in staffs:
            staff_remaining_balance = (
                    staff_remaining_balance + staff.remaining_balance())

        staffs = Staff.objects.filter(staff_type=Staff.STAFF_WEEKLY)

        staff_remaining_amount = 0
        for staff in staffs:
            staff_remaining_amount = (
                    staff_remaining_amount + staff.remaining_amount())

        staffs = Staff.objects.filter(staff_type=Staff.STAFF_OTHER)

        staff_other_remaining_amount = 0
        for staff in staffs:
            staff_other_remaining_amount = (
                    staff_other_remaining_amount + staff.other_remaining_amount())

        if self.season and self.bhatta:
            staff_ledger = StaffLedger.objects.filter(
                staff__bhatta__name=self.bhatta,
                season__season_year=self.season
            )
        else:
            staff_ledger = StaffLedger.objects.all()

        if staff_ledger.exists():
            ledger_amount = staff_ledger.aggregate(Sum('amount'))
            ledger_amount = ledger_amount.get('amount__sum')
        else:
            ledger_amount = 0

        if self.season and self.bhatta:
            advance_staff_ledger = StaffAdvanceCredit.objects.filter(
                staff__bhatta__name=self.bhatta,
                season__season_year=self.season
            )
        else:
            advance_staff_ledger = StaffAdvanceCredit.objects.all()

        if advance_staff_ledger.exists():
            advance_amount = advance_staff_ledger.aggregate(
                Sum('net_payment'))
            advance_amount = advance_amount.get('net_payment__sum')
        else:
            advance_amount = 0

        if self.season and self.bhatta:
            ledger_payment = StaffLedgerPayment.objects.filter(
                staff__bhatta__name=self.bhatta,
                season__season_year=self.season
            )
        else:
            ledger_payment = StaffLedgerPayment.objects.all()

        if ledger_payment.exists():
            payment_amount = ledger_payment.aggregate(Sum('amount'))
            payment_amount = payment_amount.get('amount__sum')
        else:
            payment_amount = 0

        total_remaining_balance = (
                (ledger_amount + advance_amount) - payment_amount)

        context.update({
            'bhattas': Bhatta.objects.all().order_by('name'),
            'seasons': Season.objects.all().order_by('season_year'),
            'season_kw': self.season,
            'bhatta_kw': self.bhatta,
            'total_staff': self.get_queryset().count(),
            'remaining_balance': total_remaining_balance
        })
        return context


class CreateStaffView(FormView):
    template_name = 'staff/create_staff.html'
    form_class = StaffForm
    success_url = reverse_lazy('staff:list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                CreateStaffView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(CreateStaffView, self).get_context_data(**kwargs)
        context.update({
            'bhattas': Bhatta.objects.all().order_by('name'),
            'staff_model': Staff,
        })
        return context
    
    def form_valid(self, form):
        staff = form.save(commit=False)
        try:
            staff.bhatta = Bhatta.objects.get(
                name=self.request.POST.get('bhatta_name'))
        except:
            pass
        staff.save()
        return super(CreateStaffView, self).form_valid(form)
    
    def form_invalid(self, form):
        return super(CreateStaffView, self).form_invalid(form)


class StaffUpdateView(UpdateView):
    form_class = StaffForm
    model = Staff
    template_name = 'staff/update_staff.html'
    success_url = reverse_lazy('staff:list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                StaffUpdateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        staff = form.save(commit=False)
        staff.bhatta = Bhatta.objects.get(
            name=self.request.POST.get('bhatta_name'))
        staff.save()
        return super(StaffUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(StaffUpdateView, self).get_context_data(**kwargs)
        context.update({
            'staff_model': Staff
        })
        return context


class StaffCreditView(FormView):
    """
    Credit would be the Ledger of the Staff,
    Debit would be the ledger Payment of the Staff
    """
    form_class = StaffLedgerForm
    template_name = 'staff/normal_staff_credit.html'
    success_url = reverse_lazy('staff:list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                StaffCreditView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(StaffCreditView, self).get_context_data(**kwargs)
        context.update({
            'staff': Staff.objects.get(id=self.kwargs.get('pk')),
            'seasons': Season.objects.all().order_by('-season_year')
        })
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            credit = form.save()
            credit.season = Season.objects.get(
                season_year=self.request.POST.get('season_name'))
            credit.save()
            return HttpResponseRedirect(
                reverse('staff:details', kwargs={'pk': credit.staff.id}))


class StaffDebitView(FormView):
    """
    Credit would be the Ledger of the Staff,
    Debit would be the ledger Payment of the Staff
    """
    template_name = 'staff/normal_staff_debit.html'
    form_class = StaffLedgerPaymentForm
    success_url = reverse_lazy('staff:list')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                StaffDebitView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(StaffDebitView, self).get_context_data(**kwargs)
        context.update({
            'staff': Staff.objects.get(id=self.kwargs.get('pk')),
            'seasons': Season.objects.all().order_by('-id')
        })
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            debit = form.save()
            debit.season = Season.objects.get(
                season_year=self.request.POST.get('season_name'))
            debit.save()
            if debit.staff.staff_type == debit.staff.STAFF_WEEKLY:
                return HttpResponseRedirect(reverse(
                    'staff:details_advance',
                    kwargs={'pk': debit.staff.id}
                ))

            return HttpResponseRedirect(
                reverse('staff:details', kwargs={'pk': debit.staff.id}))


class NormalStaffDetailsView(TemplateView):
    template_name = 'staff/normal_staff_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                NormalStaffDetailsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(
            NormalStaffDetailsView, self).get_context_data(**kwargs)

        staff = Staff.objects.get(id=self.kwargs.get('pk'))

        staff_credit = staff.staff_ledger.all()
        staff_debit = staff.staff_ledger_payment.all()

        if staff_credit.exists():
            credit_amount = staff_credit.aggregate(Sum('amount'))
            credit_amount = float(credit_amount.get('amount__sum'))
        else:
            credit_amount = 0

        if staff_debit.exists():
            debit_amount = staff_debit.aggregate(Sum('amount'))
            debit_amount = float(debit_amount.get('amount__sum'))
        else:
            debit_amount = 0

        context.update({
            'staff': Staff.objects.get(id=self.kwargs.get('pk')),
            'staff_credit': staff_credit.order_by('-date_added'),
            'staff_debit': staff_debit.order_by('-payment_date'),
            'credit_amount': credit_amount,
            'debit_amount': debit_amount,
            'grand_total': debit_amount - credit_amount,
        })
        return context


class NormalStaffDetailsReportsView(TemplateView):
    template_name = 'staff/normal_staff_details_reports.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                NormalStaffDetailsReportsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(NormalStaffDetailsReportsView, self).get_context_data(**kwargs)
        staff = Staff.objects.get(id=self.kwargs.get('pk'))

        if self.kwargs.get('season'):
            staff_credit = staff.staff_ledger.filter(
                season__season_year=self.kwargs.get('season')
            )
            staff_debit = staff.staff_ledger_payment.filter(
                season__season_year=self.kwargs.get('season')
            )
            context.update({
                'season_kw': Season.objects.get(
                    season_year=self.kwargs.get('season')
                )
            })
        else:

            staff_credit = staff.staff_ledger.all()
            staff_debit = staff.staff_ledger_payment.all()

        if staff_credit.exists():
            credit_amount = staff_credit.aggregate(Sum('amount'))
            credit_amount = float(credit_amount.get('amount__sum'))
        else:
            credit_amount = 0

        if staff_debit.exists():
            debit_amount = staff_debit.aggregate(Sum('amount'))
            debit_amount = float(debit_amount.get('amount__sum'))
        else:
            debit_amount = 0

        context.update({
            'staff': Staff.objects.get(id=self.kwargs.get('pk')),
            'staff_credit': staff_credit.order_by('-date_added'),
            'staff_debit': staff_debit.order_by('-payment_date'),
            'credit_amount': credit_amount,
            'debit_amount': debit_amount,
            'grand_total': debit_amount - credit_amount,
            'seasons': Season.objects.all().order_by('-id')

        })
        return context


class AdvanceStaffCreditFormView(FormView):
    template_name = 'staff/advance_staff_credit.html'
    form_class = StaffAdvanceCreditForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AdvanceStaffCreditFormView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        with transaction.atomic():
            credit = form.save(commit=False)
            credit.season = Season.objects.get(
                season_year=self.request.POST.get('season_name'))
            credit.save()
            return HttpResponseRedirect(
                reverse('staff:details_advance', kwargs={'pk': credit.staff.id}))

    def get_context_data(self, **kwargs):
        context = super(
            AdvanceStaffCreditFormView, self).get_context_data(**kwargs)
        context.update({
            'staff': Staff.objects.get(id=self.kwargs.get('pk')),
            'seasons': Season.objects.all().order_by('-id')
        })
        return context


class AdvanceStaffCreditUpdateView(UpdateView):
    template_name = 'staff/advance_staff_credit_update.html'
    form_class = StaffAdvanceCreditForm
    model = StaffAdvanceCredit

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AdvanceStaffCreditUpdateView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        with transaction.atomic():
            credit = form.save(commit=False)
            credit.season = Season.objects.get(
                season_year=self.request.POST.get('season_name'))
            credit.save()
            return HttpResponseRedirect(
                reverse(
                    'staff:details_advance', kwargs={'pk': credit.staff.id}
                )
            )

    def get_context_data(self, **kwargs):
        context = super(
            AdvanceStaffCreditUpdateView, self).get_context_data(**kwargs)
        context.update({
            'seasons': Season.objects.all().order_by('-id')
        })
        return context


class AdvanceStaffDetails(TemplateView):
    template_name = 'staff/advance_staff_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                AdvanceStaffDetails, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(AdvanceStaffDetails, self).get_context_data(**kwargs)
        staff = Staff.objects.get(id=self.kwargs.get('pk'))

        if self.kwargs.get('season'):
            staff_credit = staff.staff_credit_advance.filter(
                season__season_year=self.kwargs.get('season')
            )
            staff_debit = staff.staff_ledger_payment.filter(
                season__season_year=self.kwargs.get('season')
            )
            context.update({
                'season_kw': Season.objects.get(
                    season_year=self.kwargs.get('season')
                )
            })
        else:
            staff_credit = staff.staff_credit_advance.all()
            staff_debit = staff.staff_ledger_payment.all()

        if staff_credit.exists():
            credit_net = staff_credit.aggregate(Sum('net_payment'))
            net_amount = float(credit_net.get('net_payment__sum'))

            total_bricks = staff_credit.aggregate(Sum('total_bricks'))
            total_bricks = float(total_bricks.get('total_bricks__sum'))

            weekly_kharcha = staff_credit.aggregate(Sum('weekly_amount'))
            weekly_kharcha = float(weekly_kharcha.get('weekly_amount__sum'))

        else:
            net_amount = 0
            total_bricks = 0
            weekly_kharcha = 0

        if staff_debit.exists():
            debit_amount = staff_debit.aggregate(Sum('amount'))
            debit_amount = float(debit_amount.get('amount__sum'))
        else:
            debit_amount = 0

        context.update({
            'staff': staff,
            'staff_credit': staff_credit.order_by('-date_added'),
            'staff_debit': staff_debit.order_by('-payment_date'),
            'total_bricks': total_bricks,
            'net_amount': net_amount,
            'payments': weekly_kharcha + debit_amount,
            'remaining_payment': net_amount - (weekly_kharcha + debit_amount),
            'debit_amount': debit_amount,
            'seasons': Season.objects.all().order_by('-id')
        })
        return context


class WeeklyStaffDetailsReportsView(TemplateView):
    template_name = 'staff/weekly_staff_details_reports.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                WeeklyStaffDetailsReportsView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(WeeklyStaffDetailsReportsView, self).get_context_data(**kwargs)
        staff = Staff.objects.get(id=self.kwargs.get('pk'))

        if self.kwargs.get('season'):
            staff_credit = staff.staff_credit_advance.filter(
                season__season_year=self.kwargs.get('season')
            )
            staff_debit = staff.staff_ledger_payment.filter(
                season__season_year=self.kwargs.get('season')
            )
            context.update({
                'season_kw': Season.objects.get(
                    season_year=self.kwargs.get('season')
                )
            })
        else:
            staff_credit = staff.staff_credit_advance.all()
            staff_debit = staff.staff_ledger_payment.all()

        if staff_credit.exists():
            credit_net = staff_credit.aggregate(Sum('net_payment'))
            net_amount = float(credit_net.get('net_payment__sum'))

            total_bricks = staff_credit.aggregate(Sum('total_bricks'))
            total_bricks = float(total_bricks.get('total_bricks__sum'))

            weekly_kharcha = staff_credit.aggregate(Sum('weekly_amount'))
            weekly_kharcha = float(weekly_kharcha.get('weekly_amount__sum'))

        else:
            net_amount = 0
            total_bricks = 0
            weekly_kharcha = 0

        if staff_debit.exists():
            debit_amount = staff_debit.aggregate(Sum('amount'))
            debit_amount = float(debit_amount.get('amount__sum'))
        else:
            debit_amount = 0

        context.update({
            'staff': staff,
            'staff_credit': staff_credit.order_by('-date_added'),
            'staff_debit': staff_debit.order_by('-payment_date'),
            'total_bricks': total_bricks,
            'net_amount': net_amount,
            'payments': weekly_kharcha + debit_amount,
            'remaining_payment': (weekly_kharcha + debit_amount) - net_amount,
            'debit_amount': debit_amount,
            'seasons': Season.objects.all().order_by('-id')
        })
        return context


class OtherStaffCreditFormView(FormView):
    template_name = 'staff/other_staff_credit.html'
    form_class = StaffOtherCreditForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                OtherStaffCreditFormView, self).dispatch(
                request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        with transaction.atomic():
            credit = form.save(commit=False)
            credit.season = Season.objects.get(
                season_year=self.request.POST.get('season_name'))
            credit.save()
            return HttpResponseRedirect(
                reverse('staff:details_other', kwargs={'pk': credit.staff.id}))

    def get_context_data(self, **kwargs):
        context = super(
            OtherStaffCreditFormView, self).get_context_data(**kwargs)
        context.update({
            'staff': Staff.objects.get(id=self.kwargs.get('pk')),
            'seasons': Season.objects.all().order_by('-id')
        })
        return context


class OtherStaffDebitView(FormView):
    template_name = 'staff/other_staff_debit.html'
    form_class = StaffOtherDebitForm
    success_url = reverse_lazy('staff:details_other')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                OtherStaffDebitView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def form_valid(self, form):
        with transaction.atomic():
            debit_other = form.save()
            debit_other.season = Season.objects.get(
                season_year=self.request.POST.get('season_name'))
            debit_other.save()
            return HttpResponseRedirect(
                reverse('staff:details_other', kwargs={'pk': debit_other.staff.id}))

    def get_context_data(self, **kwargs):
        context = super(OtherStaffDebitView, self).get_context_data(**kwargs)
        context.update({
            'staff': Staff.objects.get(id=self.kwargs.get('pk')),
            'seasons': Season.objects.all().order_by('-id')
        })
        return context


class OtherStaffDetails(TemplateView):
    template_name = 'staff/other_staff_details.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(
                OtherStaffDetails, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(OtherStaffDetails, self).get_context_data(**kwargs)
        staff = Staff.objects.get(id=self.kwargs.get('pk'))

        if self.kwargs.get('season'):
            staff_credit = staff.staff_credit_other.filter(
                season__season_year=self.kwargs.get('season')
            )
            staff_debit = staff.staff_debit_payment.filter(
                season__season_year=self.kwargs.get('season')
            )
            context.update({
                'season_kw': Season.objects.get(
                    season_year=self.kwargs.get('season')
                )
            })
        else:
            staff_credit = staff.staff_credit_other.all()
            staff_debit = staff.staff_debit_payment.all()

        if staff_credit.exists():
            credit_net = staff_credit.aggregate(Sum('total_payment'))
            net_amount = float(credit_net.get('total_payment__sum'))

            total_load = staff_credit.aggregate(Sum('total_load'))
            total_load = float(total_load.get('total_load__sum'))

        else:
            net_amount = 0
            total_load = 0

        if staff_debit.exists():
            debit_amount = staff_debit.aggregate(Sum('amount'))
            debit_amount = float(debit_amount.get('amount__sum'))
        else:
            debit_amount = 0

        context.update({
            'staff': staff,
            'staff_credit': staff_credit.order_by('-date_added'),
            'staff_debit': staff_debit.order_by('-payment_date'),
            'total_load': total_load,
            'net_amount': net_amount,
            'payments': debit_amount,
            'remaining_payment': net_amount - debit_amount,
            'debit_amount': debit_amount,
            'seasons': Season.objects.all().order_by('-id')
        })
        return context
