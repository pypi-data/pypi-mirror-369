from django.core.management.base import BaseCommand

from aida_notifications.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Create sample notification templates'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'welcome_email',
                'channel': NotificationTemplate.CHANNEL_EMAIL,
                'subject': 'Welcome to {{ site_name }}!',
                'body_template': """Dear {{ user.first_name|default:"User" }},

Welcome to {{ site_name }}! We're excited to have you on board.

Your account has been successfully created. You can now log in and start exploring our features.

If you have any questions, feel free to reach out to our support team.

Best regards,
The {{ site_name }} Team""",
                'html_template': """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f9f9f9; }
        .footer { text-align: center; padding: 10px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to {{ site_name }}!</h1>
        </div>
        <div class="content">
            <p>Dear {{ user.first_name|default:"User" }},</p>
            <p>Welcome to <strong>{{ site_name }}</strong>! We're excited to have you on board.</p>
            <p>Your account has been successfully created. You can now log in and start exploring our features.</p>
            <p>If you have any questions, feel free to reach out to our support team.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The {{ site_name }} Team</p>
        </div>
    </div>
</body>
</html>""",
                'variables': {
                    'user': 'User object',
                    'site_name': 'Website name',
                },
            },
            {
                'name': 'password_reset_email',
                'channel': NotificationTemplate.CHANNEL_EMAIL,
                'subject': 'Password Reset Request - {{ site_name }}',
                'body_template': """Hello {{ user.first_name|default:"User" }},

We received a request to reset your password for your {{ site_name }} account.

Please click the link below to reset your password:
{{ reset_link }}

This link will expire in {{ expiry_hours }} hours.

If you didn't request this password reset, please ignore this email.

Best regards,
The {{ site_name }} Team""",
                'variables': {
                    'user': 'User object',
                    'site_name': 'Website name',
                    'reset_link': 'Password reset URL',
                    'expiry_hours': 'Link expiry time in hours',
                },
            },
            {
                'name': 'order_confirmation_sms',
                'channel': NotificationTemplate.CHANNEL_SMS,
                'body_template': 'Your order #{{ order_id }} has been confirmed! Total: ${{ total_amount }}. Track your order: {{ tracking_url }}',
                'variables': {
                    'order_id': 'Order ID',
                    'total_amount': 'Order total',
                    'tracking_url': 'Order tracking URL',
                },
            },
            {
                'name': 'verification_code_sms',
                'channel': NotificationTemplate.CHANNEL_SMS,
                'body_template': 'Your {{ site_name }} verification code is: {{ code }}. This code expires in {{ expiry_minutes }} minutes.',
                'variables': {
                    'site_name': 'Website name',
                    'code': 'Verification code',
                    'expiry_minutes': 'Code expiry time in minutes',
                },
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = NotificationTemplate.objects.update_or_create(
                name=template_data['name'],
                defaults=template_data,
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}'),
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}'),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} templates created, {updated_count} templates updated',
            ),
        )
