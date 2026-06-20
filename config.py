import os

class Config:
    # دیتابیس – خواندن از متغیرهای محیطی با fallback به مقادیر لوکال
    MYSQL_HOST     = os.environ.get('DB_HOST', 'localhost')
    MYSQL_PORT     = int(os.environ.get('DB_PORT', 3306))
    MYSQL_USER     = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('DB_NAME', 'daftar5')
    MYSQL_CHARSET  = 'utf8mb4'
    
    # مسیرها
    UPLOAD_FOLDER = "uploads"
    STATIC_FOLDER = "assets"
    
    # امنیت
    SESSION_TIMEOUT = 3600  # ۱ ساعت
    SECRET_KEY = "daft_nursing_permanent_secret_key_1394_fixed"

    
