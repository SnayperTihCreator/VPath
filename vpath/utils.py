import os
import importlib
from urllib.parse import urlparse, parse_qs
from typing import Tuple, Dict, Any, Type

from attrs import define, field


class URLParser:
    @staticmethod
    def parse(url: str) -> Tuple[str, str, str, str, Dict[str, Any]]:
        """Разбирает URL на (scheme, folder, filename, ext, kwargs)."""
        is_win_path = len(url) > 1 and url[1] == ":"
        if "://" not in url and not is_win_path and not url.startswith("/"):
            url = "file://" + url
        elif is_win_path or url.startswith("/"):
            url = "file://" + url
        
        parsed = urlparse(url)
        scheme = parsed.scheme
        
        full_path = f"{parsed.netloc}{parsed.path}" if scheme != "file" else parsed.path
        
        if full_path.endswith('/'):
            directory, filename = full_path.rstrip('/'), ""
        else:
            directory, filename = os.path.split(full_path)
        
        _, ext = os.path.splitext(filename)
        kwargs = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        
        if parsed.username: kwargs['user'] = parsed.username
        if parsed.password: kwargs['password'] = parsed.password
        if parsed.hostname and scheme != "file": kwargs['host'] = parsed.hostname
        
        return scheme, directory, filename, ext, kwargs


class LazyLoader:
    """Объект-заглушка для отложенного импорта класса."""
    
    def __init__(self, import_path: str):
        self.import_path = import_path
    
    def load(self) -> Type[Any]:
        mod_name, obj_name = self.import_path.split(":")
        module = importlib.import_module(mod_name)
        return getattr(module, obj_name)


class MetaSingleton(type):
    _instances = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instances is None:
            cls._instances = super().__call__(*args, **kwargs)
        return cls._instances


@define(frozen=True, repr=False)
class VStat:
    _data: dict = field(alias="metadata")
    
    @property
    def st_size(self) -> int:
        return self._data.get("size", 0)
    
    @property
    def st_mtime(self) -> float:
        return self._data.get("mtime", 0.0)
    
    @property
    def is_dir(self) -> bool:
        return self._data.get("type") == "dir"
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'VStat' object has no attribute '{name}'")
    
    def __repr__(self):
        return f"vstat_result(size={self.st_size}, type='{self._data.get('type', 'unknown')}')"
