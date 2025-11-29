from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_trip', 'end_trip', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_trip'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Trip Dates', {
            'fields': ('start_trip', 'end_trip')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
