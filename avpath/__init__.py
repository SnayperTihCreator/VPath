try:
    import anyio
    import aiofiles
except ImportError:
    raise ImportError(
        "Пакет avpath требует дополнительных зависимостей. "
        "Установите их командой: pip install vpath[async]"
    ) from None

from .paths import AsyncVPath
from .base import AsyncStorage
from .middleware import *
from . import storages
