"""
توابع عمومی و پرکاربرد دیتابیس
همه ماژول‌ها از این توابع استفاده می‌کنند
"""

from models.database import query


def get_active_shift():
    """دریافت آخرین شیفت فعال"""
    sql = "SELECT ID_shift, tarkib FROM shift_namt ORDER BY ID_shift DESC LIMIT 1"
    return query(sql, fetch_one=True)


def get_departments():
    """دریافت لیست بخش‌ها"""
    sql = "SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh"
    return query(sql, fetch_all=True) or []


def get_personnel_list(search="", status="all", limit=100):
    """دریافت لیست پرسنل با قابلیت جستجو"""
    sql = "SELECT ID_person, nam, famil, kod_meli, isActiv FROM tbl_person WHERE 1=1"
    params = []
    
    if status == "active":
        sql += " AND isActiv = 1"
    elif status == "inactive":
        sql += " AND isActiv = 0"
    
    if search:
        sql += " AND (nam LIKE %s OR famil LIKE %s OR kod_meli LIKE %s)"
        s = f"%{search}%"
        params.extend([s, s, s])
    
    sql += " ORDER BY famil ASC LIMIT %s"
    params.append(limit)
    
    return query(sql, params=params, fetch_all=True) or []


def get_personnel_by_department(dept_id):
    """دریافت پرسنل یک بخش خاص"""
    sql = """
        SELECT p.ID_person, p.nam, p.famil, p.kod_meli
        FROM tbl_person p
        JOIN tbl_sazema_person s ON p.ID_person = s.nam_person
        WHERE s.nam_bakhsh = %s AND p.isActiv = 1
        AND (s.payani_sazmandehi = 0 OR s.payani_sazmandehi IS NULL)
    """
    return query(sql, params=(dept_id,), fetch_all=True) or []


def check_shift_owner(shift_id, user_id):
    """بررسی اینکه شیفت متعلق به این کاربر است"""
    sql = "SELECT ID_shift FROM shift_namt WHERE ID_shift = %s AND UserID = %s"
    result = query(sql, params=(shift_id, user_id), fetch_one=True)
    return result is not None