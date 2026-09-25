from rest_framework.pagination import PageNumberPagination
class GalleryPagination(PageNumberPagination):
    page_size = 10