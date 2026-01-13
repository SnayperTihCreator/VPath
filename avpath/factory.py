from __future__ import annotations
import importlib.metadata
from typing import Type, Optional

from attrs import define

from vpath.utils import URLParser, LazyLoader
from vpath.abc import BaseStorageContainer
from .storage import AsyncStorage
from .paths import AsyncVPath


@define
class DefaultAsyncContainer(BaseStorageContainer):
    """Контейнер для асинхронного хранилища."""
    storage: Type[AsyncStorage]
    
    async def async_get_storage(self, root: str, **kwargs) -> AsyncStorage:
        if not isinstance(self.storage, type) and hasattr(self.storage, 'load'):
            self.storage = self.storage.load()
        
        return self.storage(root, **kwargs)


class AsyncFileSystem:
    _registry: dict[str, BaseStorageContainer] = {}
    _loaded: bool = False
    _built_in = {
        "file": "avpath.storages.local:AsyncLocalStorage",
        "mem": "avpath.storages.memory:AsyncMemoryStorage",
    }
    
    @classmethod
    def register(cls, *schemes: str, container: Optional[BaseStorageContainer] = None):
        def wrapper(cls_obj: Type[AsyncStorage]):
            for s in schemes:
                cls._registry[s] = container or DefaultAsyncContainer(cls_obj)
            return cls_obj
        
        return wrapper
    
    @classmethod
    def add_container(cls, scheme: str, container: BaseStorageContainer):
        cls._registry[scheme] = container
    
    @classmethod
    async def open(cls, url: str, **kwargs) -> AsyncVPath:
        cls._ensure_loaded()
        from avpath import AsyncVPath
        
        scheme, folder, file, _, url_args = URLParser.parse(url)
        
        if scheme not in cls._registry:
            raise ValueError(f"Async driver for '{scheme}' not found")
        
        container = cls._registry[scheme]
        storage = await container.async_get_storage(root=folder, **{**url_args, **kwargs})
        return AsyncVPath(file, storage=storage)
    
    @classmethod
    def _ensure_loaded(cls):
        if cls._loaded: return
        for s, path in cls._built_in.items():
            if s not in cls._registry:
                cls.add_container(s, DefaultAsyncContainer(LazyLoader(path)))
        for entry in importlib.metadata.entry_points(group='vpath.async_drivers'):
            cls.add_container(entry.name, DefaultAsyncContainer(entry))
        cls._loaded = True
