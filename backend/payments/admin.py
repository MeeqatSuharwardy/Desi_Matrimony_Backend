from django.contrib import admin

from backend.payments.models import PaymentPlan, PaymentEvent


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'created_at', 'is_active')
    list_filter = (
        'amount', 'created_at', 'is_active'
    )
    search_fields = ('title', 'amount')


@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = ('type', 'payment_plan', 'amount', 'currency', 'user', 'created_at')
    list_filter = (
        'amount', 'created_at', 'type'
    )
