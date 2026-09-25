from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group


class TransportTransferAdminSite(AdminSite):
    site_title = "T&T"
    site_header = "T&T administration"
    index_title = "T&T site admin"

admin.site = TransportTransferAdminSite(name='TransportTransfer')

# Register User model here.

admin.site.register(Group)
