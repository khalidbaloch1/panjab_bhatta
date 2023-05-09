from __future__ import unicode_literals
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.views.generic import FormView, TemplateView, RedirectView
from django.core.urlresolvers import reverse, reverse_lazy

from django.http import HttpResponseRedirect
from django.utils import timezone
from django.db.models import Sum

from batta_staff.models import (
    Staff, StaffLedger, StaffLedgerPayment, StaffAdvanceCredit, StaffOtherCredit
)
from batta_sales.models import Invoice
from batta_customers.models import Customer, CustomerLedger, CustomerLedgerPayment
from common.models import Bhatta, Season

from batta_koylas.models import (
    KoylaLedger, KoylaLedgerPayment, Koyla
)
from other_expense.models import (OtherExpense, DieselLedger, MittiLedger)
from batta_account.models import (Account, IncomeLedger)

from batta_expense.models import (
    SeasonalExpenditure, ExpenditureAmount, SeasonalIncome, SeasonalStock
)

from batta_stock.models import PurchasedStock, Stock


class LoginView(FormView):
    template_name = 'login.html'
    form_class = auth_forms.AuthenticationForm
    success_url = reverse_lazy('common:index')

    def dispatch(self, request, *args, **kwargs):

        if self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('common:index'))

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)
        return HttpResponseRedirect(reverse('common:index'))

    def form_invalid(self, form):
        return super(LoginView, self).form_invalid(form)


class LogoutView(RedirectView):
    def dispatch(self, request, *args, **kwargs):
        auth_logout(self.request)
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('common:login'))


class IndexView(TemplateView):
    template_name = 'index.html'
    total_invoices = ''
    season = ''

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(IndexView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('common:login'))

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        total_staff = Staff.objects.filter(
            staff_type__in=[Staff.STAFF_WEEKLY, Staff.STAFF_SALARY]).count()

        invoices = Invoice.objects.all()
        customers = Customer.objects.filter(customer_type=Customer.TYPE_KHATA)

        customer_remaining_balance = 0
        for customer in customers:
            customer_remaining_balance = (
                customer_remaining_balance + customer.remaining_balance())

        bhattas = Bhatta.objects.all().order_by('name')
        seasons = Season.objects.all().order_by('season_year')

        if self.kwargs.get('season') and not self.kwargs.get('season') == 'Seasons':
            self.season = self.kwargs.get('season')
            season_kw = self.season
            self.season = Season.objects.get(season_year=self.season)
            invoices = invoices.filter(season__season_year=season_kw)
        else:
            season_kw = ''

        context.update({
            'total_staff': total_staff,
            'total_invoices': invoices.count(),
            'total_customers': customers.count(),
            'total_customer_balance': customer_remaining_balance,
            'today_date': timezone.now().date(),
            'bhattas': bhattas,
            'seasons': seasons,
            'season_kw': season_kw,
            'season': self.season

        })

        return context


class ReportsView(TemplateView):
    template_name = 'reports/reports.html'

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        seasonal_expenditures = SeasonalExpenditure.objects.filter(
            season__season_year=self.kwargs.get('season'),
        )

        seasonal_expense_ids = [s.id for s in seasonal_expenditures]

        expenditure = ExpenditureAmount.objects.filter(
            expense__in=seasonal_expense_ids)

        if expenditure.exists():
            expenditure_amount = expenditure.aggregate(Sum('amount'))
            expenditure_amount = float(expenditure_amount.get('amount__sum'))
        else:
            expenditure_amount = 0

        monthly_staff_ledger = StaffLedger.objects.filter(
            staff__staff_type=Staff.STAFF_SALARY,
            staff__expense_count=False,
            season__season_year=self.kwargs.get('season')
        )

        monthly_staff_payment = StaffLedgerPayment.objects.filter(
            staff__staff_type=Staff.STAFF_SALARY,
            season__season_year=self.kwargs.get('season')
        )

        if monthly_staff_ledger.exists():
            monthly_ledger_amount = monthly_staff_ledger.aggregate(
                Sum('amount'))
            monthly_ledger_amount = float(
                monthly_ledger_amount.get('amount__sum'))
        else:
            monthly_ledger_amount = 0

        total_monthly_expense = monthly_ledger_amount

        tractor_staff_ledger = StaffLedger.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Tractor'
        )

        tractor_staff_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Tractor'
        )

        if tractor_staff_ledger.exists():
            tractor_ledger_amount = tractor_staff_ledger.aggregate(
                Sum('amount'))
            tractor_ledger_amount = float(
                tractor_ledger_amount.get('amount__sum'))
        else:
            tractor_ledger_amount = 0

        total_tractor_expense = tractor_ledger_amount

        partai = StaffAdvanceCredit.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Partai'
        )
        partai_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Partai'
        )
        if partai.exists():
            partai_expense = partai.aggregate(Sum('net_payment'))
            partai_expense = float(
                partai_expense.get('net_payment__sum'))

            partai_quantity = partai.aggregate(Sum('total_bricks'))
            partai_quantity = float(
                partai_quantity.get('total_bricks__sum'))

            partai_weekly_kharcha = partai.aggregate(
                Sum('weekly_amount'))
            partai_weekly_kharcha = float(
                partai_weekly_kharcha.get('weekly_amount__sum'))

        else:
            partai_expense = 0
            partai_quantity = 0
            partai_weekly_kharcha = 0

        if partai_payment.exists():
            partai_payment_amount = partai_payment.aggregate(Sum('amount'))
            partai_payment_amount = float(
                partai_payment_amount.get('amount__sum'))
        else:
            partai_payment_amount = 0

        total_partai_expense = (
                partai_expense - (partai_payment_amount + partai_weekly_kharcha)
        )

        reet = StaffOtherCredit.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Reet'
        )
        reet_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Reet'
        )
        if reet.exists():
            reet_expense = reet.aggregate(Sum('total_payment'))
            reet_expense = float(
                reet_expense.get('total_payment__sum'))

            reet_quantity = reet.aggregate(Sum('total_load'))
            reet_quantity = float(
                reet_quantity.get('total_load__sum'))

        else:
            reet_expense = 0
            reet_quantity = 0

        if reet_payment.exists():
            reet_payment_amount = partai_payment.aggregate(Sum('amount'))
            reet_payment_amount = float(
                reet_payment_amount.get('amount__sum'))
        else:
            reet_payment_amount = 0

        total_reet_expense = (
                reet_expense - reet_payment_amount
        )

        petroleum = StaffAdvanceCredit.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Petroleum'
        )
        petroleum_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Petroleum'
        )
        if petroleum.exists():
            petroleum_expense = petroleum.aggregate(Sum('net_payment'))
            petroleum_expense = float(
                petroleum_expense.get('net_payment__sum'))

            petroleum_quantity = petroleum.aggregate(Sum('total_bricks'))
            petroleum_quantity = float(
                petroleum_quantity.get('total_bricks__sum'))

            petroleum_weekly_kharcha = petroleum.aggregate(
                Sum('weekly_amount'))
            petroleum_weekly_kharcha = float(
                petroleum_weekly_kharcha.get('weekly_amount__sum'))

        else:
            petroleum_expense = 0
            petroleum_quantity = 0
            petroleum_weekly_kharcha = 0

        if petroleum_payment.exists():
            petroleum_payment_amount = petroleum_payment.aggregate(Sum('amount'))
            petroleum_payment_amount = float(
                petroleum_payment_amount.get('amount__sum'))
        else:
            petroleum_payment_amount = 0

        total_petroleum_expense = (
                petroleum_expense - (petroleum_payment_amount + petroleum_weekly_kharcha)
        )

        nakasi = StaffAdvanceCredit.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Nakasi'
        )
        nakasi_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Nakasi'
        )
        if nakasi.exists():
            nakasi_expense = nakasi.aggregate(Sum('net_payment'))
            nakasi_expense = float(
                nakasi_expense.get('net_payment__sum'))

            nakasi_quantity = nakasi.aggregate(Sum('total_bricks'))
            nakasi_quantity = float(
                nakasi_quantity.get('total_bricks__sum'))

            nakasi_weekly_kharcha = nakasi.aggregate(
                Sum('weekly_amount'))
            nakasi_weekly_kharcha = float(
                nakasi_weekly_kharcha.get('weekly_amount__sum'))

        else:
            nakasi_expense = 0
            nakasi_quantity = 0
            nakasi_weekly_kharcha = 0

        if nakasi_payment.exists():
            nakasi_payment_amount = nakasi_payment.aggregate(Sum('amount'))
            nakasi_payment_amount = float(
                nakasi_payment_amount.get('amount__sum'))
        else:
            nakasi_payment_amount = 0

        total_nakasi_expense = (
            nakasi_expense - (nakasi_payment_amount + nakasi_weekly_kharcha)
        )

        bharai = StaffAdvanceCredit.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Bharai'
        )
        bharai_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Bharai'
        )
        if bharai.exists():
            bharai_expense = bharai.aggregate(Sum('net_payment'))
            bharai_expense = float(bharai_expense.get('net_payment__sum'))

            bharai_quantity = bharai.aggregate(Sum('total_bricks'))
            bharai_quantity = float(bharai_quantity.get('total_bricks__sum'))

            bharai_weekly_kharcha = bharai.aggregate(
                Sum('weekly_amount'))
            bharai_weekly_kharcha = float(
                bharai_weekly_kharcha.get('weekly_amount__sum'))
        else:
            bharai_expense = 0
            bharai_quantity = 0
            bharai_weekly_kharcha = 0

        if bharai_payment.exists():
            bharai_payment_amount = bharai_payment.aggregate(Sum('amount'))
            bharai_payment_amount = float(
                bharai_payment_amount.get('amount__sum'))
        else:
            bharai_payment_amount = 0

        total_bharai_expense = (
            bharai_expense - (bharai_payment_amount + bharai_weekly_kharcha)
        )

        pathair = StaffAdvanceCredit.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Pathair'
        )
        pathair_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='Pathair'
        )
        if pathair.exists():
            pathair_expense = pathair.aggregate(Sum('net_payment'))
            pathair_expense = float(
                pathair_expense.get('net_payment__sum'))

            pathair_quantity = pathair.aggregate(Sum('total_bricks'))
            pathair_quantity = float(
                pathair_quantity.get('total_bricks__sum'))

            pathair_weekly_kharcha = pathair.aggregate(
                Sum('weekly_amount'))
            pathair_weekly_kharcha = float(
                pathair_weekly_kharcha.get('weekly_amount__sum'))

        else:
            pathair_expense = 0
            pathair_quantity = 0
            pathair_weekly_kharcha = 0

        if pathair_payment.exists():
            pathair_payment_amount = pathair_payment.aggregate(Sum('amount'))
            pathair_payment_amount = float(
                pathair_payment_amount.get('amount__sum'))
        else:
            pathair_payment_amount = 0

        total_pathair_expense = (
            pathair_expense - (pathair_payment_amount + pathair_weekly_kharcha)
        )

        khari_mitti = StaffAdvanceCredit.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='khari_mitti'
        )
        khari_mitti_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.kwargs.get('season'),
            staff__designation='khari_mitti'
        )
        if khari_mitti.exists():
            khari_mitti_expense = khari_mitti.aggregate(Sum('net_payment'))
            khari_mitti_expense = float(khari_mitti_expense.get('net_payment__sum'))

            khari_mitti_quantity = khari_mitti.aggregate(Sum('total_bricks'))
            khari_mitti_quantity = float(khari_mitti_quantity.get('total_bricks__sum'))

            khari_mitti_weekly_kharcha = khari_mitti.aggregate(
                Sum('weekly_amount'))
            khari_mitti_weekly_kharcha = float(
                khari_mitti_weekly_kharcha.get('weekly_amount__sum'))
        else:
            khari_mitti_expense = 0
            khari_mitti_quantity = 0
            khari_mitti_weekly_kharcha = 0

        if khari_mitti_payment.exists():
            khari_mitti_payment_amount = khari_mitti_payment.aggregate(Sum('amount'))
            khari_mitti_payment_amount = float(
                khari_mitti_payment_amount.get('amount__sum'))
        else:
            khari_mitti_payment_amount = 0

        total_khari_mitti_expense = (
                khari_mitti_expense - (khari_mitti_payment_amount + khari_mitti_weekly_kharcha)

        )

        coal_expense = KoylaLedger.objects.filter(
            season__season_year=self.kwargs.get('season'),
            koyla__department='Koyla'
        )

        if coal_expense.exists():
            total_carriage = coal_expense.aggregate(Sum('carriage'))
            total_carriage = float(total_carriage.get('carriage__sum'))

            coal_total = coal_expense.aggregate(Sum('amount'))
            coal_total = float(coal_total.get('amount__sum'))

        else:
            total_carriage = 0
            coal_total = 0

        toh_expense = KoylaLedger.objects.filter(
            season__season_year=self.kwargs.get('season'),
            koyla__department='Toh'
        )

        if toh_expense.exists():
            toh_carriage = toh_expense.aggregate(Sum('carriage'))
            toh_carriage = float(toh_carriage.get('carriage__sum'))

            toh_total = toh_expense.aggregate(Sum('amount'))
            toh_total = float(toh_total.get('amount__sum'))

        else:
            toh_carriage = 0
            toh_total = 0

        total_expense_amount = (
            pathair_expense + bharai_expense + khari_mitti_expense +
            nakasi_expense + total_monthly_expense + coal_total + toh_total +
            expenditure_amount + reet_expense + petroleum_expense
        )

        '''
        Seasonal Income Details
        '''
        seasonal_stock = SeasonalStock.objects.filter(

            season__season_year=self.kwargs.get('season'),
        )

        if seasonal_stock.exists():
            stock_amount = seasonal_stock.aggregate(Sum('stock_amount'))
            stock_amount = float(stock_amount.get('stock_amount__sum'))
        else:
            stock_amount = 0

        '''
        Seasonal Income Details
        '''
        seasonal_income = SeasonalIncome.objects.filter(

            season__season_year=self.kwargs.get('season'),
        ).order_by('stock__item_name')

        if seasonal_income.exists():
            income_amount = seasonal_income.aggregate(Sum('total_amount'))
            income_amount = float(income_amount.get('total_amount__sum'))
        else:
            income_amount = 0

        '''
        Purchased Stock Details
        '''
        purchased_stocks = PurchasedStock.objects.filter(
            season__season_year=self.kwargs.get('season')
        )

        if purchased_stocks.exists():
            purchased_amount = purchased_stocks.aggregate(Sum('total_amount'))
            purchased_amount = float(
                purchased_amount.get('total_amount__sum'))
        else:
            purchased_amount = 0

        total_income_amount = purchased_amount + income_amount

        total_stock_amount = purchased_amount + income_amount - stock_amount

        stocks = Stock.objects.filter(
        )

        '''
        Total Profit
        '''
        profit = total_income_amount - total_expense_amount

        context.update({
            'seasons': Season.objects.filter(season_status=Season.TYPE_ACTIVATE).order_by('-season_year'),
            'season_kw': self.kwargs.get('season'),
            'seasonal_expenditures': seasonal_expenditures,
            'total_monthly_expense': total_monthly_expense,
            'total_tractor_expense': total_tractor_expense,
            'pathair_expense': pathair_expense,
            'pathair_quantity': pathair_quantity,
            'bharai_expense': bharai_expense,
            'bharai_quantity': bharai_quantity,
            'nakasi_expense': nakasi_expense,
            'nakasi_quantity': nakasi_quantity,
            'petroleum_expense': petroleum_expense,
            'petroleum_quantity': petroleum_quantity,
            'partai_expense': partai_expense,
            'partai_quantity': partai_quantity,
            'khari_mitti_expense': khari_mitti_expense,
            'khari_mitti_quantity': khari_mitti_quantity,
            'reet_expense': reet_expense,
            'reet_quantity': reet_quantity,
            'total_carriage': total_carriage,
            'coal_expense': coal_total,
            'toh_expense': toh_total,
            'toh_carriage': toh_carriage,
            'total_expense_qty': (
                pathair_quantity + khari_mitti_quantity + bharai_quantity + nakasi_quantity),
            'total_expense_amount': total_expense_amount,
            'seasonal_income': seasonal_income,
            'stocks': stocks,
            'total_income_amount': total_income_amount,
            'total_stock_amount': total_stock_amount,
            'stock_amount': stock_amount,
            'profit': profit - stock_amount

        })
        return context


class KhattaReportsView(TemplateView):
    template_name = 'reports/khatta_reports.html'

    def get_context_data(self, **kwargs):
        context = super(KhattaReportsView, self).get_context_data(**kwargs)

        customers = Customer.objects.filter(
            customer_status=Customer.TYPE_ACTIVATE,
            customer_type=Customer.TYPE_ADVANCE,
        )

        customer_advance_remaining_balance = 0
        for customer in customers:
            customer_advance_remaining_balance = (
                    customer_advance_remaining_balance + customer.remaining_balance()
            )

        customer_advance = customer_advance_remaining_balance

        khata_customer = Customer.objects.filter(
            customer_type=Customer.TYPE_KHATA,
            customer_status=Customer.TYPE_ACTIVATE,
        )

        customer_remaining_balance = 0
        for customer in khata_customer:
            customer_remaining_balance = (
                    customer_remaining_balance + customer.remaining_balance())

        customer_khata = customer_remaining_balance

        context.update({
            'customers': customers,
            'customer_advance': customer_advance,
            'khata_customer': khata_customer,
            'customer_khata': customer_khata,

        })

        return context


class QualityReportsView(TemplateView):
    template_name = 'reports/quality_wise_report.html'

    def get_context_data(self, **kwargs):
        context = super(QualityReportsView, self).get_context_data(**kwargs)

        start = self.request.GET.get('start_date')
        end = self.request.GET.get('end_date')

        seasonal_expenditures = SeasonalExpenditure.objects.filter(
            season__season_year=self.request.GET.get('season'),
        )

        seasonal_expense_ids = [s.id for s in seasonal_expenditures]

        expenditure = ExpenditureAmount.objects.filter(
            expense__in=seasonal_expense_ids)
        if start and end:
            expenditure = expenditure.filter(
                added_date__range=[start, end]
            )

        if expenditure.exists():
            expenditure_amount = expenditure.aggregate(Sum('amount'))
            expenditure_amount = float(expenditure_amount.get('amount__sum'))
        else:
            expenditure_amount = 0

        monthly_staff_ledger = StaffLedger.objects.filter(
            staff__staff_type=Staff.STAFF_SALARY,
            staff__expense_count=False,
            season__season_year=self.request.GET.get('season')
        )

        if start and end:
            monthly_staff_ledger = monthly_staff_ledger.filter(
                date_added__range=[start, end]
            )

        if monthly_staff_ledger.exists():
            monthly_ledger_amount = monthly_staff_ledger.aggregate(
                Sum('amount'))
            monthly_ledger_amount = float(
                monthly_ledger_amount.get('amount__sum'))
        else:
            monthly_ledger_amount = 0

        total_monthly_expense = monthly_ledger_amount

        nakasi = StaffAdvanceCredit.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__designation='Nakasi'
        )
        if start and end:
            nakasi = nakasi.filter(
                date_added__range=[start, end]
            )

        nakasi_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__designation='Nakasi'
        )
        if start and end:
            nakasi_payment = nakasi_payment.filter(
                payment_date__range=[start, end]
            )

        if nakasi.exists():
            nakasi_expense = nakasi.aggregate(Sum('net_payment'))
            nakasi_expense = float(nakasi_expense.get('net_payment__sum'))

            nakasi_weekly_kharcha = nakasi.aggregate(Sum('weekly_amount'))
            nakasi_weekly_kharcha = float(nakasi_weekly_kharcha.get('weekly_amount__sum'))

        else:
            nakasi_expense = 0
            nakasi_weekly_kharcha = 0

        if nakasi_payment.exists():
            nakasi_payment_amount = nakasi_payment.aggregate(Sum('amount'))
            nakasi_payment_amount = float(nakasi_payment_amount.get('amount__sum'))
        else:
            nakasi_payment_amount = 0

        bharai = StaffAdvanceCredit.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__designation='Bharai'
        )
        if start and end:
            bharai = bharai.filter(
                date_added__range=[start, end]
            )

        bharai_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__designation='Bharai'
        )
        if start and end:
            bharai_payment = bharai_payment.filter(
                payment_date__range=[start, end]
            )

        if bharai.exists():
            bharai_expense = bharai.aggregate(Sum('net_payment'))
            bharai_expense = float(bharai_expense.get('net_payment__sum'))

            bharai_weekly_kharcha = bharai.aggregate(Sum('weekly_amount'))
            bharai_weekly_kharcha = float(bharai_weekly_kharcha.get('weekly_amount__sum'))
        else:
            bharai_expense = 0
            bharai_weekly_kharcha = 0

        if bharai_payment.exists():
            bharai_payment_amount = bharai_payment.aggregate(Sum('amount'))
            bharai_payment_amount = float(bharai_payment_amount.get('amount__sum'))
        else:
            bharai_payment_amount = 0

        pathair = StaffAdvanceCredit.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__designation='Pathair'
        )
        if start and end:
            pathair = pathair.filter(
                date_added__range=[start, end]
            )
        pathair_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__designation='Pathair'
        )
        if start and end:
            pathair_payment = pathair_payment.filter(
                payment_date__range=[start, end]
            )

        if pathair.exists():
            pathair_expense = pathair.aggregate(Sum('net_payment'))
            pathair_expense = float(
                pathair_expense.get('net_payment__sum'))

            pathair_weekly_kharcha = pathair.aggregate(
                Sum('weekly_amount'))
            pathair_weekly_kharcha = float(
                pathair_weekly_kharcha.get('weekly_amount__sum'))

        else:
            pathair_expense = 0
            pathair_weekly_kharcha = 0

        if pathair_payment.exists():
            pathair_payment_amount = pathair_payment.aggregate(Sum('amount'))
            pathair_payment_amount = float(
                pathair_payment_amount.get('amount__sum'))
        else:
            pathair_payment_amount = 0

        khari_mitti = StaffAdvanceCredit.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__designation='khari_mitti'
        )
        if start and end:
            khari_mitti = khari_mitti.filter(
                date_added__range=[start, end]
            )

        khari_mitti_payment = StaffLedgerPayment.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__designation='khari_mitti'
        )
        if start and end:
            khari_mitti_payment = khari_mitti_payment.filter(
                payment_date__range=[start, end]
            )

        if khari_mitti.exists():
            khari_mitti_expense = khari_mitti.aggregate(Sum('net_payment'))
            khari_mitti_expense = float(
                khari_mitti_expense.get('net_payment__sum'))

            khari_mitti_weekly_kharcha = khari_mitti.aggregate(
                Sum('weekly_amount'))
            khari_mitti_weekly_kharcha = float(
                khari_mitti_weekly_kharcha.get('weekly_amount__sum'))
        else:
            khari_mitti_expense = 0
            khari_mitti_weekly_kharcha = 0

        if khari_mitti_payment.exists():
            khari_mitti_payment_amount = khari_mitti_payment.aggregate(
                Sum('amount'))
            khari_mitti_payment_amount = float(
                khari_mitti_payment_amount.get('amount__sum'))
        else:
            khari_mitti_payment_amount = 0

        '''
        Coala Expense
        '''

        koylas = Koyla.objects.filter()

        koyla_ledger_payment_ids = [s.id for s in koylas]

        koyla_ledger_payment = KoylaLedgerPayment.objects.filter(
            koyla__in=koyla_ledger_payment_ids)

        if start and end:
            koyla_ledger_payment = koyla_ledger_payment.filter(
                payment_date__range=[start, end]
            )

        if koyla_ledger_payment.exists():
            coal_total = koyla_ledger_payment.aggregate(Sum('amount'))
            coal_total = float(coal_total.get('amount__sum'))

        else:
            coal_total = 0

        '''Other Expense Diesel'''

        other_expense_mitti = OtherExpense.objects.filter()

        diesel_ledger_ids = [s.id for s in other_expense_mitti]

        diesel_ledger = DieselLedger.objects.filter(
            diesel_payment_type=DieselLedger.TYPE_DIESEL_DEBIT_AMOUNT,
            other_expense__in=diesel_ledger_ids)

        if start and end:
            diesel_ledger = diesel_ledger.filter(
                diesel_date__range=[start, end]
            )

        if diesel_ledger.exists():
            diesel_debit_amount = diesel_ledger.aggregate(Sum('diesel_debit_amount'))
            diesel_debit_amount = float(diesel_debit_amount.get('diesel_debit_amount__sum'))

        else:
            diesel_debit_amount = 0

        '''Other Expense Mitti'''

        other_expenses = OtherExpense.objects.filter()

        mitti_ledger_ids = [s.id for s in other_expenses]

        mitti_ledger = MittiLedger.objects.filter(
            mitti_payment_type=MittiLedger.TYPE_MITTI_DEBIT_AMOUNT,
            other_expense__in=mitti_ledger_ids)

        if start and end:
            mitti_ledger = mitti_ledger.filter(
                mitti_date__range=[start, end]
            )

        if mitti_ledger.exists():
            mitti_debit_amount = mitti_ledger.aggregate(Sum('mitti_debit_amount'))
            mitti_debit_amount = float(mitti_debit_amount.get('mitti_debit_amount__sum'))

        else:
            mitti_debit_amount = 0

        '''income account'''

        income_accounts = Account.objects.filter()

        income_ledger_ids = [s.id for s in income_accounts]

        income_ledger = IncomeLedger.objects.filter(
            income_payment_type=IncomeLedger.TYPE_INCOME_CREDIT_AMOUNT,
            account__in=income_ledger_ids)

        if start and end:
            income_ledger = income_ledger.filter(
                income_date__range=[start, end]
            )

        if income_ledger.exists():
            income_credit_amount = income_ledger.aggregate(Sum('income_credit_amount'))
            income_credit_amount = float(income_credit_amount.get('income_credit_amount__sum'))

        else:
            income_credit_amount = 0

        customer_ledger = Customer.objects.filter()

        customer_ledger_ids = [s.id for s in customer_ledger]

        customer_ledger = CustomerLedger.objects.filter(
            ledger_type=CustomerLedger.TYPE_LEDGER,
            customer__in=customer_ledger_ids)

        if start and end:
            customer_ledger = customer_ledger.filter(
                date_added__range=[start, end]
            )

        if customer_ledger.exists():
            total_customer_ledger = customer_ledger.aggregate(Sum('amount'))
            total_customer_ledger = float(total_customer_ledger.get('amount__sum'))
        else:
            total_customer_ledger = 0

        total_expense_amount = (
                pathair_weekly_kharcha + pathair_payment_amount +
                bharai_weekly_kharcha + bharai_payment_amount +
                khari_mitti_weekly_kharcha + khari_mitti_payment_amount +
                nakasi_weekly_kharcha + nakasi_payment_amount +
                total_monthly_expense + coal_total + total_customer_ledger +
                expenditure_amount + diesel_debit_amount + mitti_debit_amount
        )

        '''Staff Owner Payment Recived'''

        staff_ledger = StaffLedger.objects.filter(
            season__season_year=self.request.GET.get('season'),
            staff__expense_count=True
        )

        if start and end:
            staff_ledger = staff_ledger.filter(
                date_added__range=[start, end]
            )

        if staff_ledger.exists():
            total_ledger = staff_ledger.aggregate(Sum('amount'))
            total_ledger = float(
                total_ledger.get('amount__sum'))
        else:
            total_ledger = 0

        staff_expense = total_ledger

        stocks = PurchasedStock.objects.filter(
            stock__awal_count=True,
            season__season_year=self.request.GET.get('season')
        )
        if start and end:
            stocks = stocks.filter(
                added_date__range=[start, end]
            )

        if stocks.exists():
            awal_quantity = stocks.aggregate(Sum('quantity'))
            awal_quantity = float(awal_quantity.get('quantity__sum'))
        else:
            awal_quantity = 0

        stocks = PurchasedStock.objects.filter(
            stock__duyam_count=True,
            season__season_year=self.request.GET.get('season')
        )
        if start and end:
            stocks = stocks.filter(
                added_date__range=[start, end]
            )

        if stocks.exists():
            duyam_quantity = stocks.aggregate(Sum('quantity'))
            duyam_quantity = float(duyam_quantity.get('quantity__sum'))
        else:
            duyam_quantity = 0

        '''
            Rora Count
        '''
        stocks = PurchasedStock.objects.filter(
            stock__rora_count=True,
            season__season_year=self.request.GET.get('season')
        )
        if start and end:
            stocks = stocks.filter(
                added_date__range=[start, end]
            )

        if stocks.exists():
            rora_quantity = stocks.aggregate(Sum('quantity'))
            rora_quantity = float(rora_quantity.get('quantity__sum'))
        else:
            rora_quantity = 0

        pur_stock = PurchasedStock.objects.filter(
            stock__b_count=True,
            season__season_year=self.request.GET.get('season')
        )
        if start and end:
            pur_stock = pur_stock.filter(
                added_date__range=[start, end]
            )
        season = Season.objects.all()

        if pur_stock.exists():
            total_amount = pur_stock.aggregate(Sum('total_amount'))
            total_amount = float(total_amount.get('total_amount__sum'))

            total_quantity = pur_stock.aggregate(Sum('quantity'))
            total_quantity = float(total_quantity.get('quantity__sum'))
        else:
            total_amount = 0
            total_quantity = 0

        '''Staff Salary Expense'''

        staffs = Staff.objects.filter()

        staff_ledge_ids = [s.id for s in staffs]

        staff_ledger = StaffLedger.objects.filter(
            staff__in=staff_ledge_ids)

        if start and end:
            staff_ledger = staff_ledger.filter(
                date_added__range=[start, end]
            )

        if staff_ledger.exists():
            total_ledger = staff_ledger.aggregate(Sum('amount'))
            total_ledger = float(
                total_ledger.get('amount__sum'))
        else:
            total_ledger = 0

        '''Staff Weekly Expense'''

        staff_ledger_payment = StaffLedgerPayment.objects.filter(
            staff__staff_type=Staff.STAFF_WEEKLY,
            )

        if start and end:
            staff_ledger_payment = staff_ledger_payment.filter(
                payment_date__range=[start, end]
            )

        if staff_ledger_payment.exists():
            total_ledger_payment = staff_ledger_payment.aggregate(Sum('amount'))
            total_ledger_payment = float(
                total_ledger_payment.get('amount__sum'))
        else:
            total_ledger_payment = 0

        total_staff_amount = (
                total_ledger + total_ledger_payment
        )

        customers = Customer.objects.filter()

        customer_ledger_payment_ids = [s.id for s in customers]

        payments = CustomerLedgerPayment.objects.filter(
            customer__in=customer_ledger_payment_ids)

        if start and end:
            payments = payments.filter(
                payment_date__range=[start, end]
            )

        if payments.exists():
            total_payment = payments.aggregate(Sum('amount'))
            total_payment = float(total_payment.get('amount__sum'))
        else:
            total_payment = 0

        '''
        Purchased Invoice Details
        '''

        invoice = Invoice.objects.filter(
            season__season_year=self.request.GET.get('season'),
        )

        if start and end:
            invoice = invoice.filter(
                invoice_date__range=[start, end]
            )

        if invoice.exists():
            invoice_amount = invoice.aggregate(Sum('paid_amount'))
            invoice_amount = float(
                invoice_amount.get('paid_amount__sum'))
        else:
            invoice_amount = 0

        total_income_amount = invoice_amount + total_payment + income_credit_amount

        total_income = (
                total_payment + invoice_amount
        )

        '''
        Total Profit
        '''

        total_profit = total_income_amount - total_expense_amount

        profit = total_income_amount - (total_expense_amount + staff_expense)

        context.update({
            'total_expense_amount': total_expense_amount,
            'total_staff_amount': total_staff_amount,
            'season_kw': self.request.GET.get('season'),
            'seasons': Season.objects.filter().order_by('-season_year'),
            'expenditure': expenditure,
            'seasonal_expenditures': seasonal_expenditures,
            'total_monthly_expense': total_monthly_expense,
            'pathair_payment_amount': pathair_payment_amount,
            'pathair_weekly_kharcha': pathair_weekly_kharcha,
            'bharai_payment_amount': bharai_payment_amount,
            'bharai_weekly_kharcha': bharai_weekly_kharcha,
            'nakasi_payment_amount': nakasi_payment_amount,
            'nakasi_weekly_kharcha': nakasi_weekly_kharcha,
            'nakasi_expense': nakasi_expense,
            'khari_mitti_payment_amount': khari_mitti_payment_amount,
            'khari_mitti_weekly_kharcha': khari_mitti_weekly_kharcha,
            'other_expenses': other_expenses,
            'mitti_ledger': mitti_ledger,
            'mitti_debit_amount': mitti_debit_amount,
            'other_expense_mitti': other_expenses,
            'diesel_ledger': diesel_ledger,
            'diesel_debit_amount': diesel_debit_amount,
            'income_accounts': income_accounts,
            'income_ledger': income_ledger,
            'income_credit_amount': income_credit_amount,
            'koylas': koylas,
            'koyla_ledger_payment': koyla_ledger_payment,
            'coal_expense': coal_total,
            'total_income_amount': total_income_amount,
            'staff_expense': staff_expense,
            'profit': profit,
            'total_profit': total_profit,
            'stocks': stocks,
            'season': season,
            'pur_stock': pur_stock,
            'customers': customers,
            'payments': payments,
            'customer_ledger': customer_ledger,
            'total_customer_ledger': total_customer_ledger,
            'staffs': staffs,
            'staff_ledger': staff_ledger,
            'total_ledger': total_ledger,
            'staff_ledger_payment': staff_ledger_payment,
            'total_ledger_payment': total_ledger_payment,
            'total_payment': total_payment,
            'total_amount': total_amount,
            'total_quantity': total_quantity,
            'awal_quantity': awal_quantity,
            'duyam_quantity': duyam_quantity,
            'rora_quantity': rora_quantity,
            'invoice_amount': invoice_amount,
            'total_income': total_income,
            'start_date': self.request.GET.get('start_date'),
            'end_date': self.request.GET.get('end_date'),

        })

        return context


class TotalExpenseReportsView(TemplateView):
    template_name = 'reports/expense_reports.html'

    def get_context_data(self, **kwargs):
        context = super(TotalExpenseReportsView, self).get_context_data(**kwargs)

        start = self.request.GET.get('start_date')
        end = self.request.GET.get('end_date')

        '''Purchased Invoice Details'''

        invoice = Invoice.objects.filter(
            season__season_year=self.request.GET.get('season'),
        )

        if start and end:
            invoice = invoice.filter(
                invoice_date__range=[start, end]
            )

        if invoice.exists():
            invoice_amount = invoice.aggregate(Sum('paid_amount'))
            invoice_amount = float(
                invoice_amount.get('paid_amount__sum'))
        else:
            invoice_amount = 0

        customers = Customer.objects.filter()

        customer_ledger_payment_ids = [s.id for s in customers]

        customers = CustomerLedgerPayment.objects.filter(
            customer__in=customer_ledger_payment_ids)

        if start and end:
            customers = customers.filter(
                payment_date__range=[start, end]
            )

        if customers.exists():
            total_payment = customers.aggregate(Sum('amount'))
            total_payment = float(total_payment.get('amount__sum'))
        else:
            total_payment = 0

        '''Staff Salary Expense'''

        staffs = Staff.objects.filter()

        staff_ledge_ids = [s.id for s in staffs]

        staff_ledger = StaffLedger.objects.filter(
            staff__in=staff_ledge_ids)

        if start and end:
            staff_ledger = staff_ledger.filter(
                date_added__range=[start, end]
            )

        if staff_ledger.exists():
            total_ledger = staff_ledger.aggregate(Sum('amount'))
            total_ledger = float(
                total_ledger.get('amount__sum'))
        else:
            total_ledger = 0

        '''Staff Weekly Expense'''

        staff_ledger_payment = StaffLedgerPayment.objects.filter(
        )

        if start and end:
            staff_ledger_payment = staff_ledger_payment.filter(
                payment_date__range=[start, end]
            )

        if staff_ledger_payment.exists():
            total_ledger_payment = staff_ledger_payment.aggregate(Sum('amount'))
            total_ledger_payment = float(
                total_ledger_payment.get('amount__sum'))
        else:
            total_ledger_payment = 0

        seasonal_expenditures = SeasonalExpenditure.objects.filter(
            season__season_year=self.request.GET.get('season'),
        )

        seasonal_expense_ids = [s.id for s in seasonal_expenditures]

        expenditure = ExpenditureAmount.objects.filter(
            expense__in=seasonal_expense_ids)
        if start and end:
            expenditure = expenditure.filter(
                added_date__range=[start, end]
            )

        if expenditure.exists():
            expenditure_amount = expenditure.aggregate(Sum('amount'))
            expenditure_amount = float(expenditure_amount.get('amount__sum'))
        else:
            expenditure_amount = 0

        total_expense_amount = (
                total_ledger + total_ledger_payment + expenditure_amount
        )

        total_income = (
                total_payment + invoice_amount
        )

        remaining_amount = (
                total_income - total_expense_amount
        )

        context.update({
            'start_date': self.request.GET.get('start_date'),
            'end_date': self.request.GET.get('end_date'),
            'season_kw': self.request.GET.get('season'),
            'seasons': Season.objects.all().order_by('-season_year'),
            'invoice_amount': invoice_amount,
            'customers': customers,
            'total_payment': total_payment,
            'total_income': total_income,
            'staff_ledger': staff_ledger,
            'total_ledger': total_ledger,
            'staff_ledger_payment': staff_ledger_payment,
            'expenditure': expenditure,
            'seasonal_expenditures': seasonal_expenditures,
            'total_expense_amount': total_expense_amount,
            'remaining_amount': remaining_amount,

        })
        return context


class StaffJamahReportsView(TemplateView):
    template_name = 'reports/staff_jamah_reports.html'

    def get_context_data(self, **kwargs):
        context = super(StaffJamahReportsView, self).get_context_data(**kwargs)

        staffs = Staff.objects.filter(
            staff_type=Staff.STAFF_SALARY,
            staff_payment_action=Staff.TYPE_JAMAH,
        )

        staff_remaining_balance = 0
        for staff in staffs:
            staff_remaining_balance = (
                    staff_remaining_balance + staff.remaining_balance())

        staff_jamah = staff_remaining_balance

        staff_banam = Staff.objects.filter(
            staff_type=Staff.STAFF_SALARY,
            staff_payment_action=Staff.TYPE_BANAM,
        )

        staff_remaining_balance = 0
        for staff in staff_banam:
            staff_remaining_balance = (
                    staff_remaining_balance + staff.remaining_balance())

        staff_banam_payment = staff_remaining_balance

        weekly_staff_jamah = Staff.objects.filter(
            staff_type=Staff.STAFF_WEEKLY,
            staff_payment_action=Staff.TYPE_JAMAH,
        )

        weekly_staff_remaining_amount = 0
        for staff in weekly_staff_jamah:
            weekly_staff_remaining_amount = (
                    weekly_staff_remaining_amount + staff.remaining_amount())

        weekly_staff_jamah_amount = weekly_staff_remaining_amount

        weekly_staff_banam = Staff.objects.filter(
            staff_type=Staff.STAFF_WEEKLY,
            staff_payment_action=Staff.TYPE_BANAM,
        )

        weekly_staff_remaining_amount = 0
        for staff in weekly_staff_banam:
            weekly_staff_remaining_amount = (
                    weekly_staff_remaining_amount + staff.remaining_amount())

        weekly_staff_banam_amount = weekly_staff_remaining_amount

        total_jamah_amount = (
                staff_jamah + weekly_staff_jamah_amount
        )

        total_banam_amount = (
                staff_banam_payment + weekly_staff_banam_amount
        )

        context.update({
            'staffs': staffs,
            'staff_jamah': staff_jamah,
            'staff_banam': staff_banam,
            'staff_banam_payment': staff_banam_payment,
            'weekly_staff_jamah': weekly_staff_jamah,
            'weekly_staff_jamah_amount': weekly_staff_jamah_amount,
            'weekly_staff_banam': weekly_staff_banam,
            'weekly_staff_banam_amount': weekly_staff_banam_amount,
            'total_jamah_amount': total_jamah_amount,
            'total_banam_amount': total_banam_amount

        })

        return context
