from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional

from vpath.abc import BaseStorage


class Storage(BaseStorage, ABC):
    
    @abstractmethod
    def get_info(self, path: str) -> dict[str, Any]: ...
    
    @abstractmethod
    def list_dir(self, path: str) -> Iterator[tuple[str, Optional[dict]]]: ...
    
    @abstractmethod
    def open(self, path: str, mode: str) -> Any: ...
    
    @abstractmethod
    def exists(self, path: str) -> bool: ...
    
    @abstractmethod
    def unlink(self, path: str): ...
    
    @abstractmethod
    def mkdir(self, path: str, mode: int, parents: bool, exist_ok: bool): ...
    
    @abstractmethod
    def rename(self, src: str, dest: str): ...
