# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.models import OTPVerification, ProfileUser
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import  get_object_or_404
import re
from django.core.paginator import Paginator
from django.db.models import Q
@never_cache
def admin_signin(request):

    # Already logged in admin
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method=="POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        
        if not email :
            messages.error(request,"Email is required")
            return redirect('admin_signin')
        if not password :
            messages.error(request,"password is required")
            return redirect('admin_signin')
        
        
        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request,"Invalid email or password")
            return redirect('admin_signin')

        #admin acces not normal usr
        if not user.is_superuser:
            messages.error(request,"Access denied.Admin only.")
            return redirect('admin_signin')

        
        login(request, user)
        messages.success(request,"Welcome Admin!")

        return redirect('admin_dashboard')

    return render(request, 'admin_signin.html')
@never_cache
@login_required(login_url='/admin-signin/')
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('admin_signin')

    return render(request, 'admin_dashboard.html')

def admin_signout(request):
    logout(request)
    return redirect('admin_signin')


def admin_forget_password(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method=="POST":
        email=request.POST.get('email')

        if not email:
            messages.error(request,"Email required")
            return redirect('admin_forgot_password')

        try:
            user = ProfileUser.objects.get(email=email)

            
            if not user.is_superuser:
                messages.error(request,"Not authorized")
                return redirect('admin_forgot_password')

        except ProfileUser.DoesNotExist:
            messages.error(request,"Email not found")
            return redirect('admin_forgot_password')

        # if old otp have it will dlt
        OTPVerification.objects.filter(user=user).delete()
        otp =str(random.randint(1000, 9999))

        OTPVerification.objects.create(user=user,otp_code=otp,
            expires_at=timezone.now() +timedelta(minutes=2))

        
        send_mail(
            "Admin OTP",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
        )

        request.session['reset_user']=user.id
        return redirect('admin_otp_verification')


    return render(request,'admin_forget_password.html')

def admin_otp_verification(request):
    
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.user.is_authenticated:
        return redirect("home")
    
    user_id=request.session.get('reset_user')

    if not user_id:
        return redirect('admin_forgot_password')

    user=ProfileUser.objects.get(id=user_id)

    if request.method=="POST":
        entered_otp=request.POST.get('otp')

        otp_obj = OTPVerification.objects.filter(user=user).order_by('-created_at').first()

        if not otp_obj:
            messages.error(request,"OTP not found")
            return redirect('admin_otp_verification')

        if timezone.now() >otp_obj.expires_at:
            messages.error(request, "OTP expired")
            return redirect('admin_forgot_password')

        if otp_obj.otp_code!=entered_otp:
            messages.error(request,"Invalid OTP")
            return redirect('admin_otp_verification')

        otp_obj.is_verified =True
        otp_obj.save()

        otp_obj.delete() #delte otp ot[ is one ytime use]
        
        request.session['otp_verified']=True # delt otp aftr user cn still procced resset pass
        return redirect('admin_reset_password')

    return render(request,'admin_otp_verification.html')


def admin_resend_otp(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.user.is_authenticated:
        return redirect("home")
    
    user_id=request.session.get('reset_user')
    if not user_id:
        return redirect('admin_forgot_password')

    user=ProfileUser.objects.get(id=user_id)

    OTPVerification.objects.filter(user=user).delete()
    otp =str(random.randint(1000,9999))


    OTPVerification.objects.create(user=user,otp_code=otp,
        expires_at=timezone.now() +timedelta(minutes=2))

    send_mail(
        "Resend OTP",
        f"Your new OTP is {otp}",
        settings.EMAIL_HOST_USER,
        [user.email],
    )

    messages.success(request,"New OTP sent")
    return redirect('admin_otp_verification')





def admin_reset_password(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
    if request.user.is_authenticated:
        return redirect("home")
    
    user_id=request.session.get('reset_user')
    verified=request.session.get('otp_verified')

    if not user_id or not verified:
        return redirect('admin_forgot_password')

    user=ProfileUser.objects.get(id=user_id)

    if request.method =="POST":
        password=request.POST.get('password')
        confirm=request.POST.get('confirm_password')

        if not password or not confirm:
            messages.error(request,"All fields required")
            return redirect('admin_reset_password')

        if password!=confirm:
            messages.error(request,"Passwords do not match")
            return redirect('admin_reset_password')

        
        pattern_pass=r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$'
        if not re.match(pattern_pass, password):
            messages.error(request,"Weak password")
            return redirect('admin_reset_password')

        user.set_password(password)
        user.save()

        # cleanup
        OTPVerification.objects.filter(user=user).delete()
        request.session.flush()

        messages.success(request,"Password reset successful")
        return redirect('admin_signin')

    return render(request, 'admin_reset_password.html')

def user_management(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')

    users = ProfileUser.objects.filter(is_superuser=False)

    if q:
        users = users.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)  |
            Q(email__icontains=q)
        )
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'blocked':
        users = users.filter(is_active=False)

    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'user_management.html', {
        'users': page_obj,
        'page_obj': page_obj,
    })

def admin_toggle_block(request, id):
    user = get_object_or_404(ProfileUser, id=id)

    # Toggle is_activ
    user.is_active = not user.is_active
    user.save()

    if user.is_active:
        messages.success(request, "User unblocked successfully")
    else:
        messages.success(request, "User blocked successfully")

    return redirect('user_management')
