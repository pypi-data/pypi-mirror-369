from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from aida_notifications.service import notification_service

User = get_user_model()


class Command(BaseCommand):
    help = 'Test notification sending via email or SMS'

    def add_arguments(self, parser):
        parser.add_argument(
            'channel',
            type=str,
            choices=['email', 'sms'],
            help='Notification channel to test',
        )
        parser.add_argument(
            'recipient',
            type=str,
            help='Email address or phone number',
        )
        parser.add_argument(
            '--template',
            type=str,
            help='Template name to use',
        )
        parser.add_argument(
            '--subject',
            type=str,
            default='Test Notification',
            help='Email subject (for email channel)',
        )
        parser.add_argument(
            '--body',
            type=str,
            default='This is a test notification from AIDA Notifications.',
            help='Message body',
        )
        parser.add_argument(
            '--html',
            type=str,
            help='HTML body (for email channel)',
        )
        parser.add_argument(
            '--context',
            type=str,
            help='JSON context data for template rendering',
        )

    def handle(self, *args, **options):
        channel = options['channel']
        recipient = options['recipient']
        template = options.get('template')

        context = {}
        if options.get('context'):
            import json
            try:
                context = json.loads(options['context'])
            except json.JSONDecodeError:
                raise CommandError('Invalid JSON context data')

        try:
            if channel == 'email':
                if template:
                    log = notification_service.send_email(
                        recipient=recipient,
                        template_name=template,
                        context=context,
                        subject='',
                        body='',
                    )
                else:
                    log = notification_service.send_email(
                        recipient=recipient,
                        subject=options['subject'],
                        body=options['body'],
                        html_body=options.get('html'),
                    )
            else:
                if template:
                    log = notification_service.send_sms(
                        recipient=recipient,
                        template_name=template,
                        context=context,
                        body='',
                    )
                else:
                    log = notification_service.send_sms(
                        recipient=recipient,
                        body=options['body'],
                    )

            if log:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Notification sent successfully! '
                        f'Status: {log.status}, ID: {log.id}',
                    ),
                )
                if log.provider_message_id:
                    self.stdout.write(f'Provider message ID: {log.provider_message_id}')
            else:
                self.stdout.write(
                    self.style.WARNING('Notification was not sent (possibly disabled)'),
                )

        except Exception as e:
            raise CommandError(f'Failed to send notification: {e}')
