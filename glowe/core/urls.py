from django.urls import path,include
from . import views


urlpatterns = [
    path('',views.home,name ='home'),
    path('signout/',views.signout,name='signout')


]

