from flask import Blueprint, session, request, jsonify, redirect, url_for
from utils.access_control import require_module_access
admin_bp = Blueprint('admin', __name__, url_prefix='/module/admin')

def require_login():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'لطفاً وارد شوید'})
    return None

# ====================   کاربران ====================

@admin_bp.route('/users')
def admin_users_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    from core.router import render_page
    return render_page('module/admin/users', user=session['user'])

    

@admin_bp.route('/users/list')
def admin_users_list():
    err = require_login()
    if err: return err
    from modules.admin.users_form import get_users_list_api
    return jsonify(get_users_list_api())

@admin_bp.route('/users/get/<int:user_id>')
def admin_users_get(user_id):
    err = require_login()
    if err: return err
    from modules.admin.users_form import get_user_detail
    return jsonify(get_user_detail(user_id))

@admin_bp.route('/users/save', methods=['POST'])
def admin_users_save():
    err = require_login()
    if err: return err
    from modules.admin.users_form import save_user
    from flask import request
    return jsonify(save_user(request.form, request.files))






# ── NEW: دریافت امضا ──────────────────────────────────────────────────────
@admin_bp.route('/users/signature/<int:user_id>')
def admin_users_signature(user_id):
    err = require_login()
    if err: return err
    from modules.admin.users_form import get_user_signature
    return jsonify(get_user_signature(user_id))
    
    
    
  # ====================   دسترسی  ==================== 
# ====================   ساب دسترسی ====================  


@admin_bp.route('/permissions/save', methods=['POST'])
def admin_permissions_save():
    err = require_login()
    if err: return err
    from modules.admin.permissions_form import save_permissions

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'message': 'داده‌ای دریافت نشد'}), 400

    return jsonify(save_permissions(session.get('user'), data))

@admin_bp.route('/sub_permissions/save', methods=['POST'])
def admin_save_sub_permissions():
    err = require_login()
    if err: return err
    from modules.admin.permissions_form import save_sub_permissions

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'message': 'داده‌ای دریافت نشد'}), 400

    return jsonify(save_sub_permissions(session.get('user'), data))
    

# ====================   لوگوی بیمارستان ====================
@admin_bp.route('/logo')
def admin_logo_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    from modules.admin.logo_form import get_logo_form
    from core.router import render_page
    return render_page('module/admin/logo', user=session['user'])

@admin_bp.route('/logo/save', methods=['POST'])
def save_hospital_logo():
    err = require_login()
    if err: return err
    from modules.admin.logo_form import save_logo
    file = request.files.get('logo')
    result = save_logo(session['user'], file)
    return jsonify(result)

@admin_bp.route('/logo/delete', methods=['POST'])
def delete_hospital_logo():
    err = require_login()
    if err: return err
    from modules.admin.logo_form import delete_logo
    result = delete_logo()
    return jsonify(result)

# ====================   فرم تنظیمات آمار ====================
@admin_bp.route('/statistics/items/list')
def admin_statistics_items_list():
    err = require_login()
    if err: return err
    from modules.admin.statistics_form import get_items_list
    return jsonify(get_items_list())

@admin_bp.route('/statistics/items/save', methods=['POST'])
def admin_statistics_items_save():
    err = require_login()
    if err: return err
    from modules.admin.statistics_form import save_item
    return jsonify(save_item(session.get('user'),request.form))

@admin_bp.route('/statistics/items/delete', methods=['POST'])
def admin_statistics_items_delete():
    err = require_login()
    if err: return err
    from modules.admin.statistics_form import delete_item
    return jsonify(delete_item(session.get('user'),request.form))

@admin_bp.route('/statistics/depts/list')
def admin_statistics_depts_list():
    err = require_login()
    if err: return err
    from modules.admin.statistics_form import get_depts_with_amar
    return jsonify(get_depts_with_amar())

@admin_bp.route('/statistics/config/list')
def admin_statistics_config_list():
    err = require_login()
    if err: return err
    from modules.admin.statistics_form import get_config_list
    return jsonify(get_config_list())

@admin_bp.route('/statistics/config/assign', methods=['POST'])
def admin_statistics_config_assign():
    err = require_login()
    if err: return err
    from modules.admin.statistics_form import assign_item_to_dept
    return jsonify(assign_item_to_dept(session.get('user'),request.form))

@admin_bp.route('/statistics/config/delete', methods=['POST'])
def admin_statistics_config_delete():
    err = require_login()
    if err: return err
    from modules.admin.statistics_form import delete_config
    return jsonify(delete_config(session.get('user'),request.form))

# ====================   فرم تخصص پزشکان ====================
@admin_bp.route('/specialties/list')
def admin_specialties_list():
    err = require_login()
    if err: return err
    from modules.admin.specialties_form import get_specialties_list
    return jsonify(get_specialties_list())

@admin_bp.route('/specialties/save', methods=['POST'])
def admin_specialties_save():
    err = require_login()
    if err: return err
    from modules.admin.specialties_form import save_specialty
    return jsonify(save_specialty(session.get('user'),request.form))

@admin_bp.route('/specialties/delete', methods=['POST'])
def admin_specialties_delete():
    err = require_login()
    if err: return err
    from modules.admin.specialties_form import delete_specialty
    return jsonify(delete_specialty(session.get('user'),request.form))

# ====================   عناوین شیفت ====================
@admin_bp.route('/shifts/list')
def admin_shifts_list():
    err = require_login()
    if err: return err
    from modules.admin.shift_titles_form import get_shifts_list
    return jsonify(get_shifts_list())

@admin_bp.route('/shifts/save', methods=['POST'])
def admin_shifts_save():
    err = require_login()
    if err: return err
    from modules.admin.shift_titles_form import save_shift
    return jsonify(save_shift(session.get('user'),request.form))

@admin_bp.route('/shifts/update', methods=['POST'])
def admin_shifts_update():
    err = require_login()
    if err: return err
    from modules.admin.shift_titles_form import update_shift
    return jsonify(update_shift(session.get('user'),request.form))

@admin_bp.route('/shifts/delete', methods=['POST'])
def admin_shifts_delete():
    err = require_login()
    if err: return err
    from modules.admin.shift_titles_form import delete_shift
    return jsonify(delete_shift(session.get('user'),request.form))


# ====================   نام سطوح دسترسی ====================
@admin_bp.route('/access_levels/list')
def admin_access_levels_list():
    err = require_login()
    if err: return err
    from modules.admin.access_levels_form import get_levels_list
    return jsonify(get_levels_list())

@admin_bp.route('/access_levels/save', methods=['POST'])
def admin_access_levels_save():
    err = require_login()
    if err: return err
    from modules.admin.access_levels_form import save_level
    return jsonify(save_level(session.get('user'),request.form))

@admin_bp.route('/access_levels/update', methods=['POST'])
def admin_access_levels_update():
    err = require_login()
    if err: return err
    from modules.admin.access_levels_form import update_level
    return jsonify(update_level(session.get('user'),request.form))

@admin_bp.route('/access_levels/delete', methods=['POST'])
def admin_access_levels_delete():
    err = require_login()
    if err: return err
    from modules.admin.access_levels_form import delete_level
    return jsonify(delete_level(session.get('user'),request.form))

# ====================   نام مدیریت‌ها ====================
@admin_bp.route('/departments/list')
def admin_departments_list():
    err = require_login()
    if err: return err
    from modules.admin.departments_form import get_list
    return jsonify(get_list())

@admin_bp.route('/departments/save', methods=['POST'])
def admin_departments_save():
    err = require_login()
    if err: return err
    from modules.admin.departments_form import save_item
    return jsonify(save_item(session.get('user'), request.form))

@admin_bp.route('/departments/update', methods=['POST'])
def admin_departments_update():
    err = require_login()
    if err: return err
    from modules.admin.departments_form import update_item
    return jsonify(update_item(session.get('user'), request.form))

@admin_bp.route('/departments/delete', methods=['POST'])
def admin_departments_delete():
    err = require_login()
    if err: return err
    from modules.admin.departments_form import delete_item
    return jsonify(delete_item(session.get('user'), request.form))

# ====================   مدیریت بخش‌ها ====================
@admin_bp.route('/wards/list')
def admin_wards_list():
    err = require_login()
    if err: return err
    from modules.admin.wards_form import get_list
    return jsonify(get_list())

@admin_bp.route('/wards/save', methods=['POST'])
def admin_wards_save():
    err = require_login()
    if err: return err
    from modules.admin.wards_form import save_item
    return jsonify(save_item(session.get('user'),request.form))

@admin_bp.route('/wards/update', methods=['POST'])
def admin_wards_update():
    err = require_login()
    if err: return err
    from modules.admin.wards_form import update_item
    return jsonify(update_item(session.get('user'),request.form))

@admin_bp.route('/wards/delete', methods=['POST'])
def admin_wards_delete():
    err = require_login()
    if err: return err
    from modules.admin.wards_form import delete_item
    return jsonify(delete_item(session.get('user'),request.form))

# ====================   عناوین شغلی ====================
@admin_bp.route('/jobs/list')
def admin_jobs_list():
    err = require_login()
    if err: return err
    from modules.admin.job_titles_form import get_list
    return jsonify(get_list())

@admin_bp.route('/jobs/save', methods=['POST'])
def admin_jobs_save():
    err = require_login()
    if err: return err
    from modules.admin.job_titles_form import save_item
    return jsonify(save_item(session.get('user'),request.form))

@admin_bp.route('/jobs/update', methods=['POST'])
def admin_jobs_update():
    err = require_login()
    if err: return err
    from modules.admin.job_titles_form import update_item
    return jsonify(update_item(session.get('user'),request.form))

@admin_bp.route('/jobs/delete', methods=['POST'])
def admin_jobs_delete():
    err = require_login()
    if err: return err
    from modules.admin.job_titles_form import delete_item
    return jsonify(delete_item(session.get('user'),request.form))

# ====================   چارت بحران ====================
@admin_bp.route('/crisis/roles/list')
def admin_crisis_roles_list():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import get_roles_list
    return jsonify(get_roles_list())

@admin_bp.route('/crisis/role/get/<int:role_id>')
def admin_crisis_role_get(role_id):
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import get_role_detail
    return jsonify(get_role_detail(role_id))


@admin_bp.route('/crisis/role/save', methods=['POST'])
def admin_crisis_role_save():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import save_role
    return jsonify(save_role(session.get('user'), request.form))


@admin_bp.route('/crisis/role/update', methods=['POST'])
def admin_crisis_role_update():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import update_role
    return jsonify(update_role(session.get('user'),request.form))

@admin_bp.route('/crisis/role/delete', methods=['POST'])
def admin_crisis_role_delete():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import delete_role
    return jsonify(delete_role(session.get('user'),request.form))

@admin_bp.route('/crisis/assigns/list')
def admin_crisis_assigns_list():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import get_assigns_list
    return jsonify(get_assigns_list())

@admin_bp.route('/crisis/assign/get/<int:assign_id>')
def admin_crisis_assign_get(assign_id):
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import get_assign_detail
    return jsonify(get_assign_detail(assign_id))

@admin_bp.route('/crisis/assign/save', methods=['POST'])
def admin_crisis_assign_save():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import save_assign
    return jsonify(save_assign(session.get('user'),request.form))

@admin_bp.route('/crisis/assign/update', methods=['POST'])
def admin_crisis_assign_update():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import update_assign
    return jsonify(update_assign(session.get('user'),request.form))

@admin_bp.route('/crisis/assign/delete', methods=['POST'])
def admin_crisis_assign_delete():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import delete_assign
    return jsonify(delete_assign(session.get('user'),request.form))

@admin_bp.route('/crisis/titles/list')
def admin_crisis_titles_list():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import get_titles_list
    return jsonify(get_titles_list())

@admin_bp.route('/crisis/title/save', methods=['POST'])
def admin_crisis_title_save():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import save_title
    return jsonify(save_title(session.get('user'),request.form))

@admin_bp.route('/crisis/title/delete', methods=['POST'])
def admin_crisis_title_delete():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import delete_title
    return jsonify(delete_title(session.get('user'),request.form))

@admin_bp.route('/crisis/levels/list')
def admin_crisis_levels_list():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import get_levels_list
    return jsonify(get_levels_list())

@admin_bp.route('/crisis/level/save', methods=['POST'])
def admin_crisis_level_save():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import save_level
    return jsonify(save_level(session.get('user'),request.form))

@admin_bp.route('/crisis/level/delete', methods=['POST'])
def admin_crisis_level_delete():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import delete_level
    return jsonify(delete_level(session.get('user'),request.form))

@admin_bp.route('/crisis/persons/list')
def admin_crisis_persons_list():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import get_persons_list
    return jsonify(get_persons_list())

@admin_bp.route('/crisis/chart/data')
def admin_crisis_chart_data():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import get_chart_data
    level_id = request.args.get('level')
    return jsonify(get_chart_data(level_id))

@admin_bp.route('/crisis/title/update', methods=['POST'])
def admin_crisis_title_update():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import update_title
    return jsonify(update_title(session.get('user'), request.form))



@admin_bp.route('/crisis/level/update', methods=['POST'])
def admin_crisis_level_update():
    err = require_login()
    if err: return err
    from modules.admin.crisis_chart_form import update_level
    return jsonify(update_level(session.get('user'), request.form))


# ====================   مدیریت محتوای داشبورد ====================
@admin_bp.route('/dashboard/save', methods=['POST'])
def save_dashboard_content():
    err = require_login()
    if err: return err
    from modules.admin.dashboard_settings import save_dashboard_content as func
    return jsonify(func(session.get('user'),request.form))

@admin_bp.route('/dashboard/get/<int:content_id>')
def get_dashboard_content_api(content_id):
    err = require_login()
    if err: return err
    from modules.admin.dashboard_settings import get_content_by_id as func
    return jsonify(func(content_id))

@admin_bp.route('/dashboard/delete', methods=['POST'])
def delete_dashboard_content_api():
    err = require_login()
    if err: return err
    from modules.admin.dashboard_settings import delete_dashboard_content as func
    return jsonify(func(session.get('user'),request.form))

# ====================   رصد کاربران ====================
@admin_bp.route('/audit')
def admin_audit_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    from modules.admin.audit_log import get_audit_log_form
    from core.router import render_page
    return render_page('module/admin/audit', user=session['user'])

@admin_bp.route('/audit/data')
def admin_audit_data():
    err = require_login()
    if err: return err
    from modules.admin.audit_log import get_audit_data
    return jsonify(get_audit_data(request.args))
    
    

# ====================  تنظیم تاییدکننده‌های شیفت ====================


@admin_bp.route('/shift_approvers')
def admin_shift_approvers_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))

    err = require_login()
    if err: return err
    
    from core.router import render_page
    return render_page('module/admin/shift_approval', user=session['user'])

@admin_bp.route('/shift_approvers/get')
def admin_shift_approvers_get():
    err = require_login()
    if err: return err
    from modules.admin.shift_approval_form import get_approvers_for_dept
    dep_id = request.args.get('dep_id', type=int)
    return jsonify(get_approvers_for_dept(dep_id))

@admin_bp.route('/shift_approvers/list')
def admin_shift_approvers_list():
    err = require_login()
    if err: return err
    from modules.admin.shift_approval_form import get_approvers_config
    return jsonify(get_approvers_config())

@admin_bp.route('/shift_approvers/save', methods=['POST'])
def admin_shift_approvers_save():
    err = require_login()
    if err: return err
    from modules.admin.shift_approval_form import save_approver
    return jsonify(save_approver(session.get('user'), request.form))

@admin_bp.route('/shift_approvers/delete', methods=['POST'])
def admin_shift_approvers_delete():
    err = require_login()
    if err: return err
    from modules.admin.shift_approval_form import delete_approver
    return jsonify(delete_approver(request.form))
    
    