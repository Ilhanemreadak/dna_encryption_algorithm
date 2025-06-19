def xor_encrypt(data: bytes, key: int) -> bytearray:
    """
    Veriyi XOR işlemi ile şifreler.

    Parametreler:
    - data (bytes): Şifrelenecek veri
    - key (int): XOR anahtarı (0-255)

    Döndürür:
    - bytearray: XOR ile şifrelenmiş veri
    """
    return bytearray([b ^ key for b in data])

def xor_decrypt(data: bytes, key: int) -> bytearray:
    """
    XOR ile şifrelenmiş veriyi çözer.

    Parametreler:
    - data (bytes): Şifreli veri
    - key (int): XOR anahtarı (0-255)

    Döndürür:
    - bytearray: Çözülmüş veri
    """
    return xor_encrypt(data, key)