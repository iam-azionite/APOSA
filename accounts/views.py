from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')