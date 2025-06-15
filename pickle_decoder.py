import pickle

# Dosya yolunu belirt
file_path = "sifreli_karma_data.bin"

# Pickle içeriğini yükle
with open(file_path, "rb") as f:
    data = pickle.load(f)

# 'encrypted_metadata' içeriğini al
metadata = data.get("encrypted_metadata")

# İçeriği yazdır
print("Türü:", type(metadata))
if isinstance(metadata, dict):
    print("Anahtarlar:", list(metadata.keys()))
    for key, value in metadata.items():
        print(f"{key}: {value}")
else:
    print("İçerik:", metadata)
