
from django.shortcuts import render, redirect, get_object_or_404
from .utils import get_user_cart
from .models import CartItem, Cart
from user.models import Address
from django.contrib import messages
from coupons.views import calculate_discount
from coupons.models import Coupon
from django.utils import timezone
from decimal import Decimal
from wallet.models import Wallet

def cart(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    
    user_cart =get_user_cart(request.user)
    items= user_cart.items.select_related('variant__product')
    
    cart_items=[]
    total=0
    
    for item in items:
        variant=item.variant
        product=variant.product
        
        if product.is_active and  not product.is_deleted and variant.is_active:
            
            stock =variant.stock
            price=variant.price
            #out of stock  it marks akumm  out of stock ui 
            if stock == 0:
                cart_items.append({
                    'item':item,
                    'product':product,
                    'variant':variant,
                    'quantity':0,
                    'price':price,
                    'subtotal':0,
                    'stock':0,
                    'is_out_of_stock':True,
                    'low_stock':False,
                })
            else:
            
                # if selected more than stock
                if item.quantity > stock:
                    item.quantity = stock
                    item.save()
                
                qty =item.quantity
            
                subtotal =variant.price * qty
                total +=subtotal
                
                low_stock= stock > 0 and stock <=5
                
                cart_items.append({
                    'item':item,
                    'product':product,
                    'variant':variant,
                    'quantity':qty,
                    'price':price,
                    'subtotal':subtotal,
                    'stock':stock,
                    'is_out_of_stock':False,
                    'low_stock':low_stock,
                })
    is_empty = not cart_items
    cart_count = request.user.cart.items.count()
            
    return render(request, 'cart.html',{
        'cart_items':cart_items,
        'total':total,
        'is_empty':is_empty,
        'cart_count':cart_count,
    })

def update_cart(request):
    if request.method == "POST":
        item_id=request.POST.get('item_id')
        
        try:
            quantity=int(request.POST.get('quantity',1))
        except:
            quantity =1
        #prevent 0 and neg
        if quantity <=0 :
            quantity=1
        
        item=get_object_or_404(CartItem,id=item_id,cart__user=request.user)
        variant = item.variant
        stock = variant.stock
        max_qty = 5
        
        if stock == 0:
            item.quantity = 0
            item.save()
            return redirect('cart')
        
        if quantity > stock:
            quantity=stock
        
        if quantity > max_qty:
            quantity = max_qty
            
        item.quantity = quantity
        item.save()
    
    return redirect('cart') 

def remove_from_cart(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
        messages.success(request, "Item removed from cart")
    return redirect('cart')


def checkout(request):
    
    try :
        cart =request.user.cart
        cart_items =cart.items.select_related('variant','variant__product').all()
    except Cart.DoesNotExist:
        messages.error(request,"Cart not found")
        return redirect('cart')
    
    addresses = Address.objects.filter(user=request.user)
    
    #chck cart is empty
    if not cart_items.exists():
        messages.error(request, "Your cart is empty")
        return redirect('cart')
    
    default_address =addresses.filter(is_default=True).first()
    
    if not default_address:
        default_address=addresses.first()
        
    subtotal = Decimal('0.00')
    for item in cart_items:
        variant = item.variant
        product = variant.product
        
        if not product.is_active or product.is_deleted:
            messages.error(request, f"{product.name} is unavailable")
            return redirect('cart')

        if not variant:
            messages.error(request, "Product not found")
            return redirect('cart')
        
        if not variant.is_active:
            messages.error(request, f"{product.name} is not available")
            return redirect('cart')
        
        if variant.stock == 0:
            messages.error(request, f"{product.name} is out of stock")
            return redirect('cart')
            
        if item.quantity > variant.stock:
            messages.error(request, f"{product.name} only {variant.stock} left")
            return redirect('cart')
    
        item.item_total = item.quantity * variant.price 
        subtotal += Decimal(item.item_total)
        
    shipping = Decimal('0.00') if subtotal > Decimal('999') else Decimal('100.00')
    
    # check any coupon apply
    discount = calculate_discount(request, subtotal)
    
    # Get available coupons
    today = timezone.now().date()
    available_coupons = Coupon.objects.filter(
        is_active=True,
        is_deleted=False,
        start_date__lte=today,
        end_date__gte=today
    )
    
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    
    final_total = subtotal + shipping - discount
    if final_total < 0:
        final_total = Decimal('0.00')
    
    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "addresses": addresses,
        "default_address": default_address,
        "subtotal": subtotal,
        "shipping": shipping,
        "discount": discount,
        "final_total": final_total,
        "available_coupons": available_coupons,
        "wallet":wallet,
    })