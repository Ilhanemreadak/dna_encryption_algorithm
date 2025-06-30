from flask import request, jsonify
from functools import wraps
from typing import List, Dict, Any
from config import Config

def allowed_file(filename:str)->bool:
    return '.' in filename and filename.rsplit('.',1)[1].lower() in Config.ALLOWED_EXT

def validate_numeric_params(params:Dict[str,Any])->Dict[str,Any]:
    """
    Numerik parametreleri validate eder.
    
    Args:
        params: Parametre dictionary'si
        
    Returns:
        Dict[str, Any]: Validate edilmiş parametreler
        
    Raises:
        ValueError: Geçersiz parametre durumunda
    """
    validated = {}
    
    # DNA rule validasyonu
    if 'dna_rule' in params:
        dna_rule = int(params['dna_rule'])
        if not (1 <= dna_rule <= 8):  # DNA kuralları genellikle 1-8 arası
            raise ValueError("DNA kuralı 1-8 arasında olmalıdır")
        validated['dna_rule'] = dna_rule
    
    # Liste parametreleri validasyonu
    for param in ['x0_list', 'r_list']:
        if param in params:
            values = params[param]
            if not isinstance(values, list) or len(values) == 0:
                raise ValueError(f"{param} geçerli bir liste olmalıdır")
            validated[param] = values
    
    return validated

def validate_request(*, required_fields:List[str]=None, file_fields:List[str]=None):
    """
    Flask isteğinde gerekli form alanlarını ve dosya yüklemelerini doğrulayan decorator.
    Argümanlar:
        required_fields (List[str], opsiyonel): 
            Zorunlu olması gereken form alanlarının isimleri. 
            Her bir alanın request.form veya request.files içinde olup olmadığı kontrol edilir.
        file_fields (List[str], opsiyonel): 
            Dosya olarak yüklenmesi gereken alanların isimleri. 
            Her bir dosyanın allowed_file fonksiyonu ile uzantısı kontrol edilir.
    Döndürür:
        function: 
            Orijinal fonksiyonu saran ve validasyonları gerçekleştiren decorator fonksiyonu.
    Hatalar:
        400 Bad Request: 
            Eğer bir zorunlu alan eksikse veya dosya formatı geçersizse, 
            JSON formatında hata mesajı ile birlikte 400 HTTP hatası döner.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*a,**kw):
            # Dosya validasyonu
            if file_fields:
                for field in file_fields:
                    file = request.files.get(field)
                    if file and not allowed_file(file.filename):
                        return jsonify({
                            'status': 'error', 
                            'message': f'Geçersiz dosya formatı: {field}'
                        }), 400
            
            # Gerekli alan validasyonu
            if required_fields:
                for field in required_fields:
                    if not request.form.get(field) and not request.files.get(field):
                        return jsonify({
                            'status': 'error', 
                            'message': f'Gerekli alan eksik: {field}'
                        }), 400
            return f(*a,**kw)
        return wrapper
    return decorator
