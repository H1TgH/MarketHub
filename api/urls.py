from rest_framework.routers import DefaultRouter

from django.urls import path, re_path
from .views import (
    LoginView,
    ConfirmView,
    GoodCategoryDetailView,
    GoodCategoryListView,
    GoodListView, 
    GoodDetailView,
    PaymentMethodListView, 
    PaymentMethodDetailView,
    DeliveryMethodListView, 
    DeliveryMethodDetailView,
    BasketItemView,
    BasketItemsView,
    CheckoutDetailView,
    CheckoutListCreateView,
    TransactionListCreateView,
    TransactionDetailView,
    UserRecipientAPIView,
    AdminRecipientAPIView,
    UserRecipientDetailView,
)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Marketplace API",
        default_version='v1',
        description="Документация для API маркетплейса",
        # terms_of_service="https://www.google.com/policies/terms/",
        # contact=openapi.Contact(email="support@example.com"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/confirm/', ConfirmView.as_view(), name='confirm'),
    
    path('good-categories/', GoodCategoryListView.as_view(), name='good_category_list'),
    path('good-categories/<int:id>/', GoodCategoryDetailView.as_view(), name='good_category_detail'), 

    path('goods/', GoodListView.as_view(), name='goods_list'),
    path('goods/<int:id>/', GoodDetailView.as_view(), name='goods_detail'),

    
    path('payment-methods/', PaymentMethodListView.as_view(), name='payment_method_list'),
    path('payment-methods/<int:id>/', PaymentMethodDetailView.as_view(), name='payment_method_detail'),

    path('delivery-methods/', DeliveryMethodListView.as_view(), name='delivery_method_list'),
    path('delivery-methods/<int:id>/', DeliveryMethodDetailView.as_view(), name='delivery_method_detail'),

    path('admin/recipients/', AdminRecipientAPIView.as_view(), name='admin-recipients'),
    path('recipients/', UserRecipientAPIView.as_view(), name='user-recipients'),
    path('recipients/<int:id>/', UserRecipientDetailView.as_view(), name='user-recipient-detail'),

    path('me/basket-items/', BasketItemsView.as_view(), name='basket_items'),
    path('me/basket-items/', BasketItemsView.as_view(), name='add_to_basket'),
    path('me/basket-items/<int:id>', BasketItemView.as_view(), name='delete_basket_item'),
    path('me/basket-items/<int:id>', BasketItemView.as_view(), name='update_basket_item'),

    path('checkouts/', CheckoutListCreateView.as_view(), name='checkout_list_create'),
    path('checkouts/<int:pk>/', CheckoutDetailView.as_view(), name='checkout_detail'),

    path('transactions/', TransactionListCreateView.as_view(), name='transaction_list_create'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns.extend(router.urls)
