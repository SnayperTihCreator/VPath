from __future__ import annotations
import importlib.metadata
from typing import Type, Optional

from attrs import define

from .abc import BaseStorageContainer
from .utils import MetaSingleton, URLParser, LazyLoader
from .paths import VPath
from .storage import Storage


@define
class DefaultStorageContainer(BaseStorageContainer):
    storage: Type[Storage]
    
    def get_storage(self, root: str, **kwargs) -> Storage:
        if not isinstance(self.storage, type) and hasattr(self.storage, 'load'):
            self.storage = self.storage.load()
        return self.storage(root, **kwargs)


class FileSystem(metaclass=MetaSingleton):
    _registry: dict[str, BaseStorageContainer] = {}
    _loaded: bool = False
    _built_in = {
        "file": "vpath.storages.local:LocalStorage",
        "mem": "vpath.storages.memory:MemoryStorage",
    }
    
    @classmethod
    def register(cls, *schemes: str, container: Optional[BaseStorageContainer] = None):
        def wrapper(cls_obj: Type[Storage]):
            for s in schemes:
                cls._registry[s] = container or DefaultStorageContainer(cls_obj)
            return cls_obj
        
        return wrapper
    
    @classmethod
    def add_container(cls, scheme: str, container: BaseStorageContainer):
        cls._registry[scheme] = container
    
    @classmethod
    def open(cls, url: str, **kwargs) -> VPath:
        cls._ensure_loaded()
        scheme, folder, file, _, url_args = URLParser.parse(url)
        
        if scheme not in cls._registry:
            raise ValueError(f"Sync driver for '{scheme}' not found")
        
        container = cls._registry[scheme]
        storage = container.get_storage(root=folder, **{**url_args, **kwargs})
        return VPath(file, storage=storage)
    
    @classmethod
    def _ensure_loaded(cls):
        if cls._loaded: return
        for s, path in cls._built_in.items():
            if s not in cls._registry:
                cls.add_container(s, DefaultStorageContainer(LazyLoader(path)))
        for entry in importlib.metadata.entry_points(group='vpath.sync_drivers'):
            cls.add_container(entry.name, DefaultStorageContainer(entry))
        cls._loaded = True
