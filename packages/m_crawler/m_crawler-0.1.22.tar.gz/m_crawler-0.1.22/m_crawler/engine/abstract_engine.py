from abc import ABC, abstractmethod
from typing import Optional

from m_crawler.engine.abstract_request import AbstractRequest
from m_crawler.engine.abstract_response import AbstractResponse


class AbstractEngine(ABC):
    """
    引擎,提供与网站实际的交互能力
    """

    def before_download_hook(
        self, request: AbstractRequest
    ) -> Optional[AbstractRequest]:
        """
        before_download_hook
        """
        return request

    def after_download_hook(
        self, result: AbstractResponse
    ) -> Optional[AbstractResponse]:
        """
        after_download_hook
        """
        return result

    @abstractmethod
    def download(self, request: AbstractRequest) -> AbstractResponse:
        pass

    def run(self, request: AbstractRequest) -> Optional[AbstractResponse]:
        if not request:
            return None
        processed_request: Optional[AbstractRequest] = self.before_download_hook(request)
        if not processed_request:
            return None
        result = self.download(processed_request)
        result = self.after_download_hook(result)
        return result