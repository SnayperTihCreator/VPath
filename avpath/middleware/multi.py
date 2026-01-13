from typing import Any, AsyncIterator, Optional

from avpath import AsyncStorage
from vpath.middleware.mixins import MultiLogicMixin


class AsyncMultiStorage(AsyncStorage, MultiLogicMixin):
    """
    Асинхронная ФС, объединяющая содержимое нескольких слоев.
    """
    
    def __init__(self, use_cache: bool = False):
        super(AsyncStorage, self).__init__(use_cache)
        super(MultiLogicMixin, self).__init__()
    
    async def get_info(self, path: str) -> dict[str, Any]:
        for layer in self._layers:
            if await layer.exists(path):
                return await layer.get_info(path)
        raise FileNotFoundError(path)
    
    async def exists(self, path: str) -> bool:
        for layer in self._layers:
            if await layer.exists(path):
                return True
        return False
    
    async def list_dir(self, path: str) -> AsyncIterator[tuple[str, Optional[dict]]]:
        seen = set()
        for layer in self._layers:
            if await layer.exists(path):
                async for name, info in layer.list_dir(path):
                    if name not in seen:
                        seen.add(name)
                        yield name, info
    
    async def open(self, path: str, mode: str) -> Any:
        if any(m in mode for m in "wax+"):
            return await self.primary.open(path, mode)
        
        for layer in self._layers:
            if await layer.exists(path):
                return await layer.open(path, mode)
        raise FileNotFoundError(path)
    
    async def mkdir(self, path: str, mode: str, parents: bool, exist_ok: bool):
        await self.primary.mkdir(path, mode, parents, exist_ok)
    
    async def rename(self, src: str, dest: str):
        pass
    
    async def unlink(self, path: str):
        found = False
        for layer in self._layers:
            if await layer.exists(path):
                await layer.unlink(path)
                found = True
        if not found:
            raise FileNotFoundError(path)