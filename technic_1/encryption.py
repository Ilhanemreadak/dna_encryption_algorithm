import random
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from dna_utils import dna_encode, dna_to_numeric
from xor_utils import xor_encrypt
from chaos_utils import logistic_map

def encrypt_image_data(image_data: bytes, shape: tuple) -> dict:
    """
    Görüntü verisini DNA, XOR ve logistic map ile şifreler.

    Parametreler:
    - image_data (bytes): Görüntü verisi (flatten edilmiş RGB)
    - shape (tuple): Orijinal görüntü boyutu (h, w, c)

    Döndürür:
    - dict: Şifrelenmiş veri ve RSA şifreli metadata
    """
    dna_rule_key = random.randint(1, 8)
    xor_key = random.randint(1, 255)
    x0 = random.uniform(0.0, 1.0)
    r = random.uniform(3.9, 4.0)
    logistic_seq = logistic_map(x0, r, len(image_data))

    dna_encoded = dna_encode(image_data, dna_rule_key)
    numeric_dna = dna_to_numeric(dna_encoded)

    encrypted = bytearray([
        b ^ logistic_seq[i] ^ xor_key for i, b in enumerate(image_data)
    ])

    metadata = {
        'xor_key': xor_key,
        'x0': x0,
        'r': r,
        'shape': shape,
        'dna_rule': dna_rule_key
    }

    rsa_key = RSA.generate(2048)
    public_key = rsa_key.publickey()
    private_key = rsa_key

    cipher_rsa = PKCS1_OAEP.new(public_key)
    metadata_bytes = pickle.dumps(metadata)
    encrypted_metadata = cipher_rsa.encrypt(metadata_bytes)

    return {
        'encrypted_data': encrypted,
        'encrypted_metadata': encrypted_metadata,
        'rsa_private': private_key.export_key(),
        'rsa_public': public_key.export_key()
    }

