import pytest
from vpath import FileSystem


@pytest.mark.asyncio
async def test_async_memory_flow():
    path = await FileSystem.aopen("memory://async.data")
    
    async with await path.open("w") as f:
        await f.write("hello async")
    
    assert await path.exists() is True
    assert await path.read_text() == "hello async"


@pytest.mark.asyncio
async def test_async_local_io(tmp_path):
    root = await FileSystem.aopen(str(tmp_path))
    file = root / "async_file.txt"
    
    await file.write_text("anyio power")
    
    found = []
    async for item in root.iterdir():
        found.append(item.name)
    
    assert "async_file.txt" in found
    assert await file.read_text() == "anyio power"


@pytest.mark.asyncio
async def test_async_mkdir_unlink(tmp_path):
    folder = await FileSystem.aopen(str(tmp_path / "new_dir"))
    
    await folder.mkdir(parents=True)
    assert await folder.exists()
    
    await folder.unlink()
    assert not await folder.exists()