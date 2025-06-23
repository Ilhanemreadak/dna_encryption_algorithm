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
