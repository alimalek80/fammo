from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, AccountDeletionRequest
from django.utils import timezone
from datetime import timedelta
from django.utils.html import format_html

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'subscription_plan', 'is_writer')
    list_filter = ('subscription_plan', 'is_writer')
    search_fields = ('user__email', 'first_name', 'last_name')
    autocomplete_fields = ['subscription_plan']
    fields = ('user', 'first_name', 'last_name', 'phone', 'address', 'city', 'zip_code', 'country', 'subscription_plan', 'is_writer')

class AccountDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'status', 'requested_at', 'days_remaining', 'pets_count', 'had_clinic', 'actions_buttons')
    list_filter = ('status', 'had_clinic', 'requested_at')
    search_fields = ('user__email',)
    readonly_fields = ('user', 'requested_at', 'pets_count', 'had_pets', 'had_clinic', 'completed_at')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'requested_at', 'reason', 'status')
        }),
        ('User Data', {
            'fields': ('pets_count', 'had_pets', 'had_clinic')
        }),
        ('Admin Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'admin_notes')
        }),
        ('Deletion Schedule', {
            'fields': ('scheduled_deletion_date', 'completed_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def days_remaining(self, obj):
        days = obj.days_until_deletion()
        if days is not None:
            if days == 0:
                return format_html('<span style="color: red; font-weight: bold;">Today</span>')
            elif days <= 3:
                return format_html('<span style="color: orange; font-weight: bold;">{} days</span>', days)
            else:
                return f'{days} days'
        return '-'
    days_remaining.short_description = 'Days Until Deletion'
    
    def actions_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}">Approve</a>',
                f'/admin/userapp/accountdeletionrequest/{obj.pk}/approve/'
            )
        return '-'
    actions_buttons.short_description = 'Actions'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/approve/', self.admin_site.admin_view(self.approve_deletion), name='approve_deletion'),
        ]
        return custom_urls + urls
    
    def approve_deletion(self, request, pk):
        from django.shortcuts import redirect
        from django.contrib import messages
        from django.core.mail import send_mail
        from django.conf import settings
        
        deletion_request = AccountDeletionRequest.objects.get(pk=pk)
        
        if deletion_request.status == 'pending':
            deletion_request.status = 'approved'
            deletion_request.reviewed_by = request.user
            deletion_request.reviewed_at = timezone.now()
            deletion_request.scheduled_deletion_date = timezone.now() + timedelta(days=15)
            deletion_request.save()
            
            # Send email to user
            try:
                send_mail(
                    'Your Account Deletion Request Has Been Approved',
                    f'''Your account deletion request has been approved.

Your account will be permanently deleted on: {deletion_request.scheduled_deletion_date.strftime('%B %d, %Y at %H:%M')}

You have 15 days to cancel this request if you change your mind. After that, your account and all associated data will be permanently removed.

To cancel, log in to your dashboard at: https://fammo.ai

If you have any questions, please contact us at support@fammo.ai
                    ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [deletion_request.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                messages.warning(request, f'Approved but email failed: {str(e)}')
            
            messages.success(request, f'Deletion request approved. User will be deleted in 15 days.')
        else:
            messages.error(request, 'Request is not pending.')
        
        return redirect('/admin/userapp/accountdeletionrequest/')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AccountDeletionRequest, AccountDeletionRequestAdmin)
admin.site.register(Profile, ProfileAdmin)
