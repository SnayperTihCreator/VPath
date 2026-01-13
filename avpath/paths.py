from typing import AsyncIterator, Self

from vpath.utils import VStat
from vpath.abc import BaseVPath
from .storage import AsyncStorage
from .utils.textio import AsyncTextIO


class AsyncVPath(BaseVPath):
    @property
    def storage(self) -> AsyncStorage:
        return super().storage
    
    async def stat(self):
        if self._info_cache is None:
            self._info_cache = await self.storage.get_info(self.as_posix())
        return VStat(self._info_cache)
    
    async def iterdir(self) -> AsyncIterator['AsyncVPath']:
        async for n, m in self.storage.list_dir(self.as_posix()):
            yield AsyncVPath(self, n, storage=self.storage, info_cache=m)
    
    def chroot(self) -> Self:
        from .middleware import AsyncSubStorage
        return AsyncVPath("/", storage=AsyncSubStorage(self.storage, self.as_posix()))
    
    async def open(self, mode="r", encoding="utf-8"):
        file = await self.storage.open(self.as_posix(), mode=mode.replace("t", ""))
        if "b" not in mode:
            return AsyncTextIO(file, mode, encoding)
        return file
    
    async def write_text(self, data: str, encoding: str = "utf-8"):
        async with await self.open("w", encoding) as f:
            await f.write(data)
    
    async def read_text(self, encoding="utf-8") -> str:
        async with await self.open("r", encoding) as f:
            return await f.read()
    
    async def unlink(self):
        await self.storage.unlink(self.as_posix())
    
    async def exists(self) -> bool:
        return await self.storage.exists(self.as_posix())
    
    async def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        await self.storage.mkdir(self.as_posix(), mode, parents, exist_ok)
