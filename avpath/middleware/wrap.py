from avpath.base import AsyncStorage


class AsyncStorageWrapper(AsyncStorage):
    def __init__(self, wrapped: AsyncStorage):
        super().__init__(wrapped.use_cache)
        self.wrapped = wrapped
    
    async def get_info(self, path): return await self.wrapped.get_info(path)
    
    async def exists(self, path): return await self.wrapped.exists(path)
    
    async def open(self, path, mode="r"): return await self.wrapped.open(path, mode)
    
    async def list_dir(self, path):
        async for dest in self.wrapped.list_dir(path):
            yield dest
    
    async def unlink(self, path): await self.wrapped.unlink(path)
    
    async def mkdir(self, path, mode=0o777, parents=False, exist_ok=False): await self.wrapped.mkdir(path, mode,
                                                                                                     parents, exist_ok)
    
    async def rename(self, src: str, dest: str): await self.wrapped.rename(src, dest)