
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import NotificationBatch, NotificationLog, NotificationPreference, NotificationTemplate


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'is_active', 'created_at', 'updated_at']
    list_filter = ['channel', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'body_template']
    readonly_fields = ['id', 'created_at', 'updated_at', 'preview_template']

    fieldsets = (
        (None, {
            'fields': ('name', 'channel', 'is_active'),
        }),
        ('Content', {
            'fields': ('subject', 'body_template', 'html_template', 'preview_template'),
        }),
        ('Configuration', {
            'fields': ('variables', 'metadata'),
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def preview_template(self, obj):
        if obj.pk:
            preview_url = reverse('admin:aida_notifications_notificationtemplate_preview', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" class="button">Preview Template</a>',
                preview_url,
            )
        return 'Save template to preview'
    preview_template.short_description = 'Preview'

    def get_urls(self):
        from django.http import HttpResponse
        from django.urls import path

        urls = super().get_urls()

        def preview_view(request, pk):
            template = NotificationTemplate.objects.get(pk=pk)
            sample_context = {
                'user': {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
                'site_name': 'Your Site',
                'order_id': '12345',
                'total_amount': '99.99',
                'code': '123456',
                'expiry_minutes': '10',
                'reset_link': 'https://example.com/reset',
                'tracking_url': 'https://example.com/track/12345',
            }

            try:
                rendered = template.render(sample_context)
                if template.channel == NotificationTemplate.CHANNEL_EMAIL and 'html_body' in rendered:
                    return HttpResponse(rendered['html_body'], content_type='text/html')
                content = f"<pre>Subject: {rendered.get('subject', '')}\n\n{rendered.get('body', '')}</pre>"
                return HttpResponse(content, content_type='text/html')
            except Exception as e:
                return HttpResponse(f'<pre>Error rendering template: {e}</pre>', content_type='text/html')

        custom_urls = [
            path('<pk>/preview/', preview_view, name='aida_notifications_notificationtemplate_preview'),
        ]

        return custom_urls + urls


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'get_recipient_display', 'channel', 'get_status_badge',
        'provider', 'created_at', 'sent_at',
    ]
    list_filter = ['status', 'channel', 'provider', 'created_at']
    search_fields = ['recipient', 'subject', 'body', 'provider_message_id']
    readonly_fields = [
        'id', 'template', 'user', 'channel', 'recipient', 'subject',
        'body', 'html_body', 'status', 'provider', 'provider_message_id',
        'error_message', 'metadata', 'attempts', 'sent_at', 'created_at', 'updated_at',
    ]
    date_hierarchy = 'created_at'

    def get_recipient_display(self, obj):
        if obj.user:
            return format_html(
                '{} <small>({})</small>',
                obj.recipient,
                obj.user.get_full_name() or obj.user.username,
            )
        return obj.recipient
    get_recipient_display.short_description = 'Recipient'

    def get_status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'sent': '#28a745',
            'failed': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display(),
        )
    get_status_badge.short_description = 'Status'

    def has_add_permission(self, request):
        return False

    actions = ['resend_notifications']

    def resend_notifications(self, request, queryset):
        from .service import notification_service

        resent = 0
        for log in queryset.filter(status='failed'):
            try:
                if log.channel == NotificationTemplate.CHANNEL_EMAIL:
                    result = notification_service.email_backend.send(
                        log.recipient,
                        {
                            'subject': log.subject,
                            'body': log.body,
                            'html_body': log.html_body,
                        },
                    )
                elif log.channel == NotificationTemplate.CHANNEL_SMS:
                    result = notification_service.sms_backend.send(
                        log.recipient,
                        {'body': log.body},
                    )
                else:
                    continue

                if result['success']:
                    log.mark_sent(result.get('message_id'))
                    resent += 1
            except Exception as e:
                self.message_user(request, f'Error resending to {log.recipient}: {e}', level='ERROR')

        self.message_user(request, f'Successfully resent {resent} notifications')
    resend_notifications.short_description = 'Resend failed notifications'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'sms_enabled', 'email_address', 'phone_number']
    list_filter = ['email_enabled', 'sms_enabled', 'created_at']
    search_fields = ['user__username', 'user__email', 'email_address', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',),
        }),
        ('Email Settings', {
            'fields': ('email_enabled', 'email_address'),
        }),
        ('SMS Settings', {
            'fields': ('sms_enabled', 'phone_number'),
        }),
        ('Advanced', {
            'fields': ('preferences', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(NotificationBatch)
class NotificationBatchAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template', 'get_status_badge', 'recipients_count',
        'sent_count', 'failed_count', 'created_at',
    ]
    list_filter = ['status', 'template__channel', 'created_at']
    search_fields = ['name', 'template__name']
    readonly_fields = [
        'id', 'status', 'recipients_count', 'sent_count', 'failed_count',
        'started_at', 'completed_at', 'created_at', 'updated_at',
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('name', 'template', 'status'),
        }),
        ('Statistics', {
            'fields': ('recipients_count', 'sent_count', 'failed_count'),
        }),
        ('Configuration', {
            'fields': ('context_data', 'metadata', 'scheduled_for'),
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display(),
        )
    get_status_badge.short_description = 'Status'
