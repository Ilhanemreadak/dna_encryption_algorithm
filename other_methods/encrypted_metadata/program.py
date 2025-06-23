import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import pickle
import os

# Ana pencereyi oluştur
root = tk.Tk()
root.title("DNA ve RSA ile RGB Görüntü Şifreleme ve Çözme")
root.geometry("600x500")

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

dna_decoding_rules = {} # Dna decoding yapımında işlem tersten olacağı için var olan tabloyu tersten oluşturuyoruz.

for nucleotide, binary_code in rule.items():
    dna_decoding_rules[binary_code] = nucleotide

def dna_encode(byte_data):
    """
    Byte dizisini DNA baz dizisine dönüştürür.
    
    Girdi olarak alınan byte'lar önce 8-bit binary string'e çevrilir,
    ardından her 2 bitlik grup DNA bazlarına (A, T, G, C) eşlenir.
    
    Parametreler:
        byte_data (bytes/bytearray): Şifrelenecek ham veri
        
    Dönüş Değeri:
        str: DNA bazlarından oluşan şifreli dizi (A, T, G, C karakterleri)
        
    Örnek:
        >>> dna_encode(b'AB')
        'GAAG'  # b'AB' = [65,66] = '01000001 01000010' = 01(G),00(A),00(A),10(C)
        
    Notlar:
        - Binary uzunluk tek sayıysa sonuna '0' eklenerek çift yapılır
        - Tanımsız 2-bit gruplar için varsayılan 'A' kullanılır
    """
    binary_str = ''
    for b in byte_data:
        # Her byte'ı 8 bitlik binary stringe çevir
        binary_byte = format(b, '08b')
        # Bu binary stringi ana stringe ekle
        binary_str += binary_byte
        
    # Eğer binary_str uzunluğu 2'nin katı değilse, dolgu ekle
    if len(binary_str) % 2 != 0:
        binary_str += '0'
    dna_encoded = ''
    for i in range(0, len(binary_str), 2):
        bit_pair = binary_str[i:i+2]
        if bit_pair in dna_decoding_rules:
            dna_encoded += dna_decoding_rules[bit_pair]
        else:
            # 2 bit yoksa (son bit tek kalmış olabilir), 'A' ile dolduralım
            dna_encoded += 'A'
    return dna_encoded

def dna_decode(dna_string):
    """
    DNA baz dizisini orijinal byte verisine dönüştürür.
    
    Girdi olarak alınan DNA dizisindeki her baz, 2-bitlik binary değerine çevrilir.
    Elde edilen binary string, 8-bitlik gruplara ayrılarak byte dizisi oluşturulur.
    
    Parametreler:
        dna_string (str): DNA bazlarından oluşan şifreli dizi (A, T, G, C karakterleri)
        
    Dönüş Değeri:
        bytearray: Orijinal byte verisi
        
    Örnek:
        >>> dna_decode('GAAG')
        bytearray(b'AB')  # G(01),A(00),A(00),C(10) = '01000010' = 66 = 'B'
                          # (Not: Örnekte padding nedeniyle sonuç değişebilir)
        
    Notlar:
        - Geçersiz nükleotidler '00' olarak işlenir
        - Binary uzunluk 8'in katı değilse sonuna '0' eklenir
        - DNA kodlama kuralı, global 'rule' sözlüğüne bağlıdır
    """
    binary_str = ''
    for nuc in dna_string:
        if nuc in rule:
            binary_str += rule[nuc]
        else:
            # Eğer nükleotid tanınmıyorsa '00' ekleyelim
            binary_str += '00'
    
    padding = 0
    
    if len(binary_str) % 8 !=0 : # Eğer binary_str'nin uzunluğu 8'in katı değilse
        padding = 8 - (len(binary_str) % 8)
    else:
        padding = 0
    
    binary_str += '0' * padding
    
    byte_data = bytearray()
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        byte_data.append(int(byte, 2))
    
    return byte_data

def xor_encrypt(data, key):
    """
    Veriyi XOR işlemi ile şifreler.
    
    Parametreler:
        data (bytes/bytearray): Şifrelenecek veri
        key (int): 0-255 arası şifreleme anahtarı (1 byte)
        
    Dönüş Değeri:
        bytearray: XOR ile şifrelenmiş veri
        
    Çalışma Mantığı:
        Verinin her byte'ı ile anahtar byte'ı arasında XOR işlemi yapılır
    """
    encrypted_data = bytearray()
    
    for byte in data:
        # Byte ile anahtar arasında XOR işlemi yap
        encrypted_byte = byte ^ key
        encrypted_data.append(encrypted_byte)
    
    return encrypted_data


def xor_decrypt(data, key):
    """
        XOR ile şifrelenmiş veriyi çözer (XOR şifreleme simetrik olduğu için 
        şifreleme ile çözme işlemi aynıdır)
        
        Parametreler:
            data (bytes/bytearray): Çözülecek veri
            key (int): Şifrelemede kullanılan anahtar (1 byte)
            
        Dönüş Değeri:
            bytearray: Çözülmüş orijinal veri
    """
    # XOR şifreleme simetrik olduğundan çözme işlemi de aynıdır
    return xor_encrypt(data, key)

def encrypt_image():
    """
        RGB bir görüntüyü DNA kodlama, XOR şifreleme ve RSA şifreleme adımlarıyla güvenli şekilde şifreler.

        Adımlar:
        - Görüntü boyut bilgilerini (metadata) hazırlar.
        - Her renk kanalı için:
            - DNA kodlama uygular.
            - XOR şifreleme ile gizler.
            - RSA algoritması ile blok bazlı şifreler.
        - Metadata'yı da XOR + RSA ile şifreler.
        - Şifreli kanal verilerini ve metadata'yı 'sifreli_data.bin' dosyasına kaydeder.
        - RSA anahtar çiftini (public ve private) PEM formatında dışa aktarır.

        Parametre gerektirmez, GUI üzerindeki girdilerle çalışır.
    """
    if not 'image_path' in globals() or not image_path:
        messagebox.showerror("Hata", "Lütfen bir resim yükleyin.")
        return

    try:
        xor_key = int(xor_key_entry.get()) if xor_key_entry.get() else 123
        
        # RGB görüntüsünü kanallarına ayırma
        img = original_img
        h, w, c = img.shape
        
        # Metadata'yı şifreleyeceğimiz için önce düz metin olarak hazırlayalım
        metadata_str = f"{h}:{w}:{c}"
        
        # Her renk kanalı için ayrı şifreleme işlemi uygula
        encrypted_channels = []
        
        for channel_idx in range(c):
            channel_data = img[:,:,channel_idx].flatten()
            
            # DNA kodlama
            dna_encoded = dna_encode(channel_data)
            
            # XOR şifreleme
            xor_encrypted = xor_encrypt(bytearray(dna_encoded, 'utf-8'), xor_key)
            
            encrypted_channels.append(xor_encrypted)
        
        # RSA anahtar çifti oluştur
        key = RSA.generate(2048)
        public_key = key.publickey()
        private_key = key

        with open("rsa_private.pem", "wb") as f:
            f.write(private_key.export_key())

        with open("rsa_public.pem", "wb") as f:
            f.write(public_key.export_key())
        
        # RSA şifrelemesi için PKCS1_OAEP şifreleme oluşturucu
        cipher_rsa = PKCS1_OAEP.new(public_key)
        
        # Metadata'yı şifrele
        # Metadata'yı önce bir hash ile karıştırıp, sonra şifreleyelim
        metadata_bytes = metadata_str.encode('utf-8')
        hashed_metadata = bytearray([b ^ (xor_key * 2) for b in metadata_bytes])  # Farklı bir XOR anahtarı kullanarak hash
        encrypted_metadata = cipher_rsa.encrypt(bytes(hashed_metadata))
        
        # Her kanal için RSA şifreleme
        rsa_encrypted_channels = []
        
        for channel_data in encrypted_channels:
            # RSA blok boyutu sınırlı olduğundan, veriyi bloklara bölerek şifrele
            encrypted_blocks = []
            block_size = 190  # RSA 2048 için güvenli blok boyutu
            
            for i in range(0, len(channel_data), block_size):
                block = channel_data[i:i+block_size]
                encrypted_block = cipher_rsa.encrypt(bytes(block))
                encrypted_blocks.append(encrypted_block)
            
            rsa_encrypted_channels.append(encrypted_blocks)
        
        # Tüm şifrelenmiş kanalları ve şifrelenmiş meta verileri pickle ile dosyaya kaydet
        encrypted_data = {
            'encrypted_metadata': encrypted_metadata,
            'channels': rsa_encrypted_channels
        }
        
        with open("sifreli_data.bin", "wb") as f:
            pickle.dump(encrypted_data, f)
        
        # Kullanıcıya başarılı mesajı göster
        messagebox.showinfo("Başarılı", "RGB görüntü şifreleme tamamlandı. Anahtarlar ve şifreli veri kaydedildi.")
    
    except Exception as e:
        messagebox.showerror("Hata", f"Şifreleme sırasında bir hata oluştu: {str(e)}")

def decrypt_image():
    try:
        # Şifreli verileri ve RSA özel anahtarı yükle
        with open("sifreli_data.bin", "rb") as f:
            encrypted_data = pickle.load(f)
        
        with open("rsa_private.pem", "rb") as f:
            private_key = RSA.import_key(f.read())
        
        # XOR anahtarını al
        xor_key = int(xor_key_entry.get()) if xor_key_entry.get() else 123
        
        # RSA şifre çözücü oluştur
        cipher_rsa = PKCS1_OAEP.new(private_key)
        
        # Metadata'yı çöz
        encrypted_metadata = encrypted_data['encrypted_metadata']
        hashed_metadata = cipher_rsa.decrypt(encrypted_metadata)
        metadata_bytes = bytearray([b ^ (xor_key * 2) for b in hashed_metadata])  # XOR ile çöz
        metadata_str = metadata_bytes.decode('utf-8')
        
        # Metadata'yı parse et
        h, w, c = map(int, metadata_str.split(':'))
        
        # Her şifrelenmiş kanalı çöz
        decrypted_channels = []
        
        for encrypted_channel in encrypted_data['channels']:
            # RSA ile şifrelenmiş blokların her birini çöz
            decrypted_data = bytearray()
            
            for encrypted_block in encrypted_channel:
                decrypted_block = cipher_rsa.decrypt(encrypted_block)
                decrypted_data.extend(decrypted_block)
            
            # XOR şifrelemesini çöz
            xor_decrypted = xor_decrypt(decrypted_data, xor_key)
            
            # DNA kodlamasını çöz
            dna_string = xor_decrypted.decode('utf-8', errors='replace')
            channel_bytes = dna_decode(dna_string)
            
            # Kanalı pixel dizisine dönüştür
            channel_array = np.array(channel_bytes, dtype=np.uint8)
            
            # Eğer boyut uyuşmuyorsa, düzelt
            if len(channel_array) < h * w:
                padding = h * w - len(channel_array)
                channel_array = np.pad(channel_array, (0, padding), 'constant')
            elif len(channel_array) > h * w:
                channel_array = channel_array[:h*w]
            
            # Kanalı yeniden şekillendir
            channel_reshaped = channel_array.reshape((h, w))
            decrypted_channels.append(channel_reshaped)
        
        # Tüm kanalları birleştirerek RGB görüntüsü oluştur
        decrypted_image = np.stack(decrypted_channels, axis=2)
        
        # Çözülmüş görüntüyü kaydet ve göster
        cv2.imwrite("decrypted_image.png", decrypted_image)
        
        # Görüntüyü göster
        img_display = cv2.resize(decrypted_image, (400, 400))
        cv2.imshow("Çözülen RGB Görüntü", img_display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        messagebox.showinfo("Başarılı", "RGB görüntünün şifresi çözüldü ve 'decrypted_image.png' olarak kaydedildi.")
    
    except FileNotFoundError:
        messagebox.showerror("Hata", "Gerekli dosyalar bulunamadı. Önce bir görüntüyü şifrelemeniz gerekiyor.")
    
    except Exception as e:
        messagebox.showerror("Hata", f"Şifre çözme sırasında bir hata oluştu: {str(e)}")
        import traceback
        traceback.print_exc()
def change_dna_rule():
    try:
        global selected_rule, rule, dna_decoding_rules
        selected_rule = int(rule_entry.get())
        if 1 <= selected_rule <= 8:
            rule = dna_encoding_rules[selected_rule]
            dna_decoding_rules = {v: k for k, v in rule.items()}
            messagebox.showinfo("Bilgi", f"DNA kodlama kuralı {selected_rule} olarak değiştirildi.")
        else:
            messagebox.showerror("Hata", "DNA kuralı 1 ile 8 arasında olmalıdır.")
    except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.")

# Global değişkenler
image_path = None
original_img = None
img_shape = None

# Görüntülerin dönüşüm aşamalarını gösterme fonksiyonu
def show_transformation_steps():
    if not 'original_img' in globals() or original_img is None:
        messagebox.showerror("Hata", "Lütfen önce bir görüntü yükleyin.")
        return
    
    try:
        # Küçük bir bölüm al (10x10 piksel)
        small_region = original_img[0:10, 0:10].copy()
    
        # Her bir kanal için DNA dönüşümünü göster
        for i, channel_name in enumerate(['Blue', 'Green', 'Red']):
            channel = small_region[:,:,i]
            
            # Bu kanalın binary gösterimi
            binary_str = ''.join([format(pixel, '08b') for pixel in channel.flatten()])
            binary_preview = binary_str[:100] + "..." if len(binary_str) > 100 else binary_str
            
            # DNA kodlanmış hali
            dna_encoded = dna_encode(channel.flatten())
            dna_preview = dna_encoded[:100] + "..." if len(dna_encoded) > 100 else dna_encoded
            
            # Sonuçları bir pencerede göster
            info = f"Kanal: {channel_name}\n\n"
            info += f"Original pixels (10x10 region):\n{channel}\n\n"
            info += f"Binary format (preview):\n{binary_preview}\n\n"  
            info += f"DNA encoded (preview):\n{dna_preview}"
            
            # Bilgiyi ayrı bir pencerede göster
            info_window = tk.Toplevel(root)
            info_window.title(f"{channel_name} Kanal Dönüşüm Aşamaları")
            info_window.geometry("600x400")
            
            text_widget = tk.Text(info_window, wrap=tk.WORD)
            text_widget.insert(tk.END, info)
            text_widget.config(state=tk.DISABLED)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(info_window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
    
    except Exception as e:
        messagebox.showerror("Hata", f"Dönüşüm aşamalarını gösterirken hata: {str(e)}")

# Arayüz elemanları
frame = tk.Frame(root)
frame.pack(pady=10)

btn_load_image = tk.Button(frame, text="Resim Yükle", command=load_image, width=20)
btn_load_image.grid(row=0, column=0, padx=10, pady=5)

btn_show_steps = tk.Button(frame, text="Dönüşüm Aşamalarını Göster", command=show_transformation_steps, width=25)
btn_show_steps.grid(row=0, column=1, padx=10, pady=5)

img_info_label = tk.Label(root, text="Henüz görüntü yüklenmedi.")
img_info_label.pack(pady=5)

# DNA kural seçimi
rule_frame = tk.Frame(root)
rule_frame.pack(pady=10)

rule_label = tk.Label(rule_frame, text="DNA Kodlama Kuralı (1-8):")
rule_label.grid(row=0, column=0, padx=5)

rule_entry = tk.Entry(rule_frame, width=5)
rule_entry.insert(0, "1")  # Varsayılan kural
rule_entry.grid(row=0, column=1, padx=5)

btn_change_rule = tk.Button(rule_frame, text="Kuralı Değiştir", command=change_dna_rule)
btn_change_rule.grid(row=0, column=2, padx=5)

# XOR anahtarı girişi
xor_frame = tk.Frame(root)
xor_frame.pack(pady=10)

xor_label = tk.Label(xor_frame, text="XOR Anahtarı:")
xor_label.grid(row=0, column=0, padx=5)

xor_key_entry = tk.Entry(xor_frame, width=10)
xor_key_entry.insert(0, "123")  # Varsayılan XOR anahtarı
xor_key_entry.grid(row=0, column=1, padx=5)

# Şifreleme ve çözme butonları
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

btn_encrypt = tk.Button(btn_frame, text="Görüntüyü Şifrele", command=encrypt_image, width=20, bg="#4CAF50", fg="white")
btn_encrypt.grid(row=0, column=0, padx=10)

btn_decrypt = tk.Button(btn_frame, text="Şifreyi Çöz", command=decrypt_image, width=20, bg="#2196F3", fg="white")
btn_decrypt.grid(row=0, column=1, padx=10)

# Programı başlat
root.mainloop()