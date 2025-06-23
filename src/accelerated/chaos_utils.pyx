import numpy as np
cimport numpy as cnp
cimport cython
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy

# Import from the Cython version of dna_codec
from .dna_codec_cy import binary_to_dna, dna_xor

# Ensure numpy arrays are properly initialized
cnp.import_array()

@cython.boundscheck(False)
@cython.wraparound(False)
def chaos_xor(cnp.ndarray[cnp.uint8_t, ndim=1] prev, 
              cnp.ndarray[cnp.float64_t, ndim=1] X, 
              int dna_rule):
    """
    Kaotik float dizisi X'i DNA tabanlı bir stream'e çevirip
    prev (DNA dizisi) ile XOR'lar.
    
    Parameters:
    - prev: DNA dizisi (uint8 olarak kodlanmış: A=0, T=1, C=2, G=3)
    - X: Kaotik float dizisi (0.0-1.0 arası)
    - dna_rule: DNA kodlama kuralı (1-8)
    
    Returns:
    - DNA XOR sonucu
    """
    cdef int i
    cdef int X_len = X.shape[0]
    cdef int prev_len = prev.shape[0]
    
    # 1) X'i 0–255 aralığına indir
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] X_uint8 = np.zeros(X_len, dtype=np.uint8)
    for i in range(X_len):
        X_uint8[i] = <cnp.uint8_t>(X[i] * 255.0)
    
    # 2) Bitlere dönüştür
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] bits = np.unpackbits(X_uint8)
    
    # 3) DNA'ya çevir
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] stream = binary_to_dna(bits, dna_rule)
    
    # 4) prev boyutuna resize et
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] resized_stream = np.resize(stream, prev_len)
    
    # 5) DNA XOR'u uygula
    return dna_xor(prev, resized_stream, dna_rule)