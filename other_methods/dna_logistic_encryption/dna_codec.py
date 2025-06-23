import numpy as np

# —– 8 DNA KODLAMA KURALLARI —–
DNA_RULES = {
    1: {'00':'A','01':'G','10':'C','11':'T'},
    2: {'00':'A','01':'C','10':'G','11':'T'},
    3: {'00':'C','01':'A','10':'T','11':'G'},
    4: {'00':'C','01':'T','10':'A','11':'G'},
    5: {'00':'T','01':'C','10':'G','11':'A'},
    6: {'00':'T','01':'G','10':'C','11':'A'},
    7: {'00':'G','01':'T','10':'A','11':'C'},
    8: {'00':'G','01':'A','10':'T','11':'C'},
}
DNA_INV = {rule_num: {v: k for k, v in mapping.items()}
           for rule_num, mapping in DNA_RULES.items()}

def binary_to_dna(bin_arr: np.ndarray, rule: int = 1) -> np.ndarray:
    """
    İkili diziyi DNA dizisine çevirir, seçilen kuralı kullanarak.

    Parametreler:
    - bin_arr (np.ndarray): 0/1 dizisi, uzunluğu 2'nin katı olmalı.
    - rule (int): 1–8 arası DNA kodlama kuralı seçimi.

    Döndürür:
    - np.ndarray: DNA harfleri ('A','T','C','G') dizisi.
    """
    mapping = DNA_RULES[rule]
    pairs = bin_arr.reshape(-1, 2)
    return np.array([mapping[f"{b0}{b1}"] for b0, b1 in pairs])

def dna_to_binary(dna_arr: np.ndarray, rule: int = 1) -> np.ndarray:
    """
    DNA dizisini binary diziye çevirir, seçilen kurala göre.

    Parametreler:
    - dna_arr (np.ndarray): 'A','T','C','G' harfleri içeren dizi.
    - rule (int): 1–8 arası DNA kodlama kuralı seçimi.

    Döndürür:
    - np.ndarray: 0/1 dizisi.
    """
    inv_map = DNA_INV[rule]
    bits = [inv_map[b] for b in dna_arr]
    flat = "".join(bits)
    arr = np.frombuffer(np.packbits(np.array(list(flat), dtype=np.uint8)), dtype=np.uint8)
    return np.unpackbits(arr)[:len(dna_arr) * 2]

def dna_xor(dna1: np.ndarray, dna2: np.ndarray, rule: int = 1) -> np.ndarray:
    """
    İki DNA dizisini XOR işlemiyle birleştirir, seçilen kurala göre.

    Parametreler:
    - dna1, dna2 (np.ndarray): Aynı boyutta DNA dizileri.
    - rule (int): 1–8 arası kodlama kuralı seçimi.

    Döndürür:
    - np.ndarray: XOR uygulanmış DNA dizisi.
    """
    inv = DNA_INV[rule]
    mapping = DNA_RULES[rule]
    result = []
    for a, b in zip(dna1, dna2):
        bits_a = np.array(list(inv[a]), dtype=int)
        bits_b = np.array(list(inv[b]), dtype=int)
        xor_bits = np.bitwise_xor(bits_a, bits_b)
        pair = f"{xor_bits[0]}{xor_bits[1]}"
        result.append(mapping[pair])
    return np.array(result)

def scramble_with_sequence(flat_arr: np.ndarray, seq: np.ndarray) -> np.ndarray:
    """
    1D diziyi kaotik sıralama ile karıştırır.

    Parametreler:
    - flat_arr: 1D veri.
    - seq: Aynı uzunlukta float dizisi (kaotik).

    Döndürür:
    - np.ndarray: Scrambled dizi.
    """
    order = np.argsort(seq)
    return flat_arr[order]

def unscramble_with_sequence(scrambled: np.ndarray, seq: np.ndarray) -> np.ndarray:
    """
    Scramble edilmiş diziyi eski haline getirir.

    Parametreler:
    - scrambled: Scrambled dizi.
    - seq: Aynı kaotik dizi.

    Döndürür:
    - np.ndarray: Orijinal dizi.
    """
    order = np.argsort(seq)
    inv = np.empty_like(order)
    inv[order] = np.arange(len(order))
    return scrambled[inv]


def bytes_to_binary_array(byte_data: bytes) -> np.ndarray:
    """
    Bayt verisini 0/1 değerlerinden oluşan NumPy array'e çevirir.

    Parametreler:
    - byte_data (bytes): Dönüştürülecek bayt dizisi.

    Döndürür:
    - np.ndarray: (len(byte_data)*8,) boyutlu uint8 binary array.
    """
    return np.unpackbits(np.frombuffer(byte_data, dtype=np.uint8)).astype(np.uint8)

def binary_array_to_bytes(bin_arr: np.ndarray) -> bytes:
    """
    Binary array'i (0/1 dizisi) tekrar bayt verisine çevirir.

    Parametreler:
    - bin_arr (np.ndarray): (8 * m,) boyutlu 0/1 dizisi.

    Döndürür:
    - bytes: Orijinal bayt dizisi.
    """
    packed = np.packbits(bin_arr.astype(np.uint8))
    return packed.tobytes()