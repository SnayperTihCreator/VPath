import anyio
import aiofiles
import shutil
from typing import Any, AsyncIterator, Optional
from avpath.base import AsyncStorage
from vpath.factory import FileSystem


@FileSystem.register("file")
class AsyncLocalStorage(AsyncStorage):
    def __init__(self, base_path: str, **kwargs):
        super().__init__(**kwargs)
        self.base = anyio.Path(base_path)
    
    async def _full(self, path: str) -> anyio.Path:
        return self.base / path.lstrip("/")
    
    async def get_info(self, path: str) -> dict[str, Any]:
        p = await self._full(path)
        stat = await p.stat()
        return {
            "name": p.name,
            "size": stat.st_size,
            "type": "dir" if await p.is_dir() else "file",
            "mtime": stat.st_mtime
        }
    
    async def list_dir(self, path: str) -> AsyncIterator[tuple[str, Optional[dict]]]:
        p = await self._full(path)
        async for entry in p.iterdir():
            info = await self.get_info(entry.as_posix())
            yield entry.name, info
    
    async def open(self, path: str, mode: str) -> Any:
        p = await self._full(path)
        if "w" in mode or "a" in mode:
            await p.parent.mkdir(parents=True, exist_ok=True)
        return await aiofiles.open(p.as_posix(), mode if "b" in mode else mode + "b")
    
    async def exists(self, path: str) -> bool:
        p = await self._full(path)
        return await p.exists()
    
    async def unlink(self, path: str):
        p = await self._full(path)
        if await p.is_dir():
            await anyio.to_thread.run_sync(shutil.rmtree, p.as_posix())
        else:
            await p.unlink()
    
    async def mkdir(self, path: str, mode: int = 0o777, parents: bool = False, exist_ok: bool = False):
        p = await self._full(path)
        await p.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)
    
    async def rename(self, src: str, dest: str):
        s, d = await self._full(src), await self._full(dest)
        await anyio.to_thread.run_sync(shutil.move, s.as_posix(), d.as_posix())
