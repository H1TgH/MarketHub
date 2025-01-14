from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at < timezone.timedelta(minutes=5)  # OTP действует 5 минут
    
class GoodCategory(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

class Good(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller_id = models.BigIntegerField()
    category = models.ForeignKey(GoodCategory, on_delete=models.CASCADE, related_name="goods")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

class DeliveryMethod(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title   

class Recipient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipients"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    zip_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class BasketItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="basket_items"
    )
    good = models.ForeignKey("Good", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.good.name} (x{self.count})"

class Checkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="checkouts")
    recipient = models.ForeignKey('Recipient', on_delete=models.PROTECT, related_name="checkouts")
    basket = models.ForeignKey('BasketItem', on_delete=models.PROTECT, related_name="checkouts")
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.PROTECT, related_name="checkouts")
    delivery_method = models.ForeignKey('DeliveryMethod', on_delete=models.PROTECT, related_name="checkouts")
    payment_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Checkout {self.id} by {self.user}"

class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SUCCESS = 'SUCCESS', _('Success')
        ERROR = 'ERROR', _('Error')

    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, related_name="transactions")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"
