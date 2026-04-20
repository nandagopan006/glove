from django.urls import path,include
from . import views

urlpatterns = [
    path('admin-panel/coupons/',views.coupon_list,name='coupon_list'),
    path('admin-panel/coupons/create/',views.create_coupon,name='create_coupon'),
    path('admin-panel/coupons/edit/<int:id>/', views.edit_coupon,name='edit_coupon'),
    path('admin-panel/coupons/delete/<int:id>/',views.delete_coupon,name='delete_coupon'),
    path('admin-panel/coupons/toggle/<int:id>/',views.toggle_coupon,name='toggle_coupon'),
    
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
]