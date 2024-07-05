from django.contrib import admin

from backend.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'created_at')
    list_filter = (
        'user', 'content_type', 'created_at'
    )
    readonly_fields = ['content_object']
    search_fields = ('content', 'user__username')
