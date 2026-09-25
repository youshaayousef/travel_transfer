from django.contrib import admin
# Register your models here.

from .models import *

class GovernorateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

admin.site.register(Governorate, GovernorateAdmin)

class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'governorate__name']

admin.site.register(City, CityAdmin)

class PostOfficeAdmin(admin.ModelAdmin):
    list_display = ['id', 'city__name', 'address']

admin.site.register(PostOffice, PostOfficeAdmin)

class ParcelAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ['id', 'client_sender', 'client_receiver', 'sender', 'receiver', 'sent_mail', 'inbox_mail', 'created_at', 'details', 'postage']

admin.site.register(Parcel, ParcelAdmin)

class ShoppingAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ['id', 'is_seen', 'receiver', 'sent_mail', 'inbox_mail', 'created_at', 'details', 'postage']
    search_fields = ['id']
    list_filter = ['is_seen', 'message']
    raw_id_fields = ['parcel']

admin.site.register(Shopping, ShoppingAdmin)

class StoreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city__name', 'url', 'category', 'details']

admin.site.register(Store, StoreAdmin)