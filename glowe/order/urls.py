from django.urls import path,include
from . import views

urlpatterns = [
path('checkout/place-order/', views.place_order, name='place_order'),
]