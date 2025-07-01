import os
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import numpy as np
from PIL import Image
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from encrypt import encrypt_image
from decrypt import decrypt_image
from analysis_utils import (
    compute_and_save_histogram, compute_and_save_correlation,
    compute_psnr, compute_npcr_uaci, compute_entropy_rgb
)

from config import Config                             
from utils.logging_cfg import setup_logging, SafeRequestHandler
from utils.validators import (allowed_file, validate_request, 
                                validate_numeric_params)
from utils.io_helpers import (make_dirs, get_file_from_directory, 
                                save_image_with_metadata)

logger = setup_logging()

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
os.makedirs(Config.UPLOAD_FOLDER,  exist_ok=True)
os.makedirs(Config.ANALYZE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
@validate_request(file_fields=['image']) 
def encrypt_route():
    t0 = time.time()

    file      = request.files.get('image')
    directory = request.form.get('directory', '').strip()

    # kaynak dosyayı al
    if directory:
        fname, input_path = get_file_from_directory(directory)
        if not fname:
            return jsonify(status='error', message='Belirtilen dizinde dosya yok'), 404
        base     = directory
        filename = fname
        out_dir  = Path(Config.UPLOAD_FOLDER)/base/'out'
    else:
        if not file: 
            return jsonify(status='error', message='Dosya veya dizin gerekli'),400
        filename = secure_filename(file.filename)
        in_dir, out_dir, base = make_dirs(filename)
        input_path = os.path.join(in_dir, filename)
        file.save(input_path)

    # form parametrelerini oku + doğrula
    try:
        params = validate_numeric_params({
            'dna_rule': request.form.get('dna_rule', 1),
            'x0_list' : request.form.getlist('x0[]', type=float),
            'r_list'  : request.form.getlist('r[]',  type=float)
        })
    except ValueError as e:
        return jsonify(status='error', message=str(e)), 400

    password   = request.form.get('key','')
    output_path= os.path.join(out_dir, f"enc_{filename}")

    encrypt_image(
        input_path, output_path, password,
        params['dna_rule'], params['x0_list'], params['r_list']
    )

    dur = round(time.time()-t0, 4)
    logger.info(f"Encrypt: {filename} -> {output_path} ({dur}s)")
    return jsonify(
        status   ='success',
        directory=base,
        duration =dur,
        image_url=f"/static/uploads/{base}/out/enc_{filename}"
    )

@app.route('/decrypt', methods=['POST'])
@validate_request(file_fields=['image'])
def decrypt_route():
    t0 = time.time()
    directory = request.form.get('directory', '').strip()

    if directory:
        fname, input_path = get_file_from_directory(directory)
        if not fname:
            return jsonify(status='error', message='Belirtilen dizinde dosya yok'),404
        base     = directory
        filename = fname
        out_dir  = Path(Config.UPLOAD_FOLDER)/base/'out'
    else:
        file = request.files.get('image')
        if not file:
            return jsonify(status='error', message='Dosya veya dizin gerekli'),400
        filename = secure_filename(file.filename)
        in_dir, out_dir, base = make_dirs(filename)
        input_path = os.path.join(in_dir, filename)
        file.save(input_path)

    password   = request.form.get('key','')
    output_path= os.path.join(out_dir, f"dec_{filename}")
    decrypt_image(input_path, output_path, password)

    dur = round(time.time()-t0, 4)
    logger.info(f"Decrypt: {filename} ({dur}s)")
    return jsonify(
        status   ='success',
        directory=base,
        duration =dur,
        image_url=f"/static/uploads/{base}/out/dec_{filename}"
    )

@app.route('/crop_attack', methods=['POST'])
@validate_request(file_fields=['image'])
def crop_attack():
    try:
        w = int(request.form.get('width',0))
        h = int(request.form.get('height',0))
        if not (0 < w <= Config.MAX_CROP_SIZE and 0 < h <= Config.MAX_CROP_SIZE):
            raise ValueError
    except ValueError:
        return jsonify(status='error', message='Geçersiz crop boyutu'),400

    directory = request.form.get('directory','').strip()
    if directory:
        fname, in_path = get_file_from_directory(directory)
        if not fname: return jsonify(status='error', message='Yok'),404
        base = directory
    else:
        f = request.files.get('image')
        if not f: return jsonify(status='error', message='Dosya?'),400
        filename = secure_filename(f.filename)
        in_dir, _, base = make_dirs(filename)
        in_path = os.path.join(in_dir, filename)
        f.save(in_path)

    img  = Image.open(in_path); info = img.info
    arr  = np.array(img); arr[:h,:w,:]=0
    masked = Image.fromarray(arr)
    save_image_with_metadata(masked, in_path, info)

    logger.info(f"Crop attack {w}x{h} on {in_path}")
    return jsonify(status='success', directory=base,
                   cropped_url=f"/static/uploads/{base}/in/{Path(in_path).name}")

@app.route('/noise_attack', methods=['POST'])
@validate_request(file_fields=['image'])
def noise_attack():
    ntype = request.form.get('type','').lower()
    try:
        strength = float(request.form.get('strength',0))
        if ntype not in {'gaussian','salt_pepper'}:
            raise ValueError('tip')
        if not (Config.MIN_NOISE_STRENGTH<=strength<=Config.MAX_NOISE_STRENGTH):
            raise ValueError('sev')
    except ValueError:
        return jsonify(status='error', message='Geçersiz noise param.'),400

    directory = request.form.get('directory','').strip()
    if directory:
        fname,in_path = get_file_from_directory(directory)
        if not fname: return jsonify(status='error', message='Yok'),404
        base=directory
    else:
        f=request.files.get('image')
        if not f: return jsonify(status='error', message='Dosya?'),400
        filename=secure_filename(f.filename)
        in_dir, _, base = make_dirs(filename)
        in_path=os.path.join(in_dir,filename)
        f.save(in_path)

    img = Image.open(in_path).convert('RGB'); info=img.info
    arr = np.array(img).astype(np.float32)/255.0
    if ntype=='gaussian':
        arr = np.clip(arr+np.random.normal(0,strength**0.5,arr.shape),0,1)
    else:   # salt & pepper
        mask=np.random.rand(*arr.shape[:2])
        arr[mask<strength/2]=0; arr[mask>1-strength/2]=1
    out = Image.fromarray((arr*255).astype(np.uint8))
    save_image_with_metadata(out, in_path, info)

    logger.info(f"Noise {ntype}-{strength} on {in_path}")
    return jsonify(status='success', directory=base,
                   noised_url=f"/static/uploads/{base}/in/{Path(in_path).name}")

@app.route('/analyze', methods=['POST'])
@validate_request(file_fields=['input','output'])
def analyze():
    inp = request.files.get('input'); outp = request.files.get('output')
    if not inp and not outp:
        return jsonify(status='error', message='En az bir dosya gerek'),400

    ts = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
    bname = secure_filename((inp or outp).filename).rsplit('.',1)[0]
    base  = Path(Config.ANALYZE_FOLDER)/f"{bname}_{ts}"
    in_dir, out_dir = base/'in', base/'out'
    in_dir.mkdir(parents=True); out_dir.mkdir(parents=True)

    inp_path = out_path = None
    if inp:
        inp_path = in_dir/'input.png'; inp.save(inp_path)
    if outp:
        out_path = out_dir/'output.png'; outp.save(out_path)

    def _single(p:Path, pref:str):
        stub=uuid4().hex[:6]
        h=out_dir/f"hist_{pref}_{stub}.png"
        c=out_dir/f"corr_{pref}_{stub}.png"
        compute_and_save_histogram(p,h)
        compute_and_save_correlation(p,c)
        return str(h).replace(app.root_path,''), str(c).replace(app.root_path,''), compute_entropy_rgb(p)

    res={'status':'success'}
    if not out_path:
        h,c,e=_single(inp_path,'in')
        res.update(hist_urls=[h], corr_urls=[c], entropies=[e])
    else:
        h1,c1,e1=_single(inp_path,'in'); h2,c2,e2=_single(out_path,'out')
        psnr=compute_psnr(inp_path,out_path); npcr,uaci=compute_npcr_uaci(inp_path,out_path)
        res.update(hist_urls=[h1,h2], corr_urls=[c1,c2], entropies=[e1,e2],
                   psnr=round(psnr,4), npcr=round(npcr,4), uaci=round(uaci,4))
    return jsonify(res)

@app.route('/example_images')
def example_images():
    if not Config.EXAMPLES_FOLDER.exists():
        return jsonify(status='error', message='Klasör yok'),404
    files = sorted([f for f in Config.EXAMPLES_FOLDER.iterdir() if allowed_file(f.name)])
    urls  = [f"/static/examples/{f.name}" for f in files]
    return jsonify(status='success', images=urls, count=len(urls))

@app.route('/health')
def health():
    return jsonify(status='healthy', time=datetime.now().isoformat())

@app.errorhandler(413)
def file_too_large(_): return jsonify(
        status='error',
        message=f'Max {Config.MAX_CONTENT_LENGTH//(1024*1024)} MB'
    ),413

@app.errorhandler(404)
def not_found(_): return jsonify(status='error', message='Sayfa bulunamadı'),404

@app.errorhandler(500)
def internal(err):
    logger.error(f"Internal error: {err}", exc_info=True)
    return jsonify(status='error', message='Sunucu hatası'),500

if __name__ == '__main__':
    logger.info("Flask app starting")
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode, request_handler=SafeRequestHandler)
