from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional

from vpath.abc import BaseStorage


class AsyncStorage(BaseStorage, ABC):
    
    @abstractmethod
    async def get_info(self, path: str) -> dict[str, Any]: ...
    
    @abstractmethod
    async def list_dir(self, path: str) -> AsyncIterator[tuple[str, Optional[dict]]]: ...
    
    @abstractmethod
    async def open(self, path: str, mode: str) -> Any: ...
    
    @abstractmethod
    async def exists(self, path: str) -> bool: ...
    
    @abstractmethod
    async def unlink(self, path: str): ...
    
    @abstractmethod
    async def mkdir(self, path: str, mode: str, parents: bool, exist_ok: bool): ...
    
    @abstractmethod
    async def rename(self, src: str, dest: str): ...
