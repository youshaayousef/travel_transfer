from django.contrib import admin
# Register your models here.

from .models import *

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user__username']

admin.site.register(Employee, EmployeeAdmin)