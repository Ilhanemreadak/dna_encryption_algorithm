import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio
import matplotlib.pyplot as plt
import os
import math


def compute_and_save_histogram(img_path: str, out_path: str):
    """R, G, B kanalları için histogram çizip bar plot olarak kaydeder."""
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"Görüntü bulunamadı: {img_path}")

    # Görüntüyü yükle ve RGB dizisine çevir
    img = Image.open(img_path).convert('RGB')
    arr = np.array(img)
    colors = ('r', 'g', 'b')

    # Bar plot için verileri hesapla
    fig, ax = plt.subplots()
    bins = np.arange(257)  # 256 bins
    for i, col in enumerate(colors):
        channel = arr[:, :, i].ravel()
        hist, _ = np.histogram(channel, bins=bins, range=(0, 255))
        ax.bar(bins[:-1], hist, color=col, alpha=0.3, width=1)

    ax.set_title('Histogram')
    ax.set_xlabel('Pixel değeri')
    ax.set_ylabel('Frekans')

    fig.savefig(out_path)
    plt.close(fig)


def compute_and_save_correlation(img_path: str, out_path: str):
    """Komşu piksel korelasyonunu scatter plot olarak kaydeder."""
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"Görüntü bulunamadı: {img_path}")

    # Grayscale dizisi olarak oku
    img = Image.open(img_path).convert('L')
    arr = np.array(img)
    h, w = arr.shape

    # Komşuluk çiftlerini topla
    pairs = []
    for y in range(h - 1):
        for x in range(w - 1):
            pairs.append((arr[y, x], arr[y, x+1]))
            pairs.append((arr[y, x], arr[y+1, x]))
    data = np.array(pairs)

    # Scatter plot
    fig, ax = plt.subplots()
    ax.scatter(data[:, 0], data[:, 1], s=1, alpha=0.5)
    ax.set_title('Komşu Piksel Korelasyonu')
    ax.set_xlabel('Değer (x)')
    ax.set_ylabel('Değer (y)')

    fig.savefig(out_path)
    plt.close(fig)

def compute_average_rgb_neighbor_correlation(img_path: str) -> float:
    """
    RGB görüntüde her renk kanalı için komşu piksel korelasyonunu hesaplar ve ortalamasını döner.

    Args:
        img_path (str): Görüntü dosyası yolu.

    Returns:
        float: Ortalama RGB komşu korelasyon katsayısı.
    """
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"Görüntü bulunamadı: {img_path}")

    img = Image.open(img_path).convert('RGB')
    arr = np.array(img)
    h, w, _ = arr.shape
    correlations = []

    for c in range(3):  # R, G, B
        x_vals = []
        y_vals = []

        for y in range(h - 1):
            for x in range(w - 1):
                x_vals.append(arr[y, x, c])
                y_vals.append(arr[y, x+1, c])  # sağ komşu
                x_vals.append(arr[y, x, c])
                y_vals.append(arr[y+1, x, c])  # alt komşu

        x_vals = np.array(x_vals)
        y_vals = np.array(y_vals)

        corr = np.corrcoef(x_vals, y_vals)[0, 1]
        correlations.append(corr)

    return round(float(np.mean(correlations)), 5)


def compute_psnr(img1_path: str, img2_path: str) -> str:
    """İki görüntü arasındaki PSNR değerini döner. Sonsuzsa '∞' döner."""
    if not os.path.isfile(img1_path):
        raise FileNotFoundError(f"Girdi görüntüsü bulunamadı: {img1_path}")
    if not os.path.isfile(img2_path):
        raise FileNotFoundError(f"Çıktı görüntüsü bulunamadı: {img2_path}")

    img1 = np.array(Image.open(img1_path).convert('RGB'), dtype=np.float64) / 255.0
    img2 = np.array(Image.open(img2_path).convert('RGB'), dtype=np.float64) / 255.0

    psnr_val = peak_signal_noise_ratio(img1, img2)
    if math.isinf(psnr_val) or math.isnan(psnr_val):
        return "∞"
    return str(round(psnr_val, 2))

def compute_npcr_uaci(img1_path: str, img2_path: str) -> tuple[float, float]:
    """
    İki görüntü arasındaki NPCR ve UACI metriklerini her kanal için ayrı hesaplar ardından ortalamalarını alır ve döner.
    Görseller RGB kanallarında okunur.

    NPCR: Parçalı piksel değişim oranı
    UACI: Ortalama değişim yoğunluğu

    Args:
        img1_path: Birinci (orijinal veya şifrelenmiş) görüntü yolu
        img2_path: Değişiklik uygulanmış görüntü yolu

    Returns:
        npcr (% olarak) ve uaci (% olarak)
    """
    import os
    from PIL import Image
    import numpy as np

    if not os.path.isfile(img1_path):
        raise FileNotFoundError(f"Görüntü bulunamadı: {img1_path}")
    if not os.path.isfile(img2_path):
        raise FileNotFoundError(f"Görüntü bulunamadı: {img2_path}")

    img1 = np.array(Image.open(img1_path).convert('RGB'), dtype=np.uint8)
    img2 = np.array(Image.open(img2_path).convert('RGB'), dtype=np.uint8)

    M, N, C = img1.shape
    uaci_total = 0
    npcr_total = 0

    for ch in range(3):
        c1 = img1[:, :, ch]
        c2 = img2[:, :, ch]
        diff = c1 != c2
        uaci = np.sum(np.abs(c1 - c2)) / (255 * M * N) * 100
        npcr = np.sum(diff) / (M * N) * 100
        uaci_total += uaci
        npcr_total += npcr

    return round(npcr_total / 3, 5), round(uaci_total / 3, 5)

def compute_entropy_rgb(img_path: str) -> float:
    """
    RGB görüntüler için bilgi entropisini hesaplar (her kanalın ayrı entropisinin ortalaması).
    R, G, B kanalları için Shannon entropisi ayrı ayrı hesaplanır.

    Parametre:
        img_path (str): RGB görüntü dosyasının yolu.

    Döndürür:
        float: Ortalama entropi (0-8 arası)
    """
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"Görüntü bulunamadı: {img_path}")

    img = Image.open(img_path).convert('RGB')
    arr = np.array(img)
    entropy_values = []

    for channel in range(3):  # R, G, B
        channel_data = arr[:, :, channel]
        hist, _ = np.histogram(channel_data, bins=256, range=(0, 256), density=True)
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))
        entropy_values.append(entropy)

    avg_entropy = round(np.mean(entropy_values), 5)
    return avg_entropy
