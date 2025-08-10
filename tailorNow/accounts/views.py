from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserRegistrationForm, TailorRegistrationForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from tailorNow.orders.models import Order, Dispute, Feedback
from tailorNow.accounts.forms import AvailabilityForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Avg
from tailorNow.accounts.models import CustomUser, Notification


def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('accounts:login')
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
    notifications = request.user.notifications.all()[:20]
    if request.method == 'POST' and request.POST.get('form') == 'profile_update':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:dashboard')
    else:
        form = ProfileUpdateForm(instance=request.user)
    context = {
        'orders': orders,
        'notifications': notifications,
        'profile_form': form,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def update_availability(request):
    if not request.user.role == 'tailor':
        return redirect('accounts:dashboard') # Only tailors can update availability

    if request.method == 'POST':
        form = AvailabilityForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your availability status has been updated.')
            return redirect('accounts:dashboard') # Redirect to dashboard after update
    else:
        form = AvailabilityForm(instance=request.user)
    return render(request, 'accounts/update_availability.html', {'form': form})


@login_required
@user_passes_test(lambda user: user.role == 'admin')
def analytics_dashboard(request):
    total_orders = Order.objects.count()
    active_tailors = CustomUser.objects.filter(role='tailor', is_approved=True, is_available=True).count()

    completed_orders = Order.objects.filter(status='completed')
    avg_completion_time = None
    if completed_orders.exists():
        avg_completion_time = f"{completed_orders.count()} orders completed (Placeholder)"
    else:
        avg_completion_time = "N/A"

    avg_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    feedback_count = Feedback.objects.count()

    context = {
        'total_orders': total_orders,
        'active_tailors': active_tailors,
        'avg_completion_time': avg_completion_time,
        'open_disputes': Dispute.objects.filter(status='open').count(),
        'in_review_disputes': Dispute.objects.filter(status='in_review').count(),
        'resolved_disputes': Dispute.objects.filter(status='resolved').count(),
        'closed_disputes': Dispute.objects.filter(status='closed').count(),
        'avg_rating': avg_rating,
        'feedback_count': feedback_count,
    }
    return render(request, 'accounts/analytics_dashboard.html', context)


def tailor_register(request):
    if request.method == 'POST':
        form = TailorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/tailor_register_done.html')
    else:
        form = TailorRegistrationForm()
    return render(request, 'accounts/tailor_register.html', {'form': form})


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('accounts:dashboard')

