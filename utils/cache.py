import time
import hashlib
import json

_cache_store = {}

def cached_query(key, func, ttl=300, *args, **kwargs):
    """
    اجرای تابع func و کش کردن نتیجه برای ttl ثانیه.
    اگر نتیجه در کش وجود داشت و منقضی نشده باشد، مستقیماً از کش برمی‌گرداند.
    """
    # ساختن کلید یکتا با ترکیب نام تابع و پارامترها
    raw = key + json.dumps(args, sort_keys=True, default=str) + json.dumps(kwargs, sort_keys=True, default=str)
    hashed = hashlib.md5(raw.encode()).hexdigest()

    now = time.time()
    if hashed in _cache_store and (now - _cache_store[hashed]['time']) < ttl:
        return _cache_store[hashed]['data']

    # اجرای تابع و ذخیره در کش
    data = func(*args, **kwargs)
    _cache_store[hashed] = {'data': data, 'time': now}
    return data

def invalidate_cache(key_pattern=None):
    """حذف تمام یا بخشی از کش"""
    if key_pattern is None:
        _cache_store.clear()
    else:
        to_delete = [k for k in _cache_store if key_pattern in k]
        for k in to_delete:
            del _cache_store[k]
            
            
      