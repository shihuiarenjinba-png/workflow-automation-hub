from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from pathlib import Path

from .paths import token_path

CRYPTPROTECT_UI_FORBIDDEN = 0x1


class SecureStoreError(RuntimeError):
    pass


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _input_blob(data: bytes) -> tuple[_DATA_BLOB, ctypes.Array[ctypes.c_char]]:
    buffer = ctypes.create_string_buffer(data)
    blob = _DATA_BLOB(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)))
    return blob, buffer


class DPAPITokenVault:
    """Encrypt Google OAuth credentials with Windows DPAPI for the current user."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or token_path()

    @staticmethod
    def _require_windows() -> None:
        if os.name != "nt":
            raise SecureStoreError("Windows DPAPI is available only on Windows")

    def save_text(self, text: str) -> None:
        self._require_windows()
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        in_blob, _buffer = _input_blob(text.encode("utf-8"))
        out_blob = _DATA_BLOB()
        ok = crypt32.CryptProtectData(ctypes.byref(in_blob), "WorkflowAutomationHub", None, None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(out_blob))
        if not ok:
            raise SecureStoreError("CryptProtectData failed")
        try:
            encrypted = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        finally:
            kernel32.LocalFree(out_blob.pbData)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(encrypted)

    def load_text(self) -> str | None:
        if not self.path.exists():
            return None
        self._require_windows()
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        in_blob, _buffer = _input_blob(self.path.read_bytes())
        out_blob = _DATA_BLOB()
        ok = crypt32.CryptUnprotectData(ctypes.byref(in_blob), None, None, None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(out_blob))
        if not ok:
            raise SecureStoreError("CryptUnprotectData failed")
        try:
            decrypted = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        finally:
            kernel32.LocalFree(out_blob.pbData)
        return decrypted.decode("utf-8")

    def delete(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def exists(self) -> bool:
        return self.path.exists()
