from django.contrib import admin
# Register your models here.

from .models import *
class GalleryAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('id', 'title', 'image', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ['category']

admin.site.register(Gallery, GalleryAdmin)