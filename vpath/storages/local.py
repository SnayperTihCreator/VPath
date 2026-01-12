import shutil
from pathlib import Path
from typing import Any, Iterator, Optional
from vpath.paths import Storage
from vpath.factory import FileSystem


@FileSystem.register("file")
class LocalStorage(Storage):
    def __init__(self, base_path: str | Path, **kwargs):
        super().__init__(**kwargs)
        self.base = Path(base_path).resolve()
    
    def _full(self, path: str) -> Path:
        return self.base / path.lstrip("/")
    
    def get_info(self, path: str) -> dict[str, Any]:
        p = self._full(path)
        stat = p.stat()
        return {
            "name": p.name,
            "size": stat.st_size,
            "type": "dir" if p.is_dir() else "file",
            "mtime": stat.st_mtime
        }
    
    def list_dir(self, path: str) -> Iterator[tuple[str, Optional[dict]]]:
        for entry in self._full(path).iterdir():
            yield entry.name, self.get_info(str(entry.relative_to(self.base)))
    
    def open(self, path: str, mode: str) -> Any:
        p = self._full(path)
        if "w" in mode and not p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
        return open(p, mode if "b" in mode else mode + "b")
    
    def exists(self, path: str) -> bool:
        return self._full(path).exists()
    
    def unlink(self, path: str):
        p = self._full(path)
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    
    def mkdir(self, path: str, mode: int = 0o777, parents: bool = False, exist_ok: bool = False):
        self._full(path).mkdir(mode=mode, parents=parents, exist_ok=exist_ok)
    
    def rename(self, src: str, dest: str):
        shutil.move(str(self._full(src)), str(self._full(dest)))
