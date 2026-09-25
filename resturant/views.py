# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import *

class ResturantAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        resturant = ResurantSerializer(Resturant.objects.get(name__exact='مطعم')).data
        category_tree = CategorySerializer(Category.rows.get_queryset().top_level_categories(), many=True).data
        items = ItemSerializer(Item.objects.all(), many=True).data
        response_data = {
            "resturant": resturant,
            "category_tree": category_tree,
            "items": items,
        }


        return Response(response_data)
