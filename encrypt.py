import numpy as np
import json
from utils.misc_utils import (
    load_image, save_image, flatten_rgb, reshape_rgb,
    derive_key_from_password
)
from src.accelerated.dna_codec_cy import (
    bytes_to_binary_array, binary_to_dna, dna_xor,
    scramble_with_sequence, dna_to_binary, binary_array_to_bytes
)
from src.accelerated.logistic_cy import generate_logistic_sequence, mask_chaos
from src.accelerated.chaos_utils_cy import chaos_xor
from PIL import Image, PngImagePlugin
import os


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
    sonuç olarak şifreli görüntüyü ve salt+şifrelenmiş metadata içeren PNG dosyasını oluşturur.

    Parametreler:
    - input_path: Girdi görüntü yolu.
    - output_path: Şifreli görüntü kaydedilecek yol.
    - password: Parola tabanlı key türetme için şifre.
    - dna_rule: 1–8 arası DNA kodlama kuralı.
    - x0_list: Kaotik başlangıç değerleri listesi [x0_1, x0_2, x0_3].
    - r_list: Kaotik logistic parametreleri [r_1, r_2, r_3].
    """
    try:
        if x0_list is None:
            x0_list = [0.413742, 0.526374, 0.639127]
        if r_list is None:
            r_list = [3.987652, 3.992715, 3.996427]
        if len(x0_list) != 3 or len(r_list) != 3:
            raise ValueError("x0_list ve r_list tam olarak 3 eleman içermelidir.")
        if not (1 <= dna_rule <= 8):
            raise ValueError("dna_rule 1 ile 8 arasında bir değer olmalıdır.")
        
        key_bytes, salt = derive_key_from_password(password)
        
        arr_rgb   = load_image(input_path)
        flat_rgb  = flatten_rgb(arr_rgb)
        rgb_bits  = np.unpackbits(flat_rgb.astype(np.uint8))
        key_bits  = bytes_to_binary_array(key_bytes)
        rgb_dna   = binary_to_dna(rgb_bits, rule=dna_rule)
        key_dna   = binary_to_dna(key_bits, rule=dna_rule)
        xord_dna  = dna_xor(rgb_dna, np.resize(key_dna, rgb_dna.shape), rule=dna_rule)

        length    = xord_dna.size
        X1 = generate_logistic_sequence(length, x0_list[0], r_list[0])
        X2 = generate_logistic_sequence(length, x0_list[1], r_list[1])
        X3 = generate_logistic_sequence(length, x0_list[2], r_list[2])

        X1 = mask_chaos(X1, key_bytes)
        X2 = mask_chaos(X2, key_bytes[::-1])
        X3 = mask_chaos(X3, key_bytes[::2])  
        
        dna1 = chaos_xor(xord_dna, X1, dna_rule)
        dna2 = chaos_xor(dna1,   X2, dna_rule)
        dna3 = chaos_xor(dna2,   X3, dna_rule)

        scrambled = scramble_with_sequence(dna3, X1)
        
        bin_scr   = dna_to_binary(scrambled, rule=dna_rule)
        packed    = binary_array_to_bytes(bin_scr)
        arr_enc   = reshape_rgb(np.frombuffer(packed, dtype=np.uint8), arr_rgb.shape)
        
        temp_path = output_path + ".tmp.png"
        save_image(arr_enc, temp_path)
        img = Image.open(temp_path).convert("RGB")

        meta_dict = {"dna_rule": dna_rule, "x0_list": x0_list, "r_list": r_list}
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("salt", salt.hex())
        pnginfo.add_text("params", json.dumps(meta_dict))
        img.save(output_path, pnginfo=pnginfo)
        os.remove(temp_path)

    except Exception as e:
        raise RuntimeError(f"Şifreleme sırasında hata oluştu: {e}") from e
    