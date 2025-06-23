import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
from concurrent.futures import ThreadPoolExecutor

# Ana pencereyi oluştur
root = tk.Tk()
root.title("DNA ve RSA ile Görüntü Şifreleme ve Çözme")
root.geometry("400x400")

# Görüntüyü yükleme fonksiyonu
def load_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        global image_path, img_data  # img_data'yi global olarak tanımladık
        image_path = file_path
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)  # Renkli görüntüyü okuma
        img_resized = cv2.resize(img, (300, 300))
        img_data = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)  # BGR'yi RGB'ye çevir
        cv2.imshow("Yüklenen Görüntü", img_resized)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# DNA encoding kuralları tablosu
dna_rules = {
    'A': ['00', '00', '01', '01', '10', '10', '11', '11'],
    'T': ['11', '11', '10', '10', '01', '01', '00', '00'],
    'G': ['01', '10', '00', '11', '00', '11', '01', '10'],
    'C': ['10', '01', '11', '00', '11', '00', '10', '01']
}

def dna_encode(byte_data):
    binary_str = ''.join([format(b, '08b') for b in byte_data])
    dna_encoded = ''
    for i in range(0, len(binary_str), 2):
        pair = binary_str[i:i+2]
        for nucleotide, codes in dna_rules.items():
            if pair in codes:
                dna_encoded += nucleotide
                break
    return dna_encoded

def dna_decode(dna_string):
    binary_str = ''.join([dna_rules[nuc][0] for nuc in dna_string])  # 0. indeksi alıyoruz
    byte_data = bytearray(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
    return byte_data

def xor_encrypt(data, key):
    return bytearray([b ^ key for b in data])

def xor_decrypt(data, key):
    return xor_encrypt(data, key)

# Paralel şifreleme fonksiyonu
def encrypt_channel(channel_data, xor_key):
    # RSA anahtarını her işleme özel olarak oluşturuyoruz
    key = RSA.generate(2048)
    cipher_rsa = PKCS1_OAEP.new(key.publickey())  # Her işlemde yeni RSA anahtarı

    dna_encoded = dna_encode(channel_data)  # DNA ile kodla
    xor_encrypted_data = xor_encrypt(bytearray(dna_encoded, 'utf-8'), xor_key)  # XOR şifrele
    encrypted_channel = []
    for byte in xor_encrypted_data:
        encrypted_chunk = cipher_rsa.encrypt(bytes([byte]))
        encrypted_channel.append(encrypted_chunk)
    return encrypted_channel, key  # Şifreli kanal ve RSA anahtarını döndürüyoruz

# Paralel şifre çözme fonksiyonu
def decrypt_channel(channel_encrypted, xor_key, private_key):
    cipher_rsa = PKCS1_OAEP.new(private_key)
    channel_decrypted = []
    for j in range(0, len(channel_encrypted), 256):
        chunk = channel_encrypted[j:j+256]
        decrypted_chunk = cipher_rsa.decrypt(chunk)
        channel_decrypted.append(decrypted_chunk[0])  # Sadece ilk baytı al
    decrypted_xor_data = xor_decrypt(channel_decrypted, xor_key)
    decrypted_dna_data = decrypted_xor_data.decode('utf-8')
    decoded_channel_data = dna_decode(decrypted_dna_data)
    return np.array(decoded_channel_data, dtype=np.uint8)

# Şifreleme fonksiyonu
def encrypt_image():
    if not image_path:
        messagebox.showerror("Hata", "Lütfen bir resim yükleyin.")
        return

    xor_key = int(xor_key_entry.get()) if xor_key_entry.get() else 123
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)  # Renkli resmi oku
    img_data = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR'yi RGB'ye çevir

    # Her bir renk kanalını şifrele
    encrypted_channels = []
    rsa_keys = []
    with ThreadPoolExecutor() as executor:
        future_to_channel = {
            executor.submit(encrypt_channel, img_data[:, :, i].flatten(), xor_key): i
            for i in range(3)
        }
        for future in future_to_channel:
            encrypted_data, key = future.result()
            encrypted_channels.append(encrypted_data)
            rsa_keys.append(key)  # Anahtarları kaydediyoruz

    # RSA anahtarlarını kaydet
    with open("rsa_private.pem", "wb") as f:
        f.write(rsa_keys[0].export_key())  # Birinci kanalın RSA özel anahtarını kaydediyoruz

    # Şifreli veriyi base64 ile encode et
    encrypted_base64 = base64.b64encode(b''.join([b''.join(channel) for channel in encrypted_channels])).decode('utf-8')

    # Şifreli veriyi kaydet
    with open("sifreli_data.txt", "w") as f:
        f.write(encrypted_base64)

    messagebox.showinfo("Başarılı", "Şifreleme tamamlandı. Anahtarlar ve şifreli veri kaydedildi.")

# Şifre çözme fonksiyonu
def decrypt_image():
    try:
        # Şifreli veriyi oku
        with open("sifreli_data.txt", "r") as f:
            encrypted_base64 = f.read()

        # RSA özel anahtarını oku
        with open("rsa_private.pem", "rb") as f:
            private_key = RSA.import_key(f.read())

    except FileNotFoundError:
        messagebox.showerror("Hata", "Şifreli veriler veya anahtarlar bulunamadı.")
        return

    xor_key = int(xor_key_entry.get()) if xor_key_entry.get() else 123

    # Base64 ile şifreli veriyi çöz
    encrypted_chunks = base64.b64decode(encrypted_base64)

    # 3 kanal için paralel şifre çözme
    chunk_size = len(encrypted_chunks) // 3
    decrypted_channels = []
    with ThreadPoolExecutor() as executor:
        future_to_channel = {
            executor.submit(decrypt_channel, encrypted_chunks[i * chunk_size: (i + 1) * chunk_size], xor_key, private_key): i
            for i in range(3)
        }
        for future in future_to_channel:
            decrypted_channels.append(future.result())

    # Şifre çözülmüş kanalları birleştir
    decrypted_image = np.dstack(decrypted_channels)

    # Görüntüyü kaydet ve göster
    cv2.imwrite("decrypted_image.png", decrypted_image)
    messagebox.showinfo("Başarılı", "Şifre çözme tamamlandı! Görüntü kaydedildi.")
    cv2.imshow("Çözülen Görüntü", decrypted_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# GUI bileşenlerini oluştur
image_path = None
img_data = None  # img_data'yı burada tanımladık

btn_load_image = tk.Button(root, text="Resim Yükle", command=load_image)
btn_load_image.pack(pady=10)

btn_encrypt = tk.Button(root, text="Şifrele", command=encrypt_image)
btn_encrypt.pack(pady=10)

btn_decrypt = tk.Button(root, text="Şifreyi Çöz", command=decrypt_image)
btn_decrypt.pack(pady=10)

label_xor_key = tk.Label(root, text="XOR Anahtarını Girin:")
label_xor_key.pack(pady=5)
xor_key_entry = tk.Entry(root)
xor_key_entry.pack(pady=5)

root.mainloop()
