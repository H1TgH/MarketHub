from django.shortcuts import render

import random
from rest_framework import status, pagination
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied
from .models import (
    User, 
    OTP,
    GoodCategory, 
    Good,
    PaymentMethod,
    DeliveryMethod,
    BasketItem,
    Checkout,
    Transaction,
    Recipient,
)
from .serializers import (
    GoodCategorySerializer, 
    GoodCategoriesListResponseSerializer,
    GoodSerializer, 
    GoodListSerializer,
    PaymentMethodSerializer,
    DeliveryMethodSerializer,
    RecipientSerializer,
    BasketItemSerializer,
    AddToBasketSerializer,
    CheckoutSerializer, 
    TransactionSerializer,
)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Введите свою почту'}, status=status.HTTP_400_BAD_REQUEST)

        otp_code = random.randint(100000, 999999)
        OTP.objects.create(email=email, otp=str(otp_code))

        send_mail(
            subject='OTP Code',
            message=f'Your OTP code is {otp_code}',
            from_email='noreply@example.com',
            recipient_list=[email],
        )

        return Response({'message': 'OTP sent to email'}, status=status.HTTP_200_OK)

class ConfirmView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_entry = OTP.objects.get(email=email, otp=otp)
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_entry.is_valid():
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(email=email)

        otp_entry.delete()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({'access_token': access_token}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax',
        )

        return response

class GoodCategoryDetailView(APIView):
    def get(self, request, id):
        try:
            category = GoodCategory.objects.get(id=id)
            serializer = GoodCategorySerializer(category)
            return Response(serializer.data)
        except GoodCategory.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request, id):
        try:
            category = GoodCategory.objects.get(id=id)
            serializer = GoodCategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except GoodCategory.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        try:
            category = GoodCategory.objects.get(id=id)
            category.delete()
            return Response({"message": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except GoodCategory.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

class GoodCategoryListView(APIView):
    def get(self, request):
        categories = GoodCategory.objects.all()
        paginator = pagination.PageNumberPagination()
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = GoodCategorySerializer(paginated_categories, many=True)

        next_page = paginator.get_next_link()
        prev_page = paginator.get_previous_link()

        response_data = GoodCategoriesListResponseSerializer({
            "totalCount": categories.count(),
            "nextPage": next_page,
            "prevPage": prev_page,
            "items": serializer.data
        }).data

        return paginator.get_paginated_response(response_data)

    def post(self, request):
        serializer = GoodCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

class GoodListView(APIView, PageNumberPagination):
    page_size = 20

    def get(self, request):
        goods = Good.objects.all()
        results = self.paginate_queryset(goods, request, view=self)
        serializer = GoodListSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)
    
    def post(self, request):
        serializer = GoodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class GoodDetailView(APIView):
    def get(self, request, id):
        good = get_object_or_404(Good, id=id)
        serializer = GoodSerializer(good)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, id):
        good = get_object_or_404(Good, id=id)
        serializer = GoodSerializer(good, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
            good = get_object_or_404(Good, id=id)
            good.delete()
            return Response({"message": "Good deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class PaymentMethodListView(APIView):
    def get(self, request):
        payment_methods = PaymentMethod.objects.all()
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PaymentMethodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentMethodDetailView(APIView):
    def get(self, request, id):
        payment_method = get_object_or_404(PaymentMethod, id=id)
        serializer = PaymentMethodSerializer(payment_method)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        payment_method = get_object_or_404(PaymentMethod, id=id)
        serializer = PaymentMethodSerializer(payment_method, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        payment_method = get_object_or_404(PaymentMethod, id=id)
        payment_method.delete()
        return Response({"message": "Payment method deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class DeliveryMethodListView(APIView):
    def get(self, request):
        delivery_methods = DeliveryMethod.objects.all()
        serializer = DeliveryMethodSerializer(delivery_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DeliveryMethodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeliveryMethodDetailView(APIView):
    def get(self, request, id):
        delivery_method = get_object_or_404(DeliveryMethod, id=id)
        serializer = DeliveryMethodSerializer(delivery_method)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        delivery_method = get_object_or_404(DeliveryMethod, id=id)
        serializer = DeliveryMethodSerializer(delivery_method, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        delivery_method = get_object_or_404(DeliveryMethod, id=id)
        delivery_method.delete()
        return Response({"message": "Delivery method deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class AdminRecipientAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        recipients = Recipient.objects.all()
        serializer = RecipientSerializer(recipients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecipientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRecipientAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recipients = Recipient.objects.filter(user=request.user)
        serializer = RecipientSerializer(recipients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecipientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRecipientDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        recipient = get_object_or_404(Recipient, id=id)
        serializer = RecipientSerializer(recipient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        try:
            recipient = Recipient.objects.get(pk=id, user=request.user)
        except Recipient.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = RecipientSerializer(recipient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            recipient = Recipient.objects.get(pk=id, user=request.user)
        except Recipient.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        recipient.delete()
        return Response({"message": "Recipient deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class BasketItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            basket_item = BasketItem.objects.get(id=id, user=request.user)
        except BasketItem.DoesNotExist:
            return Response({"error": "Basket item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        basket_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, id):
        try:
            basket_item = BasketItem.objects.get(id=id, user=request.user)
        except BasketItem.DoesNotExist:
            return Response({"error": "Basket item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        count = request.data.get("count")
        if not count or count < 1:
            return Response({"error": "Invalid count"}, status=status.HTTP_400_BAD_REQUEST)
        
        basket_item.count = count
        basket_item.save()
        
        return Response(BasketItemSerializer(basket_item).data)

class BasketItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        basket_items = BasketItem.objects.filter(user=request.user)
        serializer = BasketItemSerializer(basket_items, many=True)
        return Response({
            "totalCount": basket_items.count(),
            "items": serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = AddToBasketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        good_id = serializer.validated_data['goodId']
        count = serializer.validated_data['count']
        
        try:
            good = Good.objects.get(id=good_id)
        except Good.DoesNotExist:
            return Response({"error": "Good not found"}, status=status.HTTP_404_NOT_FOUND)
        
        basket_item, created = BasketItem.objects.get_or_create(
            user=request.user, 
            good=good, 
            defaults={"count": count}
        )
        if not created:
            basket_item.save()
        
        return Response(BasketItemSerializer(basket_item).data, status=status.HTTP_201_CREATED)

from rest_framework import generics, permissions

class CheckoutListCreateView(generics.ListCreateAPIView):
    queryset = Checkout.objects.all()
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CheckoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Checkout.objects.all()
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransactionListCreateView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
