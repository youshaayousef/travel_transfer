from django.contrib import admin
# Register your models here.

from .models import *

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'avatar', 'rating', 'facebook_account')

admin.site.register(Profile, ProfileAdmin)