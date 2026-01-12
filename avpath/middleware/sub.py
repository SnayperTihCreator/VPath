from vpath.middleware.mixins import SubPathLogicMixin
from .wrap import AsyncStorageWrapper
from avpath.base import AsyncStorage


class AsyncSubStorage(AsyncStorageWrapper, SubPathLogicMixin):
    def __init__(self, wrapped: AsyncStorage, base_path: str):
        super(AsyncStorageWrapper, self).__init__(wrapped)
        super(SubPathLogicMixin, self).__init__(base_path)
    
    async def get_info(self, path): return await self.wrapped.get_info(self._fix(path))
    
    async def exists(self, path): return await self.wrapped.exists(self._fix(path))
    
    async def open(self, path, mode="r"): return await self.wrapped.open(self._fix(path), mode)
    
    async def list_dir(self, path):
        async for dest in self.wrapped.list_dir(self._fix(path)):
            yield dest
    
    async def unlink(self, path): return await self.wrapped.unlink(self._fix(path))
    
    async def mkdir(self, path, mode=0o777, parents=False, exist_ok=False): return await self.wrapped.mkdir(
        self._fix(path), mode, parents, exist_ok)
    
    async def rename(self, src: str, dest: str):
        return await self.wrapped.rename(self._fix(src), self._fix(dest))