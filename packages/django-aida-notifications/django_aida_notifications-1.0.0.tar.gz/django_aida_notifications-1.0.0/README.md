# Django AIDA Notifications

[![Python Version](https://img.shields.io/pypi/pyversions/django-aida-notifications)](https://pypi.org/project/django-aida-notifications/)
[![Django Version](https://img.shields.io/badge/django-3.2%20to%205.1-blue)](https://www.djangoproject.com/)
[![PyPI Version](https://img.shields.io/pypi/v/django-aida-notifications)](https://pypi.org/project/django-aida-notifications/)
[![License](https://img.shields.io/github/license/hmesfin/aida-notifications)](https://github.com/hmesfin/aida-notifications/blob/main/LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/hmesfin/aida-notifications)](https://github.com/hmesfin/aida-notifications)

A comprehensive Django notification extension that provides email and SMS notification capabilities with template management, delivery tracking, and support for multiple providers.

## Features

- **Multi-channel Support**: Send notifications via Email and SMS
- **Template Management**: Create and manage reusable notification templates with Django template syntax
- **Provider Abstraction**: Easy switching between email providers (via Django Anymail) and SMS providers (Twilio)
- **Delivery Tracking**: Complete logging of all sent notifications with status tracking
- **User Preferences**: Allow users to control their notification preferences
- **Batch Sending**: Send notifications to multiple recipients efficiently
- **Admin Interface**: Full Django admin integration for managing templates and viewing logs
- **Test Mode**: Safe testing without sending actual notifications
- **Retry Logic**: Automatic retry for failed notifications
- **Django 5.1 Compatible**: Supports Django 3.2 through 5.1

## Installation

### From PyPI (Recommended)

```bash
pip install django-aida-notifications
```

### From GitHub

```bash
pip install git+https://github.com/hmesfin/aida-notifications.git
```

### From Source

```bash
git clone https://github.com/hmesfin/aida-notifications.git
cd aida-notifications
pip install -e .
```

## Quick Start

### 1. Add to Django Settings

```python
# settings.py

INSTALLED_APPS = [
    ...
    'aida_notifications',
    'anymail',  # Required for email support
    ...
]

# Anymail Configuration
ANYMAIL = {
    "SENDGRID_API_KEY": "your-sendgrid-api-key",
    # Or use another provider like Mailgun, Postmark, etc.
}
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"

# AIDA Notifications Configuration
AIDA_NOTIFICATIONS = {
    'DEFAULT_FROM_EMAIL': 'noreply@example.com',
    'DEFAULT_FROM_NAME': 'Your App Name',
    'TWILIO_ACCOUNT_SID': 'your-twilio-account-sid',
    'TWILIO_AUTH_TOKEN': 'your-twilio-auth-token',
    'TWILIO_FROM_NUMBER': '+1234567890',
    'LOG_NOTIFICATIONS': True,
    'TEST_MODE': False,  # Set to True for testing
}
```

### 2. Run Migrations

```bash
python manage.py migrate aida_notifications
```

### 3. Create Sample Templates

```bash
python manage.py create_sample_templates
```

### 4. Send Your First Notification

```python
from aida_notifications.service import notification_service

# Send a simple email
notification_service.send_email(
    recipient='user@example.com',
    subject='Welcome!',
    body='Welcome to our platform!',
    html_body='<h1>Welcome to our platform!</h1>'
)

# Send using a template
notification_service.send_email(
    recipient=user,  # Can be a User object
    template_name='welcome_email',
    context={
        'user': user,
        'site_name': 'My App'
    }
)

# Send an SMS
notification_service.send_sms(
    recipient='+1234567890',
    body='Your verification code is 123456'
)
```

## Configuration Options

### Email Providers (via Django Anymail)

AIDA Notifications uses Django Anymail for email delivery, supporting multiple providers:

- SendGrid
- Mailgun
- Postmark
- Amazon SES
- SparkPost
- Mandrill
- Sendinblue
- And more...

Example configuration for different providers:

```python
# SendGrid
ANYMAIL = {
    "SENDGRID_API_KEY": "your-api-key",
}
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"

# Mailgun
ANYMAIL = {
    "MAILGUN_API_KEY": "your-api-key",
    "MAILGUN_SENDER_DOMAIN": "mg.example.com",
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

# Amazon SES
ANYMAIL = {
    "AMAZON_SES_CLIENT_PARAMS": {
        "aws_access_key_id": "your-access-key",
        "aws_secret_access_key": "your-secret-key",
        "region_name": "us-east-1",
    },
}
EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
```

### SMS Configuration (Twilio)

```python
AIDA_NOTIFICATIONS = {
    'TWILIO_ACCOUNT_SID': 'your-account-sid',
    'TWILIO_AUTH_TOKEN': 'your-auth-token',
    'TWILIO_FROM_NUMBER': '+1234567890',
    # Or use Messaging Service SID instead
    'TWILIO_MESSAGING_SERVICE_SID': 'your-messaging-service-sid',
}
```

### Advanced Settings

```python
AIDA_NOTIFICATIONS = {
    # Retry Configuration
    'RETRY_FAILED_NOTIFICATIONS': True,
    'MAX_RETRY_ATTEMPTS': 3,
    'RETRY_DELAY_SECONDS': 300,
    
    # Rate Limiting
    'ENABLE_RATE_LIMITING': True,
    'RATE_LIMIT_PER_HOUR': 100,
    
    # Batch Processing
    'BATCH_SIZE': 100,
    'USE_CELERY': True,  # For async processing
    
    # Testing
    'TEST_MODE': False,
    'TEST_MODE_RECIPIENTS': {
        'email': ['test@example.com'],
        'sms': ['+1234567890']
    }
}
```

## Template Management

### Creating Templates

Templates can be created via Django admin or programmatically:

```python
from aida_notifications.models import NotificationTemplate

template = NotificationTemplate.objects.create(
    name='order_confirmation',
    channel='email',
    subject='Order #{{ order.id }} Confirmed',
    body_template='''
    Hi {{ user.first_name }},
    
    Your order #{{ order.id }} has been confirmed.
    Total: ${{ order.total }}
    
    Thank you for your purchase!
    ''',
    html_template='''
    <h2>Order Confirmation</h2>
    <p>Hi {{ user.first_name }},</p>
    <p>Your order #{{ order.id }} has been confirmed.</p>
    <p><strong>Total: ${{ order.total }}</strong></p>
    <p>Thank you for your purchase!</p>
    ''',
    variables={
        'user': 'User object',
        'order': 'Order object'
    }
)
```

### Using Templates

```python
from aida_notifications.service import notification_service

# Send to a single user
notification_service.send_notification(
    recipient=user,
    template_name='order_confirmation',
    channel='email',
    context={
        'user': user,
        'order': order
    }
)

# Send to multiple recipients
notification_service.send_batch(
    recipients=[user1, user2, user3],
    template_name='newsletter',
    channel='email',
    context={
        'newsletter_date': 'January 2024'
    }
)
```

## User Preferences

Allow users to manage their notification preferences:

```python
from aida_notifications.models import NotificationPreference

# Create or update preferences
pref, created = NotificationPreference.objects.get_or_create(
    user=user,
    defaults={
        'email_enabled': True,
        'sms_enabled': True,
        'email_address': user.email,
        'phone_number': '+1234567890'
    }
)

# Disable email notifications
pref.email_enabled = False
pref.save()
```

## Management Commands

### Test Notifications

```bash
# Test email
python manage.py test_notification email user@example.com \
    --subject "Test Email" \
    --body "This is a test email"

# Test SMS
python manage.py test_notification sms +1234567890 \
    --body "This is a test SMS"

# Test with template
python manage.py test_notification email user@example.com \
    --template welcome_email \
    --context '{"user": {"first_name": "John"}}'
```

### Create Sample Templates

```bash
python manage.py create_sample_templates
```

## Admin Interface

The extension provides a comprehensive Django admin interface for:

- **Templates**: Create, edit, and preview notification templates
- **Logs**: View all sent notifications with filtering and search
- **Preferences**: Manage user notification preferences
- **Batches**: Monitor batch notification jobs

Access the admin at `/admin/aida_notifications/`

## API Reference

### NotificationService

```python
from aida_notifications.service import notification_service

# Send email
notification_service.send_email(
    recipient='email@example.com',  # or User object
    subject='Subject',
    body='Plain text body',
    html_body='<p>HTML body</p>',
    template_name='template_name',  # Optional
    context={},  # Template context
    reply_to='reply@example.com',
    attachments=[
        {
            'filename': 'document.pdf',
            'content': file_content,
            'mimetype': 'application/pdf'
        }
    ]
)

# Send SMS
notification_service.send_sms(
    recipient='+1234567890',  # or User object
    body='SMS message',
    template_name='template_name',  # Optional
    context={},  # Template context
    media_url='https://example.com/image.jpg'  # MMS
)

# Send batch
batch = notification_service.send_batch(
    recipients=[user1, user2, user3],
    template_name='newsletter',
    channel='email',
    context={'month': 'January'},
    batch_name='January Newsletter'
)

# Retry failed notifications
retried_count = notification_service.retry_failed_notifications(hours=24)
```

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test aida_notifications

# Run with coverage
pytest --cov=aida_notifications tests/
```

### Test Mode

Enable test mode to prevent actual notifications from being sent:

```python
AIDA_NOTIFICATIONS = {
    'TEST_MODE': True,
    'TEST_MODE_RECIPIENTS': {
        'email': ['test@example.com'],
        'sms': ['+1234567890']
    }
}
```

## Celery Integration

For asynchronous notification sending, integrate with Celery:

```python
# tasks.py
from celery import shared_task
from aida_notifications.service import notification_service

@shared_task
def send_notification_async(recipient, template_name, channel, context):
    return notification_service.send_notification(
        recipient=recipient,
        template_name=template_name,
        channel=channel,
        context=context
    )
```

## Error Handling

```python
from aida_notifications.service import notification_service
from aida_notifications.models import NotificationLog

try:
    log = notification_service.send_email(
        recipient='user@example.com',
        subject='Test',
        body='Test message'
    )
    
    if log.status == NotificationLog.STATUS_SENT:
        print(f"Sent successfully: {log.provider_message_id}")
    else:
        print(f"Failed: {log.error_message}")
        
except Exception as e:
    print(f"Error: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please use the GitHub issue tracker.

## Changelog

### Version 1.0.0
- Initial release
- Email support via Django Anymail
- SMS support via Twilio
- Template management
- User preferences
- Batch sending
- Django 5.1 compatibility