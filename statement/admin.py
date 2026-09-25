from django.contrib import admin
# Register your models here.

from .models import *

class ATMAdmin(admin.ModelAdmin):
    list_display = ('id', 'city__name', 'address')

admin.site.register(ATM, ATMAdmin)

class BalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

admin.site.register(Balance, BalanceAdmin)

class DepositAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'customer', 'datetime')

admin.site.register(Deposit, DepositAdmin)

class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'customer', 'datetime')

admin.site.register(Withdraw, WithdrawAdmin)