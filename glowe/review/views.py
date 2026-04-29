from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from .models import Review, ReviewImage
from product.models import Product
from order.models import Order
from .utils import can_user_review
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.


def create_review(request, product_id, order_id):
    product = get_object_or_404(Product, id=product_id)
    order = get_object_or_404(Order, id=order_id)
    
    if not can_user_review(request.user, product, order):
        messages.error(request, "You cannot review this product")
        return redirect('orders')
    if request.method == "POST":
        rating = request.POST.get('rating')
        title = (request.POST.get('title') or "").strip()
        comment = (request.POST.get('comment') or "").strip()

        # Safe rating conversion
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            messages.error(request, "Invalid rating")
            return redirect('product_detail', product.slug)

        #Rating validation
        if rating < 1 or rating > 5:
            messages.error(request, "Rating must be between 1 and 5")
            return redirect('product_detail', product.slug)

        #Prevent empty comment
        if not comment or not comment.strip():
            messages.error(request, "Review cannot be empty")
            return redirect('product_detail', product.slug)
        if len(comment) < 7:
            messages.error(request, "Review too short")
            return redirect('product_detail', product.slug)
        if title and len(title) < 4:
            messages.error(request, "Title must be at least 4 characters")
            return redirect('product_detail', product.slug)
        images = request.FILES.getlist('images')

        if len(images) > 3:
            messages.error(request, "You can upload maximum 3 images")
            review.delete()
            return redirect('product_detail', product.slug)

        for img in images:
            if img.size > 2 * 1024 * 1024:  # 2MB limit
                messages.error(request, "Each image must be under 2MB")
                review.delete()
                return redirect('product_detail', product.slug)
        
        review = Review.objects.create(
            user=request.user,
            product=product,
            order=order,
            rating=rating,
            title=title,
            comment=comment,
            status='pending'
        )
        
        
        for img in images:
            ReviewImage.objects.create(review=review,image=img)
        
        messages.success(request, "Review added successfully")
        return redirect('product_detail', product.slug)
    
    
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404( Review,id=review_id,user=request.user,is_deleted=False)

    with transaction.atomic():
        review.is_deleted = True
        review.status = "rejected"  
        review.save()

    messages.success(request, "Your review has been deleted")

    return redirect('product_detail', slug=review.product.slug)