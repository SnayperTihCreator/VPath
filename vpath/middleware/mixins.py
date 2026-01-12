import os
from pathlib import PurePosixPath
from typing import Any


class SubPathLogicMixin:
    """Логика chroot (ограничение базовым путем)."""
    
    def __init__(self, base_path: str):
        self.base = PurePosixPath("/") / base_path.strip("/")
    
    def _fix(self, path: str) -> str:
        full_path = PurePosixPath(os.path.normpath(self.base / path.lstrip("/")))
        if not str(full_path).startswith(str(self.base)):
            raise PermissionError(f"Access denied: outside of {self.base}")
        return str(full_path)


class MountLogicMixin:
    """Логика монтирования (Mount Point)."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mounts: dict[str, Any] = {}
    
    def mount(self, name: str, storage: Any):
        self._mounts[name.strip("/")] = storage
    
    def _resolve(self, path: str) -> tuple[Any, str]:
        path = path.lstrip("/")
        if not path: return None, "/"
        parts = path.split("/", 1)
        prefix = parts[0]
        sub = "/" + (parts[1] if len(parts) > 1 else "")
        if prefix in self._mounts:
            return self._mounts[prefix], sub
        raise FileNotFoundError(f"Mount point '{prefix}' not found")


class MultiLogicMixin:
    """Логика Overlay (объединение слоев)."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._layers: list[Any] = []
    
    def add_layer(self, storage: Any):
        self._layers.insert(0, storage)  # Новый слой всегда сверху (приоритет)
    
    @property
    def primary(self) -> Any:
        if not self._layers: raise RuntimeError("No layers in OverlayStorage")
        return self._layers[0]
