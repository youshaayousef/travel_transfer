from django.contrib import admin
from .models import *

class ResturantAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

admin.site.register(Resturant, ResturantAdmin)

class CategoryAdmin(admin.ModelAdmin):
    # list_display uses the __str__ from the model (which shows the full path)
    list_display = ['name', 'parent']
    # list_filter = ['parent']
    search_fields = ['name']
    ordering = ['parent__name', 'name']
    raw_id_fields = ['parent']

    # def is_sub(self, obj):
    #     return obj.parent is not None
    #
    # is_sub.boolean = True
    # is_sub.short_description = "Sub-category?"

admin.site.register(Category, CategoryAdmin)

class ItemAdmin(admin.ModelAdmin):
    # Display the ID, name, and the category path
    list_display = ['id', 'name', 'get_category_path', 'available']

    # Filter by availability and the unified category model
    list_filter = ['available']

    search_fields = ['id', 'name', 'category__name']
    date_hierarchy = "created_at"
    actions = ['make_available', 'make_unavailable']

    # Simple ordering by category then name
    # ordering = ['category', 'name']

    # Better way to handle category path in list_display
    def get_category_path(self, obj):
        return obj.category.__str__() if obj.category else "No Category"

    get_category_path.short_description = "Category Path"

    # Optimized actions using .update() for performance
    @admin.action(description="Mark as Available")
    def make_available(self, request, queryset):
        queryset.update(available=True)

    @admin.action(description="Mark as Unavailable")
    def make_unavailable(self, request, queryset):
        queryset.update(available=False)

admin.site.register(Item, ItemAdmin)