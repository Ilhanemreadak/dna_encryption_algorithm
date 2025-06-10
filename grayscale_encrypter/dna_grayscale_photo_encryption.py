import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import random

# Ana pencereyi oluştur
root = tk.Tk()
root.title("DNA ve RSA ile Görüntü Şifreleme ve Çözme")
root.geometry("500x400")

# Görüntüyü yükleme fonksiyonu
def load_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        global image_path
        image_path = file_path
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        img_resized = cv2.resize(img, (300, 300))
        img_display = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2BGR)
        cv2.imshow("Yüklenen Görüntü", img_display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# DNA kuralları tablosuna göre kodlama (kural 1'den 8'e kadar)
dna_encoding_rules = {
    1: {'A': '00', 'T': '11', 'G': '01', 'C': '10'},
    2: {'A': '00', 'T': '11', 'G': '10', 'C': '01'},
    3: {'A': '01', 'T': '10', 'G': '00', 'C': '11'},
    4: {'A': '01', 'T': '10', 'G': '11', 'C': '00'},
    5: {'A': '10', 'T': '01', 'G': '00', 'C': '11'},
    6: {'A': '10', 'T': '01', 'G': '11', 'C': '00'},
    7: {'A': '11', 'T': '00', 'G': '01', 'C': '10'},
    8: {'A': '11', 'T': '00', 'G': '10', 'C': '01'}
}

# Şifreleme için kullanılacak DNA kuralı
selected_rule = 1
rule = dna_encoding_rules[selected_rule]
reverse_rule = {v: k for k, v in rule.items()}

def dna_encode(byte_data):
    binary_str = ''.join([format(b, '08b') for b in byte_data])
    dna_encoded = ''.join([reverse_rule[binary_str[i:i+2]] for i in range(0, len(binary_str), 2)])
    return dna_encoded

def dna_decode(dna_string):
    binary_str = ''.join([rule[nuc] for nuc in dna_string])
    byte_data = bytearray(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
    return byte_data

def xor_encrypt(data, key):
    return bytearray([b ^ key for b in data])

def xor_decrypt(data, key):
    return xor_encrypt(data, key)

def encrypt_image():
    if not image_path:
        messagebox.showerror("Hata", "Lütfen bir resim yükleyin.")
        return

    xor_key = int(xor_key_entry.get()) if xor_key_entry.get() else 123
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image_data = img.flatten()

    dna_encoded = dna_encode(image_data)
    xor_encrypted_data = xor_encrypt(bytearray(dna_encoded, 'utf-8'), xor_key)

    key = RSA.generate(2048)
    public_key = key.publickey()
    private_key = key

    with open("rsa_private.pem", "wb") as f:
        f.write(private_key.export_key())

    with open("rsa_public.pem", "wb") as f:
        f.write(public_key.export_key())

    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_data = []

    for byte in xor_encrypted_data:
        encrypted_chunk = cipher_rsa.encrypt(bytes([byte]))
        encrypted_data.append(encrypted_chunk)

    encrypted_base64 = base64.b64encode(b''.join(encrypted_data)).decode('utf-8')

    with open("sifreli_data.txt", "w") as f:
        f.write(encrypted_base64)

    messagebox.showinfo("Başarılı", "Şifreleme tamamlandı. Anahtarlar ve şifreli veri kaydedildi.")

def decrypt_image():
    try:
        with open("sifreli_data.txt", "r") as f:
            encrypted_base64 = f.read()

        with open("rsa_private.pem", "rb") as f:
            private_key = RSA.import_key(f.read())

    except FileNotFoundError:
        messagebox.showerror("Hata", "Şifreli veriler veya anahtarlar bulunamadı.")
        return

    try:
        xor_key = int(xor_key_entry.get()) if xor_key_entry.get() else 123
        cipher_rsa = PKCS1_OAEP.new(private_key)

        encrypted_chunks = base64.b64decode(encrypted_base64)
        decrypted_data = []

        for i in range(0, len(encrypted_chunks), 256):
            chunk = encrypted_chunks[i:i+256]
            decrypted_chunk = cipher_rsa.decrypt(chunk)
            decrypted_data.append(decrypted_chunk[0])

        decrypted_data = b''.join(bytes([b]) for b in decrypted_data)
        decrypted_xor_data = xor_decrypt(decrypted_data, xor_key)

        decrypted_dna_data = decrypted_xor_data.decode('utf-8')
        decoded_image_data = dna_decode(decrypted_dna_data)

        image_size = int(np.sqrt(len(decoded_image_data)))
        decrypted_image = np.array(decoded_image_data, dtype=np.uint8).reshape((image_size, image_size))

        cv2.imwrite("decrypted_image.png", decrypted_image)
        messagebox.showinfo("Başarılı", "Şifre çözme tamamlandı! Görüntü kaydedildi.")
        cv2.imshow("Çözülen Görüntü", decrypted_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")

image_path = None

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
