"""
modules/manager/routes.py — نسخه یکپارچه نهایی
"""
from flask import Blueprint, session, request, jsonify

def _csrf_exempt(fn):
    try:
        from flask_wtf.csrf import exempt
        return exempt(fn)
    except ImportError:
        fn._csrf_exempt = True
        return fn

from modules.manager.shift_edit import get_shifts_edit_form


from modules.manager.reports_form import (
    get_manager_reports_list,
    get_manager_report_detail,
    save_manager_response,
)
from modules.manager.shifts_form import (
    get_shifts_form,
    get_shifts_readonly,
    get_department_personnel,      # جایگزین get_personnel_by_dep_id
    get_assignments,
    save_assignment,
    bulk_save_assignments,
    handle_extra_shifts,
    delete_extra_shift,
    get_approval_status,
    approve_month,
    revoke_approval,
    get_approvers_config,
    get_user_departments,
)
from modules.manager.shift_review_form import (
    get_shift_review_page,
    get_pending_approvals,
    get_approved_by_user,
    get_shift_view_data,
    do_approve,
    do_revoke,
)

from modules.manager.shift_comparison_form import (
    get_shift_comparison_page,
    get_schedule_data,
    get_attendance_data,
    get_comparison_data
)


manager_bp = Blueprint('manager', __name__, url_prefix='/module/manager')

def _check_login():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'لطفاً وارد شوید'}), 401
    return None

def _ajax_only():
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return jsonify({'success': False, 'message': 'دسترسی مستقیم مجاز نیست'}), 403
    return None

def _user():
    return session['user']

# ══════ گزارشات
@manager_bp.route('/reports/list')
def manager_reports_list():
    err = _check_login()
    if err: return err
    return jsonify(get_manager_reports_list(
        _user(),
        search=request.args.get('search', ''),
        status=request.args.get('status', 'all'),
        unit=request.args.get('unit', 'all'),
        page=request.args.get('page', 1, type=int),
        per_page=request.args.get('per_page', 15, type=int),
    ))

@manager_bp.route('/reports/get/<int:report_id>')
def manager_report_detail(report_id):
    err = _check_login()
    if err: return err
    return jsonify(get_manager_report_detail(_user(), report_id))

@manager_bp.route('/reports/respond', methods=['POST'])
def manager_respond():
    err = _check_login()
    if err: return err
    return jsonify(save_manager_response(_user(), request.form))

# ══════ شیفت‌بندی (ویرایش)
from modules.manager.shift_edit import (
    get_shifts_edit_form,
    _personnel_by_dep,
    _assignments,
    save_assignment_force,
    bulk_save_force,
    extra_save_force,
    extra_delete_force,
)

# صفحه اصلی ویرایش
@manager_bp.route('/shifts_edit')
def manager_shifts_edit_page():
    err = _check_login()
    if err: return err
    return get_shifts_edit_form(_user())

# APIهای اختصاصی
@manager_bp.route('/shifts_edit/api/personnel')
def manager_shifts_edit_personnel():
    err = _check_login()
    if err: return err
    dep_id = request.args.get('dep_id', type=int)
    if not dep_id: return jsonify({'success': False})
    return jsonify(_personnel_by_dep(dep_id))

@manager_bp.route('/shifts_edit/api/assignments')
def manager_shifts_edit_assignments():
    err = _check_login()
    if err: return err
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    dep_id = request.args.get('dep_id', type=int)
    if not all([year, month, dep_id]): return jsonify({'success': False})
    return jsonify(_assignments(year, month, dep_id))

@manager_bp.route('/shifts_edit/api/save', methods=['POST'])
@_csrf_exempt
def manager_shifts_edit_save():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(save_assignment_force(_user(), request.form))

@manager_bp.route('/shifts_edit/api/bulk_save', methods=['POST'])
@_csrf_exempt
def manager_shifts_edit_bulk_save():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(bulk_save_force(_user(), request.form))

@manager_bp.route('/shifts_edit/api/extra', methods=['POST'])
@_csrf_exempt
def manager_shifts_edit_extra():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(extra_save_force(_user(), request.form))

@manager_bp.route('/shifts_edit/api/extra/delete', methods=['POST'])
@_csrf_exempt
def manager_shifts_edit_extra_delete():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(extra_delete_force(_user(), request.form))


# ══════ شیفت‌بندی 

@manager_bp.route('/shifts')
def manager_shifts_page():
    err = _check_login()
    if err: return err
    return get_shifts_form(_user())

@manager_bp.route('/shifts/personnel')
def manager_shifts_personnel():
    err = _check_login()
    if err: return err
    dep_id = request.args.get('dep_id', type=int)
    if not dep_id:
        return jsonify({'success': False, 'message': 'dep_id الزامی است'})
    return jsonify(get_department_personnel(dep_id))

@manager_bp.route('/shifts/personnel_by_dep')
def manager_shifts_personnel_by_dep():
    err = _check_login()
    if err: return err
    dep_id = request.args.get('dep_id', type=int)
    if not dep_id:
        return jsonify({'success': False, 'message': 'dep_id الزامی است'})
    return jsonify(get_department_personnel(dep_id))

@manager_bp.route('/shifts/assignments')
def manager_shifts_assignments():
    err = _check_login()
    if err: return err
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    dep_id = request.args.get('dep_id', type=int)
    if not all([year, month, dep_id]):
        return jsonify({'success': False, 'message': 'سال، ماه و بخش الزامی هستند'})
    return jsonify(get_assignments(year, month, dep_id))

@manager_bp.route('/shifts/save', methods=['POST'])
@_csrf_exempt
def manager_shifts_save():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(save_assignment(_user(), request.form))

@manager_bp.route('/shifts/bulk_save', methods=['POST'])
@_csrf_exempt
def manager_shifts_bulk_save():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(bulk_save_assignments(_user(), request.form))

@manager_bp.route('/shifts/extra', methods=['POST'])
@_csrf_exempt
def manager_shifts_extra():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(handle_extra_shifts(_user(), request))

@manager_bp.route('/shifts/extra/delete', methods=['POST'])
@_csrf_exempt
def manager_shifts_extra_delete():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(delete_extra_shift(_user(), request.form))

# تایید سطح ۱
@manager_bp.route('/shifts/approval_status')
def manager_shifts_approval_status():
    err = _check_login()
    if err: return err
    dep_id = request.args.get('dep_id', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    if not all([dep_id, year, month]):
        return jsonify({'success': False, 'message': 'پارامترها ناقص'})
    approvals = get_approval_status(dep_id, year, month)
    return jsonify({'success': True, 'approvals': approvals})

@manager_bp.route('/shifts/approvers')
def manager_shifts_approvers():
    err = _check_login()
    if err: return err
    dep_id = request.args.get('dep_id', type=int)
    if not dep_id:
        return jsonify({'success': False, 'message': 'dep_id الزامی است'})
    return jsonify({'success': True, 'approvers': get_approvers_config(dep_id)})

@manager_bp.route('/shifts/approve', methods=['POST'])
@_csrf_exempt
def manager_shifts_approve():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(approve_month(_user(), request.form))

@manager_bp.route('/shifts/revoke', methods=['POST'])
@_csrf_exempt
def manager_shifts_revoke():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(revoke_approval(_user(), request.form))

@manager_bp.route('/shifts/set_dep', methods=['POST'])
@_csrf_exempt
def manager_shifts_set_dep():
    dep_id = request.form.get('dep_id', type=int)
    if dep_id:
        session['shift_dep_id'] = dep_id
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'dep_id نامعتبر'})

# ══════ فقط‌خواندنی
@manager_bp.route('/shifts/view')
def manager_shifts_view():
    err = _check_login()
    if err: return err
    dep_id = request.args.get('dep_id', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    if not all([dep_id, year, month]):
        return '<div style="padding:40px;color:red;">پارامترهای ناقص</div>'
    user_depts = get_user_departments(_user().get('UserID'))
    return get_shifts_readonly(dep_id, year, month,
                               user_depts if len(user_depts) > 1 else None)

# ══════ کارتابل تأیید (سطوح ۲+)
@manager_bp.route('/shift_review')
def manager_shift_review_page():
    err = _check_login()
    if err: return err
    return get_shift_review_page(_user())

@manager_bp.route('/shift_review/pending')
def manager_shift_review_pending():
    err = _check_login()
    if err: return err
    user_id = _user().get('UserID')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    data = get_pending_approvals(user_id)
    if data.get('pending'):
        if month:
            data['pending'] = [r for r in data['pending'] if r['month'] == month]
        if year:
            data['pending'] = [r for r in data['pending'] if r['year'] == year]
    return jsonify(data)

@manager_bp.route('/shift_review/approved')
def manager_shift_review_approved():
    err = _check_login()
    if err: return err
    user_id = _user().get('UserID')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    data = get_approved_by_user(user_id)
    if data.get('approved'):
        if month:
            data['approved'] = [r for r in data['approved'] if r['month'] == month]
        if year:
            data['approved'] = [r for r in data['approved'] if r['year'] == year]
    return jsonify(data)

@manager_bp.route('/shift_review/view_data')
def manager_shift_review_view_data():
    err = _check_login()
    if err: return err
    dep_id = request.args.get('dep_id', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    user_id = _user().get('UserID')
    if not all([dep_id, year, month]):
        return jsonify({'success': False, 'message': 'پارامترهای ناقص'})
    return jsonify(get_shift_view_data(user_id, dep_id, year, month))

@manager_bp.route('/shift_review/approve', methods=['POST'])
@_csrf_exempt
def manager_shift_review_approve():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(do_approve(_user(), request.form))

@manager_bp.route('/shift_review/revoke', methods=['POST'])
@_csrf_exempt
def manager_shift_review_revoke():
    err = _check_login() or _ajax_only()
    if err: return err
    return jsonify(do_revoke(_user(), request.form))
    
# مقایسه برنامه شیفت با حضور ثبت‌شده
    

@manager_bp.route('/shift_comparison')
def manager_shift_comparison():
    err = _check_login()
    if err: return err
    return get_shift_comparison_page(_user())

@manager_bp.route('/shift_comparison/schedule')
def manager_shift_comparison_schedule():
    err = _check_login()
    if err: return err
    dept = request.args.get('dept', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    return jsonify(get_schedule_data(dept, year, month))

@manager_bp.route('/shift_comparison/attendance')
def manager_shift_comparison_attendance():
    err = _check_login()
    if err: return err
    dept = request.args.get('dept', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    return jsonify(get_attendance_data(dept, year, month))

@manager_bp.route('/shift_comparison/comparison')
def manager_shift_comparison_comparison():
    err = _check_login()
    if err: return err
    dept = request.args.get('dept', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    return jsonify(get_comparison_data(dept, year, month))
    