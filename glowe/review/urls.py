from django.urls import path
from . import views

urlpatterns = [
     path('review/add/<int:product_id>/<int:order_id>/', views.create_review, name='add_review'),
    
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
]
