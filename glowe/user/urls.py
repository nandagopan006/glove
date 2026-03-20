from django.urls import path,include
from . import views


urlpatterns = [
    path('profile/',views.profile_overview,name='profile_overview'),  
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/cancel-verify/', views.cancel_email_verification, name='cancel_email_verification'),
    path('profile/verify-email/', views.verify_email_change, name='verify_email_change'),
     path('profile/image/add/', views.add_profile_image, name='add_profile_image'),
    path('profile/image/remove/', views.remove_profile_image, name='remove_profile_image'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('address/', views.address, name='address'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:id>/', views.edit_address, name='edit_address'),
    path('address/dlt/<int:id>/', views.delete_address, name='delete_address'),
    path('address/set-default/<int:id>/', views.set_default_address, name='set_default_address'),
]






