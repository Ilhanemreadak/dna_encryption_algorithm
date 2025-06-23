from utils import derive_key_from_password

key, salt = derive_key_from_password("gizliŞifre")
print("Anahtar uzunluğu:", len(key))
print("Salt uzunluğu:", len(salt))
print("Salt (base64):", salt.hex())  # İsteğe bağlı: salt’ı kolayca görebilmek için
