from django.dispatch import Signal

notification_sent = Signal()
notification_failed = Signal()
batch_completed = Signal()
