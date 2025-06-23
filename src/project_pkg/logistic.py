import numpy as np

def generate_logistic_sequence(length: int, x0: float = 0.5, r: float = 3.99) -> np.ndarray:
    """
    Logistic map kullanarak kaotik bir dizi üretir.

    Parametreler:
    - length (int): Üretilmesi gereken dizi uzunluğu.
    - x0 (float): Başlangıç değeri, 0 < x0 < 1 (varsayılan 0.5).
    - r (float): Kontrol parametresi, genellikle 3.57 < r ≤ 4.0 (varsayılan 3.99).

    Döndürür:
    - np.ndarray: length boyutunda kaotik değerler içeren float64 dizisi.
    """
    seq = np.zeros(length, dtype=np.float64)
    x = float(x0)
    for i in range(length):
        x = r * x * (1 - x)
        seq[i] = x
    return seq

def generate_three_logistics(length: int, x0_list=None, r_list=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Üç ayrı logistic map dizisi üretir.

    Parametreler:
    - length (int): Her dizinin uzunluğu.
    - x0_list (list|tuple|None): Başlangıç değerleri [x0_1, x0_2, x0_3]. None ise varsayılan kullanılır.
    - r_list (list|tuple|None): Parametre değerleri [r1, r2, r3]. None ise varsayılan kullanılır.

    Döndürür:
    - tuple: (X1, X2, X3) her biri np.ndarray türünde ve length uzunluğunda.
    """
    if x0_list is None:
        x0_list = [0.41, 0.51, 0.61]
    if r_list is None:
        r_list = [3.99, 3.99, 3.99]

    X1 = generate_logistic_sequence(length, x0_list[0], r_list[0])
    X2 = generate_logistic_sequence(length, x0_list[1], r_list[1])
    X3 = generate_logistic_sequence(length, x0_list[2], r_list[2])
    return X1, X2, X3

def mask_chaos(X, key_bytes):
    """
    Kaotik diziyi parola ile maskeleme işlemi yapar.
    
    Parametreler:
    - X (np.ndarray): Kaotik dizi, 0-1 arası değer
    - key_bytes (bytes): Parola ile türetilmiş byte dizisi.
    Döndürür:
    - np.ndarray: Maskeleme uygulanmış kaotik dizi.
    """
    key_arr = np.frombuffer(key_bytes, dtype=np.uint8)
    key_seq = np.resize(key_arr, X.shape)
    return (X + key_seq / 255.0) % 1.0
