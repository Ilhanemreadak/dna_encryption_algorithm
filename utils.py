import numpy as np
from PIL import Image
import os
import hashlib
from hashlib import pbkdf2_hmac

def load_image(path: str) -> np.ndarray:
    """
    Verilen dosya yolundan bir görüntüyü yükler ve RGB formatında NumPy dizisi olarak döner.

    Parametreler:
    - path (str): Yüklenmesi istenen görüntünün dosya yolu.

    Döndürür:
    - np.ndarray: (M, N, 3) boyutlu uint8 RGB görüntü matrisi.
    """
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

def save_image(arr: np.ndarray, path: str) -> None:
    """
    NumPy dizisi halindeki RGB görüntüyü dosyaya kaydeder.

    Parametreler:
    - arr (np.ndarray): (M, N, 3) boyutlu RGB görüntü verisi (uint8).
    - path (str): Kaydedilecek dosya yolu (örn. 'out.png').

    Döndürür:
    - None
    """
    if not isinstance(arr, np.ndarray) or arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(f"Beklenen (M,N,3) uint8 NumPy dizisi. Alındı: shape={getattr(arr, 'shape', None)}")
    try:
        img = Image.fromarray(arr.astype(np.uint8), 'RGB')
        img.save(path)
    except OSError as e:
        raise OSError(f"Görüntü kaydedilemedi: {path}") from e

def sha256_key_from_image(arr: np.ndarray) -> bytes:
    """
    Görüntü verisinden SHA-256 kullanarak 256-bit (32 byte) gizli anahtar üretir.

    Parametreler:
    - arr (np.ndarray): RGB görüntü verisi (her değer 0-255 arası).

    Döndürür:
    - bytes: 32 byte'lık SHA‑256 digest.
    """
    if not isinstance(arr, np.ndarray) or arr.size == 0:
        raise ValueError("Görüntü verisi numeric NumPy dizisi olmalı ve boş olmamalı.")
    try:
        flat = arr.flatten()
        h = hashlib.sha256(flat.tobytes()).digest()
        return h
    except Exception as e:
        raise RuntimeError("SHA-256 anahtar oluşturulurken hata oluştu.") from e

def flatten_rgb(arr: np.ndarray) -> np.ndarray:
    """
    RGB (M, N, 3) dizisini üç kanalın ardışık olarak sıralandığı 1D diziye dönüştürür.

    Parametreler:
    - arr (np.ndarray): (M, N, 3) boyutlu RGB görüntü.

    Döndürür:
    - np.ndarray: (3 * M * N,) boyutlu uint8 dizi.
    """
    if not isinstance(arr, np.ndarray) or arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(f"Beklenen (M,N,3) RGB dizisi. Alındı: shape={getattr(arr, 'shape', None)}")
    return arr.reshape(-1)

def reshape_rgb(flat_arr: np.ndarray, shape: tuple) -> np.ndarray:
    """
    Tek boyutlu RGB kanal dizisini tekrar (M, N, 3) yapısına dönüştürür.

    Parametreler:
    - flat_arr (np.ndarray): 1D RGB verisi (uzunluk = 3*M*N).
    - shape (tuple): (M, N, 3) hedef şekil.

    Döndürür:
    - np.ndarray: Tekrar RGB formatlı 3D dizi.
    """
    if not isinstance(flat_arr, np.ndarray) or flat_arr.ndim != 1:
        raise ValueError("flat_arr tek boyutlu NumPy dizisi olmalı.")
    if not (isinstance(shape, tuple) and len(shape) == 3):
        raise ValueError("shape parametresi (M, N, 3) şeklinde tuple olmalı.")
    expected_size = shape[0] * shape[1] * shape[2]
    if flat_arr.size != expected_size:
        raise ValueError(f"flat_arr uzunluğu ({flat_arr.size}) target shape'ın boyutuyla uyuşmuyor ({expected_size}).")
    return flat_arr.reshape(shape)

def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Parolaya ve salt değerine dayalı olarak 256-bit (32 byte) anahtar oluşturur.

    Parametreler:
    - password (str): Kullanıcı parolası.
    - salt (bytes | None): 16 byte rastgele tuz. None ise otomatik oluşturulur.

    Döndürür:
    - key_bytes (bytes): 32 baytlık HMAC-SHA256 tabanlı anahtar.
    - salt (bytes): Kullanılan 16 bayt salt.
    """
    if salt is None:
        salt = os.urandom(16)
    key = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000, dklen=32)
    return key, salt