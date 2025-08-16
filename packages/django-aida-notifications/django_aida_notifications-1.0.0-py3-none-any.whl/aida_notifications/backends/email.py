import logging
from typing import Any, Dict, List

from anymail.exceptions import AnymailError
from anymail.message import AnymailMessage
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email

from .. import settings as notification_settings
from .base import BaseNotificationBackend

logger = logging.getLogger(__name__)


class AnymailBackend(BaseNotificationBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.from_email = kwargs.get('from_email', notification_settings.DEFAULT_FROM_EMAIL)
        self.from_name = kwargs.get('from_name', notification_settings.DEFAULT_FROM_NAME)

    def send(self, recipient: str, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        try:
            if not self.validate_recipient(recipient):
                raise ValidationError(f'Invalid email address: {recipient}')

            subject = message.get('subject', 'Notification')
            text_body = message.get('body', '')
            html_body = message.get('html_body', '')

            from_email = kwargs.get('from_email', self.from_email)
            if self.from_name:
                from_email = f'{self.from_name} <{from_email}>'

            msg = AnymailMessage(
                subject=subject,
                body=text_body,
                from_email=from_email,
                to=[recipient],
            )

            if html_body:
                msg.attach_alternative(html_body, 'text/html')

            if 'tags' in kwargs:
                msg.tags = kwargs['tags']

            if 'metadata' in kwargs:
                msg.metadata = kwargs['metadata']

            if 'track_opens' in kwargs:
                msg.track_opens = kwargs['track_opens']

            if 'track_clicks' in kwargs:
                msg.track_clicks = kwargs['track_clicks']

            if 'reply_to' in kwargs:
                msg.reply_to = [kwargs['reply_to']]

            if 'headers' in kwargs:
                for key, value in kwargs['headers'].items():
                    msg.extra_headers[key] = value

            if 'attachments' in kwargs:
                for attachment in kwargs['attachments']:
                    msg.attach(
                        attachment.get('filename', 'attachment'),
                        attachment.get('content'),
                        attachment.get('mimetype', 'application/octet-stream'),
                    )

            msg.send()

            return {
                'success': True,
                'message_id': getattr(msg, 'anymail_status', {}).get('message_id'),
                'provider': self.get_provider_name(),
                'recipient': recipient,
            }

        except AnymailError as e:
            self.handle_error(e, {'recipient': recipient, 'message': message})
            return {
                'success': False,
                'error': str(e),
                'provider': self.get_provider_name(),
                'recipient': recipient,
            }
        except Exception as e:
            self.handle_error(e, {'recipient': recipient, 'message': message})
            return {
                'success': False,
                'error': str(e),
                'provider': self.get_provider_name(),
                'recipient': recipient,
            }

    def send_bulk(self, messages: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        results = []
        for message_data in messages:
            recipient = message_data.pop('recipient')
            result = self.send(recipient, message_data, **kwargs)
            results.append(result)
        return results

    def validate_recipient(self, recipient: str) -> bool:
        try:
            validate_email(recipient)
            return True
        except ValidationError:
            return False


class DjangoEmailBackend(BaseNotificationBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.from_email = kwargs.get('from_email', notification_settings.DEFAULT_FROM_EMAIL)
        self.from_name = kwargs.get('from_name', notification_settings.DEFAULT_FROM_NAME)

    def send(self, recipient: str, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        try:
            if not self.validate_recipient(recipient):
                raise ValidationError(f'Invalid email address: {recipient}')

            subject = message.get('subject', 'Notification')
            text_body = message.get('body', '')
            html_body = message.get('html_body', '')

            from_email = kwargs.get('from_email', self.from_email)
            if self.from_name:
                from_email = f'{self.from_name} <{from_email}>'

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=from_email,
                to=[recipient],
            )

            if html_body:
                email.attach_alternative(html_body, 'text/html')

            if 'reply_to' in kwargs:
                email.reply_to = [kwargs['reply_to']]

            if 'headers' in kwargs:
                for key, value in kwargs['headers'].items():
                    email.extra_headers[key] = value

            if 'attachments' in kwargs:
                for attachment in kwargs['attachments']:
                    email.attach(
                        attachment.get('filename', 'attachment'),
                        attachment.get('content'),
                        attachment.get('mimetype', 'application/octet-stream'),
                    )

            email.send(fail_silently=False)

            return {
                'success': True,
                'provider': self.get_provider_name(),
                'recipient': recipient,
            }

        except Exception as e:
            self.handle_error(e, {'recipient': recipient, 'message': message})
            return {
                'success': False,
                'error': str(e),
                'provider': self.get_provider_name(),
                'recipient': recipient,
            }

    def send_bulk(self, messages: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        results = []
        for message_data in messages:
            recipient = message_data.pop('recipient')
            result = self.send(recipient, message_data, **kwargs)
            results.append(result)
        return results

    def validate_recipient(self, recipient: str) -> bool:
        try:
            validate_email(recipient)
            return True
        except ValidationError:
            return False
