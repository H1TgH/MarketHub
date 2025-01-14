from rest_framework import serializers
from .models import GoodCategory, Good, PaymentMethod, DeliveryMethod, BasketItem, Checkout, Transaction, Recipient

class GoodCategorySerializer(serializers.ModelSerializer):
    parentId = serializers.PrimaryKeyRelatedField(queryset=GoodCategory.objects.all(), source='parent', allow_null=True)

    class Meta:
        model = GoodCategory
        fields = ['id', 'title', 'description', 'parentId']

class GoodCategoriesListResponseSerializer(serializers.Serializer):
    totalCount = serializers.IntegerField()
    nextPage = serializers.CharField(allow_null=True)
    prevPage = serializers.CharField(allow_null=True)
    items = GoodCategorySerializer(many=True)

class GoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Good
        fields = ['id', 'title', 'description', 'price', 'seller_id', 'category']

class GoodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Good
        fields = ['id', 'title', 'price', 'category']

class GoodListResponseSerializer(serializers.Serializer):
    totalCount = serializers.IntegerField()
    nextPage = serializers.CharField(allow_null=True)
    prevPage = serializers.CharField(allow_null=True)
    items = GoodCategorySerializer(many=True)

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'title', 'description']

class DeliveryMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = ['id', 'title', 'description']

class RecipientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipient
        fields = [
            'id', 'user', 'first_name', 'last_name', 'middle_name',
            'address', 'zip_code', 'phone'
        ]
        read_only_fields = ['id', 'user']

class BasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = ['id', 'good', 'count']

class AddToBasketSerializer(serializers.Serializer):
    goodId = serializers.IntegerField()
    count = serializers.IntegerField(min_value=1)

class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
