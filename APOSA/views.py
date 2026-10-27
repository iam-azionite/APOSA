from django.shortcuts import render,redirect
from .forms import CustomUserCreationForm
from members.models import UserProfile
from django.contrib.auth import authenticate, login, logout

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            UserProfile.objects.create(
                user=user,
                role='scout'
            )

            return redirect('login')

    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})