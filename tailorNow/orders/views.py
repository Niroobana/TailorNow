from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Order
from .forms import OrderForm
from django.contrib import messages
from .forms import DisputeForm, FeedbackForm
from tailorNow.accounts.models import CustomUser, Notification

@login_required
def category_selection(request):
    categories = Category.objects.all()
    return render(request, 'orders/category_selection.html', {'categories': categories})

@login_required
def order_submission(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.category = category
            order.save()
            # Notify admins of new order submission
            for admin_user in CustomUser.objects.filter(role='admin'):
                Notification.objects.create(
                    recipient=admin_user,
                    sender=request.user,
                    message=f"New order #{order.id} submitted in {category.name}."
                )
            return redirect('orders:order_detail', order_id=order.id) # Redirect to an order detail page (will create later)
    else:
        form = OrderForm(initial={'category': category})
    return render(request, 'orders/order_form.html', {'form': form, 'category': category})

@login_required
def order_detail(request, order_id):
    # Allow customers to view their own orders, and assigned tailors to view theirs
    order = get_object_or_404(Order, id=order_id)

    if request.user.is_authenticated:
        if request.user.role == 'customer' and order.customer != request.user:
            messages.error(request, 'You are not authorized to view this order.')
            return redirect('accounts:dashboard') # Or appropriate customer order list
        elif request.user.role == 'tailor' and order.assigned_tailor != request.user:
            messages.error(request, 'You are not authorized to view this order.')
            return redirect('orders:tailor_assigned_orders') # Or appropriate tailor dashboard

    if request.method == 'POST':
        action = request.POST.get('action')
        if request.user.role == 'tailor' and order.assigned_tailor == request.user:
            if action == 'accept':
                if order.status in ['pending', 'assigned']:
                    order.status = 'in_progress'
                    order.save()
                    messages.success(request, 'Order accepted successfully!')
                    # Notify customer
                    Notification.objects.create(
                        recipient=order.customer,
                        sender=request.user,
                        message=f"Your order #{order.id} has been accepted and is now In Progress."
                    )
                else:
                    messages.error(request, 'Order cannot be accepted in its current status.')
            elif action == 'reject':
                if order.status in ['pending', 'assigned']:
                    order.status = 'cancelled'
                    order.assigned_tailor = None # Clear tailor so admin can reassign
                    order.save()
                    messages.warning(request, 'Order rejected.')
                    # Notify customer
                    Notification.objects.create(
                        recipient=order.customer,
                        sender=request.user,
                        message=f"Your order #{order.id} was rejected by the assigned tailor. We will reassign it soon."
                    )
                    # Notify admins
                    for admin_user in CustomUser.objects.filter(role='admin'):
                        Notification.objects.create(
                            recipient=admin_user,
                            sender=request.user,
                            message=f"Order #{order.id} was rejected by a tailor. Please reassign."
                        )
                else:
                    messages.error(request, 'Order cannot be rejected in its current status.')
            elif action == 'mark_in_progress':
                if order.status == 'assigned':
                    order.status = 'in_progress'
                    order.save()
                    messages.success(request, 'Order marked as In Progress.')
                    Notification.objects.create(
                        recipient=order.customer,
                        sender=request.user,
                        message=f"Your order #{order.id} is now In Progress."
                    )
                else:
                    messages.error(request, 'Order can only be marked In Progress when it is Assigned.')
            elif action == 'mark_completed':
                if order.status == 'in_progress':
                    order.status = 'completed'
                    order.save()
                    messages.success(request, 'Order marked as Completed.')
                    Notification.objects.create(
                        recipient=order.customer,
                        sender=request.user,
                        message=f"Your order #{order.id} has been completed."
                    )
                else:
                    messages.error(request, 'Order can only be marked Completed when it is In Progress.')
            return redirect('orders:tailor_assigned_orders')
        else:
            messages.error(request, 'You are not authorized to perform this action.')

    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def raise_dispute(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    # Prevent raising a dispute if one already exists for this order
    if hasattr(order, 'dispute'):
        messages.info(request, 'A dispute for this order has already been raised.')
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        form = DisputeForm(request.POST)
        if form.is_valid():
            dispute = form.save(commit=False)
            dispute.order = order
            dispute.customer = request.user
            dispute.save()
            messages.success(request, 'Your dispute has been raised successfully. We will review it shortly.')
            # Notify admins about new dispute
            for admin_user in CustomUser.objects.filter(role='admin'):
                Notification.objects.create(
                    recipient=admin_user,
                    sender=request.user,
                    message=f"New dispute raised for order #{order.id}: {dispute.reason}."
                )
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = DisputeForm()
    return render(request, 'orders/raise_dispute.html', {'form': form, 'order': order})

@login_required
def tailor_assigned_orders(request):
    if not request.user.role == 'tailor':
        return redirect('accounts:dashboard') # Only tailors can view assigned orders

    assigned_orders = Order.objects.filter(assigned_tailor=request.user).exclude(status='completed').order_by('-created_at')
    return render(request, 'orders/tailor_assigned_orders.html', {'assigned_orders': assigned_orders})

@login_required
def submit_feedback(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if order.status != 'completed':
        messages.error(request, 'You can only leave feedback for completed orders.')
        return redirect('orders:order_detail', order_id=order.id)
    if hasattr(order, 'feedback'):
        messages.info(request, 'You have already submitted feedback for this order.')
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.order = order
            feedback.customer = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = FeedbackForm()
    return render(request, 'orders/submit_feedback.html', {'form': form, 'order': order})
