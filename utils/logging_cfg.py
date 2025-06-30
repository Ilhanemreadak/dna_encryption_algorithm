import logging
from werkzeug.serving import WSGIRequestHandler

def setup_logging():
    """
    Uygulamanın logging yapılandırmasını (logging configuration) ayarlayan fonksiyon.
    Bu fonksiyon, logging seviyesini (logging level) INFO olarak belirler, log formatını (log format) ayarlar ve hem dosyaya (FileHandler ile 'app.log') hem de konsola (StreamHandler) log kaydı yapılmasını sağlar. Fonksiyon, 'app' isimli bir logger nesnesi (logger object) döndürür.
    Returns:
        logging.Logger: 'app' isimli logger nesnesi.
    """
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[ logging.FileHandler('app.log'), logging.StreamHandler() ]
    )
    return logging.getLogger('app')

class SafeRequestHandler(WSGIRequestHandler):
    """
    SafeRequestHandler, WSGIRequestHandler sınıfını genişleten bir handler'dır.
    log_request metodunu override ederek, loglama sırasında oluşabilecek UnicodeEncodeError hatalarını yakalar.
    Bu hata oluştuğunda, ilgili isteğin log kaydını atlar ve 'werkzeug' logger'ı ile uyarı mesajı ("Binary request omitted") verir.
    Bu sayede, binary veya encode edilemeyen isteklerin loglama sürecinde uygulamanın hata vermesi engellenir.

    Attributes:
        Inherits all attributes from WSGIRequestHandler.

    Methods:
        log_request(code='-', size='-'): 
            HTTP request loglanırken UnicodeEncodeError oluşursa, hata mesajı loglar ve işlemi güvenli şekilde tamamlar.
    """
    def log_request(self, code='-', size='-'):
        from logging import getLogger
        try: super().log_request(code, size)
        except UnicodeEncodeError:
            getLogger('werkzeug').warning("Binary request omitted")
