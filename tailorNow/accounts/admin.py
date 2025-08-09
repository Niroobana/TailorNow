from django.contrib import admin
from .models import CustomUser, Notification

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_approved', 'is_available', 'is_staff', 'is_active')
    list_filter = ('role', 'is_approved', 'is_available', 'is_staff', 'is_active')
    search_fields = ('email',)
    actions = ['approve_tailors', 'set_available', 'set_unavailable']

    def approve_tailors(self, request, queryset):
        updated = queryset.filter(role='tailor', is_approved=False).update(is_approved=True)
        self.message_user(request, f"{updated} tailor(s) approved.")
    approve_tailors.short_description = "Approve selected tailors"

    def set_available(self, request, queryset):
        updated = queryset.filter(role='tailor').update(is_available=True)
        self.message_user(request, f"{updated} tailor(s) set to available.")
    set_available.short_description = "Set selected tailors as available"

    def set_unavailable(self, request, queryset):
        updated = queryset.filter(role='tailor').update(is_available=False)
        self.message_user(request, f"{updated} tailor(s) set to unavailable.")
    set_unavailable.short_description = "Set selected tailors as unavailable"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'sender', 'short_message', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('recipient__email', 'sender__email', 'message')

    def short_message(self, obj):
        return (obj.message[:60] + '...') if len(obj.message) > 60 else obj.message
    short_message.short_description = 'Message'

