from __future__ import unicode_literals
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from common.models import Season


class Staff(models.Model):
    STAFF_SALARY = 'Salary Staff'
    STAFF_WEEKLY = 'Weekly Staff'
    STAFF_OTHER = 'Other Staff'
    STAFF_PETROLEUM = 'Petroleum Staff'
    STAFF_MULTIPLE = 'Multiple Staff'

    STAFF_TYPES = (
        (STAFF_SALARY, 'Salary Staff'),
        (STAFF_WEEKLY, 'Weekly Staff'),
        (STAFF_OTHER, 'Other Staff'),
        (STAFF_PETROLEUM, 'Petroleum Staff'),
        (STAFF_MULTIPLE, 'Multiple Staff'),
    )

    TYPE_JAMAH = 'Jamah'
    TYPE_BANAM = 'Banam'

    STAFF_PAYMENT_ACTION = (
        (TYPE_JAMAH, 'Jamah'),
        (TYPE_BANAM, 'Banam'),
    )

    staff_payment_action = models.CharField(max_length=100, choices=STAFF_PAYMENT_ACTION, blank=True, null=True)

    bhatta = models.ForeignKey(
        'common.Bhatta', related_name='staf_bhatta', blank=True, null=True
    )
    staff_code = models.CharField(
        max_length=5, unique=True, blank=True, null=True)
    name = models.CharField(
        max_length=200
    )
    father_name = models.CharField(
        max_length=200, blank=True, null=True
    )
    staff_type = models.CharField(
        max_length=100, blank=True, null=True,
        choices=STAFF_TYPES, default=STAFF_SALARY,
    )
    designation = models.CharField(
        max_length=100, blank=True, null=True
    )
    cnic = models.CharField(
        max_length=20, blank=True, null=True
    )
    mobile_no = models.CharField(
        max_length=20, blank=True, null=True
    )
    rate = models.CharField(
        max_length=20, blank=True, null=True
    )
    joining_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )
    leaving_date = models.DateField(
        blank=True, null=True
    )
    details = models.TextField(
        max_length=500, blank=True, null=True
    )
    expense_count = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def staff_ledger_balance(self):
        staff_credit = self.staff_ledger.all()
        if staff_credit.exists():
            credit_amount = staff_credit.aggregate(Sum('amount'))
            credit_amount = float(credit_amount.get('amount__sum'))
        else:
            credit_amount = 0

        return credit_amount

    def ledger_payment_balance(self):
        staff_debit = self.staff_ledger_payment.all()
        if staff_debit.exists():
            debit_amount = staff_debit.aggregate(Sum('amount'))
            debit_amount = float(debit_amount.get('amount__sum'))
        else:
            debit_amount = 0

        return debit_amount

    def remaining_balance(self):
        return self.ledger_payment_balance() - self.staff_ledger_balance()

    def staff_advance_credit(self):
        staff_credit = self.staff_credit_advance.all()
        if staff_credit.exists():
            credit_net = staff_credit.aggregate(Sum('net_payment'))
            net_amount = float(credit_net.get('net_payment__sum'))

        else:
            net_amount = 0

        return net_amount

    def staff_advance(self):
        staff_credit = self.staff_credit_advance.all()
        if staff_credit.exists():
            weekly_kharcha = staff_credit.aggregate(Sum('weekly_amount'))
            weekly_kharcha = float(weekly_kharcha.get('weekly_amount__sum'))
        else:
            weekly_kharcha = 0

        return weekly_kharcha

    def ledger_balance(self):
        debit = self.staff_ledger_payment.all()
        if debit.exists():
            debit = debit.aggregate(Sum('amount'))
            debit = float(debit.get('amount__sum'))
        else:
            debit = 0

        return debit

    def remaining_amount(self):
        return self.staff_advance() + self.ledger_balance() - self.staff_advance_credit()

    def staff_other_credit(self):
        staff_credit = self.staff_credit_other.all()
        if staff_credit.exists():
            credit_net = staff_credit.aggregate(Sum('total_payment'))
            total_amount = float(credit_net.get('total_payment__sum'))

        else:
            total_amount = 0

        return total_amount

    def staff_other_debit(self):
        debit = self.staff_debit_payment.all()
        if debit.exists():
            debit = debit.aggregate(Sum('amount'))
            debit = float(debit.get('amount__sum'))
        else:
            debit = 0

        return debit

    def other_remaining_amount(self):
        return self.staff_other_debit() - self.staff_other_credit()

    def remaining_pay(self):
        return self.ledger_payment_balance() - self.staff_ledger_balance()


class StaffLedger(models.Model):
    staff = models.ForeignKey(Staff, related_name='staff_ledger')
    season = models.ForeignKey(
        Season, related_name='salary_credit_season',
        blank=True, null=True
    )
    amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    page_no = models.CharField(max_length=100, blank=True, null=True)
    details = models.CharField(max_length=500, blank=True, null=True)
    date_added = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.staff.name if self.staff else ''


class StaffLedgerPayment(models.Model):
    staff = models.ForeignKey(
        Staff, related_name='staff_ledger_payment'
    )
    season = models.ForeignKey(
        Season, related_name='staff_debit_season',
        blank=True, null=True
    )
    amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    page_no = models.CharField(max_length=100, blank=True, null=True)
    payment_type = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField(max_length=500, blank=True, null=True)
    payment_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.staff.name if self.staff else ''


class StaffAdvanceCredit(models.Model):
    staff = models.ForeignKey(
        Staff, related_name='staff_credit_advance'
    )
    season = models.ForeignKey(
        Season, related_name='staff_credit_season',
        blank=True, null=True
    )
    page_no = models.CharField(max_length=100, blank=True, null=True)
    total_bricks = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True,
    )
    kharcha_rate = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True,
        help_text="The rates for 1000 bricks"
    )
    weekly_amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True,
        help_text="Dasti payment given by weekly"
    )
    net_payment = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    details = models.TextField(max_length=500, blank=True, null=True)
    date_added = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.staff.name if self.staff else ''


class StaffOtherCredit(models.Model):
    staff = models.ForeignKey(
        Staff, related_name='staff_credit_other'
    )
    season = models.ForeignKey(
        Season, related_name='other_credit_season',
        blank=True, null=True
    )
    page_no = models.CharField(max_length=100, blank=True, null=True)
    total_load = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True,
    )
    rate = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True,
        help_text="The rate for 1 load"
    )
    total_payment = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    details = models.TextField(max_length=500, blank=True, null=True)
    date_added = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.staff.name if self.staff else ''


class StaffOtherDebit(models.Model):
    staff = models.ForeignKey(
        Staff, related_name='staff_debit_payment'
    )
    season = models.ForeignKey(
        Season, related_name='other_staff_debit_season',
        blank=True, null=True
    )
    amount = models.DecimalField(
        max_digits=100, decimal_places=2, default=0, blank=True, null=True
    )
    page_no = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField(max_length=500, blank=True, null=True)
    payment_date = models.DateField(
        default=timezone.now, blank=True, null=True
    )

    def __unicode__(self):
        return self.staff.name if self.staff else ''
