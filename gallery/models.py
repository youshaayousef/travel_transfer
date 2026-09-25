from django.db import models

# Create your models here.

class Gallery(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="gallery/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.title