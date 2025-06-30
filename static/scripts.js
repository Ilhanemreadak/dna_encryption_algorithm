// Tüm event ve yardımcı fonksiyonlar DOM yüklendiğinde başlatılır
window.addEventListener('DOMContentLoaded', () => {
    let currentDir = '';

    // Elementlere güvenli şekilde event ekler
    function safeAddEventListener(id, event, handler) {
        const el = document.getElementById(id);
        if (el) el.addEventListener(event, handler);
    }

    // Upload butonuna tıklanınca dosya input'unu tetikler
    safeAddEventListener('uploadBtn', 'click', () => {
        const input = document.getElementById('imageUpload');
        if (input) input.click();
    });

    // Dosya seçildiğinde görseli gösterir
    safeAddEventListener('imageUpload', 'change', event => {
        const file = event.target.files[0];
        if (!file) return;
        currentDir = ''; // Önceki analiz temizlenir

        const reader = new FileReader();
        reader.onload = () => {
            const inputImage = document.getElementById('inputImage');
            const inputDropArea = document.getElementById('inputDropArea');
            if (inputImage) inputImage.src = reader.result;
            if (inputImage) inputImage.classList.remove('hidden');
            if (inputDropArea) inputDropArea.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    });

    // Sürükle-bırak desteği
    const dropArea = document.getElementById('inputDropArea');
    if (dropArea) {
        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropArea.classList.add('border-primary');
        });

        dropArea.addEventListener('dragleave', () => {
            dropArea.classList.remove('border-primary');
        });

        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.classList.remove('border-primary');

            const file = e.dataTransfer.files[0];
            if (!file) return;
            currentDir = '';

            const reader = new FileReader();
            reader.onload = () => {
                const inputImage = document.getElementById('inputImage');
                if (inputImage) inputImage.src = reader.result;
                if (inputImage) inputImage.classList.remove('hidden');
                dropArea.classList.add('hidden');
            };
            reader.readAsDataURL(file);

            // Dosyayı input'a da ekler
            const imageUpload = document.getElementById('imageUpload');
            if (imageUpload) imageUpload.files = e.dataTransfer.files;
        });

        dropArea.addEventListener('click', () => {
            document.getElementById('imageUpload').click();
        });
    }

    // Şifreleme işlemi
    safeAddEventListener('encryptBtn', 'click', async () => {
        const imageUpload = document.getElementById('imageUpload');
        const keyInput = document.getElementById('keyInput');
        const dnaRuleSelect = document.getElementById('dnaRuleSelect');
        if (!imageUpload || !keyInput || !dnaRuleSelect) return;
        const file = imageUpload.files[0];
        if (!file) return alert('Önce girdi görseli yükleyin.');
        const formData = new FormData();
        formData.append('image', file);
        formData.append('key', keyInput.value);
        formData.append('dna_rule', dnaRuleSelect.value);
        for (let i = 1; i <= 3; i++) {
            const x0 = document.getElementById(`x0_${i}`);
            const r = document.getElementById(`r_${i}`);
            if (x0 && r) {
                formData.append('x0[]', x0.value);
                formData.append('r[]', r.value);
            }
        }
        const res = await fetch('/encrypt', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.status === 'success') {
            currentDir = data.directory;
            const outputImage = document.getElementById('outputImage');
            const outputPlaceholder = document.getElementById('outputPlaceholder');
            if (outputImage) outputImage.src = data.image_url;
            if (outputImage) outputImage.classList.remove('hidden');
            if (outputPlaceholder) outputPlaceholder.classList.add('hidden');
        } else {
            alert('Şifreleme hatası: ' + data.message);
        }
    });

    // Çözme işlemi
    safeAddEventListener('decryptBtn', 'click', async () => {
        const imageUpload = document.getElementById('imageUpload');
        const keyInput = document.getElementById('keyInput');
        if (!imageUpload || !keyInput) return;
        const file = imageUpload.files[0];
        if (!file) return alert('Önce şifrelenmiş görseli yükleyin.');

        const formData = new FormData();
        formData.append('image', file);
        formData.append('key', keyInput.value);

        const res = await fetch('/decrypt', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.status === 'success') {
            currentDir = data.directory;
            const out = document.getElementById('outputImage');
            const outputPlaceholder = document.getElementById('outputPlaceholder');
            if (out) out.src = data.image_url;
            if (out) out.classList.remove('hidden');
            if (outputPlaceholder) outputPlaceholder.classList.add('hidden');
        } else {
            alert('Çözme hatası: ' + data.message);
        }
    });

    // Crop Attack işlemi
    safeAddEventListener('cropDecryptBtn', 'click', async () => {
        const cropWidth = document.getElementById('cropWidth');
        const cropHeight = document.getElementById('cropHeight');
        if (!cropWidth || !cropHeight) return;
        const w = parseInt(cropWidth.value, 10);
        const h = parseInt(cropHeight.value, 10);
        if (w <= 0 || h <= 0) return alert('Geçerli boyut girin.');

        const fd = new FormData();
        fd.append('width', w);
        fd.append('height', h);
        const selFile = document.getElementById('imageUpload').files[0];

        if (selFile) fd.append('image', selFile);
        else if (currentDir) fd.append('directory', currentDir);
        else return alert('Önce dosya seçin.');

        const cropRes = await fetch('/crop_attack', { method: 'POST', body: fd });
        const cropData = await cropRes.json();
        if (cropData.status !== 'success') {
            return alert('Crop hatası: ' + cropData.message);
        }

        currentDir = cropData.directory;
        const inp = document.getElementById('inputImage');
        const inputDropArea = document.getElementById('inputDropArea');
        if (inp) inp.src = cropData.cropped_url;
        if (inp) inp.classList.remove('hidden');
        if (inputDropArea) inputDropArea.classList.add('hidden');
        const cropModal = document.getElementById('cropModal');
        if (cropModal) new bootstrap.Modal(cropModal).hide();

        const fd2 = new FormData();
        fd2.append('directory', currentDir);
        const keyInput = document.getElementById('keyInput');
        if (keyInput) fd2.append('key', keyInput.value);

        const decRes = await fetch('/decrypt', { method: 'POST', body: fd2 });
        const decData = await decRes.json();
        if (decData.status !== 'success') {
            return alert('Çözme hatası: ' + decData.message);
        }

        const out = document.getElementById('outputImage');
        const outputPlaceholder = document.getElementById('outputPlaceholder');
        if (out) out.src = decData.image_url;
        if (out) out.classList.remove('hidden');
        if (outputPlaceholder) outputPlaceholder.classList.add('hidden');
    });

    // Noise Attack işlemi
    safeAddEventListener('noiseDecryptBtn', 'click', async () => {
        const noiseType = document.getElementById('noiseType');
        const noiseStrength = document.getElementById('noiseStrength');
        if (!noiseType || !noiseStrength) return;
        const type = noiseType.value;
        const strength = parseFloat(noiseStrength.value);
        if (isNaN(strength) || strength <= 0) {
            return alert('Geçerli bir güç değeri girin.');
        }

        const fd = new FormData();
        fd.append('type', type);
        fd.append('strength', strength);
        const selFile = document.getElementById('imageUpload').files[0];

        if (selFile) fd.append('image', selFile);
        else if (currentDir) fd.append('directory', currentDir);
        else return alert('Önce dosya seçin.');

        const res = await fetch('/noise_attack', { method: 'POST', body: fd });
        const data = await res.json();
        if (data.status !== 'success') {
            return alert('Noise hatası: ' + data.message);
        }

        currentDir = data.directory;
        const inp = document.getElementById('inputImage');
        const inputDropArea = document.getElementById('inputDropArea');
        if (inp) inp.src = data.noised_url;
        if (inp) inp.classList.remove('hidden');
        if (inputDropArea) inputDropArea.classList.add('hidden');
        const noiseModal = document.getElementById('noiseModal');
        if (noiseModal) new bootstrap.Modal(noiseModal).hide();

        const fd2 = new FormData();
        fd2.append('directory', currentDir);
        const keyInput = document.getElementById('keyInput');
        if (keyInput) fd2.append('key', keyInput.value);

        const decRes = await fetch('/decrypt', { method: 'POST', body: fd2 });
        const decData = await decRes.json();
        if (decData.status !== 'success') {
            return alert('Çözme hatası: ' + decData.message);
        }

        const out = document.getElementById('outputImage');
        const outputPlaceholder = document.getElementById('outputPlaceholder');
        if (out) out.src = decData.image_url;
        if (out) out.classList.remove('hidden');
        if (outputPlaceholder) outputPlaceholder.classList.add('hidden');
    });

    // Key Sensitivity: Bit gösterimi ve toggle işlemi
    safeAddEventListener('showBitsBtn', 'click', () => {
        const key = document.getElementById('keySensInput')?.value;
        if (!key) return alert('Önce bir şifre girin.');

        const bits = Array.from(key)
            .map(ch => ch.charCodeAt(0).toString(2).padStart(8, '0'))
            .join('');

        const disp = document.getElementById('bitDisplay');
        disp.innerHTML = '';
        bits.split('').forEach(b => {
            const span = document.createElement('span');
            span.textContent = b;
            span.classList.add('bit-span');
            span.onclick = () => span.textContent = span.textContent === '0' ? '1' : '0';
            disp.appendChild(span);
        });
        disp.scrollTop = 0;
        disp.classList.remove('hidden');
    });

    // Key Sensitivity: Uygula ve çöz
    safeAddEventListener('applyKeySensBtn', 'click', async () => {
        const spans = Array.from(document.querySelectorAll('#bitDisplay .bit-span'));
        if (spans.length === 0) return alert('Önce "Bit Göster" yapın.');
        const bits = spans.map(s => s.textContent).join('');
        let newKey = '';
        for (let i = 0; i < bits.length; i += 8) {
            const byte = bits.slice(i, i + 8);
            newKey += String.fromCharCode(parseInt(byte, 2));
        }
        const keySensModal = document.getElementById('keySensModal');
        if (keySensModal) new bootstrap.Modal(keySensModal).hide();

        const fd = new FormData();
        const uploadFile = document.getElementById('imageUpload').files[0];

        if (uploadFile) {
            fd.append('image', uploadFile);
        } else if (currentDir) {
            fd.append('directory', currentDir);
        } else {
            return alert('Önce bir dosya seçin.');
        }
        fd.append('key', newKey);

        const res = await fetch('/decrypt', { method: 'POST', body: fd });
        const data = await res.json();
        if (data.status !== 'success') {
            return alert('Çözme hatası: ' + data.message);
        }
        const outputImage = document.getElementById('outputImage');
        const outputPlaceholder = document.getElementById('outputPlaceholder');
        if (outputImage) outputImage.src = data.image_url;
        if (outputImage) outputImage.classList.remove('hidden');
        if (outputPlaceholder) outputPlaceholder.classList.add('hidden');
        if (data.directory) currentDir = data.directory;
        const disp = document.getElementById('bitDisplay');
        disp.innerHTML = '';
        disp.classList.add('hidden');
    });

    // Örnek görselleri gösterir
    safeAddEventListener('showExamplesBtn', 'click', async () => {
        const container = document.getElementById('exampleImages');
        if (!container) return;
        container.innerHTML = '';

        const res = await fetch('/example_images');
        const d = await res.json();

        if (d.status === 'success') {
            d.images.forEach(async url => {
                const tr = document.createElement('tr');
                const tdImg = document.createElement('td');
                const tdName = document.createElement('td');

                const img = document.createElement('img');
                img.src = url;
                img.alt = url.split('/').pop();
                img.style.width = '50px';
                img.style.height = '50px';
                img.style.cursor = 'pointer';
                img.classList.add('rounded', 'border');

                img.addEventListener('click', async () => {
                    const blob = await fetch(url).then(r => r.blob());
                    const file = new File([blob], img.alt, { type: blob.type });
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    const imageUpload = document.getElementById('imageUpload');
                    if (imageUpload) imageUpload.files = dataTransfer.files;

                    const reader = new FileReader();
                    reader.onload = () => {
                        const inputImage = document.getElementById('inputImage');
                        const inputDropArea = document.getElementById('inputDropArea');
                        if (inputImage) inputImage.src = reader.result;
                        if (inputImage) inputImage.classList.remove('hidden');
                        if (inputDropArea) inputDropArea.classList.add('hidden');
                    };
                    reader.readAsDataURL(file);

                    const modal = bootstrap.Modal.getInstance(document.getElementById('exampleModal'));
                    if (modal) modal.hide();
                });

                tdImg.appendChild(img);
                tdName.textContent = img.alt;
                tr.appendChild(tdImg);
                tr.appendChild(tdName);
                container.appendChild(tr);
            });

            const exampleModal = document.getElementById('exampleModal');
            if (exampleModal) new bootstrap.Modal(exampleModal).show();
        } else {
            alert('Örnek görseller yüklenemedi.');
        }
    });

    // Çıktı görselini kaydeder
    if (typeof safeAddEventListener === 'function') {
        safeAddEventListener('saveBtn', 'click', saveOutput);
    } else {
        document.getElementById('saveBtn').addEventListener('click', saveOutput);
    }

    // Çıktı kaydetme fonksiyonu
    async function saveOutput() {
        const imgEl = document.getElementById('outputImage');
        const src = imgEl?.src || '';
        if (!src || src.endsWith('#')) return alert('Önce çıktı görseli oluşsun.');

        // Link oluşturulur
        const a = document.createElement('a');
        a.style.display = 'none';
        document.body.appendChild(a);

        // Data-URL ise direkt indir, değilse fetch ile indir
        if (src.startsWith('data:')) {
            a.href = src;
            a.download = 'output.png';
            a.click();
        } else {
            const resp = await fetch(src);
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            a.href = url;
            a.download = src.split('/').pop() || 'output.png';
            a.click();
            URL.revokeObjectURL(url);
        }

        document.body.removeChild(a);
    }

    // Analiz UI işlemleri
    (function () {
        // Upload alanı oluşturur
        function uploadArea(id, label) {
            const extraBtn = id === 'single'
                ? `<button id="ana-set-single-out" class="btn btn-sm btn-outline-success">Çıktıyı Seç</button>`
                : '';
            const selTxt = id === 'output' ? 'Çıktıyı Seç' : 'Girdiyi Seç';

            return `
                <div class="col-md-6 text-center mb-3">
                    <h6>${label}</h6>
                    <div id="ana-drop-${id}" class="placeholder-box"><i class="bi bi-upload"></i></div>
                    <img id="ana-img-${id}" class="img-preview hidden" src="#">
                    <input id="ana-file-${id}" type="file" accept="image/*" class="d-none">
                    <div class="btn-group mt-2">
                        <button id="ana-up-${id}"  class="btn btn-sm btn-outline-info">Yükle</button>
                        <button id="ana-ex-${id}"  class="btn btn-sm btn-outline-secondary">Örnekler</button>
                        <button id="ana-set-${id}" class="btn btn-sm btn-outline-success">${selTxt}</button>
                        ${extraBtn}
                    </div>
                </div>`;
        }

        const hostCtrl = document.getElementById('ana-controls');
        const resBox = document.getElementById('ana-results');
        let anaMode = null; // 'compare' | 'single'
        let exampleTarget = null; // input | output | single | null

        // Analiz modu seçim butonları
        const btnCompare = document.getElementById('ana-btn-compare') || document.getElementById('btn-compare');
        if (btnCompare) btnCompare.onclick = () => { anaMode = 'compare'; buildUI(); };

        const btnSingle = document.getElementById('ana-btn-single') || document.getElementById('btn-single');
        if (btnSingle) btnSingle.onclick = () => { anaMode = 'single'; buildUI(); };

        // UI oluşturur
        function buildUI() {
            hostCtrl.innerHTML =
                anaMode === 'compare'
                    ? `<div class="row">${uploadArea('input', 'Girdi Görseli')}${uploadArea('output', 'Çıktı Görseli')}</div>
                       <div class="text-center"><button id="ana-run" class="btn btn-primary mt-2">Karşılaştır &amp; Analiz</button></div>`
                    : `<div class="row justify-content-center">${uploadArea('single', 'Görsel')}</div>
                       <div class="text-center"><button id="ana-run" class="btn btn-primary mt-2">Analiz Yap</button></div>`;

            resBox.classList.add('d-none');
            bindEvents();
        }

        // Event bağlama işlemleri
        function bindEvents() {
            ['input', 'output', 'single'].forEach(id => {
                const f = document.getElementById(`ana-file-${id}`); if (!f) return;
                const d = document.getElementById(`ana-drop-${id}`);
                const img = document.getElementById(`ana-img-${id}`);

                // Yükle butonu
                document.getElementById(`ana-up-${id}`).onclick = () => f.click();
                // Örnekler butonu
                document.getElementById(`ana-ex-${id}`).onclick = () => { exampleTarget = id; openExampleModal(); };
                // Şifreleme tarafındaki resmi al
                document.getElementById(`ana-set-${id}`).onclick = () => copyFromEncryption(id, f, img, d);
                if (id === 'single') {
                    const btnOut = document.getElementById('ana-set-single-out');
                    btnOut.onclick = () => copyFromEncryption('output', f, img, d);
                }
                // Drag & Drop işlemleri
                d.onclick = () => f.click();
                d.ondragover = e => { e.preventDefault(); d.classList.add('border', 'border-primary'); };
                d.ondragleave = e => { e.preventDefault(); d.classList.remove('border', 'border-primary'); };
                d.ondrop = e => {
                    e.preventDefault();
                    d.classList.remove('border', 'border-primary');
                    const file = e.dataTransfer.files[0];
                    if (file) { f.files = e.dataTransfer.files; preview(file, img, d); }
                };

                f.onchange = e => preview(e.target.files[0], img, d);
            });

            // Analiz çalıştırma butonu
            document.getElementById('ana-run').onclick = runAnalysis;
        }

        // Dosya önizlemesi
        function preview(file, img, drop) {
            if (!file) return;
            const fr = new FileReader();
            fr.onload = () => { img.src = fr.result; img.classList.remove('hidden'); drop.classList.add('hidden'); };
            fr.readAsDataURL(file);
        }

        // Şifreleme kısmından dosya kopyalama
        function copyFromEncryption(id, f, img, drop) {
            const src = document.getElementById(id === 'output' ? 'outputImage' : 'inputImage')?.src || '';
            if (!src || src.endsWith('#')) return alert('Şifreleme kısmında uygun resim yok');
            fetch(src).then(r => r.blob()).then(b => {
                const safeName = src.startsWith('data:')
                    ? 'image.png'
                    : (src.split('/').pop() || 'image.png');
                const file = new File([b], safeName, { type: b.type });
                const dt = new DataTransfer(); dt.items.add(file); f.files = dt.files;
                preview(file, img, drop);
            });
        }

        // Analiz isteği gönderir
        async function runAnalysis() {
            const fd = new FormData();
            if (anaMode === 'compare') {
                const fin = document.getElementById('ana-file-input').files[0];
                const fout = document.getElementById('ana-file-output').files[0];
                if (!fin || !fout) return alert('Her iki görseli de yükleyin');
                fd.append('input', fin); fd.append('output', fout);
            } else {
                const f = document.getElementById('ana-file-single').files[0];
                if (!f) return alert('Görsel yükleyin');
                fd.append('input', f);
            }
            const res = await fetch('/analyze', { method: 'POST', body: fd });
            showResults(await res.json());
        }

        // Analiz sonuçlarını gösterir
        function showResults(data) {
            if (data.status !== 'success') { alert(data.message || 'Hata'); return; }

            const resBox = document.getElementById('ana-results');
            resBox.innerHTML = '';
            const card = document.createElement('div');
            card.className = 'analysis-card';
            card.innerHTML = '<h5 class="text-center">Analiz Sonuçları</h5>';
            resBox.appendChild(card);

            // Histogram ve correlation görselleri
            const grid = document.createElement('div');
            grid.className = 'row g-4 mb-3';

            data.hist_urls.forEach((hist, i) => {
                const col = document.createElement('div');
                col.className = data.hist_urls.length === 2 ? 'col-md-6' : 'col-md-8 offset-md-2';
                col.innerHTML = `
                    <div class="analysis-pair">
                        <img src="${hist}" class="analysis-img">
                        <img src="${data.corr_urls[i]}" class="analysis-img">
                        <div class="analysis-metric">
                            ${(data.entropies.length === 2 ? (i === 0 ? 'Girdi' : 'Çıktı') + ' ' : '')}
                            Entropisi : ${data.entropies[i]}
                        </div>
                    </div>`;
                grid.appendChild(col);
            });
            card.appendChild(grid);

            // Karşılaştırma metrikleri
            if (data.psnr !== undefined) {
                const box = document.createElement('div');
                box.className = 'metric-list';
                box.innerHTML = `
                    <p>PSNR : ${data.psnr}</p>
                    <p>NPCR : ${data.npcr}</p>
                    <p>UACI : ${data.uaci}</p>`;
                card.appendChild(box);
            }

            resBox.classList.remove('d-none');
        }

        // Ortak örnekler modalı açar
        async function openExampleModal() {
            const tbody = document.getElementById('exampleImages'); tbody.innerHTML = '';
            try {
                const d = await fetch('/example_images').then(r => r.json());
                if (d.status !== 'success') return alert('Örnekler yüklenemedi');
                d.images.forEach(url => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `<td><img src="${url}" style="width:60px;cursor:pointer" class="rounded border"></td><td>${url.split('/').pop()}</td>`;
                    tr.querySelector('img').onclick = () => chooseExample(url);
                    tbody.appendChild(tr);
                });
                new bootstrap.Modal(document.getElementById('exampleModal')).show();
            } catch { alert('Örnekler hatası'); }
        }

        // Örnek seçildiğinde ilgili input'a aktarır
        async function chooseExample(url) {
            const blob = await fetch(url).then(r => r.blob());
            const safeName = url.split('/').pop() || 'example.png';
            const file = new File([blob], safeName, { type: blob.type });
            if (exampleTarget) {
                const fi = document.getElementById(`ana-file-${exampleTarget}`);
                const drop = document.getElementById(`ana-drop-${exampleTarget}`);
                const img = document.getElementById(`ana-img-${exampleTarget}`);
                const dt = new DataTransfer(); dt.items.add(file); fi.files = dt.files;
                preview(file, img, drop);
            } else {
                const dt = new DataTransfer(); dt.items.add(file);
                document.getElementById('imageUpload').files = dt.files;
                const fr = new FileReader();
                fr.onload = () => {
                    const inputImage = document.getElementById('inputImage');
                    const inputDropArea = document.getElementById('inputDropArea');
                    inputImage.src = fr.result;
                    inputImage.classList.remove('hidden');
                    inputDropArea.classList.add('hidden');
                };
                fr.readAsDataURL(file);
            }
            bootstrap.Modal.getInstance(document.getElementById('exampleModal')).hide();
        }
    })();
});