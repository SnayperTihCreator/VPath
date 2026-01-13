from abc import ABC, abstractmethod
from pathlib import PurePosixPath
from typing import Optional, Self

from attrs import define


class BaseStorage(ABC):
    def __init__(self, use_cache=False, **kwargs):
        self.use_cache = use_cache


@define
class BaseStorageContainer(ABC):
    def get_storage(self, root: str, **kwargs) -> BaseStorage: ...
    
    async def async_get_storage(self, root: str, **kwargs) -> BaseStorage: ...


class BaseVPath(PurePosixPath, ABC):
    __slots__ = ("_storage", "_info_cache")
    
    def __new__(cls, *args, storage: Optional[BaseStorage] = None, info_cache=None):
        self = super().__new__(cls, *args)
        self._storage = storage
        self._info_cache = info_cache
        return self
    
    @classmethod
    def _from_parts(cls, args):
        obj = super()._from_parts(args)
        obj._storage = None
        obj._info_cache = None
        return obj
    
    @property
    def storage(self) -> BaseStorage:
        if self._storage is None: raise ValueError("VPath detached")
        return self._storage
    
    def __truediv__(self, other) -> Self:
        return type(self)(super().__truediv__(other), storage=self.storage)
    
    @abstractmethod
    def chroot(self) -> Self: ...
