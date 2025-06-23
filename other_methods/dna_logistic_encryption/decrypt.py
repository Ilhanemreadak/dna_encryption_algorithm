import numpy as np
import json
import os
from utils import (
    load_image, save_image, flatten_rgb, reshape_rgb,
    derive_key_from_password
)
from dna_codec import (
    bytes_to_binary_array, binary_to_dna, dna_to_binary,
    dna_xor, unscramble_with_sequence, binary_array_to_bytes
)
from logistic import generate_three_logistics

def decrypt_image(
    input_path: str,
    output_path: str,
    password: str
) -> None:
    """
    Parola ve metadata bilgileri kullanılarak şifreli görüntüyü çözer ve orijinal görüntüyü kaydeder.

    Parametreler:
    - input_path: Şifreli görüntü dosya yolu.
    - output_path: Çözülen görüntünün kaydedileceği yol.
    - password: Şifreleme sırasında kullanılan parola.

    Döndürür:
    - None (işlem sonucu orijinal görüntü kaydedilir).
    """
    # İçerik: .salt ve .meta dosyalarını oku, parola ile key türet, 
    # DNA ve kaotik adımların tersini uygula, görüntüyü kaydet.

    salt_file = input_path + ".salt"
    meta_file = input_path + ".meta"
    if not os.path.exists(salt_file):
        raise FileNotFoundError("Salt dosyası yok: " + salt_file)
    if not os.path.exists(meta_file):
        raise FileNotFoundError("Metadata yok: " + meta_file)

    with open(salt_file, "rb") as f:
        salt = f.read()
    with open(meta_file, "r") as f:
        meta = json.load(f)

    dna_rule = meta["dna_rule"]
    x0_list = meta["x0_list"]
    r_list = meta["r_list"]

    key_bytes, _ = derive_key_from_password(password, salt)
    arr_enc = load_image(input_path)
    flat_enc = flatten_rgb(arr_enc)
    enc_bits = np.unpackbits(flat_enc.astype(np.uint8))
    dna_enc = binary_to_dna(enc_bits, rule=dna_rule)

    length = dna_enc.size
    X1, X2, X3 = generate_three_logistics(length, x0_list, r_list)
    dna_unscr = unscramble_with_sequence(dna_enc, X1)

    def chaos_xor(prev_dna, X):
        bits = np.unpackbits(((X * 255).astype(np.uint8)))
        return dna_xor(prev_dna,
                       np.resize(binary_to_dna(bits, rule=dna_rule), prev_dna.shape),
                       rule=dna_rule)

    dna_x3 = chaos_xor(dna_unscr, X3)
    dna_x2 = chaos_xor(dna_x3, X2)
    dna_x1 = chaos_xor(dna_x2, X1)

    key_bits = bytes_to_binary_array(key_bytes)
    key_dna = binary_to_dna(key_bits, rule=dna_rule)
    dna_plain = dna_xor(dna_x1, np.resize(key_dna, dna_x1.shape), rule=dna_rule)

    bits_plain = dna_to_binary(dna_plain, rule=dna_rule)
    bytes_plain = binary_array_to_bytes(bits_plain)
    arr_plain = np.frombuffer(bytes_plain, dtype=np.uint8)
    arr_plain = reshape_rgb(arr_plain, arr_enc.shape)
    save_image(arr_plain, output_path)

    print(f"Decryption tamamlandı. Sonuç kaydedildi: {output_path}")
