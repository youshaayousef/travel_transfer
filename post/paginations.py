from rest_framework.pagination import PageNumberPagination


class GovernoratePagination(PageNumberPagination):
    page_size = 14


class CityPagination(PageNumberPagination):
    page_size = 41


class PostOfficePagination(PageNumberPagination):
    page_size = 41
