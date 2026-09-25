from django.shortcuts import render

# Create your views here.

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Gallery
from .serializers import GallerySerializer
from .paginations import GalleryPagination
class GalleryViewSet(ReadOnlyModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    search_fields = ['title']
    filterset_fields = ['category']
    ordering_fields = ['created_at', 'title']
    permission_classes = [IsAdminUser]
    pagination_class = GalleryPagination

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def carousel(self, request):
        queryset = Gallery.objects.filter(category='carousel')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset,many=True)
            return Response(serializer.data)


