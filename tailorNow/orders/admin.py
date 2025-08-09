from django.contrib import admin
from .models import Category, Order, Dispute, Feedback
from tailorNow.accounts.models import CustomUser, Notification
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

admin.site.register(Category)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'category', 'status', 'is_urgent', 'assigned_tailor', 'created_at')
    list_filter = ('status', 'is_urgent', 'category', 'assigned_tailor')
    search_fields = ('customer__email', 'assigned_tailor__email', 'category__name')
    raw_id_fields = ('customer',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_tailor":
            kwargs["queryset"] = CustomUser.objects.filter(role='tailor', is_approved=True, is_available=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        previous_assigned_tailor = None
        previous_status = None
        if change:
            try:
                prev = Order.objects.get(pk=obj.pk)
                previous_assigned_tailor = prev.assigned_tailor
                previous_status = prev.status
            except Order.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
        # Notify on assignment changes
        if obj.assigned_tailor and obj.assigned_tailor != previous_assigned_tailor:
            Notification.objects.create(
                recipient=obj.assigned_tailor,
                sender=request.user,
                message=f"You have been assigned to order #{obj.id} ({obj.category.name if obj.category else 'N/A'})."
            )
            Notification.objects.create(
                recipient=obj.customer,
                sender=request.user,
                message=f"Your order #{obj.id} has been assigned to {obj.assigned_tailor.email}."
            )
        # Notify on status changes
        if previous_status and obj.status != previous_status:
            # Notify customer
            Notification.objects.create(
                recipient=obj.customer,
                sender=request.user,
                message=f"Order #{obj.id} status changed from {previous_status.replace('_',' ').title()} to {obj.status.replace('_',' ').title()}."
            )
            # Notify tailor if exists
            if obj.assigned_tailor:
                Notification.objects.create(
                    recipient=obj.assigned_tailor,
                    sender=request.user,
                    message=f"Order #{obj.id} status updated to {obj.status.replace('_',' ').title()} by admin."
                )

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'customer', 'reason', 'status', 'created_at', 'resolved_by')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('order__id__iexact', 'customer__email', 'reason', 'description')
    raw_id_fields = ('order', 'customer', 'resolved_by')
    actions = ['mark_in_review', 'mark_resolved', 'mark_closed']

    def order_link(self, obj):
        link = reverse("admin:orders_order_change", args=[obj.order.id])
        return format_html('<a href="{}">Order {}</a>', link, obj.order.id)
    order_link.short_description = "Order"

    def _notify_dispute_update(self, dispute, new_status, actor):
        # Notify customer
        Notification.objects.create(
            recipient=dispute.customer,
            sender=actor,
            message=f"Your dispute for order #{dispute.order.id} is now {new_status.replace('_',' ').title()}."
        )
        # Notify tailor if any
        if dispute.order.assigned_tailor:
            Notification.objects.create(
                recipient=dispute.order.assigned_tailor,
                sender=actor,
                message=f"Dispute for order #{dispute.order.id} is now {new_status.replace('_',' ').title()}."
            )

    def mark_in_review(self, request, queryset):
        updated = 0
        for dispute in queryset.select_related('order', 'customer'):
            if dispute.status == 'open':
                dispute.status = 'in_review'
                dispute.save(update_fields=['status'])
                self._notify_dispute_update(dispute, 'in_review', request.user)
                updated += 1
        self.message_user(request, f"{updated} dispute(s) marked as In Review.")
    mark_in_review.short_description = "Mark selected disputes as In Review"

    def mark_resolved(self, request, queryset):
        updated = 0
        for dispute in queryset.select_related('order', 'customer'):
            if dispute.status in ['open', 'in_review']:
                dispute.status = 'resolved'
                dispute.resolved_at = timezone.now()
                dispute.resolved_by = request.user
                dispute.save(update_fields=['status', 'resolved_at', 'resolved_by'])
                self._notify_dispute_update(dispute, 'resolved', request.user)
                updated += 1
        self.message_user(request, f"{updated} dispute(s) marked as Resolved.")
    mark_resolved.short_description = "Mark selected disputes as Resolved"

    def mark_closed(self, request, queryset):
        updated = 0
        for dispute in queryset.select_related('order', 'customer'):
            if dispute.status != 'closed':
                dispute.status = 'closed'
                dispute.resolved_at = timezone.now()
                dispute.resolved_by = request.user
                dispute.save(update_fields=['status', 'resolved_at', 'resolved_by'])
                self._notify_dispute_update(dispute, 'closed', request.user)
                updated += 1
        self.message_user(request, f"{updated} dispute(s) marked as Closed.")
    mark_closed.short_description = "Mark selected disputes as Closed"

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'customer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('order__id__iexact', 'customer__email')
