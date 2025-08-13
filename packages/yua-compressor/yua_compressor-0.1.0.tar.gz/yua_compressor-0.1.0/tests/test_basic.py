import os, tempfile
from yua_compressor import compress_bytes, decompress_bytes, compress_file, decompress_file

def roundtrip(data: bytes, **kw):
    blob = compress_bytes(data, **kw)
    out = decompress_bytes(blob, password=kw.get("password"))
    assert out == data

def test_store():
    roundtrip(b"A"*1024, algo="store")

def test_zlib():
    roundtrip(b"Hello"*1000, algo="zlib", level=6)

def test_zstd():
    try:
        import zstandard  # noqa
    except Exception:
        return
    roundtrip(b"Z"*10000, algo="zstd", level=10)

def test_encrypt():
    roundtrip(b"secret-data"*100, algo="zlib", password="pass123")

def test_cli_files(tmp_path):
    src = tmp_path / "data.bin"
    out = tmp_path / "data.yuac"
    back = tmp_path / "back.bin"
    src.write_bytes(b"X"*5000)
    compress_file(str(src), str(out), algo="zlib", level=5, password=None)
    decompress_file(str(out), str(back), password=None)
    assert back.read_bytes() == src.read_bytes()
