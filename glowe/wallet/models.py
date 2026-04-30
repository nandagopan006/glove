from django.db import models
from django.conf import settings
import uuid


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Wallet"


class WalletTransaction(models.Model):

    TRANSACTION_TYPE = (
        ("ADD", "Add Fund"),
        ("PURCHASE", "Purchase"),
        ("REFUND", "Refund"),
    )

    STATUS = (
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    )

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    order = models.ForeignKey(
        "order.Order", on_delete=models.SET_NULL, null=True, blank=True
    )

    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE
    )
    transaction_id = models.CharField(
        max_length=100, unique=True, default=uuid.uuid4
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default="PENDING")

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
