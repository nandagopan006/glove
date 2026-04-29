from django.db import models
from django.conf import settings
from product.models import Product
from order.models import Order
class Review(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    rating = models.IntegerField()
    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')

    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/') 
