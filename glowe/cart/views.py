
from django.shortcuts import render, redirect, get_object_or_404
from product.models import Variant,Product
from .utils import get_user_cart

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
                
                qty =item.quantity
                
                # if selected more than stock
                if qty > stock:
                    qty =stock
            
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
    is_empty= not cart_items
            
    return render(request, 'cart.html',{
        'cart_items':cart_items,
        'total':total,
        'is_empty':is_empty,
    })
