from rest_framework.pagination import PageNumberPagination
class StationsPagination(PageNumberPagination):
    page_size = 41

class SeatPagination(PageNumberPagination):
    page_size = 40