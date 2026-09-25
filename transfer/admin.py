from django.contrib import admin
# Register your models here.

from .models import *

class FeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'min', 'max', 'fee']

admin.site.register(Fee, FeeAdmin)

class GiftAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ['id', 'payer', 'payee', 'gift', 'created_at']

admin.site.register(Gift, GiftAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'nationality_number', 'phone_number']

admin.site.register(Client, ClientAdmin)

class UndirectTransferAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ['is_received', 'user', 'id', 'payer', 'payee', 'amount', 'created_at']

admin.site.register(UndirectTransfer, UndirectTransferAdmin)


class DirectTransferAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ['is_received', 'id', 'payer', 'payee', 'amount', 'created_at']


admin.site.register(DirectTransfer, DirectTransferAdmin)