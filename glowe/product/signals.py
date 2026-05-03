
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import Variant, Product


@receiver(pre_save, sender=Variant)
def track_variant_before_save(sender, instance, **kwargs):
    """Track old values before saving."""
    if kwargs.get("raw"):
        return
    if instance.pk:
        try:
            old = Variant.objects.get(pk=instance.pk)
            instance._old_stock = old.stock
            instance._old_is_active = old.is_active
        except Variant.DoesNotExist:
            instance._old_stock = 0
            instance._old_is_active = False
    else:
        instance._old_stock = 0
        instance._old_is_active = False


@receiver(post_save, sender=Variant)
def notify_users_on_restock(sender, instance, created, **kwargs):
    """Send email notifications when a variant is back in stock or re-activated."""
    if kwargs.get("raw") or created:
        return

    old_stock = getattr(instance, "_old_stock", None)
    old_is_active = getattr(instance, "_old_is_active", None)

    was_unavailable = (old_stock == 0) or (old_is_active is False)
    is_now_available = instance.stock > 0 and instance.is_active and instance.product.is_active

    if was_unavailable and is_now_available:
        _send_stock_notifications(instance)


@receiver(pre_save, sender=Product)
def track_product_before_save(sender, instance, **kwargs):
    """Track old product active state before saving."""
    if kwargs.get("raw"):
        return
    if instance.pk:
        try:
            old = Product.objects.get(pk=instance.pk)
            instance._old_is_active = old.is_active
        except Product.DoesNotExist:
            instance._old_is_active = False
    else:
        instance._old_is_active = False


@receiver(post_save, sender=Product)
def notify_users_on_product_reactivation(sender, instance, created, **kwargs):
    """Send notifications to all variant subscribers when a product is re-activated."""
    if kwargs.get("raw") or created:
        return

    old_is_active = getattr(instance, "_old_is_active", None)
    if old_is_active is False and instance.is_active and not instance.is_deleted:
        # Notify for ALL active variants of this product
        for variant in instance.variants.filter(is_active=True, stock__gt=0):
            _send_stock_notifications(variant)


def _send_stock_notifications(variant):
    """Send email to all subscribed users for a variant and mark them notified."""
    from wishlist.models import StockNotification

    notifications = StockNotification.objects.filter(
        variant=variant, is_notified=False
    ).select_related("user")

    if not notifications.exists():
        return

    product = variant.product
    product_url = f"https://nandagopan.online/product/{product.slug}/?variant={variant.id}"

    # Get primary image
    primary_image = product.images.filter(is_primary=True).first()
    if not primary_image:
        primary_image = product.images.first()

    for notification in notifications:
        user = notification.user
        try:
            context = {
                "user": user,
                "product": product,
                "variant": variant,
                "product_url": product_url,
                "primary_image": primary_image,
            }
            html_content = render_to_string(
                "wishlist/email/stock_notification.html", context
            )
            text_content = (
                f"Hi {user.full_name or user.email},\n\n"
                f"Great news! '{product.name}' ({variant.size}) is back in stock.\n"
                f"Shop now: {product_url}\n\n"
                f"— The Glowé Team"
            )

            email = EmailMultiAlternatives(
                subject=f"✨ Back in Stock: {product.name} | Glowé",
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=True)

            notification.is_notified = True
            notification.save()

        except Exception:
            pass  # Never crash the save operation due to email failure
