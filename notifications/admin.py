from django.contrib import admin
from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('event', 'status', 'created_at', 'short_message')
    list_filter = ('event', 'status')
    search_fields = ('message',)
    readonly_fields = ('event', 'message', 'status', 'error_detail', 'created_at')
    ordering = ('-created_at',)

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Message Preview'
