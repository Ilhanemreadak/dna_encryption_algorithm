import numpy as np
from src.accelerated.dna_codec import binary_to_dna, dna_xor


def chaos_xor(prev: np.ndarray, X: np.ndarray, dna_rule: int) -> np.ndarray:
    """
    Kaotik float dizisi X’i DNA tabanlı bir stream’e çevirip
    prev (DNA dizisi) ile XOR’lar.
    """
    # 1) X’i 0–255 aralığına indir, bitlere dönüştür
    bits = np.unpackbits((X * 255).astype(np.uint8))
    # 2) Bu bitleri DNA’ya çevir, prev boyutuna resize et
    stream = np.resize(binary_to_dna(bits, rule=dna_rule), prev.shape)
    # 3) DNA XOR’u uygula
    return dna_xor(prev, stream, rule=dna_rule)
