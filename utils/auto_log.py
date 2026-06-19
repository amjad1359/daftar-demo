"""
سیستم لاگینگ خودکار برای تمام فرم‌ها
"""
from utils.audit import log_action

# نگاشت نام تابع به جدول دیتابیس
TABLE_MAP = {
    'save_personnel': 'tbl_person',
    'save_shift': 'shift_namt',
    'save_gozaresh': 'tbl_gozaresh',
    'save_amar': 'tbl_amar_data',
    'save_ankal': 'tbl_ankal',
    'save_blood': 'tbl_blood_trans',
    'save_ghaybat': 'tbl_ghaybat',
    'save_attendance': 'tbl_hozor',
    'save_round': 'tbl_arziabi_bakhsh',
    'save_code': 'tbl_amliat_kod',
    'save_crisis': 'tbl_kod_omomy',
    'save_user': 'users',
    'save_permissions': 'userlevelpermissions',
    'delete_shift': 'shift_namt',
    'delete_ankal': 'tbl_ankal',
    'delete_ghaybat': 'tbl_ghaybat',
    'delete_blood': 'tbl_blood_trans',
    'delete_round': 'tbl_arziabi_bakhsh',
    'delete_code': 'tbl_amliat_kod',
    'delete_crisis': 'tbl_kod_omomy',
    'delete_report': 'tbl_gozaresh',
    'update_shift': 'shift_namt',
    'update_ankal': 'tbl_ankal',
    'approve_matron_report': 'tbl_gozaresh_modir_parastari',
    'save_fanni_opinion': 'tbl_nazar_fanni',
    'save_raiss_order': 'tbl_nazar_raiis',
    'save_manager_response': 'tbl_pasokh_modir_javab',
    'save_dashboard_content': 'dashboard_content',
    'save_logo': 'site_settings',
    'save_org_record': 'tbl_sazema_person',
    'delete_org_record': 'tbl_sazema_person',
    'delete_personnel': 'tbl_person',
    'add_title_api': 'tbl_arzibi_onvan',
    'save_item_api': 'tbl_arziabi_cheklist',
    'update_item_api': 'tbl_arziabi_cheklist',
    'add_code_api': 'tbl_onvan_kod',
    'update_code_api': 'tbl_onvan_kod',
    'delete_code_api': 'tbl_onvan_kod',
    'add_role_api': 'tbl_onvan_naghsh',
    'update_role_api': 'tbl_onvan_naghsh',
    'delete_role_api': 'tbl_onvan_naghsh',
    'save_user': 'users',
    'save_item': 'tbl_nam_modiriat',
    'update_item': 'tbl_nam_modiriat',
    'delete_item': 'tbl_nam_modiriat',
    'save_role': 'tbl_onvan_naghsh_bohran',
    'update_role': 'tbl_onvan_naghsh_bohran',
    'delete_role': 'tbl_onvan_naghsh_bohran',
    'save_assign': 'tbl_chart_bohran',
    'update_assign': 'tbl_chart_bohran',
    'delete_assign': 'tbl_chart_bohran',
    'save_title': 'tbl_onvan_kod_omomy',
    'delete_title': 'tbl_onvan_kod_omomy',
    'save_level': 'tbl_sath_bohran',
    'delete_level': 'tbl_sath_bohran',
    'save_level': 'accesslevels',
    'update_level': 'accesslevels',
    'delete_level': 'accesslevels',
    'save_ward': 'tbl_bakhsh',
    'update_ward': 'tbl_bakhsh',
    'delete_ward': 'tbl_bakhsh', 
    'save_job': 'tbl_onvan_shoghl',
    'update_job': 'tbl_onvan_shoghl',
    'delete_job': 'tbl_onvan_shoghl',
    'save_specialty': 'tbl_onvan_takhasos',
    'update_specialty': 'tbl_onvan_takhasos',
    'delete_specialty': 'tbl_onvan_takhasos',                          
    'save_shift_title': 'onvan_shift',
    'update_shift_title': 'onvan_shift',
    'delete_shift_title': 'onvan_shift',
    'save_amar_item': 'tbl_amar_items',
    'delete_amar_item': 'tbl_amar_items',
    'assign_amar_config': 'tbl_bakhsh_amar_config',
    'delete_amar_config': 'tbl_bakhsh_amar_config',
    'save_dashboard': 'dashboard_content',
    'delete_dashboard': 'dashboard_content',

















       
}


def log_crud(action_name, user_id, table_name=None, key_value=None,
             old_value=None, new_value=None, status="Success", error_msg=None):
    """
    ثبت خودکار لاگ برای عملیات CRUD

    پارامترها:
        action_name: نام تابع فعلی (مثلاً 'save_personnel')
        user_id: شناسه کاربر
        table_name: نام جدول - اگر None باشد، از TABLE_MAP خوانده می‌شود
        key_value: مقدار کلید رکورد (ID)
        old_value: مقدار قبلی
        new_value: مقدار جدید
        status: "Success" یا "Failed"
        error_msg: پیام خطا
    """
    # تشخیص نوع عملیات
    action = "UNKNOWN"
    if 'save' in action_name or 'insert' in action_name.lower():
        if key_value and old_value:
            action = "UPDATE"
        else:
            action = "INSERT"
    elif 'delete' in action_name:
        action = "DELETE"
    elif 'update' in action_name:
        action = "UPDATE"
    elif 'approve' in action_name or 'verify' in action_name:
        action = "APPROVE"
    elif 'login' in action_name.lower():
        action = "Login"
    elif 'logout' in action_name.lower():
        action = "Logout"

    # اگر نام جدول داده نشده، از TABLE_MAP بخوان
    if not table_name:
        table_name = TABLE_MAP.get(action_name, "Unknown")

    # محدود کردن طول مقادیر
    if old_value and len(str(old_value)) > 500:
        old_value = str(old_value)[:497] + '...'
    if new_value and len(str(new_value)) > 500:
        new_value = str(new_value)[:497] + '...'

    # ثبت لاگ با تابع اصلی
    log_action(
        action=action,
        user_id=user_id,
        table_name=table_name,
        key_value=key_value,
        old_value=old_value,
        new_value=new_value,
        status=status,
        error_msg=error_msg
    )
    
    