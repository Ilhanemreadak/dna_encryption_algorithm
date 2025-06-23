import numpy as np
cimport numpy as cnp
cimport cython
from libc.math cimport fmod

# Ensure numpy arrays are properly initialized
cnp.import_array()

@cython.boundscheck(False)
@cython.wraparound(False)
def generate_logistic_sequence(int length, double x0=0.5, double r=3.99):
    """
    Logistic map kullanarak kaotik bir dizi üretir.
    
    Parameters:
    - length: Üretilmesi gereken dizi uzunluğu
    - x0: Başlangıç değeri, 0 < x0 < 1 (varsayılan 0.5)
    - r: Kontrol parametresi (varsayılan 3.99)
    
    Returns:
    - Kaotik değerler içeren float64 dizisi
    """
    cdef cnp.ndarray[cnp.float64_t, ndim=1] seq = np.zeros(length, dtype=np.float64)
    cdef double x = x0
    cdef int i
    
    for i in range(length):
        x = r * x * (1.0 - x)
        seq[i] = x
    
    return seq

@cython.boundscheck(False)
@cython.wraparound(False)
def generate_three_logistics(int length, x0_list=None, r_list=None):
    """
    Üç ayrı logistic map dizisi üretir.
    
    Parameters:
    - length: Her dizinin uzunluğu
    - x0_list: Başlangıç değerleri [x0_1, x0_2, x0_3]
    - r_list: Parametre değerleri [r1, r2, r3]
    
    Returns:
    - (X1, X2, X3) tuple
    """
    # Varsayılan değerler
    cdef double[3] x0_values
    cdef double[3] r_values
    
    if x0_list is None:
        x0_values[0] = 0.41
        x0_values[1] = 0.51
        x0_values[2] = 0.61
    else:
        x0_values[0] = x0_list[0]
        x0_values[1] = x0_list[1]
        x0_values[2] = x0_list[2]
    
    if r_list is None:
        r_values[0] = 3.99
        r_values[1] = 3.99
        r_values[2] = 3.99
    else:
        r_values[0] = r_list[0]
        r_values[1] = r_list[1]
        r_values[2] = r_list[2]
    
    # Üç dizi oluştur
    cdef cnp.ndarray[cnp.float64_t, ndim=1] X1 = np.zeros(length, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] X2 = np.zeros(length, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] X3 = np.zeros(length, dtype=np.float64)
    
    cdef double x1 = x0_values[0]
    cdef double x2 = x0_values[1] 
    cdef double x3 = x0_values[2]
    cdef int i
    
    for i in range(length):
        x1 = r_values[0] * x1 * (1.0 - x1)
        x2 = r_values[1] * x2 * (1.0 - x2)
        x3 = r_values[2] * x3 * (1.0 - x3)
        
        X1[i] = x1
        X2[i] = x2
        X3[i] = x3
    
    return X1, X2, X3

@cython.boundscheck(False)
@cython.wraparound(False)
def mask_chaos(cnp.ndarray[cnp.float64_t, ndim=1] X, bytes key_bytes):
    """
    Kaotik diziyi parola ile maskeleme işlemi yapar.
    
    Parameters:
    - X: Kaotik dizi, 0-1 arası değer
    - key_bytes: Parola ile türetilmiş byte dizisi
    
    Returns:
    - Maskeleme uygulanmış kaotik dizi
    """
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] key_arr = np.frombuffer(key_bytes, dtype=np.uint8)
    cdef int X_len = X.shape[0]
    cdef int key_len = key_arr.shape[0]
    
    cdef cnp.ndarray[cnp.float64_t, ndim=1] result = np.zeros(X_len, dtype=np.float64)
    cdef double temp_val
    cdef int i
    
    for i in range(X_len):
        # Key dizisini döngüsel olarak kullan
        temp_val = X[i] + (<double>key_arr[i % key_len]) / 255.0
        result[i] = fmod(temp_val, 1.0)
    
    return result