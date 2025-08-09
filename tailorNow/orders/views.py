from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Order
from .forms import OrderForm

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
            return redirect('orders:order_detail', order_id=order.id) # Redirect to an order detail page (will create later)
    else:
        form = OrderForm(initial={'category': category})
    return render(request, 'orders/order_form.html', {'form': form, 'category': category})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user) # Ensure customer can only view their own orders
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})
