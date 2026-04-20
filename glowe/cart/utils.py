from .models import Cart

def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart 

def get_cart_total(user):

    cart = get_user_cart(user)
    cart_items = cart.items.select_related('variant', 'variant__product')
    
    total = 0
    for item in cart_items:
        variant = item.variant
        product = variant.product
        
        # Only include active products, active variants, and stock > 0
        if product.is_active and not product.is_deleted and variant.is_active and variant.stock > 0:
            # Quantity should not exceed stock
            quantity = min(item.quantity, variant.stock)
            total += quantity * variant.price
            
    return total