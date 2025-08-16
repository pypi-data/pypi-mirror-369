import logging
import re
from typing import Any, Dict, List

from twilio.base.exceptions import TwilioException
from twilio.rest import Client

from .. import settings as notification_settings
from .base import BaseNotificationBackend

logger = logging.getLogger(__name__)


class TwilioBackend(BaseNotificationBackend):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.account_sid = kwargs.get('account_sid', notification_settings.TWILIO_ACCOUNT_SID)
        self.auth_token = kwargs.get('auth_token', notification_settings.TWILIO_AUTH_TOKEN)
        self.from_number = kwargs.get('from_number', notification_settings.TWILIO_FROM_NUMBER)
        self.messaging_service_sid = kwargs.get('messaging_service_sid', notification_settings.TWILIO_MESSAGING_SERVICE_SID)

        if not self.account_sid or not self.auth_token:
            raise ValueError('Twilio account SID and auth token are required')

        if not self.from_number and not self.messaging_service_sid:
            raise ValueError('Either Twilio from_number or messaging_service_sid is required')

        self.client = Client(self.account_sid, self.auth_token)

    def send(self, recipient: str, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        try:
            if not self.validate_recipient(recipient):
                raise ValueError(f'Invalid phone number: {recipient}')

            body = message.get('body', '')
            if not body:
                raise ValueError('Message body is required for SMS')

            to_number = self._normalize_phone_number(recipient)

            message_params = {
                'body': body[:1600],
                'to': to_number,
            }

            if self.messaging_service_sid:
                message_params['messaging_service_sid'] = self.messaging_service_sid
            else:
                message_params['from_'] = kwargs.get('from_number', self.from_number)

            if 'media_url' in kwargs:
                message_params['media_url'] = kwargs['media_url']

            if 'status_callback' in kwargs:
                message_params['status_callback'] = kwargs['status_callback']

            twilio_message = self.client.messages.create(**message_params)

            return {
                'success': True,
                'message_id': twilio_message.sid,
                'provider': self.get_provider_name(),
                'recipient': recipient,
                'status': twilio_message.status,
            }

        except TwilioException as e:
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
        phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        return bool(phone_pattern.match(recipient.replace(' ', '').replace('-', '')))

    def _normalize_phone_number(self, phone: str) -> str:
        phone = re.sub(r'\D', '', phone)

        if not phone.startswith('+'):
            if len(phone) == 10:
                phone = '+1' + phone
            elif (not phone.startswith('1') and len(phone) == 11) or (phone.startswith('1') and len(phone) == 11):
                phone = '+' + phone
            else:
                phone = '+' + phone

        return phone

    def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                'sid': message.sid,
                'status': message.status,
                'date_sent': message.date_sent,
                'error_code': message.error_code,
                'error_message': message.error_message,
            }
        except TwilioException as e:
            logger.error(f'Error fetching message status: {e}')
            return {'error': str(e)}


class DummySMSBackend(BaseNotificationBackend):

    def send(self, recipient: str, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        if not self.validate_recipient(recipient):
            return {
                'success': False,
                'error': f'Invalid phone number: {recipient}',
                'provider': self.get_provider_name(),
                'recipient': recipient,
            }

        logger.info(f"[DummySMS] Sending to {recipient}: {message.get('body', '')[:100]}")

        return {
            'success': True,
            'message_id': f'dummy_{id(message)}',
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
        phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        return bool(phone_pattern.match(recipient.replace(' ', '').replace('-', '')))
