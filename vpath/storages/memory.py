import io
import time
from typing import Any, Iterator, Optional
from vpath.storage import Storage
from vpath.factory import FileSystem


@FileSystem.register("memory")
class MemoryStorage(Storage):
    def __init__(self, _base_path, **kwargs):
        super().__init__(**kwargs)
        self._files: dict[str, bytes] = {}
        self._metadata: dict[str, float] = {}
        self._dirs: set[str] = {"/"}
    
    @staticmethod
    def _normalize(path: str) -> str:
        return "/" + path.strip("/")
    
    def get_info(self, path: str) -> dict[str, Any]:
        p = self._normalize(path)
        if p in self._dirs:
            return {"name": p.split("/")[-1], "type": "dir", "size": 0, "mtime": self._metadata.get(p, 0.0)}
        if p in self._files:
            return {"name": p.split("/")[-1], "type": "file", "size": len(self._files[p]),
                    "mtime": self._metadata.get(p, 0.0)}
        raise FileNotFoundError(f"Memory file not found: {p}")
    
    def list_dir(self, path: str) -> Iterator[tuple[str, Optional[dict]]]:
        p = self._normalize(path)
        p_slash = p if p.endswith("/") else p + "/"
        
        found = set()
        for f_path in list(self._files.keys()) + list(self._dirs):
            if f_path.startswith(p_slash) and f_path != p:
                relative = f_path[len(p_slash):]
                name = relative.split("/")[0]
                if name not in found:
                    found.add(name)
                    yield name, self.get_info(p_slash + name)
    
    def open(self, path: str, mode: str) -> Any:
        p = self._normalize(path)
        if "w" in mode:
            parts = p.split("/")
            for i in range(2, len(parts)):
                parent_dir = "/".join(parts[:i])
                if parent_dir not in self._dirs:
                    self._dirs.add(parent_dir)
                    self._metadata[parent_dir] = time.time()
            
            buf = io.BytesIO()
            orig_close = buf.close
            
            def _save():
                self._files[p] = buf.getvalue()
                self._metadata[p] = time.time()
                self._dirs.discard(p)
                orig_close()
            
            buf.close = _save
            return buf
        
        if p not in self._files:
            raise FileNotFoundError(p)
        return io.BytesIO(self._files[p])
    
    def exists(self, path: str) -> bool:
        p = self._normalize(path)
        return p in self._files or p in self._dirs
    
    def unlink(self, path: str):
        p = self._normalize(path)
        self._files.pop(p, None)
        self._metadata.pop(p, None)
        self._dirs.discard(p)
    
    def mkdir(self, path: str, mode: int = 0o777, parents: bool = False, exist_ok: bool = False):
        p = self._normalize(path)
        if p in self._dirs and not exist_ok:
            raise FileExistsError(p)
        self._dirs.add(p)
        self._metadata[p] = time.time()
    
    def rename(self, src: str, dest: str):
        s, d = self._normalize(src), self._normalize(dest)
        if s in self._files:
            self._files[d] = self._files.pop(s)
            self._metadata[d] = self._metadata.pop(s)
        elif s in self._dirs:
            self._dirs.remove(s)
            self._dirs.add(d)