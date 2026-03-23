from django.shortcuts import render,redirect
from .forms import CategoryForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Category

def category_management(request):   
    return render(request,'category_management.html')


def add_category(request):
    
    if request.method == 'POST' :
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request,'category is created successfully')
            return redirect ('category_management') 
            
        else:
            form = CategoryForm()
            
    
    
    return redirect('category_management')

def edit_category(request,id):
    
    category=get_object_or_404(Category,id=id,is_deleted=False)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST,instance=category)
        
        if form.is_valid():
            form.save()
            messages.success(request,'category successfully updated....')
            return redirect('category_management')
        else :
            form =CategoryForm(instance=category)
    
    return redirect('category_management')

def delete_category(request):
    return redirect('category_management')
# Create your views here.
