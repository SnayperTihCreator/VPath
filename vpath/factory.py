from __future__ import annotations
from typing import Type

from .base import BaseVPath
from .paths import VPath, Storage
from .protocols import AsyncStorageProtocol, AsyncVPathProtocol


class _MetaSingleton(type):
    _instances = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instances is None:
            cls._instances = super().__call__(*args, **kwargs)
        return cls._instances


class FileSystem(metaclass=_MetaSingleton):
    _sync_drivers: dict[str, Type[Storage]] = {}
    _async_drivers: dict[str, Type[AsyncStorageProtocol]] = {}
    
    @classmethod
    def register(cls, scheme: str):
        def wrapper(cls_obj):
            mro_names = [base.__name__ for base in cls_obj.__mro__]
            
            if 'Storage' in mro_names:
                cls._sync_drivers[scheme] = cls_obj
            if 'AsyncStorage' in mro_names:
                cls._async_drivers[scheme] = cls_obj
            return cls_obj
        
        return wrapper
    
    @classmethod
    def open(cls, url: str, **kwargs) -> VPath:
        scheme, full_path = url.split("://", 1) if "://" in url else ("file", url)
        if scheme not in cls._sync_drivers:
            raise ValueError(f"Sync driver {scheme} not found")
        storage_instance = cls._sync_drivers[scheme]("/", **kwargs)
        return VPath(full_path, storage=storage_instance)
    
    @classmethod
    async def aopen(cls, url: str, **kwargs) -> AsyncVPathProtocol | BaseVPath:
        try:
            from avpath import AsyncVPath, AsyncStorage
        except ImportError:
            raise ImportError(
                "AsyncVPath requires 'vpath[async]' dependencies. "
                "Install them with: pip install vpath[async]"
            )
        
        scheme, full_path = url.split("://", 1) if "://" in url else ("file", url)
        if scheme not in cls._async_drivers:
            raise ValueError(f"Async driver {scheme} not found")
        storage_instance: AsyncStorage = cls._async_drivers[scheme]("/", **kwargs)
        return AsyncVPath(full_path, storage=storage_instance)
