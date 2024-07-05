from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin

from backend.events.models import Event, UserEvent


class EventAdminForm(forms.ModelForm):
    detail = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Event
        fields = '__all__'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    readonly_fields = (
        'created_by', 'created_at', 'updated_at',
        'attend_count', 'not_attend_count', 'ignore_count'
    )
    list_display = ('title', 'start_date', 'end_date', 'created_by', 'is_active')
    list_filter = ('start_date', 'end_date', 'is_active')
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='Event Attend Count')
    def attend_count(self, instance):
        return instance.user_events.filter(interest_status=UserEvent.InterestStatus.ATTEND).count()

    @admin.display(description='Event Not Attend Count')
    def not_attend_count(self, instance):
        return instance.user_events.filter(interest_status=UserEvent.InterestStatus.NOT_ATTEND).count()

    @admin.display(description='Event Ignore Count')
    def ignore_count(self, instance):
        return instance.user_events.filter(interest_status=UserEvent.InterestStatus.IGNORE).count()
