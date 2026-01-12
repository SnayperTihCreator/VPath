from typing import Any, Optional, Iterator

from vpath.paths import Storage
from .mixins import MultiLogicMixin


class MultiStorage(Storage, MultiLogicMixin):
    """
    Синхронная ФС, объединяющая содержимое нескольких слоев.
    """
    
    def __init__(self, use_cache: bool = False):
        super(Storage, self).__init__(use_cache=use_cache)
        super(MultiLogicMixin, self).__init__()
    
    def get_info(self, path: str) -> dict[str, Any]:
        """Ищет информацию о файле в слоях, начиная с верхнего."""
        for layer in self._layers:
            try:
                if layer.exists(path):
                    return layer.get_info(path)
            except Exception:
                continue
        raise FileNotFoundError(f"Файл {path} не найден ни в одном слое.")
    
    def exists(self, path: str) -> bool:
        """Проверяет существование файла в любом из слоев."""
        return any(layer.exists(path) for layer in self._layers)
    
    def list_dir(self, path: str) -> Iterator[tuple[str, Optional[dict]]]:
        """Объединяет списки файлов изо всех слоев, исключая дубликаты."""
        seen = set()
        for layer in self._layers:
            try:
                if layer.exists(path):
                    for name, info in layer.list_dir(path):
                        if name not in seen:
                            seen.add(name)
                            yield name, info
            except Exception:
                continue
    
    def open(self, path: str, mode: str) -> Any:
        """
        Открывает файл. Если режим на запись — всегда в primary слое.
        Если на чтение — в первом найденном.
        """
        if any(m in mode for m in "wax+"):
            return self.primary.open(path, mode)
        
        for layer in self._layers:
            if layer.exists(path):
                return layer.open(path, mode)
        raise FileNotFoundError(path)
    
    def mkdir(self, path: str, mode: str, parents: bool, exist_ok: bool):
        """Создает папку только в приоритетном слое."""
        self.primary.mkdir(path, mode, parents, exist_ok)
    
    def unlink(self, path: str):
        """Удаляет файл из всех слоев (или только из тех, где есть доступ)."""
        found = False
        for layer in self._layers:
            if layer.exists(path):
                layer.unlink(path)
                found = True
        if not found:
            raise FileNotFoundError(path)
    
    def rename(self, src: str, dest: str):
        """Переименование поддерживается только внутри одного (primary) слоя."""
        self.primary.rename(src, dest)
