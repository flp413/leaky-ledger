from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    iban = models.CharField(max_length=34, unique=True)
    balance_eur = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    balance_usd = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_verified = models.BooleanField(default=False)
    avatar_url = models.URLField(blank=True)


class Transaction(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="sent")
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="received")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
