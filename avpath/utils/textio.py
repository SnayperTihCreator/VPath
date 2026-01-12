import codecs
import inspect
from collections import deque
from collections.abc import AsyncIterable, AsyncIterator
from typing import Optional

__all__ = ["AsyncTextIO", "AsyncTextReader", "AsyncTextWriter"]


class AsyncTextReader(AsyncIterable):
    def __init__(self, stream, encoding: str, chunk_size: int, history_limit: int):
        self.stream = stream
        self.encoding = encoding
        self.decoder = codecs.getincrementaldecoder(encoding)()
        self.buffer = ""
        self.chunk_size = chunk_size
        self._eof = False
        self.history = deque(maxlen=history_limit)
    
    def _reset(self):
        self.decoder = codecs.getincrementaldecoder(self.encoding)()
        self.buffer = ""
        self._eof = False
    
    async def read(self, size: int = -1) -> str:
        while not self._eof and (size < 0 or len(self.buffer) < size):
            chunk = await self.stream.read(self.chunk_size)
            if not chunk:
                self._eof = True
                self.buffer += self.decoder.decode(b'', final=True)
                break
            self.buffer += self.decoder.decode(chunk, final=False)
        
        if size < 0:
            res, self.buffer = self.buffer, ""
        else:
            res, self.buffer = self.buffer[:size], self.buffer[size:]
        return res
    
    async def readline(self) -> str:
        while not self._eof and '\n' not in self.buffer:
            chunk = await self.stream.read(self.chunk_size)
            if not chunk:
                self._eof = True
                self.buffer += self.decoder.decode(b'', final=True)
                break
            self.buffer += self.decoder.decode(chunk, final=False)
        
        if '\n' in self.buffer:
            line, sep, self.buffer = self.buffer.partition('\n')
            full_line = line + sep
        else:
            full_line, self.buffer = self.buffer, ""
        
        if full_line:
            self.history.append(full_line)
        return full_line
    
    def __aiter__(self) -> AsyncIterator:
        return self
    
    async def __anext__(self) -> str:
        line = await self.readline()
        if not line:
            raise StopAsyncIteration
        return line


class AsyncTextWriter:
    def __init__(self, stream, encoding: str, buffer_size: int):
        self.stream = stream
        self.encoding = encoding
        self.buffer_size = buffer_size
        self._buffer = []
        self._current_size = 0
    
    async def write(self, text: str):
        self._buffer.append(text)
        self._current_size += len(text)
        if self._current_size >= self.buffer_size:
            await self.flush()
    
    async def flush(self):
        if self._buffer:
            data = "".join(self._buffer).encode(self.encoding)
            await self.stream.write(data)
            self._buffer = []
            self._current_size = 0
        if hasattr(self.stream, 'flush'):
            await self.stream.flush()


class AsyncTextIO(AsyncIterable):
    """Полноценный асинхронный текстовый IO с проверкой режимов доступа."""
    
    def __init__(self, stream, mode: str = 'r', encoding: str = 'utf-8',
                 history_limit: int = 10, buffer_size: int = 16384):
        self.stream = stream
        self.mode = mode
        
        can_read = 'r' in mode or '+' in mode
        can_write = 'w' in mode or 'a' in mode or '+' in mode
        
        self._reader = AsyncTextReader(stream, encoding, buffer_size, history_limit) if can_read else None
        self._writer = AsyncTextWriter(stream, encoding, buffer_size) if can_write else None
    
    # Методы чтения
    async def read(self, size: int = -1):
        if not self._reader: raise IOError("File not open for reading")
        return await self._reader.read(size)
    
    async def readline(self):
        if not self._reader: raise IOError("File not open for reading")
        return await self._reader.readline()
    
    # Методы записи
    async def write(self, text: str):
        if not self._writer: raise IOError("File not open for writing")
        return await self._writer.write(text)
    
    async def flush(self):
        if self._writer:
            await self._writer.flush()
            
        if hasattr(self.stream, 'flush'):
            res = self.stream.flush()
            if inspect.isawaitable(res):
                await res
    
    # Навигация и управление
    async def seek(self, offset: int, whence: int = 0):
        await self.flush()
        res = await self.stream.seek(offset, whence)
        if self._reader:
            self._reader._reset()
        return res
    
    async def truncate(self, size: Optional[int] = None):
        """Обрезает файл до указанного размера (или текущей позиции)."""
        await self.flush()
        return await self.stream.truncate(size)
    
    @property
    def history(self):
        return self._reader.history if self._reader else deque()
    
    async def close(self):
        await self.flush()
        if hasattr(self.stream, 'close'):
            res = self.stream.close()
            if inspect.isawaitable(res):  # Проверяем, можно ли это авейтить
                await res
    
    def __aiter__(self) -> AsyncIterator:
        if not self._reader: raise TypeError("Object not iterable (no read access)")
        return self._reader.__aiter__()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()