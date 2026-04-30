from django.db import models
from accounts.models import ProfileUser


class Address(models.Model):
    LABEL_CHOICES = (
        ("HOME", "Home"),
        ("OFFICE", "Office"),
        ("OTHER", "Other"),
    )

    user = models.ForeignKey(
        ProfileUser, on_delete=models.CASCADE, related_name="addresses"
    )

    label = models.CharField(max_length=10, choices=LABEL_CHOICES)
    full_name = models.CharField(max_length=100)
    street_address = models.TextField()

    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=6)
    country = models.CharField(max_length=100, default="India")

    phone_number = models.CharField(max_length=10)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]
