from index.admin import admin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'is_blocked')
    search_fields = ('phone_number', 'username')

admin.site.register(CustomUser, CustomUserAdmin)

