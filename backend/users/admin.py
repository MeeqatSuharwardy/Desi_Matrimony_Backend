from django.contrib import admin

from backend.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'created_at', 'is_active')
    list_filter = (
        'is_active', 'created_at', 'created_by',
        'gender', 'religion', 'blood_group',
        'marital_status',
    )
    search_fields = ('username', 'email')
