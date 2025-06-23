def logistic_map(x0: float, r: float, size: int) -> list:
    """
    Logistic map algoritması ile kaotik sayı dizisi üretir.

    Parametreler:
    - x0 (float): Başlangıç değeri (0 < x0 < 1)
    - r (float): Kaos parametresi (3.57 < r < 4)
    - size (int): Üretilecek sayı adedi

    Döndürür:
    - list: 0–255 arası tamsayı dizisi
    """
    x = x0
    return [int((x := r * x * (1 - x)) * 256) % 256 for _ in range(size)]