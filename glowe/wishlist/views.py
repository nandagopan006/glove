from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Min

from .models import Wishlist, StockNotification
from product.models import Variant
from cart.models import CartItem
from cart.utils import get_user_cart


@login_required
def toggle_wishlist(request, variant_id):

    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER", "wishlist"))

    variant = get_object_or_404(Variant, id=variant_id)

    wishlist_item = Wishlist.objects.filter(user=request.user, variant=variant)

    if wishlist_item.exists():
        wishlist_item.delete()
        status = "removed"
        message = "Removed from wishlist"
    else:
        Wishlist.objects.create(user=request.user, variant=variant)
        status = "added"
        message = "Added to Wishlist"

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"status": status, "message": message})

    if status == "added":
        messages.success(request, message)
    else:
        messages.info(request, message)

    return redirect(request.META.get("HTTP_REFERER", "wishlist"))


@login_required
def remove_from_wishlist(request, variant_id):

    if request.method != "POST":
        return redirect("wishlist")

    variant = get_object_or_404(Variant, id=variant_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user, variant=variant
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, "Item removed from wishlist")
    else:
        messages.warning(request, "Item not found")

    return redirect("wishlist")


@login_required
def wishlist_page(request):

    wishlist_items = list(
        Wishlist.objects.filter(user=request.user)
        .select_related(
            "variant",
            "variant__product",
            "variant__product__category",
        )
        .prefetch_related("variant__product__images")
        .order_by("-created_at")
    )

    wishlist_count = len(wishlist_items)

    # Get variants this user is already subscribed to for notifications
    notified_variant_ids = set(
        StockNotification.objects.filter(
            user=request.user, is_notified=False
        ).values_list("variant_id", flat=True)
    )

    # Annotate each wishlist item with availability status
    for item in wishlist_items:
        variant = item.variant
        product = variant.product
        category = product.category

        # Product is unavailable if product or category is inactive/deleted
        item.is_unavailable = (
            not product.is_active
            or product.is_deleted
            or not category.is_active
            or category.is_deleted
            or not variant.is_active
        )
        item.is_out_of_stock = variant.stock == 0
        item.notify_requested = variant.id in notified_variant_ids

    # IDs of products already in wishlist (to exclude from recommendations)
    wishlisted_product_ids = [
        item.variant.product_id for item in wishlist_items
    ]

    one_variant_ids = (
        Variant.objects.filter(
            is_active=True,
            product__is_active=True,
            product__is_deleted=False,
            product__category__is_active=True,
            product__category__is_deleted=False,
        )
        .exclude(product_id__in=wishlisted_product_ids)
        .values("product_id")
        .annotate(first_variant=Min("id"))
        .values_list("first_variant", flat=True)
    )

    recommend_products = (
        Variant.objects.filter(id__in=one_variant_ids)
        .select_related("product")
        .prefetch_related("product__images")[:8]
    )

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "wishlist_items": wishlist_items,
            "wishlist_count": wishlist_count,
            "recommend_products": recommend_products,
        },
    )


@login_required
def clear_wishlist(request):

    if request.method == "POST":
        Wishlist.objects.filter(user=request.user).delete()

    return redirect("wishlist")


@login_required
def move_to_cart(request, variant_id):

    if request.method != "POST":
        return redirect("wishlist")

    variant = get_object_or_404(Variant, id=variant_id)
    product = variant.product
    category = product.category

    # Check full availability
    if (
        not product.is_active
        or product.is_deleted
        or not category.is_active
        or category.is_deleted
        or not variant.is_active
    ):
        messages.error(request, "Product not available")
        return redirect("wishlist")

    if variant.stock == 0:
        messages.warning(request, "Out of stock")
        return redirect("wishlist")

    cart = get_user_cart(request.user)

    cart_item = CartItem.objects.filter(cart=cart, variant=variant).first()

    max_limit = 5

    if cart_item:
        if cart_item.quantity >= max_limit:
            messages.warning(
                request,
                f"You can only add {max_limit} items. You already have the max quantity.",
            )
            return redirect("wishlist")

        if cart_item.quantity >= variant.stock:
            messages.warning(request, "Maximum stock reached")
            return redirect("wishlist")

        cart_item.quantity += 1
        cart_item.save()
    else:
        CartItem.objects.create(cart=cart, variant=variant, quantity=1)

    Wishlist.objects.filter(user=request.user, variant=variant).delete()

    messages.success(request, "Added to cart")
    return redirect("wishlist")


@login_required
def notify_me(request, variant_id):
    if request.method != "POST":
        return redirect("wishlist")

    variant = get_object_or_404(Variant, id=variant_id)
    product = variant.product
    category = product.category

    # Check if product is available — no need for notification
    is_available = (
        product.is_active
        and not product.is_deleted
        and category.is_active
        and not category.is_deleted
        and variant.is_active
        and variant.stock > 0
    )

    if is_available:
        messages.info(request, "Product is already available — add it to your cart!")
        return redirect("wishlist")

    obj, created = StockNotification.objects.get_or_create(
        user=request.user, variant=variant,
        defaults={"is_notified": False}
    )

    if created:
        messages.success(
            request,
            f"We'll email you at {request.user.email} when '{product.name}' is back!"
        )
    else:
        if obj.is_notified:
            # Reset so they get notified again
            obj.is_notified = False
            obj.save()
            messages.success(
                request,
                f"Notification re-activated for '{product.name}'!"
            )
        else:
            messages.info(request, "You're already on the notification list for this item.")

    return redirect("wishlist")
