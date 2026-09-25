from django.db import models

class Resturant(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    tel_number = models.CharField(max_length=100, null=True, blank=True)
    business_hours = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to='resturant', default='resturant/default.jpg')
    cover = models.ImageField(null=True, blank=True, upload_to='resturant', default='resturant/cover.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CategoryQueryset(models.QuerySet):
    def top_level_categories(self):
        return self.filter(parent__isnull=True)
    def bottom_level_categories(self):
        return self.filter(child__isnull=True)

class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQueryset(self.model, using=self._db)

class Category(models.Model):
    name = models.CharField(max_length=100)
    # This field allows a category to point to another category as its parent
    # If parent is NULL, it is a Top-Level Category
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_set',
        related_query_name='child'
    )

    objects = models.Manager()
    rows = CategoryManager()

    class Meta:
        verbose_name_plural = "Categories"


    def __str__(self):
        # This shows the full path (e.g., Beverages > Coffee > Espresso)
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveSmallIntegerField()
    offer = models.PositiveSmallIntegerField(null=True, blank=True)
    # count = models.PositiveSmallIntegerField(default=0)
    # display = models.BooleanField(default=True)
    # Now an item can link to ANY level (Category, Sub-category, etc.)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    available = models.BooleanField(default=True)
    image = models.ImageField(null=True, blank=True, upload_to='menu', default='menu/default.jpg')
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
