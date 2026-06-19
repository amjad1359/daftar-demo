"""
تنظیمات سراسری برنامه
"""

class Config:
    # دیتابیس
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DATABASE = "daftar5"
    MYSQL_CHARSET = "utf8mb4"
    
    # مسیرها
    UPLOAD_FOLDER = "uploads"
    STATIC_FOLDER = "assets"
    
    # امنیت
    SESSION_TIMEOUT = 3600  # ۱ ساعت
    SECRET_KEY = "daft_nursing_permanent_secret_key_1394_fixed"  # یک رشته ثابت و امن
    
    