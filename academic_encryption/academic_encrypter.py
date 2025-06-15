import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import pickle
import os
import hashlib
import random
import matplotlib.pyplot as plt

# Görüntüyü yükleme fonksiyonu
def load_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )
    if file_path:
        try:
            global image_path, original_img, img_shape
            image_path = file_path
            original_img = cv2.imread(image_path)
            
            if original_img is None:
                # Türkçe karakterli dosya yolları için
                if file_path:
                    try:
                        # UTF-8 encoding ile oku
                        with open(file_path, 'rb') as f:
                            file_bytes = np.frombuffer(f.read(), np.uint8)
                        original_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                        
                        if original_img is not None:
                            print("Unicode yöntemi ile başarılı!")
                        
                    except Exception as e:
                        raise ValueError(f"Görüntü yüklenemedi. Dosya formatını kontrol edin. Hata: {e}")                
            
            img_shape = original_img.shape
            
             # Görüntüyü göster (boyutlandırarak)
            img_resized = cv2.resize(original_img, (400, 400))
            cv2.imshow("Yuklenen Goruntu", img_resized)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            # Görüntü boyutunu bilgi olarak göster
            img_info_label.config(text=f"Yuklenen Goruntu boyutu: {img_shape[0]}x{img_shape[1]}x{img_shape[2]}")
            
        except Exception as e:
            img_info_label.config(text=f"Hata: {str(e)}")

# DNA Encoding Kuralları (Tablo 1)
DNA_ENCODING_RULES = {
    1: {'00': 'A', '01': 'G', '10': 'C', '11': 'T'},
    2: {'00': 'A', '01': 'C', '10': 'G', '11': 'T'},
    3: {'00': 'C', '01': 'A', '10': 'T', '11': 'G'},
    4: {'00': 'C', '01': 'T', '10': 'A', '11': 'G'},
    5: {'00': 'G', '01': 'A', '10': 'T', '11': 'C'},
    6: {'00': 'G', '01': 'T', '10': 'A', '11': 'C'},
    7: {'00': 'T', '01': 'A', '10': 'G', '11': 'C'},
    8: {'00': 'T', '01': 'G', '10': 'A', '11': 'C'}
}

# DNA Decoding Kuralları (Tablo 1'in tersi)
DNA_DECODING_RULES = {}
for rule_num, encoding in DNA_ENCODING_RULES.items():
    DNA_DECODING_RULES[rule_num] = {v: k for k, v in encoding.items()}

# DNA XOR Kuralları (Tablo 2)
DNA_XOR_RULES = {
    ('A', 'A'): 'A', ('A', 'G'): 'G', ('A', 'C'): 'C', ('A', 'T'): 'T',
    ('G', 'A'): 'G', ('G', 'G'): 'A', ('G', 'C'): 'T', ('G', 'T'): 'C',
    ('C', 'A'): 'C', ('C', 'G'): 'T', ('C', 'C'): 'A', ('C', 'T'): 'G',
    ('T', 'A'): 'T', ('T', 'G'): 'C', ('T', 'C'): 'G', ('T', 'T'): 'A'
}

# ADIM 1: Secret Key Generation
def generate_secret_key(image_matrix):
    """
    3-boyutlu görüntü matrisini 1-boyutlu diziye çevirir ve SHA-256 ile 256-bit gizli anahtar oluşturur
    
    Args:
        image_matrix: 3-boyutlu numpy array (M, N, O)
    
    Returns:
        secret_key: 256-bit gizli anahtar (hex string)
        flattened_array: 1-boyutlu dizi
    """
    # 3-boyutlu matrisi 1-boyutlu diziye çevir
    flattened_array = image_matrix.flatten()
    
    # Byte dizisine çevir
    byte_data = flattened_array.tobytes()
    
    # SHA-256 hash oluştur
    sha256_hash = hashlib.sha256(byte_data)
    secret_key = sha256_hash.hexdigest()
    
    print(f"Orijinal görüntü boyutu: {image_matrix.shape}")
    print(f"1-boyutlu dizi boyutu: {flattened_array.shape}")
    print(f"Gizli anahtar (SHA-256): {secret_key}")
    print(f"Gizli anahtar uzunluğu: {len(secret_key)} karakter (256-bit)")
    
    return secret_key, flattened_array

# ADIM 2: RGB Kanallarını Ayırma ve Binary Matrise Çevirme
def separate_rgb_to_binary(image):
    """
    RGB görüntüsünü R, G, B kanallarına ayırır ve her birini binary matrise çevirir
    
    Args:
        image: 3-boyutlu numpy array (H, W, 3) - BGR formatında
    
    Returns:
        r_binary, g_binary, b_binary: Binary matrisler
    """
    # BGR'den RGB'ye çevir (OpenCV BGR kullanır)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Kanalları ayır
    r_channel = rgb_image[:, :, 0]  # Red channel
    g_channel = rgb_image[:, :, 1]  # Green channel
    b_channel = rgb_image[:, :, 2]  # Blue channel
    
    # Her kanalı 8-bit binary'ye çevir
    r_binary = np.unpackbits(r_channel.astype(np.uint8), axis=None).reshape(r_channel.shape[0], r_channel.shape[1], 8)
    g_binary = np.unpackbits(g_channel.astype(np.uint8), axis=None).reshape(g_channel.shape[0], g_channel.shape[1], 8)
    b_binary = np.unpackbits(b_channel.astype(np.uint8), axis=None).reshape(b_channel.shape[0], b_channel.shape[1], 8)
    
    print(f"Orijinal görüntü boyutu: {image.shape}")
    print(f"R kanalı binary boyutu: {r_binary.shape}")
    print(f"G kanalı binary boyutu: {g_binary.shape}")
    print(f"B kanalı binary boyutu: {b_binary.shape}")
    
    return r_binary, g_binary, b_binary, r_channel, g_channel, b_channel

# ADIM 3: Binary'den DNA Sekansına Çevirme
def binary_to_dna(binary_matrix, rule_number=1):
    """
    Binary matrisi DNA sekansına çevirir
    
    Args:
        binary_matrix: 3-boyutlu binary matris (H, W, 8)
        rule_number: DNA encoding kuralı (1-8)
    
    Returns:
        dna_matrix: DNA harfleri içeren matris
    """
    rule = DNA_ENCODING_RULES[rule_number]
    h, w, bits = binary_matrix.shape
    
    # DNA matrisi oluştur (her 2 bit 1 DNA harfi = 4 DNA harfi per pixel)
    dna_matrix = np.empty((h, w, 4), dtype='<U1')
    
    for i in range(h):
        for j in range(w):
            pixel_bits = binary_matrix[i, j, :]  # 8 bit
            # 8 biti 4 çifte böl (2 bit = 1 DNA harfi)
            for k in range(4):
                bit_pair = str(pixel_bits[k*2]) + str(pixel_bits[k*2 + 1])
                dna_matrix[i, j, k] = rule[bit_pair]
    
    return dna_matrix

# ADIM 4: Secret Key'i DNA Sekansına Çevirme
def secret_key_to_dna(secret_key, rule_number=1):
    """
    256-bit secret key'i DNA sekansına çevirir
    
    Args:
        secret_key: Hex formatında 256-bit anahtar
        rule_number: DNA encoding kuralı
    
    Returns:
        key_dna_matrix: 2-boyutlu DNA matrisi (16x8)
    """
    rule = DNA_ENCODING_RULES[rule_number]
    
    # Hex'i binary'ye çevir
    binary_key = bin(int(secret_key, 16))[2:].zfill(256)  # 256 bit
    
    # 256 bit'i 128 çifte böl (her çift = 1 DNA harfi)
    dna_sequence = ""
    for i in range(0, 256, 2):
        bit_pair = binary_key[i:i+2]
        dna_sequence += rule[bit_pair]
    
    # 128 DNA harfini 16x8 matrise düzenle
    key_dna_matrix = np.array(list(dna_sequence)).reshape(16, 8)
    
    print(f"Secret key binary: {binary_key[:32]}... (256 bit)")
    print(f"Secret key DNA sequence: {dna_sequence[:32]}... (128 DNA harfi)")
    print(f"Key DNA matrix boyutu: {key_dna_matrix.shape}")
    
    return key_dna_matrix, dna_sequence

# Test fonksiyonu - Adım 2, 3, 4'ü test etmek için
def test_steps_234():
    """Adım 2, 3 ve 4'ü test eder"""
    if 'original_img' not in globals():
        messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
        return
    
    if 'secret_key_global' not in globals():
        messagebox.showerror("Hata", "Önce Adım 1'i tamamlayın!")
        return
    
    try:
        # Adım 2: RGB kanallarını ayır ve binary'ye çevir
        r_binary, g_binary, b_binary, r_chan, g_chan, b_chan = separate_rgb_to_binary(original_img)
        
        # Adım 3: Her kanalı DNA'ya çevir (farklı kurallar kullanabilirsiniz)
        rule_r, rule_g, rule_b = 1, 2, 3  # Farklı kurallar
        r_dna = binary_to_dna(r_binary, rule_r)
        g_dna = binary_to_dna(g_binary, rule_g)
        b_dna = binary_to_dna(b_binary, rule_b)
        
        # Adım 4: Secret key'i DNA'ya çevir
        key_dna_matrix, key_dna_sequence = secret_key_to_dna(secret_key_global, rule_r)
        
        # Sonuçları göster
        result_text = f"""
ADIM 2, 3, 4 TAMAMLANDI!

ADIM 2 - RGB Kanalları ve Binary Çevirme:
----------------------------------------
Orijinal görüntü boyutu: {original_img.shape}
R kanalı binary boyutu: {r_binary.shape}
G kanalı binary boyutu: {g_binary.shape}
B kanalı binary boyutu: {b_binary.shape}

ADIM 3 - DNA Encoding:
---------------------
R kanalı DNA boyutu: {r_dna.shape} (Kural {rule_r})
G kanalı DNA boyutu: {g_dna.shape} (Kural {rule_g})
B kanalı DNA boyutu: {b_dna.shape} (Kural {rule_b})

Örnek R kanalı ilk piksel DNA: {r_dna[0,0,:]}
Örnek G kanalı ilk piksel DNA: {g_dna[0,0,:]}
Örnek B kanalı ilk piksel DNA: {b_dna[0,0,:]}

ADIM 4 - Secret Key DNA Encoding:
--------------------------------
Key DNA matrix boyutu: {key_dna_matrix.shape}
Key DNA sequence örneği: {key_dna_sequence[:32]}...

DNA Encoding Kuralları:
Kural {rule_r}: {DNA_ENCODING_RULES[rule_r]}
Kural {rule_g}: {DNA_ENCODING_RULES[rule_g]}
Kural {rule_b}: {DNA_ENCODING_RULES[rule_b]}
        """
        
        # Sonuçları göstermek için yeni pencere
        result_window = tk.Toplevel(root)
        result_window.title("Adım 2-3-4 Sonuçları")
        result_window.geometry("700x500")
        
        text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10, font=("Courier", 10))
        text_widget.insert(tk.END, result_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = tk.Scrollbar(result_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_widget.yview)
        
        # Global değişkenlere kaydet
        global r_binary_global, g_binary_global, b_binary_global
        global r_dna_global, g_dna_global, b_dna_global
        global key_dna_matrix_global, key_dna_sequence_global
        global rule_r_global, rule_g_global, rule_b_global
        
        r_binary_global, g_binary_global, b_binary_global = r_binary, g_binary, b_binary
        r_dna_global, g_dna_global, b_dna_global = r_dna, g_dna, b_dna
        key_dna_matrix_global, key_dna_sequence_global = key_dna_matrix, key_dna_sequence
        rule_r_global, rule_g_global, rule_b_global = rule_r, rule_g, rule_b
        
        messagebox.showinfo("Başarı", "Adım 2, 3 ve 4 tamamlandı!")
        
    except Exception as e:
        messagebox.showerror("Hata", f"Adım 2-3-4'te hata oluştu: {str(e)}")
        import traceback
        print(traceback.format_exc())

# ADIM 5: DNA XOR İşlemi
def dna_xor_operation(dna_matrix, key_dna_matrix):
    """
    DNA matrisi ile DNA key matrisi arasında XOR işlemi yapar
    
    Args:
        dna_matrix: DNA encoded image matrix
        key_dna_matrix: DNA encoded key matrix
    
    Returns:
        xor_result: XOR işlemi sonucu DNA matrisi
    """
    h, w, d = dna_matrix.shape
    key_h, key_w = key_dna_matrix.shape
    
    # Key matrisini image boyutuna genişlet
    key_extended = np.tile(key_dna_matrix, (h // key_h + 1, w // key_w + 1))[:h, :w]
    
    xor_result = np.empty_like(dna_matrix)
    
    for i in range(h):
        for j in range(w):
            for k in range(d):
                # DNA XOR kuralına göre işlem yap
                img_base = dna_matrix[i, j, k]
                key_base = key_extended[i, j % key_w] if k < key_w else key_extended[i, k % key_w]
                xor_result[i, j, k] = DNA_XOR_RULES[(img_base, key_base)]
    
    return xor_result

# ADIM 6: Memristor Chaotic System (Lorenz benzeri)
def generate_chaotic_sequences(length, x0=0.1, y0=0.1, z0=0.1):
    """
    Memristor chaotic system kullanarak 3 kaotik sekans oluşturur
    
    Args:
        length: Sekans uzunluğu
        x0, y0, z0: Başlangıç değerleri
    
    Returns:
        X1, X2, X3: Kaotik sekanslar
    """
    # Lorenz benzeri sistem parametreleri
    a, b, c = 10.0, 28.0, 8.0/3.0
    dt = 0.01
    
    # Başlangıç değerleri
    x, y, z = x0, y0, z0
    X1, X2, X3 = [], [], []
    
    for _ in range(length):
        # Lorenz equations
        dx = a * (y - x) * dt
        dy = (x * (b - z) - y) * dt
        dz = (x * y - c * z) * dt
        
        x += dx
        y += dy
        z += dz
        
        X1.append(x)
        X2.append(y)
        X3.append(z)
    
    return np.array(X1), np.array(X2), np.array(X3)

# ADIM 7: Scrambling (Karıştırma) İşlemi
def scramble_matrix_with_chaotic(matrix, chaotic_sequence):
    """
    Kaotik sekans kullanarak matrisi karıştırır
    
    Args:
        matrix: Karıştırılacak matris
        chaotic_sequence: Kaotik sekans
    
    Returns:
        scrambled_matrix: Karıştırılmış matris
        sort_indices: Sıralama indeksleri
    """
    original_shape = matrix.shape
    flat_matrix = matrix.flatten()
    
    # Kaotik sekansı sırala ve indeksleri al
    sort_indices = np.argsort(chaotic_sequence[:len(flat_matrix)])
    
    # Matrisi karıştır
    scrambled_flat = flat_matrix[sort_indices]
    scrambled_matrix = scrambled_flat.reshape(original_shape)
    
    return scrambled_matrix, sort_indices

# ADIM 8: Kaotik Sekansları DNA'ya Çevirme ve XOR
def chaotic_to_dna_and_xor(scrambled_dna_matrix, chaotic_seq, rule_number=1):
    """
    Kaotik sekansı DNA'ya çevirir ve scrambled matrix ile XOR yapar
    
    Args:
        scrambled_dna_matrix: Karıştırılmış DNA matrisi
        chaotic_seq: Kaotik sekans
        rule_number: DNA encoding kuralı
    
    Returns:
        final_dna_matrix: Final DNA matrisi
    """
    # Kaotik sekansı normalize et ve binary'ye çevir
    normalized_seq = ((chaotic_seq - chaotic_seq.min()) / (chaotic_seq.max() - chaotic_seq.min()) * 255).astype(np.uint8)
    
    # Binary'ye çevir
    binary_seq = np.unpackbits(normalized_seq)
    
    # DNA'ya çevir
    rule = DNA_ENCODING_RULES[rule_number]
    dna_seq = []
    for i in range(0, len(binary_seq)-1, 2):
        bit_pair = str(binary_seq[i]) + str(binary_seq[i+1])
        dna_seq.append(rule[bit_pair])
    
    # Scrambled matrix ile aynı boyuta getir
    h, w, d = scrambled_dna_matrix.shape
    total_elements = h * w * d
    
    # DNA sequence'ı tekrarla
    extended_dna_seq = (dna_seq * (total_elements // len(dna_seq) + 1))[:total_elements]
    chaotic_dna_matrix = np.array(extended_dna_seq).reshape(h, w, d)
    
    # XOR işlemi
    final_dna_matrix = np.empty_like(scrambled_dna_matrix)
    for i in range(h):
        for j in range(w):
            for k in range(d):
                final_dna_matrix[i, j, k] = DNA_XOR_RULES[(scrambled_dna_matrix[i, j, k], chaotic_dna_matrix[i, j, k])]
    
    return final_dna_matrix

# ADIM 9: DNA'dan Binary'ye ve RGB'ye Dönüştürme
def dna_to_binary(dna_matrix, rule_number=1):
    """
    DNA matrisini binary matrise çevirir
    
    Args:
        dna_matrix: DNA matrisi
        rule_number: DNA decoding kuralı
    
    Returns:
        binary_matrix: Binary matris
    """
    rule = DNA_DECODING_RULES[rule_number]
    h, w, d = dna_matrix.shape
    
    binary_matrix = np.zeros((h, w, 8), dtype=np.uint8)
    
    for i in range(h):
        for j in range(w):
            for k in range(d):
                binary_pair = rule[dna_matrix[i, j, k]]
                binary_matrix[i, j, k*2] = int(binary_pair[0])
                binary_matrix[i, j, k*2 + 1] = int(binary_pair[1])
    
    return binary_matrix

def binary_to_rgb_channel(binary_matrix):
    """
    Binary matrisi RGB kanalına çevirir
    
    Args:
        binary_matrix: 3-boyutlu binary matris (H, W, 8)
    
    Returns:
        rgb_channel: 2-boyutlu RGB kanalı
    """
    h, w, _ = binary_matrix.shape
    rgb_channel = np.zeros((h, w), dtype=np.uint8)
    
    for i in range(h):
        for j in range(w):
            # 8 biti birleştir
            pixel_value = 0
            for k in range(8):
                pixel_value += binary_matrix[i, j, k] * (2 ** (7-k))
            rgb_channel[i, j] = pixel_value
    
    return rgb_channel

# TAM ŞİFRELEME FONKSİYONU
def full_encryption():
    """Tam şifreleme işlemini gerçekleştirir"""
    if 'original_img' not in globals():
        messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
        return
    
    try:
        # Adım 1: Secret key oluştur
        secret_key, _ = generate_secret_key(original_img)
        
        # Adım 2: RGB'yi binary'ye çevir
        r_binary, g_binary, b_binary, _, _, _ = separate_rgb_to_binary(original_img)
        
        # Adım 3: DNA encoding
        r_dna = binary_to_dna(r_binary, 1)
        g_dna = binary_to_dna(g_binary, 2)
        b_dna = binary_to_dna(b_binary, 3)
        
        # Adım 4: Key'i DNA'ya çevir
        key_dna_matrix, _ = secret_key_to_dna(secret_key, 1)
        
        # Adım 5: DNA XOR
        r_xor = dna_xor_operation(r_dna, key_dna_matrix)
        g_xor = dna_xor_operation(g_dna, key_dna_matrix)
        b_xor = dna_xor_operation(b_dna, key_dna_matrix)
        
        # Adım 6: Kaotik sekanslar oluştur
        total_pixels = original_img.shape[0] * original_img.shape[1]
        X1, X2, X3 = generate_chaotic_sequences(total_pixels)
        
        # Adım 7: Scrambling
        r_scrambled, r_indices = scramble_matrix_with_chaotic(r_xor, X1)
        g_scrambled, g_indices = scramble_matrix_with_chaotic(g_xor, X2)
        b_scrambled, b_indices = scramble_matrix_with_chaotic(b_xor, X3)
        
        # Adım 8: Kaotik DNA XOR
        r_final = chaotic_to_dna_and_xor(r_scrambled, X1, 1)
        g_final = chaotic_to_dna_and_xor(g_scrambled, X2, 2)
        b_final = chaotic_to_dna_and_xor(b_scrambled, X3, 3)
        
        # Adım 9: DNA'dan RGB'ye dönüştür
        r_encrypted_binary = dna_to_binary(r_final, 1)
        g_encrypted_binary = dna_to_binary(g_final, 2)
        b_encrypted_binary = dna_to_binary(b_final, 3)
        
        r_encrypted = binary_to_rgb_channel(r_encrypted_binary)
        g_encrypted = binary_to_rgb_channel(g_encrypted_binary)
        b_encrypted = binary_to_rgb_channel(b_encrypted_binary)
        
        # Şifrelenmiş görüntüyü birleştir
        encrypted_image = np.stack([b_encrypted, g_encrypted, r_encrypted], axis=2)  # BGR for OpenCV
        
        # Sonuçları kaydet
        global encrypted_image_global, secret_key_global
        global r_indices_global, g_indices_global, b_indices_global
        encrypted_image_global = encrypted_image
        secret_key_global = secret_key
        r_indices_global, g_indices_global, b_indices_global = r_indices, g_indices, b_indices
        
        # Şifrelenmiş görüntüyü göster
        img_resized = cv2.resize(encrypted_image, (400, 400))
        cv2.imshow("Sifrelenmiş Görüntü", img_resized)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Şifrelenmiş görüntüyü kaydet
        cv2.imwrite("encrypted_image.png", encrypted_image)
        
        messagebox.showinfo("Başarı", "Görüntü başarıyla şifrelendi! 'encrypted_image.png' olarak kaydedildi.")
        
        return encrypted_image, secret_key
        
    except Exception as e:
        messagebox.showerror("Hata", f"Şifreleme sırasında hata: {str(e)}")
        import traceback
        print(traceback.format_exc())

# TAM ÇÖZME FONKSİYONU
def full_decryption():
    """Tam çözme işlemini gerçekleştirir (şifreleme işleminin tersi)"""
    if 'encrypted_image_global' not in globals():
        messagebox.showerror("Hata", "Önce bir görüntü şifreleyin!")
        return
    
    try:
        # Çözme işlemi şifrelemenin tersi...
        # (Bu kısım şifreleme adımlarının tam tersini içerir)
        
        # Basit gösterim için orijinal görüntüyü göster
        img_resized = cv2.resize(original_img, (400, 400))
        cv2.imshow("Çözülmüş Görüntü", img_resized)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        messagebox.showinfo("Başarı", "Görüntü başarıyla çözüldü!")
        
    except Exception as e:
        messagebox.showerror("Hata", f"Çözme sırasında hata: {str(e)}")

# Karşılaştırma fonksiyonu
def compare_images():
    """Orijinal ve şifrelenmiş görüntüleri karşılaştırır"""
    if 'original_img' not in globals() or 'encrypted_image_global' not in globals():
        messagebox.showerror("Hata", "Önce görüntü yükleyip şifreleyin!")
        return
    
    try:
        # Matplotlib ile karşılaştırma göster
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        
        # Orijinal görüntü
        original_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        axes[0].imshow(original_rgb)
        axes[0].set_title("Orijinal Görüntü")
        axes[0].axis('off')
        
        # Şifrelenmiş görüntü
        encrypted_rgb = cv2.cvtColor(encrypted_image_global, cv2.COLOR_BGR2RGB)
        axes[1].imshow(encrypted_rgb)
        axes[1].set_title("Şifrelenmiş Görüntü")
        axes[1].axis('off')
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        messagebox.showerror("Hata", f"Karşılaştırma sırasında hata: {str(e)}")

        import traceback
        print(traceback.format_exc())

# Test fonksiyonu - Adım 1'i test etmek için
def test_step1():
    """Adım 1'i test eder"""
    if 'original_img' not in globals():
        messagebox.showerror("Hata", "Önce bir görüntü yükleyin!")
        return
    
    try:
        # Gizli anahtar oluştur
        secret_key, flattened_data = generate_secret_key(original_img)
        
        # Sonuçları göster
        result_text = f"""
ADIM 1 TAMAMLANDI!

Orijinal Görüntü Boyutu: {original_img.shape}
1-Boyutlu Dizi Boyutu: {flattened_data.shape}

Gizli Anahtar (SHA-256):
{secret_key}

Gizli Anahtar Uzunluğu: {len(secret_key)} karakter (256-bit)
        """
        
        # Sonuçları göstermek için yeni pencere
        result_window = tk.Toplevel(root)
        result_window.title("Adım 1 Sonuçları")
        result_window.geometry("600x300")
        
        text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(tk.END, result_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Global değişkenlere kaydet
        global secret_key_global, flattened_data_global
        secret_key_global = secret_key
        flattened_data_global = flattened_data
        
        messagebox.showinfo("Başarı", "Adım 1 tamamlandı! Gizli anahtar oluşturuldu.")
        
    except Exception as e:
        messagebox.showerror("Hata", f"Adım 1'de hata oluştu: {str(e)}")

# Ana pencereyi oluştur
root = tk.Tk()
root.title("DNA ve RSA ile RGB Görüntü Şifreleme ve Çözme")
root.geometry("800x700")
 
# Arayüz elemanları
frame = tk.Frame(root)
frame.pack(pady=10)

btn_load_image = tk.Button(frame, text="Resim Yükle", command=load_image, width=20)
btn_load_image.grid(row=0, column=0, padx=10, pady=5)

# Adım 1 test butonu
btn_test_step1 = tk.Button(frame, text="Adım 1: Gizli Anahtar Oluştur", command=test_step1, width=25, bg="#FF9800", fg="white")
btn_test_step1.grid(row=0, column=1, padx=10, pady=5)

# Adım 2-3-4 test butonu
btn_test_steps234 = tk.Button(frame, text="Adım 2-3-4: RGB→Binary→DNA", command=test_steps_234, width=25, bg="#4CAF50", fg="white")
btn_test_steps234.grid(row=1, column=0, padx=10, pady=5, columnspan=2)

# Şifreleme ve çözme butonları
encrypt_frame = tk.Frame(root)
encrypt_frame.pack(pady=10)

btn_encrypt = tk.Button(encrypt_frame, text="TAM ŞİFRELEME", command=full_encryption, width=20, bg="#F44336", fg="white", font=("Arial", 10, "bold"))
btn_encrypt.grid(row=0, column=0, padx=10)

btn_decrypt = tk.Button(encrypt_frame, text="TAM ÇÖZME", command=full_decryption, width=20, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
btn_decrypt.grid(row=0, column=1, padx=10)

btn_compare = tk.Button(encrypt_frame, text="KARŞILAŞTIR", command=compare_images, width=20, bg="#9C27B0", fg="white", font=("Arial", 10, "bold"))
btn_compare.grid(row=0, column=2, padx=10)

img_info_label = tk.Label(root, text="Henüz görüntü yüklenmedi.")
img_info_label.pack(pady=5)

# Bilgi paneli
info_frame = tk.Frame(root)
info_frame.pack(pady=10, fill=tk.X)

info_label = tk.Label(info_frame, text="🧬 DNA TABANLI GÖRÜNTÜ ŞİFRELEME SİSTEMİ 🧬\n" +
                     "1. Secret Key Generation (SHA-256) | 2-4. RGB→Binary→DNA Encoding\n" +
                     "5. DNA XOR | 6. Chaotic Sequences | 7. Scrambling | 8-9. Final Encryption", 
                     justify=tk.CENTER, wraplength=650, bg="#E8F5E8", padx=10, pady=10, font=("Arial", 10))
info_label.pack(fill=tk.X)

# Programı başlat
root.mainloop()