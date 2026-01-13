from vpath.storage import Storage


class StorageWrapper(Storage):
    def __init__(self, wrapped: Storage):
        super().__init__(wrapped.use_cache)
        self.wrapped = wrapped
    
    def get_info(self, path): return self.wrapped.get_info(path)
    
    def exists(self, path): return self.wrapped.exists(path)
    
    def open(self, path, mode="r"): return self.wrapped.open(path, mode)
    
    def list_dir(self, path): return self.wrapped.list_dir(path)
    
    def unlink(self, path): return self.wrapped.unlink(path)
    
    def mkdir(self, path, mode=0o777, parents=False, exist_ok=False): return self.wrapped.mkdir(path, mode, parents,
                                                                                                exist_ok)
    
    def rename(self, src, dist): return self.wrapped.rename(src, dist)
