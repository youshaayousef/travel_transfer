from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from .models import *
from .serializers import *
from index.paginations import CustomPagination
from index.permissions import IsPostmasterOrOnlyRead
@method_decorator(cache_page(60 * 60 * 2), name='dispatch')
class GovernorateViewSet(ReadOnlyModelViewSet):
    queryset = Governorate.objects.all()
    serializer_class = GovernorateSerializer
    permission_classes = [AllowAny]
    from .paginations import GovernoratePagination
    pagination_class = GovernoratePagination


class CityViewSet(ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    filterset_fields = ["governorate"]
    from .paginations import CityPagination
    pagination_class = CityPagination


class PostOfficeViewSet(ReadOnlyModelViewSet):
    queryset = PostOffice.objects.all()
    serializer_class = PostOfficeSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["city", 'city__governorate']
    from .paginations import PostOfficePagination
    pagination_class = PostOfficePagination


class ParcelViewSet(ModelViewSet):
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer
    permission_classes = [IsPostmasterOrOnlyRead]
    pagination_class = CustomPagination
    filterset_fields = ["sender", "receiver", "client_receiver__phone_number", "client_sender__phone_number"]
    ordering = ["-created_at"]
    search_fields = ['id']


    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        from employees.models import Employee
        post_employee = user.employee
        data['sent_mail'] = post_employee.post_office.id

        if "client_sender" in data:
            from transfer.models import Client
            data["client_sender"] = get_object_or_404(Client, phone_number= data["client_sender"]).id
        if "client_receiver" in data:
            from transfer.models import Client
            data["client_receiver"] = get_object_or_404(Client, phone_number=data["client_receiver"]).id
        if "sender" in data:
            data["sender"] = get_object_or_404(User, username=data["sender"]).id
        if "receiver" in data:
            data["receiver"] = get_object_or_404(User, username=data["receiver"]).id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            if data['is_paid'] == 'on':
                is_paid = True
            elif data['is_paid'] == 'false':
                is_paid = False
            if "sender" in data:
                sender = get_object_or_404(User,id=int(data["sender"]))
                balance_sender = sender.balance.balance
                if balance_sender < int(data["postage"]) and is_paid:
                    return Response({"detail": "sender's balance not enough"}, status=HTTP_400_BAD_REQUEST)

                if "receiver" in data:
                    receiver = get_object_or_404(User,id=int(data["receiver"]))
                    from statement.models import Balance
                    balance_receiver = receiver.balance.balance
                    if balance_receiver < int(data["postage"]) and not is_paid:
                        return Response({"detail": "receiver's balance not enough"}, status=HTTP_400_BAD_REQUEST)

                serializer.save(user=user)
                return Response(serializer.data, status=HTTP_201_CREATED)

            elif "client_sender" in data:

                if "receiver" in data:
                    receiver = get_object_or_404(User,id=int(data["receiver"]))

                    balance_receiver = receiver.balance.balance
                    if balance_receiver < int(data["postage"]) and not is_paid:
                        return Response({"detail": "receiver's balance not enough"}, status=HTTP_400_BAD_REQUEST)

                serializer.save(user=user)
                return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True, permission_classes=[IsPostmasterOrOnlyRead])
    def pickup(self, request, pk=None):
        user = request.user
        data = request.data
        instance = get_object_or_404(Parcel, pk=pk)
        serializer = self.get_serializer(instance, data=data, partial=True)
        from django.utils import timezone
        in_inbox_mail = timezone.now()
        if serializer.is_valid():
            if instance.in_inbox_mail:
                return Response({"detail": "pickup already"}, status=HTTP_400_BAD_REQUEST)
            parcel_employee = user.employee
            if instance.inbox_mail != parcel_employee.post_office:
                return Response({"detail": "you not employee here!"}, status=HTTP_400_BAD_REQUEST)
            serializer.save(parcel_employee=user, in_inbox_mail=in_inbox_mail)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True, permission_classes=[IsPostmasterOrOnlyRead])
    def delivery(self, request, pk=None):
        user = request.user
        data = request.data
        instance = get_object_or_404(Parcel, pk=pk)
        serializer = self.get_serializer(instance, data=data, partial=True)
        from django.utils import timezone
        received_at = timezone.now()
        if serializer.is_valid():
            if not instance.in_inbox_mail:
                return Response({"detail": "parcel not pickup"}, status=HTTP_400_BAD_REQUEST)
            if instance.is_received:
                return Response({"detail": "parcel already deliver"}, status=HTTP_400_BAD_REQUEST)
            delivery_employee = user.employee
            if instance.inbox_mail != delivery_employee.post_office:
                return Response({"detail": "you not employee here!"}, status=HTTP_400_BAD_REQUEST)
            serializer.save(delivery_employee=user, is_received=True, received_at=received_at)
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)


class ShoppingViewSet(ModelViewSet):
    queryset = Shopping.objects.all()
    serializer_class = ShoppingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    ordering = ["-created_at"]

    def get_queryset(self):
        return Shopping.objects.filter(receiver=self.request.user)

    def get_object(self):
        return get_object_or_404(Shopping,receiver=self.request.user, id=self.kwargs.get("pk"))

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            balance = user.balance.balance
            if balance < int(data["postage"]):
                return Response({"detail": "balance not enough"}, status=HTTP_400_BAD_REQUEST)
            serializer.save(receiver=user)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "not allowed"}, status=HTTP_400_BAD_REQUEST)


class StoreViewSet(ReadOnlyModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]
    from index.paginations import CustomPagination
    pagination_class = CustomPagination
    filterset_fields = ["city", "name", "category"]


class StoreCategory(APIView):
    def get(self, request):
        queryset = [i['category'] for i in Store.objects.all().values('category').distinct()]
        return Response({'category':queryset}, status=HTTP_200_OK)

