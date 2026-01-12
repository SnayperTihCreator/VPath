from abc import ABC, abstractmethod
from io import TextIOWrapper
from typing import Optional, Self, Any, Iterator

from attrs import define, field

from .base import BaseStorage, BaseVPath


@define(frozen=True, repr=False)
class VStat:
    _data: dict = field(alias="metadata")
    
    @property
    def st_size(self) -> int:
        return self._data.get("size", 0)
    
    @property
    def st_mtime(self) -> float:
        return self._data.get("mtime", 0.0)
    
    @property
    def is_dir(self) -> bool:
        return self._data.get("type") == "dir"
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'VStat' object has no attribute '{name}'")
    
    def __repr__(self):
        return f"vstat_result(size={self.st_size}, type='{self._data.get('type', 'unknown')}')"


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


class VPath(BaseVPath):
    storage: Storage
    
    @property
    def storage(self) -> Storage:
        return super().storage
    
    def stat(self):
        if self._info_cache is None:
            self._info_cache = self.storage.get_info(self.as_posix())
        return VStat(self._info_cache)
    
    def open(self, mode="r", encoding="utf-8"):
        file = self.storage.open(self.as_posix(), mode.replace("t", ""))
        if "b" not in mode:
            return TextIOWrapper(file, encoding=encoding)
        return file
    
    def exists(self) -> bool:
        return self.storage.exists(self.as_posix())
    
    def iterdir(self):
        for n, m in self.storage.list_dir(self.as_posix()):
            yield VPath(self, n, storage=self.storage, info_cache=m)
    
    def chroot(self) -> Self:
        from vpath.middleware import SubStorage
        return VPath("/", storage=SubStorage(self.storage, self.as_posix()))
    
    def unlink(self):
        self.storage.unlink(self.as_posix())
    
    def write_text(self, data: str, encoding="utf-8"):
        with self.open("w", encoding=encoding) as f:
            f.write(data)
    
    def read_text(self, encoding="utf-8") -> str:
        with self.open("r", encoding=encoding) as f:
            return f.read()
    
    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        self.storage.mkdir(self.as_posix(), mode, parents, exist_ok)
