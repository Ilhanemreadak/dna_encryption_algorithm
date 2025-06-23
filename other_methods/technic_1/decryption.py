import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from xor_utils import xor_decrypt
from chaos_utils import logistic_map

def decrypt_image_data(encrypted_data: bytes, encrypted_metadata: bytes, rsa_private_key: bytes) -> tuple:
    """
    Şifrelenmiş görüntü verisini RSA ve XOR ile çözer.

    Parametreler:
    - encrypted_data (bytes): XOR + logistic ile şifrelenmiş görüntü verisi
    - encrypted_metadata (bytes): RSA ile şifrelenmiş metadata
    - rsa_private_key (bytes): RSA özel anahtarı

    Döndürür:
    - tuple: (çözülmüş görüntü verisi, orijinal boyut)
    """
    private_key = RSA.import_key(rsa_private_key)
    cipher_rsa = PKCS1_OAEP.new(private_key)

    metadata_bytes = cipher_rsa.decrypt(encrypted_metadata)
    metadata = pickle.loads(metadata_bytes)

    xor_key = metadata['xor_key']
    x0 = metadata['x0']
    r = metadata['r']
    shape = metadata['shape']

    logistic_seq = logistic_map(x0, r, len(encrypted_data))

    decrypted = bytearray([
        b ^ logistic_seq[i] ^ xor_key for i, b in enumerate(encrypted_data)
    ])

    return decrypted, shape
