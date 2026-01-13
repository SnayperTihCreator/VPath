from io import TextIOWrapper
from typing import Self

from .abc import BaseVPath
from .storage import Storage
from .utils import VStat


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
