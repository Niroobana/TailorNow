from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_approved', 'is_staff', 'is_active')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('email',)
    actions = ['approve_tailors']

    def approve_tailors(self, request, queryset):
        updated = queryset.filter(role='tailor', is_approved=False).update(is_approved=True)
        self.message_user(request, f"{updated} tailor(s) approved.")
    approve_tailors.short_description = "Approve selected tailors"

