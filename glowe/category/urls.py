from django.urls import path,include
from . import views

urlpatterns = [
   
     path('category-management/',views.category_management,name='category_management'),
    
     
]