from .protocols import RequesterProtocol
from aionetworking.types.logging import LoggerType
from typing import Protocol


class BaseRequester(RequesterProtocol, Protocol):
    async def start(self, logger: LoggerType = None):
        parent_logger = logger or self.logger
        self.logger = parent_logger.get_child(name='requester')

    async def close(self): ...

