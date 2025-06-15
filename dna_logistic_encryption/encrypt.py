import numpy as np
import json
from utils import (
    load_image, save_image, flatten_rgb, reshape_rgb,
    derive_key_from_password
)
from dna_codec import (
    bytes_to_binary_array, binary_to_dna, dna_xor,
    scramble_with_sequence, dna_to_binary, binary_array_to_bytes
)
from logistic import generate_three_logistics

def encrypt_image(
    input_path: str,
    output_path: str,
    password: str,
    dna_rule: int = 1,
    x0_list: list[float] = None,
    r_list: list[float] = None
) -> None:
    """
    Görüntüyü parola, DNA ve logistic parametreleriyle şifreler;
    sonuç olarak şifreli görüntü, salt dosyası ve metadata dosyası oluşturur.

    Parametreler:
    - input_path: Girdi görüntü yolu.
    - output_path: Şifreli görüntü kaydedilecek yol.
    - password: Parola tabanlı key türetme için şifre.
    - dna_rule: 1–8 arası DNA kodlama kuralı.
    - x0_list: Kaotik başlangıç değerleri listesi [x0_1, x0_2, x0_3].
    - r_list: Kaotik logistic parametreleri [r_1, r_2, r_3].

    Döndürür:
    - None (işlem sonucu görüntü, .salt ve .meta dosyaları oluşur).
    """
    # İçerik: parola → key, salt üretim; görüntü → DNA → XOR adımları;
    # Kaotik XOR işlemleri; scramble; kaydetme; metadata yazımı.
    
    # 1️⃣ Parola ve salt ile key üret
    key_bytes, salt = derive_key_from_password(password)

    # 2️⃣ Görüntüyü yükle ve bit dönüşümleri
    arr_rgb = load_image(input_path)
    flat_rgb = flatten_rgb(arr_rgb)
    rgb_bits = np.unpackbits(flat_rgb.astype(np.uint8))

    # 3️⃣ DNA Key dönüşümü
    key_bits = bytes_to_binary_array(key_bytes)
    rgb_dna = binary_to_dna(rgb_bits, rule=dna_rule)
    key_dna = binary_to_dna(key_bits, rule=dna_rule)
    xord_dna = dna_xor(rgb_dna, np.resize(key_dna, rgb_dna.shape), rule=dna_rule)

    # 4️⃣ Kaotik diziler
    length = xord_dna.size
    X1, X2, X3 = generate_three_logistics(length, x0_list, r_list)

    # 5️⃣ DNA XOR kaotik dizilerle
    def chaos_xor(prev_dna, X):
        bits = np.unpackbits(((X * 255).astype(np.uint8)))
        return dna_xor(prev_dna,
                       np.resize(binary_to_dna(bits, rule=dna_rule), prev_dna.shape),
                       rule=dna_rule)

    dna1 = chaos_xor(xord_dna, X1)
    dna2 = chaos_xor(dna1, X2)
    dna3 = chaos_xor(dna2, X3)

    # 6️⃣ Scramble
    scrambled = scramble_with_sequence(dna3, X1)

    # 7️⃣ Döndürme işlemleri
    bin_scr = dna_to_binary(scrambled, rule=dna_rule)
    packed = binary_array_to_bytes(bin_scr)
    arr_enc = tile = np.frombuffer(packed, dtype=np.uint8)
    arr_enc = reshape_rgb(arr_enc, arr_rgb.shape)
    save_image(arr_enc, output_path)

    # 8️⃣ Salt dosyası
    with open(output_path + ".salt", "wb") as f:
        f.write(salt)

    # 9️⃣ Metadata kaydı
    meta = {
        "dna_rule": dna_rule,
        "x0_list": x0_list,
        "r_list": r_list
    }
    with open(output_path + ".meta", "w") as f:
        json.dump(meta, f)

    print(f"Şifreleme tamamlandı!\nŞifreli resim: {output_path}\nSalt: {output_path}.salt\nMetadata: {output_path}.meta")
