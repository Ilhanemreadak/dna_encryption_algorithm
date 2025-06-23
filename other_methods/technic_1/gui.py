import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import pickle
import os
from datetime import datetime
from encryption import encrypt_image_data
from decryption import decrypt_image_data

def load_image():
    """
    Kullanıcının seçtiği görüntüyü yükler ve global olarak saklar.
    """
    global image_path, original_img, img_shape
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")])
    if file_path:
        image_path = file_path
        original_img = cv2.imread(file_path)
        if original_img is None:
            with open(file_path, 'rb') as f:
                file_bytes = np.frombuffer(f.read(), np.uint8)
            original_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        img_shape = original_img.shape
        resized = cv2.resize(original_img, (400, 400))
        cv2.imshow("Yüklenen Görüntü", resized)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        img_info_label.config(text=f"Görüntü boyutu: {img_shape}")

def encrypt():
    """
    Yüklü görüntüyü şifreler ve zaman damgalı klasöre kaydeder.
    """
    if original_img is None:
        messagebox.showerror("Hata", "Önce bir görüntü yükleyin.")
        return
    try:
        img_data = original_img.flatten()
        result = encrypt_image_data(img_data, original_img.shape)

        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_folder = os.path.join(current_dir, "encryptions")
        os.makedirs(root_folder, exist_ok=True)
        enc_folder = os.path.join(root_folder, f"encryption_{timestamp}")
        os.makedirs(enc_folder, exist_ok=True)

        with open(os.path.join(enc_folder, f"encrypted_{timestamp}.bin"), "wb") as f:
            pickle.dump({
                'encrypted_data': result['encrypted_data'],
                'encrypted_metadata': result['encrypted_metadata']
            }, f)
        with open(os.path.join(enc_folder, f"private_{timestamp}.pem"), "wb") as f:
            f.write(result['rsa_private'])
        with open(os.path.join(enc_folder, f"public_{timestamp}.pem"), "wb") as f:
            f.write(result['rsa_public'])

        messagebox.showinfo("Başarılı", f"Şifreleme tamamlandı ve {enc_folder} klasörüne kaydedildi.")
    except Exception as e:
        messagebox.showerror("Hata", str(e))

def decrypt():
    """
    Kullanıcının seçtiği dosyaları kullanarak şifre çözme işlemini yapar.
    """
    try:
        enc_file = filedialog.askopenfilename(title="Şifreli Veriyi Seç", filetypes=[("Binary Files", "*.bin")])
        key_file = filedialog.askopenfilename(title="RSA Özel Anahtarı Seç", filetypes=[("PEM Files", "*.pem")])

        if not enc_file or not key_file:
            messagebox.showwarning("Uyarı", "Lütfen hem .bin dosyasını hem de .pem anahtarını seçin.")
            return

        with open(enc_file, "rb") as f:
            data = pickle.load(f)
        with open(key_file, "rb") as f:
            rsa_priv = f.read()

        decrypted, shape = decrypt_image_data(
            data['encrypted_data'], data['encrypted_metadata'], rsa_priv
        )
        img = np.frombuffer(decrypted, dtype=np.uint8).reshape(shape)
        cv2.imshow("Çözülen Görüntü", cv2.resize(img, (400, 400)))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        messagebox.showinfo("Başarılı", "Görüntü başarıyla geri yüklendi.")
    except Exception as e:
        messagebox.showerror("Hata", str(e))

# Uygulama penceresi
root = tk.Tk()
root.title("Görüntü Şifreleme Arayüzü")
root.geometry("600x400")

frame = tk.Frame(root)
frame.pack(pady=20)

btn_load = tk.Button(frame, text="Resim Yükle", command=load_image, width=20)
btn_load.grid(row=0, column=0, padx=10)

btn_encrypt = tk.Button(frame, text="Şifrele", command=encrypt, width=20, bg="#4CAF50", fg="white")
btn_encrypt.grid(row=0, column=1, padx=10)

btn_decrypt = tk.Button(frame, text="Şifreyi Çöz", command=decrypt, width=20, bg="#2196F3", fg="white")
btn_decrypt.grid(row=0, column=2, padx=10)

img_info_label = tk.Label(root, text="Henüz bir görüntü yüklenmedi.")
img_info_label.pack(pady=10)

# Global değişkenler
global image_path, original_img, img_shape
image_path = None
original_img = None
img_shape = None

root.mainloop()