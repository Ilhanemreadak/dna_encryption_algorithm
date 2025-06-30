import numpy as np
from PIL import Image
import os
import hashlib
from hashlib import pbkdf2_hmac
from typing import Tuple

def load_image(path: str) -> np.ndarray:
    try:
        img = Image.open(path).convert('RGB')
        arr = np.array(img)
        if arr.ndim != 3 or arr.shape[2] != 3:
            raise ValueError(f"Beklenen RGB formatında değil: {arr.shape}")
        return arr
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Görüntü dosyası bulunamadı: {path}") from e
    except OSError as e:
        raise OSError(f"Görüntü okunamıyor veya geçersiz: {path}") from e
    except Exception as e:
        raise RuntimeError(f"Görüntü yüklenirken beklenmeyen hata: {e}") from e

def save_image(arr: np.ndarray, path: str) -> None:
    try:
        if not isinstance(arr, np.ndarray) or arr.ndim != 3 or arr.shape[2] != 3:
            raise ValueError(f"Beklenen (M,N,3) uint8 NumPy dizisi. Alındı: shape={getattr(arr, 'shape', None)}")
        img = Image.fromarray(arr.astype(np.uint8), 'RGB')
        img.save(path)
    except OSError as e:
        raise OSError(f"Görüntü kaydedilemedi: {path}") from e
    except Exception as e:
        raise RuntimeError(f"Görüntü kaydedilirken beklenmeyen hata: {e}") from e

def sha256_key_from_image(arr: np.ndarray) -> bytes:
    try:
        if not isinstance(arr, np.ndarray) or arr.size == 0:
            raise ValueError("Görüntü verisi numeric NumPy dizisi olmalı ve boş olmamalı.")
        flat = arr.flatten()
        h = hashlib.sha256(flat.tobytes()).digest()
        return h
    except Exception as e:
        raise RuntimeError("SHA-256 anahtar oluşturulurken hata oluştu.") from e

def flatten_rgb(arr: np.ndarray) -> np.ndarray:
    try:
        if not isinstance(arr, np.ndarray) or arr.ndim != 3 or arr.shape[2] != 3:
            raise ValueError(f"Beklenen (M,N,3) RGB dizisi. Alındı: shape={getattr(arr, 'shape', None)}")
        return arr.reshape(-1)
    except Exception as e:
        raise RuntimeError(f"RGB düzleştirilirken hata oluştu: {e}") from e

def reshape_rgb(flat_arr: np.ndarray, shape: tuple) -> np.ndarray:
    try:
        if not isinstance(flat_arr, np.ndarray) or flat_arr.ndim != 1:
            raise ValueError("flat_arr tek boyutlu NumPy dizisi olmalı.")
        if not (isinstance(shape, tuple) and len(shape) == 3):
            raise ValueError("shape parametresi (M, N, 3) şeklinde tuple olmalı.")
        expected_size = shape[0] * shape[1] * shape[2]
        if flat_arr.size != expected_size:
            raise ValueError(f"flat_arr uzunluğu ({flat_arr.size}) target shape'ın boyutuyla uyuşmuyor ({expected_size}).")
        return flat_arr.reshape(shape)
    except Exception as e:
        raise RuntimeError(f"RGB yeniden şekillendirilirken hata oluştu: {e}") from e

def derive_key_from_password(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    try:
        if salt is None:
            salt = os.urandom(16)
        key = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000, dklen=32)
        return key, salt
    except Exception as e:
        raise RuntimeError(f"Paroladan anahtar türetilirken hata oluştu: {e}") from e
