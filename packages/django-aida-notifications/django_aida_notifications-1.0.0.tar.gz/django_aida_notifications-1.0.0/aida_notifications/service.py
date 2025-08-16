import logging
from typing import Any, Dict, List, Optional, Union

from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string

from . import settings as notification_settings
from .models import NotificationBatch, NotificationLog, NotificationPreference, NotificationTemplate

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:

    def __init__(self):
        self._email_backend = None
        self._sms_backend = None

    @property
    def email_backend(self):
        if self._email_backend is None:
            backend_class = import_string(notification_settings.EMAIL_BACKEND)
            self._email_backend = backend_class()
        return self._email_backend

    @property
    def sms_backend(self):
        if self._sms_backend is None:
            backend_class = import_string(notification_settings.SMS_BACKEND)
            self._sms_backend = backend_class()
        return self._sms_backend

    def send_notification(
        self,
        recipient: Union[str, User],
        template_name: Optional[str] = None,
        channel: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> NotificationLog:

        if isinstance(recipient, User):
            user = recipient
            preferences = self._get_user_preferences(user)

            if channel == NotificationTemplate.CHANNEL_EMAIL:
                recipient_address = preferences.email_address or user.email
                if not preferences.email_enabled:
                    logger.info(f'Email notifications disabled for user {user.id}')
                    return None
            elif channel == NotificationTemplate.CHANNEL_SMS:
                recipient_address = preferences.phone_number
                if not preferences.sms_enabled:
                    logger.info(f'SMS notifications disabled for user {user.id}')
                    return None
                if not recipient_address:
                    raise ValueError(f'No phone number found for user {user.id}')
            else:
                recipient_address = str(recipient)
        else:
            user = None
            recipient_address = str(recipient)

        log_entry = NotificationLog(
            user=user,
            channel=channel,
            recipient=recipient_address,
        )

        try:
            if template_name:
                template = NotificationTemplate.objects.get(
                    name=template_name,
                    channel=channel,
                    is_active=True,
                )
                log_entry.template = template

                rendered = template.render(context or {})
                message = rendered
            else:
                message = kwargs.get('message', {})
                if 'subject' in kwargs:
                    message['subject'] = kwargs['subject']
                if 'body' in kwargs:
                    message['body'] = kwargs['body']
                if 'html_body' in kwargs:
                    message['html_body'] = kwargs['html_body']

            log_entry.subject = message.get('subject', '')
            log_entry.body = message.get('body', '')
            log_entry.html_body = message.get('html_body', '')

            if notification_settings.TEST_MODE:
                test_recipients = notification_settings.TEST_MODE_RECIPIENTS.get(channel, [])
                if test_recipients:
                    recipient_address = test_recipients[0]
                else:
                    logger.info(f'[TEST MODE] Would send {channel} to {recipient_address}')
                    log_entry.status = NotificationLog.STATUS_SENT
                    log_entry.save()
                    return log_entry

            if channel == NotificationTemplate.CHANNEL_EMAIL:
                result = self.email_backend.send(recipient_address, message, **kwargs)
            elif channel == NotificationTemplate.CHANNEL_SMS:
                result = self.sms_backend.send(recipient_address, message, **kwargs)
            else:
                raise ValueError(f'Unsupported channel: {channel}')

            log_entry.provider = result.get('provider', '')

            if result['success']:
                log_entry.mark_sent(result.get('message_id'))
            else:
                log_entry.mark_failed(result.get('error', 'Unknown error'))

        except Exception as e:
            logger.exception(f'Error sending notification: {e}')
            log_entry.mark_failed(str(e))

        if notification_settings.LOG_NOTIFICATIONS:
            log_entry.save()

        return log_entry

    def send_email(
        self,
        recipient: Union[str, User],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> NotificationLog:

        if template_name:
            return self.send_notification(
                recipient=recipient,
                template_name=template_name,
                channel=NotificationTemplate.CHANNEL_EMAIL,
                context=context,
                **kwargs,
            )

        return self.send_notification(
            recipient=recipient,
            channel=NotificationTemplate.CHANNEL_EMAIL,
            subject=subject,
            body=body,
            html_body=html_body,
            **kwargs,
        )

    def send_sms(
        self,
        recipient: Union[str, User],
        body: str,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> NotificationLog:

        if template_name:
            return self.send_notification(
                recipient=recipient,
                template_name=template_name,
                channel=NotificationTemplate.CHANNEL_SMS,
                context=context,
                **kwargs,
            )

        return self.send_notification(
            recipient=recipient,
            channel=NotificationTemplate.CHANNEL_SMS,
            body=body,
            **kwargs,
        )

    def send_batch(
        self,
        recipients: List[Union[str, User]],
        template_name: str,
        channel: str,
        context: Optional[Dict[str, Any]] = None,
        batch_name: Optional[str] = None,
        **kwargs,
    ) -> NotificationBatch:

        template = NotificationTemplate.objects.get(
            name=template_name,
            channel=channel,
            is_active=True,
        )

        batch = NotificationBatch.objects.create(
            name=batch_name or f'Batch for {template_name}',
            template=template,
            recipients_count=len(recipients),
            context_data=context or {},
        )

        batch.status = NotificationBatch.STATUS_PROCESSING
        batch.save()

        sent_count = 0
        failed_count = 0

        for recipient in recipients:
            try:
                log = self.send_notification(
                    recipient=recipient,
                    template_name=template_name,
                    channel=channel,
                    context=context,
                    **kwargs,
                )

                if log and log.status == NotificationLog.STATUS_SENT:
                    sent_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                logger.error(f'Error in batch send: {e}')
                failed_count += 1

        batch.sent_count = sent_count
        batch.failed_count = failed_count
        batch.status = NotificationBatch.STATUS_COMPLETED
        batch.save()

        return batch

    def retry_failed_notifications(self, hours: int = 24) -> int:
        from datetime import timedelta

        from django.utils import timezone

        if not notification_settings.RETRY_FAILED_NOTIFICATIONS:
            return 0

        cutoff = timezone.now() - timedelta(hours=hours)
        failed_logs = NotificationLog.objects.filter(
            status=NotificationLog.STATUS_FAILED,
            created_at__gte=cutoff,
            attempts__lt=notification_settings.MAX_RETRY_ATTEMPTS,
        )

        retried = 0
        for log in failed_logs:
            log.attempts += 1
            log.save()

            try:
                if log.channel == NotificationTemplate.CHANNEL_EMAIL:
                    result = self.email_backend.send(
                        log.recipient,
                        {
                            'subject': log.subject,
                            'body': log.body,
                            'html_body': log.html_body,
                        },
                    )
                elif log.channel == NotificationTemplate.CHANNEL_SMS:
                    result = self.sms_backend.send(
                        log.recipient,
                        {'body': log.body},
                    )
                else:
                    continue

                if result['success']:
                    log.mark_sent(result.get('message_id'))
                    retried += 1
                else:
                    log.error_message = result.get('error', 'Retry failed')
                    log.save()

            except Exception as e:
                logger.error(f'Error retrying notification {log.id}: {e}')
                log.error_message = str(e)
                log.save()

        return retried

    def _get_user_preferences(self, user: User) -> NotificationPreference:
        preferences, created = NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'email_address': user.email,
                'email_enabled': True,
                'sms_enabled': True,
            },
        )
        return preferences


notification_service = NotificationService()
