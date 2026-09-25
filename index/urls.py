from django.contrib import admin
from django.urls import re_path, path, include

urlpatterns = [
    path('users/', include('users.urls')),
    path('statement/', include('statement.urls')),
    path('profile/', include('profiles.urls')),
    path('gallery/', include('gallery.urls')),
    path('travel/', include('travel.urls')),
    path('transfer/', include('transfer.urls')),
    path('post/', include('post.urls')),
    path('reports/', include('reports.urls')),
    path('notifications/', include('notifications.urls')),
    path('employees/', include('employees.urls')),
    path('auth/', include('auth_kit.urls')),
    path('resturant/', include('resturant.urls')),
]