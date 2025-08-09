from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserRegistrationForm, TailorRegistrationForm
from django.contrib.auth.decorators import login_required
from tailorNow.orders.models import Order


def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def dashboard(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def tailor_profile(request):
    # For now, just display the existing user details.
    # In the future, you might fetch related tailor-specific data here.
    return render(request, 'accounts/tailor_profile.html', {'user': request.user})


def tailor_register(request):
    if request.method == 'POST':
        form = TailorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/tailor_register_done.html')
    else:
        form = TailorRegistrationForm()
    return render(request, 'accounts/tailor_register.html', {'form': form})

