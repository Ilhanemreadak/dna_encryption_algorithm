import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio
import matplotlib.pyplot as plt
import os
import math


def compute_and_save_histogram(
        img_path: str,
        out_path: str,
        mode: str = "auto",            # ["auto", "log", "clip", "pdf"]
        clip_pct: float = 99.5         # mode=="clip" ise üst % eşiği
):
    """
        R, G, B kanalları için histogram çizip bar plot olarak kaydeder.
        Histogramı kaydederken aykırı değerlerden kaynaklanan ölçek sorunlarını önler.
        mode:
        • "auto" -> medyan / max oranına bakıp 'log' veya 'clip' seçer
        • "log"  -> log-ölçekli y-ekseni
        • "clip" -> üst clip_pct yüzdesini keser
        • "pdf"  -> normalize edilmiş yoğunluk (probability mass)
    """
    try:
        if not os.path.isfile(img_path):
            raise FileNotFoundError(img_path)

        arr = np.array(Image.open(img_path).convert("RGB"))
        colors = ("r", "g", "b")
        bins = np.arange(257)

        fig, ax = plt.subplots()
        all_counts = []

        for i, col in enumerate(colors):
            channel = arr[:, :, i].ravel()
            hist, _ = np.histogram(channel, bins=bins, range=(0, 256))
            all_counts.append(hist)
            ax.bar(bins[:-1], hist, color=col, alpha=0.35, width=1)

        all_counts = np.concatenate(all_counts)
        maxc, medc = all_counts.max(), np.median(all_counts)

        if mode == "auto":
            mode = "log" if maxc > 10 * medc else "clip"

        if mode == "log":
            ax.set_yscale("log", nonpositive="clip")

        elif mode == "clip":
            ymax = np.percentile(all_counts, clip_pct)
            ax.set_ylim(0, ymax)

        elif mode == "pdf":
            ax.clear()
            for i, col in enumerate(colors):
                channel = arr[:, :, i].ravel()
                hist, _ = np.histogram(channel, bins=bins, range=(0, 256),
                                    density=True)  # <- normalize
                ax.bar(bins[:-1], hist, color=col, alpha=0.35, width=1)

        ax.set_title("Histogram")
        ax.set_xlabel("Piksel değeri")
        ax.set_ylabel("Frekans" if mode != "pdf" else "Yoğunluk")
        fig.tight_layout()
        fig.savefig(out_path)
        plt.close(fig)
    except Exception as e:
        print(f"Histogram oluşturulurken hata oluştu: {e}")


def compute_and_save_correlation(img_path: str, out_path: str):
    """Komşu piksel korelasyonunu scatter plot olarak kaydeder."""
    try:
        if not os.path.isfile(img_path):
            raise FileNotFoundError(f"Görüntü bulunamadı: {img_path}")

        img = Image.open(img_path).convert('L')
        arr = np.array(img)
        h, w = arr.shape

        pairs = []
        for y in range(h - 1):
            for x in range(w - 1):
                pairs.append((arr[y, x], arr[y, x+1]))
                pairs.append((arr[y, x], arr[y+1, x]))
        data = np.array(pairs)

        fig, ax = plt.subplots()
        ax.scatter(data[:, 0], data[:, 1], s=1, alpha=0.5)
        ax.set_title('Komşu Piksel Korelasyonu')
        ax.set_xlabel('Değer (x)')
        ax.set_ylabel('Değer (y)')

        fig.savefig(out_path)
        plt.close(fig)
    except Exception as e:
        print(f"Korelasyon grafiği oluşturulurken hata oluştu: {e}")

def compute_average_rgb_neighbor_correlation(img_path: str) -> float:
    """
    RGB görüntüde her renk kanalı için komşu piksel korelasyonunu hesaplar ve ortalamasını döner.

    Args:
        img_path (str): Görüntü dosyası yolu.

    Returns:
        float: Ortalama RGB komşu korelasyon katsayısı.
    """
    try:
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

            if np.std(x_vals) == 0 or np.std(y_vals) == 0:
                corr = 0.0
            else:
                corr = np.corrcoef(x_vals, y_vals)[0, 1]
            correlations.append(corr)

        return round(float(np.mean(correlations)), 5)
    except Exception as e:
        print(f"Komşu piksel korelasyonu hesaplanırken hata oluştu: {e}")
        return 0.0


def compute_psnr(img1_path: str, img2_path: str) -> str:
    """İki görüntü arasındaki PSNR değerini döner."""
    try:
        if not os.path.isfile(img1_path):
            raise FileNotFoundError(f"Girdi görüntüsü bulunamadı: {img1_path}")
        if not os.path.isfile(img2_path):
            raise FileNotFoundError(f"Çıktı görüntüsü bulunamadı: {img2_path}")

        img1 = np.array(Image.open(img1_path).convert('RGB'), dtype=np.float64) / 255.0
        img2 = np.array(Image.open(img2_path).convert('RGB'), dtype=np.float64) / 255.0

        psnr_val = peak_signal_noise_ratio(img1, img2)
        return round(psnr_val, 2)
    except Exception as e:
        print(f"PSNR hesaplanırken hata oluştu: {e}")
        return 0.0

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
    try:
        if not os.path.isfile(img1_path):
            raise FileNotFoundError(f"Görüntü bulunamadı: {img1_path}")
        if not os.path.isfile(img2_path):
            raise FileNotFoundError(f"Görüntü bulunamadı: {img2_path}")

        img1 = np.array(Image.open(img1_path).convert('RGB'), dtype=np.uint8)
        img2 = np.array(Image.open(img2_path).convert('RGB'), dtype=np.uint8)

        M, N, _ = img1.shape
        uaci_total = 0
        npcr_total = 0

        for ch in range(3):
            c1 = img1[:, :, ch]
            c2 = img2[:, :, ch]
            diff = c1 != c2
            uaci = np.sum(np.abs(c1.astype(np.int16) - c2.astype(np.int16))) / (255 * M * N) * 100
            npcr = np.sum(diff) / (M * N) * 100
            uaci_total += uaci
            npcr_total += npcr

        return round(npcr_total / 3, 5), round(uaci_total / 3, 5)
    except Exception as e:
        print(f"NPCR/UACI hesaplanırken hata oluştu: {e}")
        return 0.0, 0.0

def compute_entropy_rgb(img_path: str) -> float:
    """
    RGB görüntüler için bilgi entropisini hesaplar (her kanalın ayrı entropisinin ortalaması).
    R, G, B kanalları için Shannon entropisi ayrı ayrı hesaplanır.

    Parametre:
        img_path (str): RGB görüntü dosyasının yolu.

    Döndürür:
        float: Ortalama entropi (0-8 arası)
    """
    try:
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
            hist, _ = np.histogram(channel_data, bins=np.arange(257), density=True)

        avg_entropy = round(np.mean(entropy_values), 5)
        return avg_entropy
    except Exception as e:
        print(f"Entropi hesaplanırken hata oluştu: {e}")
        return 0.0
