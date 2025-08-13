from __future__ import annotations
import os, struct, hashlib, secrets, io
from typing import Optional, Literal

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# zstdは任意依存
try:
    import zstandard as zstd  # type: ignore
except Exception:  # pragma: no cover
    zstd = None

import zlib

MAGIC = b"YUAC"
VERSION = 1

# flags
FLAG_ENCRYPTED = 0b00000001

# algo codes
ALGO_STORE = 0
ALGO_ZLIB = 1
ALGO_ZSTD = 2

Algo = Literal["store", "zlib", "zstd"]

def _algo_code(algo: Algo) -> int:
    if algo == "store":
        return ALGO_STORE
    if algo == "zlib":
        return ALGO_ZLIB
    if algo == "zstd":
        return ALGO_ZSTD
    raise ValueError("unknown algo")

def _algo_name(code: int) -> str:
    return {ALGO_STORE:"store", ALGO_ZLIB:"zlib", ALGO_ZSTD:"zstd"}.get(code, f"unknown({code})")

def _compress_raw(data: bytes, algo: Algo, level: int) -> bytes:
    if algo == "store":
        return data
    if algo == "zlib":
        level = max(0, min(level, 9))
        return zlib.compress(data, level)
    if algo == "zstd":
        if zstd is None:
            raise RuntimeError("zstandard is not installed. Use `pip install yua-compressor[zstd]`.")
        cctx = zstd.ZstdCompressor(level=level)
        return cctx.compress(data)
    raise ValueError("invalid algo")

def _decompress_raw(data: bytes, algo_code: int, out_size_hint: int | None) -> bytes:
    if algo_code == ALGO_STORE:
        return data
    if algo_code == ALGO_ZLIB:
        return zlib.decompress(data)
    if algo_code == ALGO_ZSTD:
        if zstd is None:
            raise RuntimeError("zstandard is not installed. Use `pip install yua-compressor[zstd]`.")
        dctx = zstd.ZstdDecompressor()
        if out_size_hint is None:
            return dctx.decompress(data)
        return dctx.decompress(data, max_output_size=out_size_hint)
    raise ValueError("invalid algo code")

def _checksum_b16(data: bytes) -> bytes:
    return hashlib.blake2s(data, digest_size=16).digest()

def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return kdf.derive(password.encode("utf-8"))

def compress_bytes(data: bytes, *, algo: Algo = "zstd", level: int = 6, password: Optional[str] = None) -> bytes:
    """Compress to YUAC bytes. If password is provided, AES-256-GCM encrypts the payload.
    """
    flags = 0
    algo_code = _algo_code(algo)
    orig_size = len(data)
    checksum = _checksum_b16(data)

    compressed = _compress_raw(data, algo, level)

    salt = nonce = b""
    payload = compressed

    if password is not None:
        flags |= FLAG_ENCRYPTED
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        key = _derive_key(password, salt)
        aes = AESGCM(key)
        # AAD: magic+version+flags+algo
        aad = MAGIC + bytes([VERSION, flags, algo_code, 0])
        payload = aes.encrypt(nonce, compressed, aad)

    header = bytearray()
    header += MAGIC
    header += bytes([VERSION, flags, algo_code, 0])  # reserved=0
    header += struct.pack('<Q', orig_size)
    header += checksum
    if flags & FLAG_ENCRYPTED:
        header += salt
        header += nonce

    return bytes(header) + payload

def decompress_bytes(blob: bytes, *, password: Optional[str] = None) -> bytes:
    mv = memoryview(blob)
    if len(mv) < 32:
        raise ValueError("too short")

    if mv[:4].tobytes() != MAGIC:
        raise ValueError("bad magic")
    version = mv[4]
    if version != VERSION:
        raise ValueError(f"unsupported version: {version}")
    flags = mv[5]
    algo_code = mv[6]
    # reserved = mv[7]
    orig_size = struct.unpack('<Q', mv[8:16].tobytes())[0]
    checksum = mv[16:32].tobytes()
    off = 32

    encrypted = bool(flags & FLAG_ENCRYPTED)
    if encrypted:
        if password is None:
            raise ValueError("password required")
        if len(mv) < off + 28:
            raise ValueError("corrupt header (enc)")
        salt = mv[off:off+16].tobytes(); off += 16
        nonce = mv[off:off+12].tobytes(); off += 12
        key = _derive_key(password, salt)
        aes = AESGCM(key)
        aad = MAGIC + bytes([VERSION, flags, algo_code, 0])
        ciphertext = mv[off:].tobytes()
        try:
            compressed = aes.decrypt(nonce, ciphertext, aad)
        except Exception as e:
            raise ValueError("decryption failed (wrong password or corrupted data)") from e
    else:
        compressed = mv[off:].tobytes()

    data = _decompress_raw(compressed, algo_code, orig_size if algo_code != ALGO_STORE else len(compressed))

    if _checksum_b16(data) != checksum:
        raise ValueError("checksum mismatch")

    if len(data) != orig_size:
        # not critical but indicates corruption
        raise ValueError("size mismatch")

    return data

def compress_file(src_path: str, dst_path: str, *, algo: Algo = "zstd", level: int = 6, password: Optional[str] = None) -> None:
    with open(src_path, "rb") as f:
        data = f.read()
    blob = compress_bytes(data, algo=algo, level=level, password=password)
    with open(dst_path, "wb") as f:
        f.write(blob)

def decompress_file(src_path: str, dst_path: str, *, password: Optional[str] = None) -> None:
    with open(src_path, "rb") as f:
        blob = f.read()
    data = decompress_bytes(blob, password=password)
    with open(dst_path, "wb") as f:
        f.write(data)
