from django.urls import path,include
from . import views



urlpatterns = [
    path("signup/", views.signup_page , name = 'signup'),
    path('signin/', views.signin_page,name='signin'),
    path('signup-otp-verify/',views.signup_otp_verify,name='signup_otp_verify'),
    path('signup-otp/resend/',views.signup_resend_otp,name='signup_resend_otp'),

    
path('forgot-password/', views.forget_password, name='forget_password'),
path('forgot-password/sent/', views.forget_password_link, name='forget_password_link'),
path('forgot-password/resend/', views.resend_reset_email, name='resend_reset_email'),
path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
path('reset-password-invalid/',views.reset_password_invalid,name ='reset_password_invalid'),
path('referral/', views.referral_page, name='referral_page'),


    
]
