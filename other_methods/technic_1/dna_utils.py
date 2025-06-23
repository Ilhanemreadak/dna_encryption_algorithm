import numpy as np

dna_encoding_rules = {
    1: {'A': '00', 'T': '11', 'G': '01', 'C': '10'},
    2: {'A': '00', 'T': '11', 'G': '10', 'C': '01'},
    3: {'A': '01', 'T': '10', 'G': '00', 'C': '11'},
    4: {'A': '01', 'T': '10', 'G': '11', 'C': '00'},
    5: {'A': '10', 'T': '01', 'G': '00', 'C': '11'},
    6: {'A': '10', 'T': '01', 'G': '11', 'C': '00'},
    7: {'A': '11', 'T': '00', 'G': '01', 'C': '10'},
    8: {'A': '11', 'T': '00', 'G': '10', 'C': '01'}
}

def dna_encode(byte_data: bytes, rule_key: int) -> str:
    """
    Byte dizisini DNA baz dizisine dönüştürür.

    Parametreler:
    - byte_data (bytes): Şifrelenecek ham veri
    - rule_key (int): 1–8 arası DNA kodlama kuralı seçimi

    Döndürür:
    - str: DNA harflerinden oluşan dizi (A, T, G, C)
    """
    rule = dna_encoding_rules[rule_key]
    reverse_rule = {v: k for k, v in rule.items()}
    binary_str = ''.join([format(b, '08b') for b in byte_data])
    if len(binary_str) % 2 != 0:
        binary_str += '0'
    dna_encoded = ''.join([reverse_rule.get(binary_str[i:i+2], 'A') for i in range(0, len(binary_str), 2)])
    return dna_encoded

def dna_decode(dna_string: str, rule_key: int) -> bytearray:
    """
    DNA baz dizisini orijinal byte verisine dönüştürür.

    Parametreler:
    - dna_string (str): DNA harflerinden oluşan dizi (A, T, G, C)
    - rule_key (int): 1–8 arası DNA kodlama kuralı seçimi

    Döndürür:
    - bytearray: Orijinal byte verisi
    """
    rule = dna_encoding_rules[rule_key]
    binary_str = ''.join([rule.get(nuc, '00') for nuc in dna_string])
    if len(binary_str) % 8 != 0:
        binary_str += '0' * (8 - len(binary_str) % 8)
    return bytearray([int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8)])

def dna_to_numeric(dna_sequence: str) -> list:
    """
    DNA harflerini sayısal değerlere dönüştürür.

    Parametreler:
    - dna_sequence (str): DNA dizisi (örn. "ATGC")

    Döndürür:
    - list: DNA harflerinin sayısal karşılıkları
    """
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    return [mapping[base] for base in dna_sequence]
