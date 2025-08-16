import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseNotificationBackend(ABC):

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def send(self, recipient: str, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError('Subclasses must implement send method')

    @abstractmethod
    def send_bulk(self, messages: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        raise NotImplementedError('Subclasses must implement send_bulk method')

    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        raise NotImplementedError('Subclasses must implement validate_recipient method')

    def get_provider_name(self) -> str:
        return self.__class__.__name__.replace('Backend', '')

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        logger.error(
            f'Error in {self.get_provider_name()}: {error!s}',
            exc_info=True,
            extra={'context': context or {}},
        )
