import numpy as np
cimport numpy as cnp
cimport cython
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy

# Ensure numpy arrays are properly initialized
cnp.import_array()

# DNA kodlama tabloları - Cython için optimize edilmiş
# DNA harfleri: A=0, T=1, C=2, G=3 olarak kodlanır
cdef cnp.uint8_t[8][4] DNA_ENCODE_TABLE = [
    [0, 0, 0, 0],  # Dummy for rule 0
    [0, 3, 2, 1],  # Rule 1: 00->A, 01->G, 10->C, 11->T
    [0, 2, 3, 1],  # Rule 2: 00->A, 01->C, 10->G, 11->T
    [2, 0, 1, 3],  # Rule 3: 00->C, 01->A, 10->T, 11->G
    [2, 1, 0, 3],  # Rule 4: 00->C, 01->T, 10->A, 11->G
    [1, 2, 3, 0],  # Rule 5: 00->T, 01->C, 10->G, 11->A
    [1, 3, 2, 0],  # Rule 6: 00->T, 01->G, 10->C, 11->A
    [3, 1, 0, 2],  # Rule 7: 00->G, 01->T, 10->A, 11->C
]

# DNA decode tabloları
cdef cnp.uint8_t[8][4] DNA_DECODE_TABLE = [
    [0, 0, 0, 0],  # Dummy for rule 0
    [0, 3, 2, 1],  # Rule 1: A->00, T->11, C->10, G->01
    [0, 3, 1, 2],  # Rule 2: A->00, T->11, G->10, C->01
    [1, 2, 0, 3],  # Rule 3: C->00, A->01, T->10, G->11
    [2, 1, 0, 3],  # Rule 4: C->00, T->01, A->10, G->11
    [3, 0, 1, 2],  # Rule 5: T->00, C->01, G->10, A->11
    [3, 0, 2, 1],  # Rule 6: T->00, G->01, C->10, A->11
    [2, 1, 3, 0],  # Rule 7: G->00, T->01, A->10, C->11
]

# DNA XOR tabloları - her kural için önceden hesaplanmış
cdef cnp.uint8_t[8][4][4] DNA_XOR_TABLE

# XOR tablolarını başlat
cdef void init_xor_tables():
    cdef int rule, a, b, bit_a0, bit_a1, bit_b0, bit_b1, xor0, xor1, pair_idx
    
    for rule in range(1, 8):
        for a in range(4):
            for b in range(4):
                # A ve B harflerini bit çiftlerine çevir
                if a == 0:  # A
                    bit_a0, bit_a1 = 0, 0
                elif a == 1:  # T
                    bit_a0, bit_a1 = 1, 1
                elif a == 2:  # C
                    bit_a0, bit_a1 = 1, 0
                else:  # G
                    bit_a0, bit_a1 = 0, 1
                
                if b == 0:  # A
                    bit_b0, bit_b1 = 0, 0
                elif b == 1:  # T
                    bit_b0, bit_b1 = 1, 1
                elif b == 2:  # C
                    bit_b0, bit_b1 = 1, 0
                else:  # G
                    bit_b0, bit_b1 = 0, 1
                
                # Kurala göre decode et
                if rule == 1:
                    if a == 0: bit_a0, bit_a1 = 0, 0
                    elif a == 3: bit_a0, bit_a1 = 0, 1
                    elif a == 2: bit_a0, bit_a1 = 1, 0
                    elif a == 1: bit_a0, bit_a1 = 1, 1
                    
                    if b == 0: bit_b0, bit_b1 = 0, 0
                    elif b == 3: bit_b0, bit_b1 = 0, 1
                    elif b == 2: bit_b0, bit_b1 = 1, 0
                    elif b == 1: bit_b0, bit_b1 = 1, 1
                
                # XOR işlemi
                xor0 = bit_a0 ^ bit_b0
                xor1 = bit_a1 ^ bit_b1
                
                # Sonucu DNA harfine çevir
                pair_idx = (xor0 << 1) | xor1
                DNA_XOR_TABLE[rule][a][b] = DNA_ENCODE_TABLE[rule][pair_idx]

# Modül yüklendiğinde tabloları başlat
init_xor_tables()

@cython.boundscheck(False)
@cython.wraparound(False)
def binary_to_dna(cnp.ndarray[cnp.uint8_t, ndim=1] bin_arr, int rule=1):
    """
    İkili diziyi DNA dizisine çevirir.
    
    Parameters:
    - bin_arr: 0/1 dizisi, uzunluğu 2'nin katı olmalı
    - rule: 1-8 arası DNA kodlama kuralı
    
    Returns:
    - DNA dizisi (0=A, 1=T, 2=C, 3=G olarak kodlanmış)
    """
    cdef int i, pair_idx
    cdef int length = bin_arr.shape[0]
    cdef int pairs_count = length // 2
    
    # Çift sayı uzunluğu kontrolü
    if length % 2 != 0:
        raise ValueError("Binary array length must be even")
    
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] result = np.zeros(pairs_count, dtype=np.uint8)
    
    for i in range(pairs_count):
        pair_idx = (bin_arr[2*i] << 1) | bin_arr[2*i + 1]
        result[i] = DNA_ENCODE_TABLE[rule][pair_idx]
    
    return result

@cython.boundscheck(False)
@cython.wraparound(False)
def dna_to_binary(cnp.ndarray[cnp.uint8_t, ndim=1] dna_arr, int rule=1):
    """
    DNA dizisini binary diziye çevirir.
    
    Parameters:
    - dna_arr: DNA dizisi (0=A, 1=T, 2=C, 3=G)
    - rule: 1-8 arası DNA kodlama kuralı
    
    Returns:
    - 0/1 dizisi
    """
    cdef int i, j, dna_val, bit_pair
    cdef int length = dna_arr.shape[0]
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] result = np.zeros(length * 2, dtype=np.uint8)
    
    # Reverse lookup tablosu
    cdef cnp.uint8_t[4] reverse_lookup
    for i in range(4):
        reverse_lookup[DNA_ENCODE_TABLE[rule][i]] = i
    
    for i in range(length):
        dna_val = dna_arr[i]
        bit_pair = reverse_lookup[dna_val]
        result[2*i] = (bit_pair >> 1) & 1
        result[2*i + 1] = bit_pair & 1
    
    return result

@cython.boundscheck(False)
@cython.wraparound(False)
def dna_xor(cnp.ndarray[cnp.uint8_t, ndim=1] dna1, 
            cnp.ndarray[cnp.uint8_t, ndim=1] dna2, 
            int rule=1):
    """
    İki DNA dizisini XOR işlemiyle birleştirir.
    
    Parameters:
    - dna1, dna2: Aynı boyutta DNA dizileri
    - rule: 1-8 arası kodlama kuralı
    
    Returns:
    - XOR uygulanmış DNA dizisi
    """
    cdef int i
    cdef int length = dna1.shape[0]
    
    if length != dna2.shape[0]:
        raise ValueError("DNA arrays must have the same length")
    
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] result = np.zeros(length, dtype=np.uint8)
    
    for i in range(length):
        result[i] = DNA_XOR_TABLE[rule][dna1[i]][dna2[i]]
    
    return result

@cython.boundscheck(False)
@cython.wraparound(False)
def scramble_with_sequence(cnp.ndarray[cnp.uint8_t, ndim=1] flat_arr, 
                          cnp.ndarray[cnp.float64_t, ndim=1] seq):
    """
    1D diziyi kaotik sıralama ile karıştırır.
    
    Parameters:
    - flat_arr: 1D veri
    - seq: Aynı uzunlukta float dizisi (kaotik)
    
    Returns:
    - Scrambled dizi
    """
    cdef cnp.ndarray[cnp.intp_t, ndim=1] order = np.argsort(seq)
    return flat_arr[order]

@cython.boundscheck(False)
@cython.wraparound(False)
def unscramble_with_sequence(cnp.ndarray[cnp.uint8_t, ndim=1] scrambled, 
                            cnp.ndarray[cnp.float64_t, ndim=1] seq):
    """
    Scramble edilmiş diziyi eski haline getirir.
    
    Parameters:
    - scrambled: Scrambled dizi
    - seq: Aynı kaotik dizi
    
    Returns:
    - Orijinal dizi
    """
    cdef cnp.ndarray[cnp.intp_t, ndim=1] order = np.argsort(seq)
    cdef cnp.ndarray[cnp.intp_t, ndim=1] inv = np.empty_like(order)
    
    cdef int i
    for i in range(order.shape[0]):
        inv[order[i]] = i
    
    return scrambled[inv]

@cython.boundscheck(False)
@cython.wraparound(False)
def bytes_to_binary_array(bytes byte_data):
    """
    Bayt verisini 0/1 değerlerinden oluşan NumPy array'e çevirir.
    
    Parameters:
    - byte_data: Dönüştürülecek bayt dizisi
    
    Returns:
    - Binary array
    """
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] byte_arr = np.frombuffer(byte_data, dtype=np.uint8)
    return np.unpackbits(byte_arr).astype(np.uint8)

@cython.boundscheck(False)
@cython.wraparound(False)
def binary_array_to_bytes(cnp.ndarray[cnp.uint8_t, ndim=1] bin_arr):
    """
    Binary array'i (0/1 dizisi) tekrar bayt verisine çevirir.
    
    Parameters:
    - bin_arr: 0/1 dizisi
    
    Returns:
    - Bayt dizisi
    """
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] packed = np.packbits(bin_arr.astype(np.uint8))
    return packed.tobytes()