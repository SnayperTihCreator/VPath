from typing import Any, AsyncIterator, Optional

from avpath.base import AsyncStorage
from vpath.middleware.mixins import MountLogicMixin


class AsyncMountStorage(AsyncStorage, MountLogicMixin):
    """
    Виртуальное асинхронное хранилище.
    """
    
    def __init__(self, use_cache: bool = False):
        super(AsyncStorage, self).__init__(use_cache)
        super(MountLogicMixin, self).__init__()
    
    async def get_info(self, path: str) -> dict[str, Any]:
        if path.strip("/") == "":
            return {"name": "/", "type": "dir", "size": 0}
        target, sub_path = self._resolve(path)
        return await target.get_info(sub_path)
    
    async def exists(self, path: str) -> bool:
        if path.strip("/") == "":
            return True
        try:
            target, sub_path = self._resolve(path)
            return await target.exists(sub_path)
        except FileNotFoundError:
            return False
    
    async def list_dir(self, path: str) -> AsyncIterator[tuple[str, Optional[dict]]]:
        if path.strip("/") == "":
            for name in self._mounts:
                yield name, {"type": "dir", "mount": True}
            return
        target, sub_path = self._resolve(path)
        async for item in target.list_dir(sub_path):
            yield item
    
    async def open(self, path: str, mode: str) -> Any:
        target, sub_path = self._resolve(path)
        return await target.open(sub_path, mode)
    
    async def mkdir(self, path: str, mode: str, parents: bool, exist_ok: bool):
        target, sub_path = self._resolve(path)
        await target.mkdir(sub_path, mode, parents, exist_ok)
    
    async def unlink(self, path: str):
        target, sub_path = self._resolve(path)
        await target.unlink(sub_path)
    
    async def rename(self, src: str, dest: str):
        s_target, s_path = self._resolve(src)
        d_target, d_path = self._resolve(dest)
        if s_target != d_target:
            raise PermissionError("Асинхронный перенос между разными точками монтирования запрещен.")
        await s_target.rename(s_path, d_path)
