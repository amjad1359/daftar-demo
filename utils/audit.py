"""
ثبت لاگ در جدول audittrail
"""

from models.database import query
from datetime import datetime


def log_action(action, user_id=None, table_name=None, field=None, 
               key_value=None, old_value=None, new_value=None, 
               status="Success", error_msg=None):
    """ثبت یک عملیات در جدول لاگ"""
    
    now = datetime.now()
    
    sql = """
        INSERT INTO audittrail 
        (DateTime, Script, User, Action, `Table`, Field, KeyValue, 
         OldValue, NewValue, Status, ErrorMessage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    params = (
        now,
        "app.py",
        f"UserID:{user_id}" if user_id else "Unknown",
        action,
        table_name,
        field,
        str(key_value) if key_value else None,
        str(old_value)[:500] if old_value else None,
        str(new_value)[:500] if new_value else None,
        status,
        error_msg
    )
    
    try:
        query(sql, params=params, commit=True)
    except Exception as e:
        print(f"[AUDIT ERROR] {e}")