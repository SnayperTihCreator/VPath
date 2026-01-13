import io
import time
from typing import Any, AsyncIterator, Optional

import anyio

from avpath import AsyncStorage
from vpath.factory import FileSystem


@FileSystem.register("memory")
class AsyncMemoryStorage(AsyncStorage):
    def __init__(self, _base_path, **kwargs):
        super().__init__(**kwargs)
        self._files: dict[str, bytes] = {}
        self._metadata: dict[str, float] = {}
        self._dirs: set[str] = {"/"}
    
    @staticmethod
    def _normalize(path: str) -> str:
        return "/" + path.strip("/")
    
    async def get_info(self, path: str) -> dict[str, Any]:
        p = self._normalize(path)
        
        # СНАЧАЛА проверяем файлы
        if p in self._files:
            return {
                "name": p.split("/")[-1],
                "type": "file",
                "size": len(self._files[p]),
                "mtime": self._metadata.get(p, 0.0)
            }
        
        # ТОЛЬКО ПОТОМ директории
        if p in self._dirs:
            return {
                "name": p.split("/")[-1],
                "type": "dir",
                "size": 0,
                "mtime": self._metadata.get(p, 0.0)
            }
            
        raise FileNotFoundError(p)
    
    async def list_dir(self, path: str) -> AsyncIterator[tuple[str, Optional[dict]]]:
        p = self._normalize(path)
        p_slash = p if p.endswith("/") else p + "/"
        
        found = set()
        for f_path in list(self._files.keys()) + list(self._dirs):
            if f_path.startswith(p_slash) and f_path != p:
                name = f_path[len(p_slash):].split("/")[0]
                if name not in found:
                    found.add(name)
                    info = await self.get_info(p_slash + name)
                    yield name, info
    
    async def open(self, path: str, mode: str) -> Any:
        p = self._normalize(path)
        
        if "w" in mode:
            # Создаем цепочку папок, если нужно (логика как в синхронке)
            parts = p.split("/")
            for i in range(2, len(parts)):
                self._dirs.add("/".join(parts[:i]))
            
            buf = io.BytesIO()
            orig_close = buf.close
            
            def _save():
                self._files[p] = buf.getvalue()
                self._metadata[p] = time.time()
                orig_close()
            
            buf.close = _save
            return anyio.wrap_file(buf)
        
        if p not in self._files:
            raise FileNotFoundError(p)
        
        return anyio.wrap_file(io.BytesIO(self._files[p]))
    
    async def exists(self, path: str) -> bool:
        return self._normalize(path) in self._files or self._normalize(path) in self._dirs
    
    async def unlink(self, path: str):
        p = self._normalize(path)
        self._files.pop(p, None)
        self._dirs.discard(p)
    
    async def mkdir(self, path: str, mode: str = "0o777", parents: bool = False, exist_ok: bool = False):
        p = self._normalize(path)
        self._dirs.add(p)
        self._metadata[p] = time.time()
    
    async def rename(self, src: str, dest: str):
        s, d = self._normalize(src), self._normalize(dest)
        if s in self._files:
            self._files[d] = self._files.pop(s)
        elif s in self._dirs:
            self._dirs.remove(s)
            self._dirs.add(d)
