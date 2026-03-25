from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProductForm
from .models import ProductImage

def add_product(request):
    form = ProductForm() # empty form for Get request
    
    if request.method == "POST":
        form=ProductForm(request.POST)
        images=request.FILES.getlist('images')
        
        if form.is_valid():
            if len(images) < 3 :
                messages.error(request,"Please upload at least 3 images")
                return render(request, 'admin/add_product.html',{'form': form})
            
            valid_types = ['image/jpeg','image/png','image/webp',"image/jpg"]
            for img in images:
                
                if img.content_type not in valid_types:
                    messages.error(request,"Only JPG,PNG,WEBP allowed")
                    return render(request,'admin/add_product.html', {'form': form})
          
                if img.size > 2* 1024* 1024:
                    messages.error(request, "Each image must be under 2MB")
                    return render(request,'admin/add_product.html', {'form': form})
        
            product=form.save() #for save product
            
            for i,img in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=img,is_primary= (i == 0),
                )
            
            messages.success(request,"Product added successfully")
            return redirect('product_management')
    
    return render(request,'admin/add_product.html',{'form': form})
        

# Create your views here.
