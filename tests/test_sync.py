import pytest
from vpath import FileSystem


def test_memory_storage_flow():
    # FileSystem.register("mem")(MemoryStorage)
    
    path = FileSystem.open("memory://test.txt")
    
    # Запись
    with path.open("w") as f:
        f.write("hello sync")
    
    # Проверка существования и чтения
    assert path.exists() is True
    assert path.read_text() == "hello sync"
    
    # Stat
    stat = path.stat()
    assert stat.st_size > 0
    assert stat.is_dir is False


def test_local_storage_tmp(tmp_path):
    # Используем встроенную фикстуру pytest tmp_path
    # FileSystem.register("file")(LocalStorage)
    
    root = FileSystem.open(str(tmp_path))
    file_path = root / "subdir" / "file.log"
    
    file_path.write_text("data")
    assert (tmp_path / "subdir" / "file.log").exists()
    assert file_path.read_text() == "data"