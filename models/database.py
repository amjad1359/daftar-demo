
import mysql.connector
from mysql.connector import Error, pooling
from config import Config

# ==================== Pool Configuration ====================
_pool = None

def get_pool():
    """ایجاد یا بازگرداندن Pool اتصالات یکتا"""
    global _pool
    if _pool is None:
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name="daftar_pool",
                pool_size=10,
                pool_reset_session=False,
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,          # ← اضافه شود
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                charset=Config.MYSQL_CHARSET,
                use_unicode=True,
                autocommit=True
            )          
            
            print("[DB] Connection pool created successfully.")
        except Error as e:
            print(f"[DB ERROR] Pool creation failed: {e}")
            return None
    return _pool


def get_connection():
    """دریافت یک اتصال از Pool (یا ایجاد new در صورت عدم وجود Pool)"""
    pool = get_pool()
    if pool:
        try:
            conn = pool.get_connection()
            return conn
        except Error as e:
            print(f"[DB ERROR] Cannot get connection from pool: {e}")
            return None
    else:
        # Fallback (اگر Pool ساخته نشد)
        print("[DB WARNING] Pool not available, using single connection.")
        try:
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,          # ← اضافه شود
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                charset=Config.MYSQL_CHARSET,
                use_unicode=True,
                autocommit=True
            )           
            return conn
        except Error as e:
            print(f"[DB ERROR] Direct connection failed: {e}")
            return None


def _safe_str(value):
    """تبدیل bytearray/bytes به string"""
    if value is None:
        return ""
    if isinstance(value, (bytearray, bytes)):
        return value.decode('utf-8', errors='ignore')
    return str(value)


def _fix_row(row):
    """اصلاح فیلدهای bytearray"""
    if not row:
        return row
    for key, val in row.items():
        if isinstance(val, (bytearray, bytes)):
            row[key] = val.decode('utf-8', errors='ignore')
    return row


def query(sql, params=None, fetch_one=False, fetch_all=False, commit=False):
    """اجرای کوئری – اتصال را از Pool گرفته و بعد از کار به Pool برمی‌گرداند"""
    conn = get_connection()
    if not conn:
        return None

    cursor = None
    result = None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        if commit:
            # تضمین commit صریح (اگر autocommit خاموش باشد)
            conn.commit()
        elif fetch_one:
            result = cursor.fetchone()
            if result:
                result = _fix_row(result)
        elif fetch_all:
            result = cursor.fetchall()
            if result:
                result = [_fix_row(r) for r in result]

        return result

    except Error as e:
        print(f"[DB ERROR] {e}")
        if commit:
            conn.rollback()
        return None
    finally:
        if 'cursor' in locals() and cursor:
            try:
                cursor.close()
            except Exception:
                pass
                
        if 'conn' in locals() and conn:
            try:
                # بسیار مهم: اتصال را با close به Pool برمی‌گردانیم
                conn.close()
            except Exception as e:
                print(f"[DB WARN] Could not close connection cleanly: {e}")
        

        
