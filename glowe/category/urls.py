from django.urls import path,include
from . import views

urlpatterns = [
   
     path('admin/categories/',views.category_management,name='category_management'),
     path('admin/categories/add/',views.add_category,name='add_category'),
     path('admin/categories/edit/<int:id>/',views.edit_category,name='edit_category'),
     path('admin/categories/delete/<int:id>/',views.delete_category,name='delete_category'),
]