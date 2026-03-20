from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,logout
# Create your views here.
def home(request):
    return render(request,'home.html')

def signout(request):
    logout(request)
    return redirect('signin')