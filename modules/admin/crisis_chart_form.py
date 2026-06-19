"""
تنظیمات چارت بحران – ادمین (بازنویسی کامل با D3.js + d3-org-chart نسخه ۲)
مدیریت نقش‌ها، انتصابات، عناوین و سطوح بحران + نمایش چارت سازمانی مدرن
رفع باگ از هم‌گسیختگی درخت (D3 Missing Parent Error) و بهینه‌سازی ساختاری
"""

from models.database import query
import json
from utils.auto_log import log_crud
import jdatetime
from datetime import datetime
from flask import render_template

# ==========================================
# توابع کمکی (Helper Functions)
# ==========================================

def _last_insert_id(table, column):
    # برای جلوگیری از تداخل در درخواست‌های همزمان، بهتر است در صورت امکان 
    # از SELECT LAST_INSERT_ID() استفاده شود، اما برای حفظ سازگاری با ساختار شما:
    row = query(f"SELECT MAX({column}) as max_id FROM {table}", fetch_one=True)
    return row['max_id'] if row and row['max_id'] else None


def get_crisis_chart_form(user):
    return render_template('admin/crisis_chart.html')

# ==========================================
# بخش API ها (توابع اصلی و کنترلرها)
# ==========================================

# ---------- مدیریت نقش‌ها (Roles) ----------

def get_roles_list():
    items = query("SELECT * FROM tbl_onvan_naghsh_bohran ORDER BY mahal2, mahal4", fetch_all=True) or []
    return {'success': True, 'items': items}

def get_role_detail(role_id):
    item = query("SELECT * FROM tbl_onvan_naghsh_bohran WHERE ID_onvan_naghsh_bohran = %s", (role_id,), fetch_one=True)
    return {'success': True, 'item': item} if item else {'success': False, 'message': 'نقش یافت نشد'}

def save_role(user, form_data):
    user_id = user.get('UserID', 0)
    name = form_data.get('name', '').strip()
    if not name: 
        return {'success': False, 'message': 'نام نقش الزامی است'}
    
    query("""INSERT INTO tbl_onvan_naghsh_bohran 
             (nam_onvan_naghsh_bohran, tozihat, mahal1, mahal2, mahal3, mahal4, rang_bohran)
             VALUES (%s, %s, %s, %s, %s, %s, %s)""",
          (name, 
           form_data.get('desc', ''), 
           form_data.get('parent') or 0,
           form_data.get('level', 1), 
           1, 
           form_data.get('order', 1), 
           form_data.get('color', '#3498db')), commit=True)
    
    new_id = _last_insert_id('tbl_onvan_naghsh_bohran', 'ID_onvan_naghsh_bohran')
    log_data = {
        "name": name, 
        "parent": form_data.get('parent'), 
        "level": form_data.get('level'), 
        "order": form_data.get('order'), 
        "color": form_data.get('color')
    }
    
    log_crud('save_role', user_id, key_value=new_id, new_value=json.dumps(log_data, ensure_ascii=False))
    return {'success': True, 'message': 'نقش با موفقیت ثبت شد'}

def update_role(user, form_data):
    user_id = user.get('UserID', 0)
    role_id = form_data.get('id')
    name = form_data.get('name', '').strip()
    
    if not name: 
        return {'success': False, 'message': 'نام نقش الزامی است'}
        
    old_record = query("SELECT * FROM tbl_onvan_naghsh_bohran WHERE ID_onvan_naghsh_bohran=%s", (role_id,), fetch_one=True)
    
    query("""UPDATE tbl_onvan_naghsh_bohran 
             SET nam_onvan_naghsh_bohran=%s, tozihat=%s, mahal1=%s, mahal2=%s, mahal3=%s, mahal4=%s, rang_bohran=%s
             WHERE ID_onvan_naghsh_bohran=%s""",
          (name, form_data.get('desc', ''), form_data.get('parent') or 0, form_data.get('level', 1),
           1, form_data.get('order', 1), form_data.get('color', '#3498db'), role_id), commit=True)
           
    log_data = {
        "name": name, 
        "parent": form_data.get('parent'), 
        "level": form_data.get('level'), 
        "order": form_data.get('order'), 
        "color": form_data.get('color')
    }
    
    log_crud('update_role', user_id, key_value=role_id,
             old_value=json.dumps(old_record, ensure_ascii=False, default=str),
             new_value=json.dumps(log_data, ensure_ascii=False))
             
    return {'success': True, 'message': 'نقش با موفقیت ویرایش شد'}

def delete_role(user, form_data):
    user_id = user.get('UserID', 0)
    role_id = form_data.get('id')
    
    used = query("SELECT COUNT(*) as cnt FROM tbl_chart_bohran WHERE id_nam_nagsh = %s", (role_id,), fetch_one=True)
    if used and used['cnt'] > 0:
        return {'success': False, 'message': 'این نقش در چار‌ت‌های بحران دارای انتصاب است و قابل حذف نیست'}
        
    old_record = query("SELECT * FROM tbl_onvan_naghsh_bohran WHERE ID_onvan_naghsh_bohran=%s", (role_id,), fetch_one=True)
    query("DELETE FROM tbl_onvan_naghsh_bohran WHERE ID_onvan_naghsh_bohran = %s", (role_id,), commit=True)
    log_crud('delete_role', user_id, key_value=role_id, old_value=json.dumps(old_record, ensure_ascii=False, default=str))
    
    return {'success': True, 'message': 'نقش با موفقیت حذف شد'}

def move_role(user, form_data):
    user_id = user.get('UserID', 0)
    role_id = form_data.get('id')
    direction = form_data.get('direction')
    
    if not role_id or direction not in ('up', 'down'):
        return {'success': False, 'message': 'پارامترهای ارسالی نامعتبر است'}
        
    role = query("SELECT * FROM tbl_onvan_naghsh_bohran WHERE ID_onvan_naghsh_bohran = %s", (role_id,), fetch_one=True)
    if not role: 
        return {'success': False, 'message': 'نقش یافت نشد'}
        
    parent = role['mahal1'] or 0
    level = role['mahal2']
    
    siblings = query("SELECT ID_onvan_naghsh_bohran, mahal4 FROM tbl_onvan_naghsh_bohran WHERE mahal1 = %s AND mahal2 = %s ORDER BY mahal4", (parent, level), fetch_all=True) or []
    current_index = next((i for i, s in enumerate(siblings) if s['ID_onvan_naghsh_bohran'] == int(role_id)), None)
    
    if current_index is None: 
        return {'success': False, 'message': 'موقعیت نقش در لیست جهت جابجایی یافت نشد'}
        
    if direction == 'up' and current_index > 0:
        swap_with = siblings[current_index - 1]
    elif direction == 'down' and current_index < len(siblings) - 1:
        swap_with = siblings[current_index + 1]
    else:
        return {'success': False, 'message': 'امکان جابجایی در این جهت وجود ندارد'}
        
    old_order = role['mahal4']
    new_order = swap_with['mahal4']
    
    query("UPDATE tbl_onvan_naghsh_bohran SET mahal4 = %s WHERE ID_onvan_naghsh_bohran = %s", (new_order, role_id), commit=True)
    query("UPDATE tbl_onvan_naghsh_bohran SET mahal4 = %s WHERE ID_onvan_naghsh_bohran = %s", (old_order, swap_with['ID_onvan_naghsh_bohran']), commit=True)
    
    log_crud('move_role', user_id, key_value=role_id,
             new_value=json.dumps({"action": "move", "direction": direction, "swapped_with": swap_with['ID_onvan_naghsh_bohran']}, ensure_ascii=False))
             
    return {'success': True, 'message': 'ترتیب نقش‌ها با موفقیت بروزرسانی شد'}


# ---------- مدیریت انتصابات (Assignments) ----------

def get_assigns_list():
    items = query("""SELECT c.*, CONCAT(p.nam,' ',p.famil) as person_name, r.nam_onvan_naghsh_bohran as role_name,
                     k.nam_kod_o as crisis_name, s.nam_sath_bohran as level_name
                     FROM tbl_chart_bohran c 
                     LEFT JOIN tbl_person p ON c.id_person=p.ID_person
                     LEFT JOIN tbl_onvan_naghsh_bohran r ON c.id_nam_nagsh=r.ID_onvan_naghsh_bohran
                     LEFT JOIN tbl_onvan_kod_omomy k ON c.nam_bohran=k.ID_onvan_kod_o
                     LEFT JOIN tbl_sath_bohran s ON c.Id_sath_bohran=s.Id_sath_bohran 
                     ORDER BY c.ID_chart_bohran DESC""", fetch_all=True) or []
    return {'success': True, 'items': items}

def get_assign_detail(assign_id):
    item = query("SELECT * FROM tbl_chart_bohran WHERE ID_chart_bohran = %s", (assign_id,), fetch_one=True)
    return {'success': True, 'item': item} if item else {'success': False, 'message': 'انتصاب یافت نشد'}

def save_assign(user, form_data):
    user_id = user.get('UserID', 0)
    person = form_data.get('person')
    role = form_data.get('role')
    crisis = form_data.get('crisis')
    level = form_data.get('level')
    
    if not all([person, role, crisis, level]): 
        return {'success': False, 'message': 'تمامی فیلدهای ستاره‌دار الزامی هستند'}
        
    dup = query("SELECT COUNT(*) as cnt FROM tbl_chart_bohran WHERE nam_bohran=%s AND Id_sath_bohran=%s AND id_person=%s AND id_nam_nagsh=%s",
                (crisis, level, person, role), fetch_one=True)
    if dup and dup['cnt'] > 0: 
        return {'success': False, 'message': 'این شخص قبلاً به این نقش در همین سطح و بحران منتصب شده است'}
        
    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now().strftime("%H:%M:%S")
    
    query("""INSERT INTO tbl_chart_bohran (nam_bohran, Id_sath_bohran, id_person, id_nam_nagsh, description, dat_sabt, zaman_sabt, UserID)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
          (crisis, level, person, role, form_data.get('desc', ''), today, now, user_id), commit=True)
          
    new_id = _last_insert_id('tbl_chart_bohran', 'ID_chart_bohran')
    log_data = {"person": person, "role": role, "crisis": crisis, "level": level}
    log_crud('save_assign', user_id, key_value=new_id, new_value=json.dumps(log_data, ensure_ascii=False))
    
    return {'success': True, 'message': 'انتصاب با موفقیت در سیستم ثبت شد'}

def update_assign(user, form_data):
    user_id = user.get('UserID', 0)
    assign_id = form_data.get('id')
    person = form_data.get('person')
    role = form_data.get('role')
    crisis = form_data.get('crisis')
    level = form_data.get('level')
    
    if not all([assign_id, person, role, crisis, level]):
        return {'success': False, 'message': 'اطلاعات ارسالی ناقص است'}
        
    old_record = query("SELECT * FROM tbl_chart_bohran WHERE ID_chart_bohran=%s", (assign_id,), fetch_one=True)
    query("""UPDATE tbl_chart_bohran 
             SET nam_bohran=%s, Id_sath_bohran=%s, id_person=%s, id_nam_nagsh=%s, description=%s
             WHERE ID_chart_bohran=%s""",
          (crisis, level, person, role, form_data.get('desc', ''), assign_id), commit=True)
          
    log_data = {"person": person, "role": role, "crisis": crisis, "level": level}
    log_crud('update_assign', user_id, key_value=assign_id,
             old_value=json.dumps(old_record, ensure_ascii=False, default=str),
             new_value=json.dumps(log_data, ensure_ascii=False))
             
    return {'success': True, 'message': 'انتصاب با موفقیت بروزرسانی شد'}

def delete_assign(user, form_data):
    user_id = user.get('UserID', 0)
    assign_id = form_data.get('id')
    
    old_record = query("SELECT * FROM tbl_chart_bohran WHERE ID_chart_bohran=%s", (assign_id,), fetch_one=True)
    query("DELETE FROM tbl_chart_bohran WHERE ID_chart_bohran = %s", (assign_id,), commit=True)
    
    log_crud('delete_assign', user_id, key_value=assign_id, old_value=json.dumps(old_record, ensure_ascii=False, default=str))
    return {'success': True, 'message': 'انتصاب از سیستم حذف شد'}


# ---------- مدیریت عناوین بحران (Crisis Titles) ----------

def get_titles_list():
    items = query("SELECT * FROM tbl_onvan_kod_omomy ORDER BY ID_onvan_kod_o DESC", fetch_all=True) or []
    return {'success': True, 'items': items}

def save_title(user, form_data):
    user_id = user.get('UserID', 0)
    name = form_data.get('name', '').strip()
    if not name: 
        return {'success': False, 'message': 'عنوان بحران الزامی است'}
        
    query("INSERT INTO tbl_onvan_kod_omomy (nam_kod_o) VALUES (%s)", (name,), commit=True)
    new_id = _last_insert_id('tbl_onvan_kod_omomy', 'ID_onvan_kod_o')
    
    log_crud('save_title', user_id, key_value=new_id, new_value=json.dumps({"name": name}, ensure_ascii=False))
    return {'success': True, 'message': 'عنوان بحران با موفقیت ثبت شد'}

def update_title(user, form_data):
    user_id = user.get('UserID', 0)
    title_id = form_data.get('id')
    name = form_data.get('name', '').strip()
    if not name: 
        return {'success': False, 'message': 'نام عنوان الزامی است'}
        
    old_record = query("SELECT * FROM tbl_onvan_kod_omomy WHERE ID_onvan_kod_o=%s", (title_id,), fetch_one=True)
    query("UPDATE tbl_onvan_kod_omomy SET nam_kod_o=%s WHERE ID_onvan_kod_o=%s", (name, title_id), commit=True)
    
    log_crud('update_title', user_id, key_value=title_id,
             old_value=json.dumps(old_record, ensure_ascii=False, default=str),
             new_value=json.dumps({"name": name}, ensure_ascii=False))
    return {'success': True, 'message': 'عنوان بحران ویرایش شد'}

def delete_title(user, form_data):
    user_id = user.get('UserID', 0)
    title_id = form_data.get('id')
    
    used = query("SELECT COUNT(*) as cnt FROM tbl_chart_bohran WHERE nam_bohran = %s", (title_id,), fetch_one=True)
    if used and used['cnt'] > 0:
        return {'success': False, 'message': 'این بحران در بخش انتصابات مورد استفاده قرار گرفته و قابل حذف نیست'}
        
    old_record = query("SELECT * FROM tbl_onvan_kod_omomy WHERE ID_onvan_kod_o=%s", (title_id,), fetch_one=True)
    query("DELETE FROM tbl_onvan_kod_omomy WHERE ID_onvan_kod_o = %s", (title_id,), commit=True)
    
    log_crud('delete_title', user_id, key_value=title_id, old_value=json.dumps(old_record, ensure_ascii=False, default=str))
    return {'success': True, 'message': 'عنوان بحران با موفقیت حذف شد'}


# ---------- مدیریت سطوح بحران (Crisis Levels) ----------

def get_levels_list():
    items = query("SELECT * FROM tbl_sath_bohran ORDER BY Id_sath_bohran", fetch_all=True) or []
    return {'success': True, 'items': items}

def save_level(user, form_data):
    user_id = user.get('UserID', 0)
    name = form_data.get('name', '').strip()
    if not name: 
        return {'success': False, 'message': 'نام سطح الزامی است'}
        
    query("INSERT INTO tbl_sath_bohran (nam_sath_bohran, tozaihat) VALUES (%s,%s)", 
          (name, form_data.get('desc', '')), commit=True)
          
    new_id = _last_insert_id('tbl_sath_bohran', 'Id_sath_bohran')
    log_crud('save_level', user_id, key_value=new_id, new_value=json.dumps({"name": name}, ensure_ascii=False))
    return {'success': True, 'message': 'سطح بحران با موفقیت ثبت شد'}

def update_level(user, form_data):
    user_id = user.get('UserID', 0)
    level_id = form_data.get('id')
    name = form_data.get('name', '').strip()
    if not name: 
        return {'success': False, 'message': 'نام سطح الزامی است'}
        
    old_record = query("SELECT * FROM tbl_sath_bohran WHERE Id_sath_bohran=%s", (level_id,), fetch_one=True)
    query("UPDATE tbl_sath_bohran SET nam_sath_bohran=%s, tozaihat=%s WHERE Id_sath_bohran=%s",
          (name, form_data.get('desc', ''), level_id), commit=True)
          
    log_crud('update_level', user_id, key_value=level_id,
             old_value=json.dumps(old_record, ensure_ascii=False, default=str),
             new_value=json.dumps({"name": name}, ensure_ascii=False))
    return {'success': True, 'message': 'سطح بحران با موفقیت ویرایش شد'}

def delete_level(user, form_data):
    user_id = user.get('UserID', 0)
    level_id = form_data.get('id')
    
    used = query("SELECT COUNT(*) as cnt FROM tbl_chart_bohran WHERE Id_sath_bohran = %s", (level_id,), fetch_one=True)
    if used and used['cnt'] > 0:
        return {'success': False, 'message': 'این سطح در بخش انتصابات استفاده شده است و قابل حذف نیست'}
        
    old_record = query("SELECT * FROM tbl_sath_bohran WHERE Id_sath_bohran=%s", (level_id,), fetch_one=True)
    query("DELETE FROM tbl_sath_bohran WHERE Id_sath_bohran = %s", (level_id,), commit=True)
    
    log_crud('delete_level', user_id, key_value=level_id, old_value=json.dumps(old_record, ensure_ascii=False, default=str))
    return {'success': True, 'message': 'سطح بحران با موفقیت حذف شد'}


# ---------- اشخاص و دریافت دیتای نمودار (Persons & Chart Data) ----------

def get_persons_list():
    items = query("SELECT ID_person, CONCAT(nam,' ',famil) as FullName FROM tbl_person WHERE isActiv=1 ORDER BY famil", fetch_all=True) or []
    return {'success': True, 'items': items}


def get_chart_data(level_id=None):
    """
    دریافت اطلاعات چارت سازمانی.
    برای رفع خطای D3 Missing Parent، در زمان فیلتر بر اساس سطح، 
    الگوریتم بازگشتی تمامی والدهای نقش‌های انتصاب‌یافته را نیز واکشی می‌کند.
    """
    # 1. واکشی تمامی نقش‌های موجود به عنوان دیتابیس مرجع
    all_roles = query(
        "SELECT * FROM tbl_onvan_naghsh_bohran "
        "WHERE nam_onvan_naghsh_bohran IS NOT NULL AND nam_onvan_naghsh_bohran != '' "
        "ORDER BY mahal1, mahal2, mahal3, mahal4",
        fetch_all=True
    ) or []

    final_roles = all_roles
    
    if level_id:
        # 2. پیدا کردن نقش‌هایی که مستقیماً در این سطح دارای انتصاب هستند
        assigned_records = query(
            "SELECT DISTINCT id_nam_nagsh FROM tbl_chart_bohran WHERE Id_sath_bohran = %s",
            (level_id,), fetch_all=True
        ) or []
        
        assigned_role_ids = {r['id_nam_nagsh'] for r in assigned_records}
        
        # 3. ساخت نگاشت والد-فرزندی برای پیدا کردن سریع والدها
        # ساختار: {role_id: parent_id}
        parent_map = {r['ID_onvan_naghsh_bohran']: (r['mahal1'] or 0) for r in all_roles}
        
        # 4. الگوریتم بازگشتی جهت افزودن تمام والدها به مجموعه مورد نیاز (ترمیم درخت)
        required_role_ids = set(assigned_role_ids)
        
        for role_id in assigned_role_ids:
            current_id = role_id
            while current_id in parent_map and parent_map[current_id] != 0:
                parent_id = parent_map[current_id]
                if parent_id in required_role_ids:
                    break # این شاخه قبلا پردازش شده است
                required_role_ids.add(parent_id)
                current_id = parent_id
                
        # 5. فیلتر نهایی نقش‌ها بر اساس شناسه‌های استخراج شده
        final_roles = [r for r in all_roles if r['ID_onvan_naghsh_bohran'] in required_role_ids]

    # 6. واکشی اطلاعات انتصابات (پرسنل متصل به نقش‌ها)
    params = []
    condition = ""
    if level_id:
        condition = "WHERE c.Id_sath_bohran = %s"
        params.append(level_id)

    assignments = query(f"""SELECT c.id_nam_nagsh, CONCAT(p.nam,' ',p.famil) as person_name,
                                  k.nam_kod_o as crisis_name
                          FROM tbl_chart_bohran c 
                          JOIN tbl_person p ON c.id_person=p.ID_person
                          LEFT JOIN tbl_onvan_kod_omomy k ON c.nam_bohran=k.ID_onvan_kod_o
                          {condition}""", tuple(params) if params else None, fetch_all=True) or []

    return {'success': True, 'roles': final_roles, 'assignments': assignments}
    
    