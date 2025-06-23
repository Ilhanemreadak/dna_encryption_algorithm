from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL import Image, PngImagePlugin
import numpy as np

from encrypt import encrypt_image
from decrypt import decrypt_image
from analysis_utils import (
    compute_and_save_histogram,
    compute_and_save_correlation,
    compute_psnr,
)

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['ANALYZE_FOLDER'] = os.path.join('static', 'analysis')
os.makedirs(app.config['ANALYZE_FOLDER'], exist_ok=True)

ALLOWED = {'png','jpg','jpeg'}

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED

def make_dirs(filename: str):
    ts = datetime.now().strftime("%d_%m_%Y_%H_%M")
    base = f"{Path(filename).stem}_{ts}"
    base_dir = os.path.join(UPLOAD_FOLDER, base)
    in_dir  = os.path.join(base_dir, 'in')
    out_dir = os.path.join(base_dir, 'out')
    os.makedirs(in_dir,  exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    return in_dir, out_dir, base

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    file = request.files.get('image')
    dir_name = request.form.get('directory')
    if dir_name:
        # use existing directory
        base = dir_name
        in_dir = os.path.join(UPLOAD_FOLDER, base, 'in')
        files = [f for f in os.listdir(in_dir) if allowed_file(f)]
        if not files:
            return jsonify({'status':'error','message':'Original file missing'}),404
        filename = files[0]
        input_path = os.path.join(in_dir, filename)
    else:
        if not file or not allowed_file(file.filename):
            return jsonify({'status':'error','message':'Invalid input'}),400
        filename = secure_filename(file.filename)
        in_dir, out_dir, base = make_dirs(filename)
        input_path = os.path.join(in_dir, filename)
        file.save(input_path)

    password = request.form.get('key','')
    dna_rule = int(request.form.get('dna_rule',1))
    x0_list = request.form.getlist('x0[]',type=float)
    r_list = request.form.getlist('r[]',type=float)

    # determine out_dir
    if not dir_name:
        _, out_dir, _ = make_dirs(filename)
    out_dir = os.path.join(UPLOAD_FOLDER, base, 'out')
    encrypted_name = f"enc_{filename}"
    output_path = os.path.join(out_dir, encrypted_name)
    try:
        encrypt_image(input_path, output_path, password, dna_rule, x0_list, r_list)
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}),500
    return jsonify({'status':'success','image_url':f'/static/uploads/{base}/out/{encrypted_name}','directory':base})

@app.route('/decrypt', methods=['POST'])
def decrypt_route():
    from decrypt import decrypt_image  # mevcut logic

    # 1) Eğer directory gelmişse, o klasörden oku
    directory = request.form.get('directory')
    if directory:
        in_dir = os.path.join(UPLOAD_FOLDER, directory, 'in')
        files = [f for f in os.listdir(in_dir) if allowed_file(f)]
        if not files:
            return jsonify(status='error', message='Girdi dosyası bulunamadı'), 404
        filename = files[0]
        input_path = os.path.join(in_dir, filename)
    else:
        # eskiden olduğu gibi doğrudan yüklenen blob
        file = request.files.get('image')
        if not file or not allowed_file(file.filename):
            return jsonify(status='error', message='Dosya gereklidir'), 400
        filename = secure_filename(file.filename)
        in_dir, out_dir, directory = make_dirs(filename)
        input_path = os.path.join(in_dir, filename)
        file.save(input_path)

    # 2) Çöz
    password = request.form.get('key', '')
    _, out_dir, _ = make_dirs(filename) if not directory else (None, os.path.join(UPLOAD_FOLDER, directory, 'out'), None)
    output_name = f"dec_{filename}"
    output_path = os.path.join(out_dir, output_name)

    try:
        decrypt_image(input_path, output_path, password)
    except Exception as e:
        return jsonify(status='error', message=str(e)), 500

    url = f"/static/uploads/{directory}/out/{output_name}"
    return jsonify(status='success', image_url=url, directory=directory)


@app.route('/crop_attack', methods=['POST'])
def crop_attack():
    # 1) Parametreler
    try:
        w = int(request.form.get('width', 0))
        h = int(request.form.get('height', 0))
    except ValueError:
        return jsonify(status='error', message='Geçersiz crop boyutları'), 400
    if w<=0 or h<=0:
        return jsonify(status='error', message='Geçersiz crop boyutları'), 400

    # 2) Hangi görüntü?
    directory = request.form.get('directory')
    if directory:
        # Önceden oluşturulan in/ klasöründeki resmi al
        in_dir = os.path.join(UPLOAD_FOLDER, directory, 'in')
        files = [f for f in os.listdir(in_dir) if allowed_file(f)]
        if not files:
            return jsonify(status='error', message='Orijinal dosya bulunamadı'), 404
        filename = files[0]
    else:
        # Doğrudan form'dan gelen dosyayı al ve yeni bir directory oluştur
        file = request.files.get('image')
        if not file or not allowed_file(file.filename):
            return jsonify(status='error', message='Dosya gereklidir'), 400
        filename = secure_filename(file.filename)
        in_dir, _, directory = make_dirs(filename)
        file.save(os.path.join(in_dir, filename))

    in_path = os.path.join(in_dir, filename)
    img = Image.open(in_path)
    info = img.info           # metadata (salt/params) burada

    # 3) Sol üst köşeyi siyahla doldur
    arr = np.array(img)
    arr[0:h, 0:w, :] = 0
    masked = Image.fromarray(arr)

    # 4) Metadata'yı koru
    meta = PngImagePlugin.PngInfo()
    if 'salt' in info:   meta.add_text('salt', info['salt'])
    if 'params' in info: meta.add_text('params', info['params'])

    # 5) Üzerine yaz
    masked.save(in_path, pnginfo=meta)

    # 6) URL döndür
    url = f"/static/uploads/{directory}/in/{filename}"
    return jsonify(status='success', directory=directory, cropped_url=url)

@app.route('/noise_attack', methods=['POST'])
def noise_attack():
    # 1) Parametreleri al
    noise_type = request.form.get('type')
    strength   = float(request.form.get('strength', 0))
    if noise_type not in {'gaussian','salt_pepper'} or strength <= 0:
        return jsonify(status='error', message='Geçersiz noise parametreleri'),400

    # 2) Hangi görsel?
    directory = request.form.get('directory')
    if directory:
        in_dir = os.path.join(UPLOAD_FOLDER, directory, 'in')
        files = [f for f in os.listdir(in_dir) if allowed_file(f)]
        if not files:
            return jsonify(status='error', message='Orijinal dosya bulunamadı'),404
        filename = files[0]
    else:
        file = request.files.get('image')
        if not file or not allowed_file(file.filename):
            return jsonify(status='error', message='Dosya gereklidir'),400
        filename = secure_filename(file.filename)
        in_dir, _, directory = make_dirs(filename)
        file.save(os.path.join(in_dir, filename))

    in_path = os.path.join(in_dir, filename)
    img = Image.open(in_path).convert('RGB')
    info = img.info  # salt/params metadata burada

    arr = np.array(img).astype(np.float32) / 255.0

    # 3) Noise uygulama
    if noise_type == 'gaussian':
        mean = 0.0
        var  = strength
        gauss = np.random.normal(mean, var**0.5, arr.shape)
        arr_noised = np.clip(arr + gauss, 0.0, 1.0)
    else:  # salt_pepper
        prob = strength
        mask = np.random.rand(*arr.shape[:2])
        sp_arr = arr.copy()
        sp_arr[mask < (prob/2)] = 0.0
        sp_arr[mask > 1 - (prob/2)] = 1.0
        arr_noised = sp_arr

    noised = (arr_noised * 255).astype(np.uint8)
    out_img = Image.fromarray(noised)

    # 4) Metadata’yı koru
    pnginfo = PngImagePlugin.PngInfo()
    if 'salt' in info:   pnginfo.add_text('salt', info['salt'])
    if 'params' in info: pnginfo.add_text('params', info['params'])

    # 5) Üzerine yaz
    save_path = os.path.join(in_dir, filename)
    out_img.save(save_path, pnginfo=pnginfo)

    url = f"/static/uploads/{directory}/in/{filename}"
    return jsonify(status='success', directory=directory, noised_url=url)

@app.route('/analyze', methods=['POST'])
def analyze():
    input_file = request.files.get('input')
    output_file = request.files.get('output')

    if not input_file and not output_file:
        return jsonify({'status': 'error', 'message': 'Görsel dosyası yüklenmedi'}), 400

    # klasör adı
    timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")
    base_name = secure_filename((input_file or output_file).filename).rsplit('.', 1)[0]
    folder_name = f"{base_name}_{timestamp}"

    base_path = os.path.join(app.root_path, app.config['ANALYZE_FOLDER'], folder_name)
    in_dir = os.path.join(base_path, "in")
    out_dir = os.path.join(base_path, "out")
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # görsellerin yolu
    input_path, output_path = None, None

    if input_file:
        input_path = os.path.join(in_dir, 'input.png')
        input_file.save(input_path)

    if output_file:
        output_path = os.path.join(out_dir, 'output.png')
        output_file.save(output_path)

    # histogram + corr her zaman çıktı dosyası üzerinden hesaplanacak
    analysis_target_path = output_path if output_path else input_path
    filename_wo_ext = os.path.splitext(os.path.basename(analysis_target_path))[0]

    hist_path = os.path.join(out_dir, f"hist_{filename_wo_ext}.png")
    corr_path = os.path.join(out_dir, f"corr_{filename_wo_ext}.png")
    compute_and_save_histogram(analysis_target_path, hist_path)
    compute_and_save_correlation(analysis_target_path, corr_path)

    # PSNR hesapla (sadece ikisi varsa)
    if input_path and output_path:
        psnr = compute_psnr(input_path, output_path)
    else:
        psnr = "∞"

    return jsonify({
        'status': 'success',
        'directory': folder_name,
        'hist_url': f'/static/analysis/{folder_name}/out/hist_{filename_wo_ext}.png',
        'corr_url': f'/static/analysis/{folder_name}/out/corr_{filename_wo_ext}.png',
        'psnr': psnr
    })

@app.route('/example_images', methods=['GET'])
def get_example_images():
    examples_path = os.path.join(app.root_path, 'static', 'examples')
    if not os.path.exists(examples_path):
        return jsonify({'status': 'error', 'message': 'Klasör bulunamadı'}), 404

    files = [
        f for f in os.listdir(examples_path)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    urls = [f'/static/examples/{f}' for f in files]

    return jsonify({'status': 'success', 'images': urls})


if __name__ == '__main__':
    app.run(debug=True)
