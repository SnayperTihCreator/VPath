from typing import Any, Iterator, Optional

from vpath.paths import Storage
from .mixins import MountLogicMixin


class MountStorage(Storage, MountLogicMixin):
    """
    Виртуальное хранилище, объединяющее несколько других синхронных хранилищ.
    """
    
    def __init__(self, use_cache: bool = False):
        Storage.__init__(self, use_cache=use_cache)
        MountLogicMixin.__init__(self)
    
    def get_info(self, path: str) -> dict[str, Any]:
        """Возвращает информацию о файле или виртуальной папке монтирования."""
        if path.strip("/") == "":
            return {"name": "/", "type": "dir", "size": 0}
        target, sub_path = self._resolve(path)
        return target.get_info(sub_path)
    
    def exists(self, path: str) -> bool:
        """Проверяет существование пути или точки монтирования."""
        if path.strip("/") == "":
            return True
        try:
            target, sub_path = self._resolve(path)
            return target.exists(sub_path)
        except FileNotFoundError:
            return False
    
    def list_dir(self, path: str) -> Iterator[tuple[str, Optional[dict]]]:
        """Листинг директории: либо список точек монтирования, либо содержимое конкретной ФС."""
        if path.strip("/") == "":
            for name in self._mounts:
                yield name, {"type": "dir", "mount": True}
            return
        target, sub_path = self._resolve(path)
        yield from target.list_dir(sub_path)
    
    def open(self, path: str, mode: str) -> Any:
        """Открывает файл в соответствующем хранилище."""
        target, sub_path = self._resolve(path)
        return target.open(sub_path, mode)
    
    def mkdir(self, path: str, mode: str, parents: bool, exist_ok: bool):
        """Создает директорию в целевом хранилище."""
        target, sub_path = self._resolve(path)
        target.mkdir(sub_path, mode, parents, exist_ok)
    
    def unlink(self, path: str):
        """Удаляет файл в целевом хранилище."""
        target, sub_path = self._resolve(path)
        target.unlink(sub_path)
    
    def rename(self, src: str, dest: str):
        """Переименовывает объект. Перенос между разными хранилищами не поддерживается."""
        s_target, s_path = self._resolve(src)
        d_target, d_path = self._resolve(dest)
        if s_target != d_target:
            raise PermissionError("Перенос файлов между разными точками монтирования запрещен.")
        s_target.rename(s_path, d_path)