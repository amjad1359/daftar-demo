from flask import Blueprint, session, request, jsonify
from modules.matron.personnel_form import (
    get_personnel_form, 
    get_personnel_list_api, 
    get_person_detail, 
    save_personnel, 
    delete_personnel_api,
    get_majors_api,
    get_org_history_api,
    get_org_record_api,
    save_org_record_api,
    delete_org_record_api,
    get_tab2_data,
    get_tab3_data,
    export_tab2_excel,
    export_tab3_excel,
    get_intro_letter_html
)

matron_bp = Blueprint('matron', __name__, url_prefix='/module/matron')

def require_login():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'لطفاً وارد شوید'})
    return None

# ==================== کارتابل مترون ====================
@matron_bp.route('/reports/list')
def matron_reports_list():
    err = require_login()
    if err: return err
    from modules.matron.reports_form import get_matron_reports_list as func
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    return jsonify(func(search, status, page, per_page))

@matron_bp.route('/reports/get/<int:report_id>')
def matron_report_detail(report_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.reports_form import get_matron_report_detail as func
    return jsonify(func(report_id))

@matron_bp.route('/reports/approve', methods=['POST'])
def matron_approve_report():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.reports_form import approve_matron_report as func
    return jsonify(func(session['user'], request.form))

# ==================== مدیریت پرسنل ====================
@matron_bp.route('/personnel/list')
def matron_personnel_list():
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    doctor = request.args.get('doctor', 0)
    
    # اضافه کردن دریافت شماره صفحه و تعداد در هر صفحه
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # پاس دادن متغیرهای جدید به تابع
    return jsonify(get_personnel_list_api(search, status, doctor, page, per_page))

@matron_bp.route('/personnel/delete/<int:person_id>', methods=['POST'])
def matron_delete_person(person_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import delete_personnel_api
    return jsonify(delete_personnel_api(session.get('user'), person_id))

@matron_bp.route('/personnel/get/<int:person_id>')
def matron_personnel_get(person_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import get_person_detail as func
    return jsonify(func(person_id))

@matron_bp.route('/personnel/save', methods=['POST'])
def matron_personnel_save():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import save_personnel as func
    return jsonify(func(session['user'], request.form))

@matron_bp.route('/personnel/majors')
def matron_personnel_majors():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import get_majors_api as func
    return jsonify(func())

@matron_bp.route('/personnel/org_history/<int:person_id>')
def matron_org_history(person_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import get_org_history_api as func
    return jsonify(func(person_id))

@matron_bp.route('/personnel/get_org/<int:org_id>')
def matron_get_org(org_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import get_org_record_api as func
    return jsonify(func(org_id))

@matron_bp.route('/personnel/save_org', methods=['POST'])
def matron_save_org():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import save_org_record_api as func
    return jsonify(func(session['user'], request.form))

@matron_bp.route('/personnel/delete_org/<int:org_id>', methods=['POST'])
def matron_delete_org(org_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import delete_org_record_api as func
    return jsonify(func(session['user'], org_id))

# ══════ تب ۲ – پرسنل بر اساس بخش ══════
@matron_bp.route('/personnel/tab2')
def matron_tab2():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import get_tab2_data as func
    # دریافت چندتایی بخش‌ها و گروه‌ها
    dept = request.args.getlist('dept') or None
    grop = request.args.getlist('grop') or None
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    employment = request.args.get('employment', '')
    degree = request.args.get('degree', '')
    field = request.args.get('field', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return jsonify(func(dept=dept, grop=grop, status=status, search=search,
                        employment=employment, degree=degree, field=field,
                        page=page, per_page=per_page))

# ══════ تب ۳ – پزشکان ══════
@matron_bp.route('/personnel/tab3')
def matron_tab3():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.personnel_form import get_tab3_data as func
    spec = request.args.getlist('spec') or None
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return jsonify(func(spec=spec, status=status, search=search,
                        page=page, per_page=per_page))

# ══════ Excel تب ۲ ══════
@matron_bp.route('/personnel/excel/tab2')
def matron_excel_tab2():
    if 'user' not in session: return "دسترسی غیرمجاز", 401
    from modules.matron.personnel_form import export_tab2_excel as func
    dept = request.args.getlist('dept') or None
    grop = request.args.getlist('grop') or None
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    employment = request.args.get('employment', '')
    degree = request.args.get('degree', '')
    field = request.args.get('field', '')
    return func(dept=dept, grop=grop, status=status, search=search,
                employment=employment, degree=degree, field=field)

# ══════ Excel تب ۳ ══════
@matron_bp.route('/personnel/excel/tab3')
def matron_excel_tab3():
    if 'user' not in session: return "دسترسی غیرمجاز", 401
    from modules.matron.personnel_form import export_tab3_excel as func
    spec = request.args.getlist('spec') or None
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    return func(spec=spec, status=status, search=search)



@matron_bp.route('/personnel/intro_letter/<int:org_id>')
def matron_intro_letter(org_id):
    if 'user' not in session:
        from flask import redirect, url_for
        return redirect(url_for('login_page'))
    from modules.matron.personnel_form import get_intro_letter_html
    return get_intro_letter_html(org_id)

# ==================== تنظیمات چک‌لیست ====================
@matron_bp.route('/checklist/add_title', methods=['POST'])
def matron_checklist_add_title():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.checklist_form import add_title_api as func
    return jsonify(func(session['user'], request.form.get('title', '')))

@matron_bp.route('/checklist/save_item', methods=['POST'])
def matron_checklist_save_item():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.checklist_form import save_item_api as func
    return jsonify(func(session['user'], request.form))

@matron_bp.route('/checklist/items/<int:title_id>')
def matron_checklist_items(title_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.checklist_form import get_items_api as func
    return jsonify(func(title_id))

@matron_bp.route('/checklist/update_item', methods=['POST'])
def matron_checklist_update_item():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.checklist_form import update_item_api as func
    return jsonify(func(session['user'], request.form))

# ==================== کدهای عملیاتی ====================
@matron_bp.route('/codes/add_code', methods=['POST'])
def matron_codes_add_code():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.codes_form import add_code_api as func
    return jsonify(func(session['user'], request.form.get('code_name', '')))

@matron_bp.route('/codes/add_role', methods=['POST'])
def matron_codes_add_role():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.codes_form import add_role_api as func
    return jsonify(func(session.get('user'), request.form.get('code_id'), request.form.get('role_name', '')))



@matron_bp.route('/codes/list')
def matron_codes_list():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.codes_form import list_codes_api as func
    return jsonify(func())

@matron_bp.route('/codes/update_role', methods=['POST'])
def matron_codes_update_role():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.codes_form import update_role_api as func
    return jsonify(func(request.form.get('role_id'), request.form.get('role_name', '')))

    
    
@matron_bp.route('/codes/update_code', methods=['POST'])
def matron_codes_update_code():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.codes_form import update_code_api as func
    return jsonify(func(session.get('user'), request.form.get('code_id'), request.form.get('code_name', '')))

@matron_bp.route('/codes/delete_code', methods=['POST'])
def matron_codes_delete_code():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.codes_form import delete_code_api as func
    return jsonify(func(session.get('user'), request.form.get('code_id')))

@matron_bp.route('/codes/delete_role', methods=['POST'])
def matron_codes_delete_role():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.matron.codes_form import delete_role_api as func
    return jsonify(func(session.get('user'), request.form.get('role_id')))    