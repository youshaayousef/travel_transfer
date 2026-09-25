import math

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        return Response({
         'count': self.page.paginator.count,
         'total_pages': total_pages,
         'previous': self.get_previous_link(),
         'next': self.get_next_link(),
         'results': data
        })