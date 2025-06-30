import numpy as np
import json
from utils.misc_utils import (
    load_image, save_image, flatten_rgb, reshape_rgb,
    derive_key_from_password
)
from src.accelerated.dna_codec_cy import (
    bytes_to_binary_array, binary_to_dna, dna_to_binary,
    dna_xor, unscramble_with_sequence, binary_array_to_bytes
)
from src.accelerated.logistic_cy import generate_logistic_sequence, mask_chaos
from src.accelerated.chaos_utils_cy import chaos_xor

from PIL import Image

def decrypt_image(
    input_path: str,
    output_path: str,
    password: str
) -> None:
    """
    Şifreli PNG içindeki salt ve XOR'lanmış metadata’yı parola ile çözüp,
    orijinal DNA/kaos parametrelerini elde eder, görüntüyü çözer.

    Parametreler:
    - input_path: Şifreli görüntü dosya yolu.
    - output_path: Çözülen görüntü kaydedilecek yol.
    - password: Doğru parametreleri çıkarmak için gerekli parola.
    """
    try:
        img  = Image.open(input_path)
        info = img.info
        salt = bytes.fromhex(info.get("salt", ""))
        meta = json.loads(info.get("params", "{}"))

        if not salt or not meta:
            raise ValueError("Salt veya metadata eksik.")

        dna_rule = meta.get("dna_rule", 1)
        x0_list  = meta.get("x0_list", [0.413742, 0.526374, 0.639127])
        r_list   = meta.get("r_list", [3.987652, 3.992715, 3.996427])

        key_bytes = derive_key_from_password(password, salt)[0]
        arr_enc   = np.array(img.convert('RGB'))
        flat_enc  = flatten_rgb(arr_enc)
        enc_bits  = np.unpackbits(flat_enc.astype(np.uint8))
        dna_enc   = binary_to_dna(enc_bits, rule=dna_rule)

        X1 = generate_logistic_sequence(dna_enc.size, x0_list[0], r_list[0])
        X2 = generate_logistic_sequence(dna_enc.size, x0_list[1], r_list[1])
        X3 = generate_logistic_sequence(dna_enc.size, x0_list[2], r_list[2])

        # Aynı şekilde chaos dizilerini şifreye göre boz
        X1 = mask_chaos(X1, key_bytes)
        X2 = mask_chaos(X2, key_bytes[::-1])
        X3 = mask_chaos(X3, key_bytes[::2])
        
        dna_unscr = unscramble_with_sequence(dna_enc, X1)
        
        dna_x3 = chaos_xor(dna_unscr, X3, dna_rule)
        dna_x2 = chaos_xor(dna_x3,   X2, dna_rule)
        dna_x1 = chaos_xor(dna_x2,   X1, dna_rule)
        
        key_bits   = bytes_to_binary_array(key_bytes)
        key_dna    = binary_to_dna(key_bits, rule=dna_rule)
        dna_plain  = dna_xor(dna_x1, np.resize(key_dna, dna_x1.shape), rule=dna_rule)
        
        bits_plain = dna_to_binary(dna_plain, rule=dna_rule)
        bytes_plain = binary_array_to_bytes(bits_plain)
        
        arr_plain  = reshape_rgb(np.frombuffer(bytes_plain, dtype=np.uint8), arr_enc.shape)
        save_image(arr_plain, output_path)

    except Exception as e:
        print(f"Decryption failed: {e}")
        raise e
