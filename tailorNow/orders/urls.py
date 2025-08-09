from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('categories/', views.category_selection, name='category_selection'),
    path('categories/<int:category_id>/order/', views.order_submission, name='order_submission'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/raise-dispute/', views.raise_dispute, name='raise_dispute'),
    path('orders/<int:order_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('my-orders/', views.order_list, name='order_list'),
    path('tailor/assigned-orders/', views.tailor_assigned_orders, name='tailor_assigned_orders'),
]
