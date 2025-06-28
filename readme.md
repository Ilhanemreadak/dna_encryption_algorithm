# DNA Tabanlı Görüntü Şifreleme / DNA‑Based Image Encryption


---

## 🇹🇷 Türkçe Bölüm

### İçindekiler
1. [Genel Bakış](#genel-bakış)
2. [Temel Özellikler](#temel-özellikler)
3. [Yöntemsel Arka Plan](#yöntemsel-arka-plan)
4. [Mimari ve Akış](#mimari-ve-akış)
5. [Proje Yapısı](#proje-yapısı)
6. [Kurulum](#kurulum)
7. [Hızlı Başlangıç](#hızlı-başlangıç)
8. [Performans ve Analiz](#performans-ve-analiz)
9. [Geliştirme Notları](#geliştirme-notları)
10. [Harici Bağımlılıklar](#harici-bağımlılıklar)
11. [Katkı Rehberi](#katkı-rehberi)
12. [Lisans](#lisans)

---

### Genel Bakış
Bu depo, RGB görüntüleri **DNA kodlama** ve **kaotik lojistik harita** tabanlı çok katmanlı bir yaklaşımla şifrelemek ve çözmek için tam yığın (CLI + Flask UI) bir uygulama sunar. Parola temelli anahtar türetimi (PBKDF2‑HMAC‑SHA256) kaba kuvvet saldırılarına karşı dayanıklıdır; **Cython** ile derlenmiş çekirdekler işlemleri hızlandırır; şifreye ilişkin salt ve parametreler PNG *tEXt* meta‑veri alanlarında saklanarak her şifreli dosyanın kendi kendini tanımlaması sağlanır.


### Temel Özellikler
| Modül | Amaç | Öne Çıkan Noktalar |
|-------|------|-------------------|
| [`encrypt.py`](encrypt.py) | CLI & Flask üzerinden şifreleme | Salt + parametreler PNG meta‑veriye gömülür |
| [`decrypt.py`](decrypt.py) | Ters işlem | Gerekli tüm parametreler dosyanın kendisinden okunur |
| [`analysis_utils.py`](analysis_utils.py) | PSNR, NPCR/UACI, entropi hesaplar | Standart kriptanaliz metrikleri |
| [`src/accelerated/*.pyx`](src/accelerated) | Cython hızlandırıcı çekirdekler | 10‑20× performans artışı |
| [`app.py`](app.py) | Flask + Jinja2 arayüz | Basit REST API & CORS yönetimi |


### Yöntemsel Arka Plan
* **DNA Kodlama (1‑8 kuralı)** — ikili veriyi A/T/C/G taban dizisine dönüştürür.
* **Lojistik Harita  _xₙ₊₁ = r·xₙ·(1 − xₙ)_** — r ≈ 3,98–4,00 aralığında maksimum kaos üretir.
* **PBKDF2‑HMAC‑SHA256** — 256 bit anahtar + 128 bit salt, varsayılan 200 000 iterasyon.
* **Çoklu Kriptanaliz Metrikleri** — NPCR > 99 %, UACI ≈ 33 %, entropi ≈ 8 bit hedeflenir.


### Mimari ve Akış

![sifrelemeadimlari](https://github.com/user-attachments/assets/93374f64-606c-43ee-addf-52b1f975e559)
![sifrecozmeakis](https://github.com/user-attachments/assets/70f7e558-960c-467a-bf45-accab41af398)


Tüm adımlar modüler fonksiyonlar hâlinde tasarlandığından hem CLI hem Flask rotaları tarafından yeniden kullanılabilir.


### Proje Yapısı
```text
.
├── app.py
├── encrypt.py          # Ana şifreleyici/CLI arayüzü
├── decrypt.py
├── utils.py
├── analysis_utils.py
├── requirements.txt
├── src/
│   └── accelerated/
│       ├── dna_codec_cy.pyx
│       ├── logistic_cy.pyx
│       └── chaos_utils_cy.pyx
├── templates/          # Jinja2 HTML şablonları
└── static/
    ├── uploads/        # Zamana göre oluşturulan klasörler
    ├── analysis/       # Histogram & korelasyon çıktıları
    └── examples/       # Demo görseller
```
`static/uploads/` çalışma anında otomatik oluşur ve `.gitignore` içindedir.


### Kurulum
```bash
# 1) Sanal ortam oluştur
python -m venv venv && source venv/bin/activate
# 2) Temel araçlar
pip install --upgrade pip wheel cython
# 3) Proje bağımlılıkları
pip install -r requirements.txt
# 4) Cython modüllerini derle
python -m pip install .
```
> **Windows kullanıcıları:** "Visual C++ Build Tools" kurulu olmalıdır.  
> **Linux/macOS kullanıcıları:** GCC veya Clang yeterlidir.


### Hızlı Başlangıç
```bash
# Komut Satırı
python encrypt.py -i lenna.png -o cipher.png -k "S3cret!"
python decrypt.py -i cipher.png -o plain.png -k "S3cret!"

# Web Arayüzü
export FLASK_APP=app.py
flask run    # http://localhost:5000 adresinde hizmet verir
```


### Performans ve Analiz
| Metrik | Örnek Değer | Açıklama |
|--------|-------------|----------|
| PSNR   | 49,2 dB     | Şifreli ↔ çözülen görüntü arasındaki kalite |
| NPCR   | 99,65 %     | Bit‑düzeyi değişim oranı |
| UACI   | 33,27 %     | Ortalama yoğun değişim |
| Entropi| 7,999 bit   | Rastgelelik üst sınırına yakın |

`analysis_utils.py` veya `/analyze` API uç noktası ile bu metrikler otomatik hesaplanabilir.


### Geliştirme Notları
* **Cython Derleme:** `setup.cfg` şablonu ve `pyximport` desteği içerir. Ek performans için `--annotation-html` seçeneğini kullanın.
* **PNG Metadata:** Salt ve parametreler `tEXt` alanına gömülür – dosya bütünlüğü bozulmaz.
* **Ekstra Araçlar:** `flask-cors`, `tqdm`, `pytest-benchmark`, opsiyonel `Pillow-SIMD`, deneysel `numba` desteği.


### Harici Bağımlılıklar
* **UI:** Bootstrap 5 + Tailwind CSS & DaisyUI.
* **Web Yazı Tipleri:** [Inter](https://fonts.google.com/specimen/Inter) • [Roboto Mono](https://fonts.google.com/specimen/Roboto+Mono)
* **Görsel İşleme:** NumPy, Pillow, scikit‑image, matplotlib.
* **Kriptografi:** Python `hashlib` (OpenSSL PBKDF2 uygulaması).


### Katkı Rehberi
1. Çalışmanızı `dev` dalına karşı çatallayın ve PR açın.  
2. Kod biçimlendirme için **Black** + **isort** kullanılır.  
3. Yeni özelliklerde test kapsaması ≥ %90 olmalıdır.  
4. Cython değişikliklerine `make bench` raporu ekleyin.  
5. Güvenlik‑kritik PR’lar için, örnek görsellerle NPCR/UACI raporu paylaşın.


### Lisans
Kod tabanı **MIT** lisansı altındadır. Tez/sunum gibi yan materyaller Creative Commons BY‑4.0 ile paylaşılabilir.

---

## 🇬🇧 English Version

### Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Methodological Background](#methodological-background)
4. [Architecture & Flow](#architecture--flow)
5. [Project Layout](#project-layout)
6. [Installation](#installation)
7. [Quick Start](#quick-start)
8. [Performance & Analysis](#performance--analysis)
9. [Development Notes](#development-notes)
10. [External Dependencies](#external-dependencies)
11. [Contributing](#contributing)
12. [License](#license)

---

### Overview
This repository offers a full‑stack solution (CLI + Flask UI) for encrypting and decrypting RGB images through **DNA coding** and a **chaotic logistic‑map** cascade. Password‑derived keys (PBKDF2‑HMAC‑SHA256) harden brute‑force resistance; **Cython‑compiled** cores keep throughput high; salts and parameters are preserved in PNG *tEXt* chunks so every cipher file is self‑describing.


### Key Features
| Module | Purpose | Highlights |
|--------|---------|-----------|
| [`encrypt.py`](encrypt.py) | Encrypt via CLI or Flask | Stores salt + params inside PNG metadata |
| [`decrypt.py`](decrypt.py) | Reverse process | Reads all parameters from the file itself |
| [`analysis_utils.py`](analysis_utils.py) | Computes PSNR, NPCR/UACI, entropy | Standard crypto‑analysis metrics |
| [`src/accelerated/*.pyx`](src/accelerated) | Cython acceleration cores | 10‑20× speed‑up |
| [`app.py`](app.py) | Flask + Jinja2 UI | Simple REST API & CORS management |


### Methodological Background
* **DNA coding (rules 1‑8)** — maps binary to A/T/C/G.
* **Logistic map  _xₙ₊₁ = r·xₙ·(1 − xₙ)_** with r ≈ 3.98–4.00 for maximum chaos.
* **PBKDF2‑HMAC‑SHA256** — 256‑bit key, 128‑bit salt, default 200 000 iterations.
* **Multi‑metric cryptanalysis** — targets NPCR > 99 %, UACI ≈ 33 %, entropy ≈ 8 bit.


### Architecture & Flow
![sifrelemeadimlari](https://github.com/user-attachments/assets/93374f64-606c-43ee-addf-52b1f975e559)
![sifrecozmeakis](https://github.com/user-attachments/assets/70f7e558-960c-467a-bf45-accab41af398)

Each step is exposed as a reusable function for both CLI and Flask routes.


### Project Layout
*(Same tree as Turkish section.)*


### Installation
```bash
python -m venv venv && source venv/bin/activate
pip install --upgrade pip wheel cython
pip install -r requirements.txt
python -m pip install .
```


### Quick Start
```bash
python encrypt.py -i sample.png -o cipher.png -k "Passw0rd"
python decrypt.py -i cipher.png -o plain.png -k "Passw0rd"

export FLASK_APP=app.py
flask run   # open http://localhost:5000
```


### Performance & Analysis
| Metric | Sample Value | Note |
|--------|--------------|------|
| PSNR   | 49.2 dB      | High fidelity after round‑trip |
| NPCR   | 99.65 %      | Optimal pixel change rate |
| UACI   | 33.27 %      | Uniform average intensity change |
| Entropy| 7.999 bit    | Near the theoretical maximum |

`analysis_utils.py` or the `/analyze` API endpoint can generate these metrics automatically.


### Development Notes
* **Cython build:** pre‑configured `setup.cfg`; enable `--annotation-html` for insight.
* **PNG metadata:** salts & parameters live in `tEXt` chunks — file integrity intact.
* **Extra tooling:** `flask-cors`, `tqdm`, `pytest-benchmark`, optional `Pillow‑SIMD`, experimental `numba`.


### External Dependencies
* **UI:** Bootstrap 5, Tailwind CSS with DaisyUI.
* **Fonts:** [Inter](https://fonts.google.com/specimen/Inter) • [Roboto Mono](https://fonts.google.com/specimen/Roboto+Mono)
* **Imaging:** NumPy, Pillow, scikit‑image, matplotlib.
* **Cryptography:** Python `hashlib` (OpenSSL PBKDF2).


### Contributing
1. Fork → work on `dev` branch → open PR.  
2. Follow **Black** + **isort** for code style.  
3. Aim for ≥ 90 % test coverage.  
4. Attach `make bench` results for Cython changes.  
5. Provide NPCR/UACI report with example images for security‑critical PRs.


### License
Source code is released under the **MIT License**. Auxiliary academic content (thesis, slides) is shared under **CC BY‑4.0**.

