from vpath.paths import Storage
from .mixins import SubPathLogicMixin
from .wrap import StorageWrapper


class SubStorage(StorageWrapper, SubPathLogicMixin):
    def __init__(self, wrapped: Storage, base_path: str):
        super(StorageWrapper, self).__init__(wrapped)
        super(SubPathLogicMixin, self).__init__(base_path)
    
    def get_info(self, path): return self.wrapped.get_info(self._fix(path))
    
    def exists(self, path): return self.wrapped.exists(self._fix(path))
    
    def open(self, path, mode="r"): return self.wrapped.open(self._fix(path), mode)
    
    def list_dir(self, path): return self.wrapped.list_dir(self._fix(path))
    
    def unlink(self, path): return self.wrapped.unlink(self._fix(path))
    
    def mkdir(self, path, mode=0o777, parents=False, exist_ok=False): return self.wrapped.mkdir(self._fix(path), mode,
                                                                                                parents, exist_ok)
    
    def rename(self, src, dist): return self.wrapped.rename(self._fix(src), self._fix(dist))