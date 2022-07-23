# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin


from batta_staff.models import (
    Staff, StaffLedger, StaffLedgerPayment, StaffAdvanceCredit, StaffOtherCredit, StaffOtherDebit
)


class StaffAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'staff_code', 'father_name', 'staff_type',
        'designation', 'mobile_no', 'cnic', 'joining_date'
    )
    search_fields = (
        'name', 'father_name', 'staff_code',
        'designation', 'mobile_no', 'cnic'
    )
    raw_id_fields = ('bhatta',)

    @staticmethod
    def bhatta(obj):
        return obj.bhatta.name if obj.bhatta else ''


class StaffLedgerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta', 'season', 'amount', 'date_added'
    )
    search_fields = (
        'staff__name', 'staff__cnic', 'staff__mobile_no'
    )
    raw_id_fields = ('staff',)

    @staticmethod
    def bhatta(obj):
        return obj.staff.bhatta.name if obj.staff.bhatta else ''


class StaffLedgerPaymentAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta', 'season', 'amount',
        'payment_type', 'payment_date'
    )
    search_fields = (
        'staff__name', 'staff__cnic', 'staff__mobile_no'
    )
    raw_id_fields = ('staff',)

    @staticmethod
    def bhatta(obj):
        return obj.staff.bhatta.name if obj.staff.bhatta else ''


class StaffAdvanceCreditAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta', 'season', 'total_bricks', 'kharcha_rate',
        'weekly_amount', 'net_payment', 'date_added'
    )
    raw_id_fields = (
        'staff', 'season',
    )
    search_fields = (
        'staff__name', 'staff__cnic', 'staff__mobile_no'
    )

    @staticmethod
    def bhatta(obj):
        return obj.staff.bhatta.name if obj.staff.bhatta else ''


class StaffOtherCreditAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'season', 'total_load', 'page_no',
        'rate', 'total_payment'
    )
    raw_id_fields = (
        'staff', 'season',
    )
    search_fields = (
        'staff__name', 'staff__cnic', 'staff__mobile_no'
    )


class StaffOtherDebitAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'bhatta', 'season', 'amount', 'page_no',
        'payment_date'
    )
    raw_id_fields = (
        'staff', 'season',
    )
    search_fields = (
        'staff__name', 'staff__cnic', 'staff__mobile_no'
    )

    @staticmethod
    def bhatta(obj):
        return obj.staff.bhatta.name if obj.staff.bhatta else ''


admin.site.register(Staff, StaffAdmin)
admin.site.register(StaffLedger, StaffLedgerAdmin)
admin.site.register(StaffLedgerPayment, StaffLedgerPaymentAdmin)
admin.site.register(StaffAdvanceCredit, StaffAdvanceCreditAdmin)
admin.site.register(StaffOtherCredit, StaffOtherCreditAdmin)
admin.site.register(StaffOtherDebit, StaffOtherDebitAdmin)
