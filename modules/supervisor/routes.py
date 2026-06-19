"""
مسیرهای ماژول سوپروایزر – Flask Blueprint
"""

from flask import Blueprint, session, jsonify, request

# ==================== ایجاد Blueprint ====================
supervisor_bp = Blueprint('supervisor', __name__, url_prefix='/module/supervisor')

# ---------- کمکی: بررسی ورود ----------
def require_login():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'لطفاً وارد شوید'})
    return None

# ==================== Route های شیفت ====================
@supervisor_bp.route('/shift/save', methods=['POST'])
def save_shift():
    err = require_login()
    if err: return err
    from modules.supervisor.shift_form import save_shift as save_shift_func
    result = save_shift_func(session['user'], request.form)
    return jsonify(result)

@supervisor_bp.route('/shift/delete/<shift_id>', methods=['POST', 'DELETE'])
def delete_shift(shift_id):
    err = require_login()
    if err: return err
    from modules.supervisor.shift_form import delete_shift as delete_shift_func
    result = delete_shift_func(shift_id, session['user']['UserID'])
    return jsonify(result)

@supervisor_bp.route('/shift/list')
def api_shift_list():
    err = require_login()
    if err: return err
    from modules.supervisor.shift_form import get_shift_list_api
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    return jsonify(get_shift_list_api(session['user'], page, per_page))

@supervisor_bp.route('/shift/edit/<shift_id>', methods=['POST'])
def edit_shift(shift_id):
    err = require_login()
    if err: return err
    from modules.supervisor.shift_form import update_shift
    result = update_shift(shift_id, session['user']['UserID'], request.form)
    return jsonify(result)

# ==================== آمار ====================
@supervisor_bp.route('/amar/save', methods=['POST'])
def save_amar():
    err = require_login()
    if err: return err
    from modules.supervisor.amar_form import save_amar as save_amar_func
    result = save_amar_func(session['user'], request.form)
    return jsonify(result)

# ==================== انکالی ====================
@supervisor_bp.route('/ankal/save', methods=['POST'])
def save_ankal():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.ankal_form import save_ankal as func
    return jsonify(func(session['user'], request.form))

@supervisor_bp.route('/ankal/update', methods=['POST'])
def update_ankal():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.ankal_form import update_ankal as func
    return jsonify(func(session['user'], request.form))

@supervisor_bp.route('/ankal/delete', methods=['POST'])
def delete_ankal():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.ankal_form import delete_ankal as func
    return jsonify(func(session['user'], request.form))

# ==================== فرم حضور ====================
@supervisor_bp.route('/attendance/save', methods=['POST'])
def save_attendance():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.attendance_form import save_attendance as func
    return jsonify(func(session['user'], request.form))

# ==================== فرم غیبت ====================
@supervisor_bp.route('/ghaybat/save', methods=['POST'])
def save_ghaybat():
    err = require_login()
    if err: return err
    from modules.supervisor.ghaybat_form import save_ghaybat as func
    return jsonify(func(session['user'], request.form))

@supervisor_bp.route('/ghaybat/delete', methods=['POST'])
def delete_ghaybat():
    err = require_login()
    if err: return err
    from modules.supervisor.ghaybat_form import delete_ghaybat as func
    return jsonify(func(session['user'], request.form))

# ==================== فرم خون ====================
@supervisor_bp.route('/blood/save', methods=['POST'])
def save_blood():
    err = require_login()
    if err: return err
    from modules.supervisor.blood_form import save_blood as func
    return jsonify(func(session['user'], request.form))

@supervisor_bp.route('/blood/get/<blood_id>')
def get_blood(blood_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.blood_form import get_blood_record
    return jsonify(get_blood_record(blood_id))

@supervisor_bp.route('/blood/delete', methods=['POST'])
def delete_blood():
    err = require_login()
    if err: return err
    from modules.supervisor.blood_form import delete_blood as func
    return jsonify(func(session['user'], request.form))

# ==================== بحران ====================
@supervisor_bp.route('/crisis/save', methods=['POST'])
def save_crisis():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.crisis_form import save_crisis as func
    return jsonify(func(session['user'], request.form, request.files))

@supervisor_bp.route('/crisis/delete/<int:crisis_id>', methods=['POST'])
def delete_crisis(crisis_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.crisis_form import delete_crisis as func
    return jsonify(func(session['user'], crisis_id))

@supervisor_bp.route('/crisis/archive/<int:crisis_id>', methods=['POST'])
def archive_crisis(crisis_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.crisis_form import archive_crisis as func
    return jsonify(func(session['user'], crisis_id))

@supervisor_bp.route('/crisis/get/<int:crisis_id>')
def get_crisis_record(crisis_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.crisis_form import get_crisis_record as func
    return jsonify(func(crisis_id))

@supervisor_bp.route('/crisis/chart/<int:level_id>')
def get_chart_personnel(level_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.crisis_form import get_chart_personnel as func
    return jsonify(func(level_id))

@supervisor_bp.route('/crisis/personnel/all')
def get_all_personnel():
    err = require_login()
    if err: return jsonify([])
    from modules.supervisor.crisis_form import get_all_personnel as func
    return jsonify(func())

@supervisor_bp.route('/crisis/list')
def crisis_list():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.crisis_form import get_report_list as func
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    return jsonify(func(search, status))

@supervisor_bp.route('/crisis/locations')
def crisis_locations():
    if 'user' not in session: 
        return jsonify({'items': []})
    from modules.supervisor.crisis_form import get_location_suggestions
    return jsonify(get_location_suggestions())

@supervisor_bp.route('/crisis/outcomes')
def crisis_outcomes():
    if 'user' not in session: 
        return jsonify({'items': []})
    from modules.supervisor.crisis_form import get_outcome_suggestions
    return jsonify(get_outcome_suggestions())

# ==================== گزارش سوپروایزر ====================
@supervisor_bp.route('/gozaresh/save', methods=['POST'])
def save_gozaresh():
    err = require_login()
    if err: return err
    from modules.supervisor.gozaresh_form import save_report as func
    return jsonify(func(session['user'], request.form, request.files))

@supervisor_bp.route('/gozaresh/get/<int:record_id>')
def get_gozaresh(record_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.gozaresh_form import get_report as func
    return jsonify(func(record_id))

@supervisor_bp.route('/gozaresh/delete/<int:record_id>', methods=['POST'])
def delete_gozaresh(record_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.gozaresh_form import delete_report as func
    return jsonify(func(session['user'], record_id))

@supervisor_bp.route('/gozaresh/add_title', methods=['POST'])
def add_gozaresh_title():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.gozaresh_form import add_new_title as func
    return jsonify(func(request.form.get('title', '')))

@supervisor_bp.route('/gozaresh/download/<int:report_id>')
def download_gozaresh_file(report_id):
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    import os
    from flask import send_file
    file_name = request.args.get('file', '')
    file_path = os.path.join('uploads/gozaresh', str(report_id), file_name)
    safe_path = os.path.normpath(file_path)
    if not safe_path.startswith(os.path.normpath('uploads/gozaresh')):
        return 'دسترسی غیرمجاز', 403
    if not os.path.exists(safe_path):
        return 'فایل یافت نشد', 404
    return send_file(safe_path, as_attachment=True, download_name=file_name)

@supervisor_bp.route('/gozaresh/list')
def list_gozaresh():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.gozaresh_form import get_report_list as func
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    return jsonify(func(session['user'], search, status, page, per_page))

# ==================== کدها ====================
@supervisor_bp.route('/codes/save', methods=['POST'])
def save_code():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.codes_form import save_code as func
    return jsonify(func(session['user'], request.form))

@supervisor_bp.route('/codes/get/<int:record_id>')
def get_code(record_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.codes_form import get_code_record as func
    return jsonify(func(record_id))

@supervisor_bp.route('/codes/delete/<int:record_id>', methods=['POST'])
def delete_code(record_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.codes_form import delete_code as func
    return jsonify(func(session.get('user'), record_id))


@supervisor_bp.route('/codes/list/<shift_id>')
def codes_list(shift_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.codes_form import get_codes_list as func
    return jsonify(func(shift_id))

@supervisor_bp.route('/codes/roles/<code_id>')
def code_roles(code_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.codes_form import get_code_roles_for_form as func
    return jsonify(func(code_id))

@supervisor_bp.route('/codes/personnel')
def codes_personnel():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.codes_form import get_personnel_for_form as func
    return jsonify(func())

@supervisor_bp.route('/codes/suggestions')
def codes_suggestions():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.codes_form import get_suggestions_for_form as func
    return jsonify(func())

# ==================== راند بخش‌ها ====================
@supervisor_bp.route('/rounds/save', methods=['POST'])
def save_round():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.rounds_form import save_round as func
    return jsonify(func(session['user'], request.form, request.files))

@supervisor_bp.route('/rounds/get/<int:record_id>')
def get_round(record_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.rounds_form import get_round_record as func
    return jsonify(func(record_id))

@supervisor_bp.route('/rounds/delete_file', methods=['POST'])
def delete_round_file():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.rounds_form import delete_round_file as func
    return jsonify(func(request.form))

@supervisor_bp.route('/rounds/delete/<int:record_id>', methods=['POST'])
def delete_round(record_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.rounds_form import delete_round as func
    return jsonify(func(session.get('user'), record_id))  # حتماً user را پاس دهید


@supervisor_bp.route('/rounds/list/<shift_id>')
def rounds_list(shift_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.rounds_form import get_rounds_list as func
    return jsonify(func(shift_id))

@supervisor_bp.route('/rounds/items/<title_id>')
def checklist_items(title_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.supervisor.rounds_form import get_checklist_items_api as func
    return jsonify(func(title_id))
    
    