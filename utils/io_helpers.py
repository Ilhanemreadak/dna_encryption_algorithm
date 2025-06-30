from datetime import datetime
from pathlib import Path
from PIL import Image, PngImagePlugin
from typing import Tuple, Optional, Dict, Any
from config import Config
from utils.validators import allowed_file
    
def make_dirs(filename: str) -> Tuple[str, str, str]:
    """
    Verilen bir dosya adı için zaman damgalı (timestamped) input ve output klasörleri oluşturur.

    Argümanlar:
        filename (str): Klasör yapısının oluşturulacağı dosya adı.

    Döndürür:
        Tuple[str, str, str]: Şu değerleri içeren bir tuple:
            - Input klasörünün yolu (str)
            - Output klasörünün yolu (str)
            - Hem input hem de output klasörleri için kullanılan base klasör adı (str)
    """
    ts = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
    base = f'{Path(filename).stem}_{ts}'
    base_dir = Config.UPLOAD_FOLDER / base
    in_dir  = base_dir / 'in'
    out_dir = base_dir / 'out'
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    return str(in_dir), str(out_dir), base

def get_file_from_directory(directory:str)->Optional[Tuple[str,str]]:
    """
    Belirtilen dizindeki 'in' klasöründen izin verilen ilk dosyanın adını ve yolunu döndürür.

    Argümanlar:
        directory (str): Dosyanın aranacağı ana dizin adı.

    Döndürür:
        Optional[Tuple[str, str]]: Bulunan ilk dosyanın (dosya adı, dosya yolu) tuple'ı veya None.
    """
    in_dir = Config.UPLOAD_FOLDER / directory / 'in'
    if not in_dir.exists(): return None
    for f in in_dir.iterdir():
        if allowed_file(f.name):
            return f.name, str(f)
    return None

def save_image_with_metadata(img:Image.Image, out_path:str, meta:Dict[str,Any]):
    """
    Saves a PIL Image to the specified path with additional metadata embedded as PNG text fields.

    Args:
        img (Image.Image): The PIL Image to save.
        out_path (str): The file path where the image will be saved.
        meta (Dict[str, Any]): A dictionary containing metadata to embed, such as 'salt' and 'params'.
    """
    pnginfo = PngImagePlugin.PngInfo()
    for k in ['salt','params']:
        if k in meta:
            pnginfo.add_text(k, str(meta[k]))
    img.save(out_path, pnginfo=pnginfo)
