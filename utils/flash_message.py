from flask import session

def set_flash(message, category='success'):
    """ذخیره یک پیام موقت در session برای نمایش در صفحه بعد"""
    session['_flash_message'] = message
    session['_flash_category'] = category

def get_flash():
    """بازیابی و پاک کردن پیام فلش از session"""
    msg = session.pop('_flash_message', None)
    cat = session.pop('_flash_category', 'success')
    if msg:
        return msg, cat
    return None, None
    
    