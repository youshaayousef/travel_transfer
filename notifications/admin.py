from django.contrib import admin
# Register your models here.
from .models import *
class NotificationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ['id', 'created_at', 'user']

admin.site.register(Notification, NotificationAdmin)