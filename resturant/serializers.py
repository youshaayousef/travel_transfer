from rest_framework import serializers
from .models import *
from travel_transfer.settings import MY_URL
class ResurantSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()
    class Meta:
        model = Resturant
        fields = '__all__'
    def get_logo(self, obj):
        return f'{MY_URL}{obj.logo.url}'
    def get_cover(self, obj):
        return f'{MY_URL}{obj.cover.url}'

class CategorySerializer(serializers.ModelSerializer):
    # This creates the recursion: showing children within the parent
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'children']

    def get_children(self, obj):
        # We check if there are sub-categories
        if obj.child_set.exists():
            # We use the same serializer to represent the children
            return CategorySerializer(obj.child_set.all(), many=True).data
        return []


class ItemSerializer(serializers.ModelSerializer):
    # This will show the full category path string (e.g., "Food -> Pizza")
    category_name = serializers.CharField(source='category.__str__', read_only=True)
    category_path = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    # Optional: If you want the full nested object of the category
    # category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'name', 'price', 'offer', 'available',
            'image', 'description', 'category', 'category_name', 'category_path',
            'created_at', 'updated_at', 'count', 'display'
        ]
        # Simplified ordering
        ordering = ['category_name', 'name']

    def get_count(self, obj):
        return 0

    def get_display(self, obj):
        return True

    def get_category_path(self, obj):
        # This shows the full path (e.g., Beverages > Coffee > Espresso)
        full_path = [obj.category.name]
        k = obj.category.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return full_path[::-1]

    def get_image(self, obj):
        return f'{MY_URL}{obj.image.url}'