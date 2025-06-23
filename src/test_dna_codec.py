#!/usr/bin/env python3
"""
Bu script orijinal Python kodları ile Cython versiyonlarının
aynı sonuçları verip vermediğini test eder.
"""

import numpy as np
import sys
import os

# Orijinal modülleri import et
sys.path.append('src/project_pkg')
import dna_codec
import logistic
import chaos_utils

# Cython modüllerini import et (derlendikten sonra)
sys.path.append('src/accelerated')
try:
    import dna_codec_cy
    import logistic_cy
    import chaos_utils_cy
    CYTHON_AVAILABLE = True
except ImportError:
    print("Cython modülleri henüz derlenmemiş. 'python setup.py build_ext --inplace' çalıştırın.")
    CYTHON_AVAILABLE = False
    sys.exit(1)

def test_logistic_maps():
    """Logistic map fonksiyonlarını test et"""
    print("=== Logistic Maps Test ===")
    
    length = 1000
    x0, r = 0.5, 3.99
    
    # Orijinal
    seq_orig = logistic.generate_logistic_sequence(length, x0, r)
    
    # Cython
    seq_cy = logistic_cy.generate_logistic_sequence(length, x0, r)
    
    # Karşılaştır
    diff = np.abs(seq_orig - seq_cy).max()
    print(f"Single logistic sequence max difference: {diff}")
    
    # Üç logistic test
    x0_list = [0.41, 0.51, 0.61]
    r_list = [3.99, 3.98, 3.97]
    
    X1_orig, X2_orig, X3_orig = logistic.generate_three_logistics(length, x0_list, r_list)
    X1_cy, X2_cy, X3_cy = logistic_cy.generate_three_logistics(length, x0_list, r_list)
    
    diff1 = np.abs(X1_orig - X1_cy).max()
    diff2 = np.abs(X2_orig - X2_cy).max()
    diff3 = np.abs(X3_orig - X3_cy).max()
    
    print(f"Three logistics differences: X1={diff1}, X2={diff2}, X3={diff3}")
    
    # Mask chaos test
    key_bytes = b"test_key_123456789"
    masked_orig = logistic.mask_chaos(X1_orig, key_bytes)
    masked_cy = logistic_cy.mask_chaos(X1_cy, key_bytes)
    
    diff_mask = np.abs(masked_orig - masked_cy).max()
    print(f"Mask chaos difference: {diff_mask}")
    
    return diff < 1e-15 and diff1 < 1e-15 and diff2 < 1e-15 and diff3 < 1e-15 and diff_mask < 1e-15

def test_dna_codec():
    """DNA codec fonksiyonlarını test et"""
    print("\n=== DNA Codec Test ===")
    
    # Test verisi
    test_bits = np.array([0, 1, 1, 0, 1, 1, 0, 0, 1, 0], dtype=np.uint8)
    rule = 3
    
    # Binary to DNA
    dna_orig = dna_codec.binary_to_dna(test_bits, rule)
    dna_cy = dna_codec_cy.binary_to_dna(test_bits, rule)
    
    # DNA karakterlerini sayısal kodlama ile karşılaştır
    # A=0, T=1, C=2, G=3
    char_to_num = {'A': 0, 'T': 1, 'C': 2, 'G': 3}
    dna_orig_num = np.array([char_to_num[c] for c in dna_orig])
    
    dna_match = np.array_equal(dna_orig_num, dna_cy)
    print(f"Binary to DNA match: {dna_match}")
    
    # DNA to Binary
    bits_orig = dna_codec.dna_to_binary(dna_orig, rule)
    bits_cy = dna_codec_cy.dna_to_binary(dna_cy, rule)
    
    bits_match = np.array_equal(bits_orig, bits_cy)
    print(f"DNA to Binary match: {bits_match}")
    
    # DNA XOR
    dna1 = np.array([0, 1, 2, 3, 0], dtype=np.uint8)  # A, T, C, G, A
    dna2 = np.array([2, 0, 1, 3, 2], dtype=np.uint8)  # C, A, T, G, C
    
    # Orijinal için karakter dizilerine çevir
    num_to_char = {0: 'A', 1: 'T', 2: 'C', 3: 'G'}
    dna1_chars = np.array([num_to_char[n] for n in dna1])
    dna2_chars = np.array([num_to_char[n] for n in dna2])
    
    xor_orig = dna_codec.dna_xor(dna1_chars, dna2_chars, rule)
    xor_cy = dna_codec_cy.dna_xor(dna1, dna2, rule)
    
    xor_orig_num = np.array([char_to_num[c] for c in xor_orig])
    xor_match = np.array_equal(xor_orig_num, xor_cy)
    print(f"DNA XOR match: {xor_match}")
    
    # Scrambling test
    test_data = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=np.uint8)
    chaos_seq = np.array([0.8, 0.2, 0.6, 0.9, 0.3, 0.1, 0.4, 0.5], dtype=np.float32)
    scrambled_orig = dna_codec.scramble_data(test_data, chaos_seq)
    scrambled_cy = dna_codec_cy.scramble_data(test_data, chaos_seq)
    scrambled_match = np.array_equal(scrambled_orig, scrambled_cy)
    print(f"Scrambling match: {scrambled_match}")
    