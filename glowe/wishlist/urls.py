from django.urls import path
from . import views

urlpatterns = [
    path("wishlist/", views.wishlist_page, name="wishlist"),
    path('wishlist/toggle/<int:variant_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    
    
    
]