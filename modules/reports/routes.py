from flask import Blueprint, session, request, jsonify, redirect, url_for

reports_bp = Blueprint('reports', __name__, url_prefix='/module/reports')

def require_login():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'لطفاً وارد شوید'})
    return None

# مسیرهای رندر صفحات گزارش (داشبورد و زیرمجموعه‌ها)
@reports_bp.route('/')
@reports_bp.route('/<sub_page>')
def reports_module(sub_page=None):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    from core.router import render_page
    return render_page(f'module/reports/{sub_page}' if sub_page else 'reports', user=session['user'])

# ====================  گزارش آنکال ====================
@reports_bp.route('/ankal/data')
def reports_ankal_data():
    err = require_login()
    if err: return err
    from modules.reports.ankal_report import api_data
    return jsonify(api_data(request.args))

@reports_bp.route('/ankal/export')
def reports_ankal_export():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.ankal_report import api_export
    return api_export(request.args)

@reports_bp.route('/ankal/print')
def reports_ankal_print():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.ankal_report import api_print
    return api_print(request.args)

@reports_bp.route('/ankal/detail/<int:record_id>')
def reports_ankal_detail(record_id):
    err = require_login()
    if err: return err
    from modules.reports.ankal_report import api_detail
    return jsonify(api_detail(record_id))

@reports_bp.route('/ankal/analyze')
def reports_ankal_analyze():
    err = require_login()
    if err: return err
    from modules.reports.ankal_report import api_analyze
    return jsonify(api_analyze(request.args))

# ====================  گزارش خون ====================
@reports_bp.route('/blood/data')
def reports_blood_data():
    err = require_login()
    if err: return err
    from modules.reports.blood_report import api_data
    return jsonify(api_data(request.args))

@reports_bp.route('/blood/export')
def reports_blood_export():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.blood_report import api_export
    return api_export(request.args)

@reports_bp.route('/blood/print')
def reports_blood_print():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.blood_report import api_print
    return api_print(request.args)

@reports_bp.route('/blood/detail/<int:record_id>')
def reports_blood_detail(record_id):
    err = require_login()
    if err: return err
    from modules.reports.blood_report import api_detail
    return jsonify(api_detail(record_id))

@reports_bp.route('/blood/analyze')
def reports_blood_analyze():
    err = require_login()
    if err: return err
    from modules.reports.blood_report import api_analyze
    return jsonify(api_analyze(request.args))

# ====================  گزارش کدها ====================
@reports_bp.route('/codes/data')
def reports_codes_data():
    err = require_login()
    if err: return err
    from modules.reports.codes_report import api_data
    return jsonify(api_data(request.args))

@reports_bp.route('/codes/export')
def reports_codes_export():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.codes_report import api_export
    return api_export(request.args)

@reports_bp.route('/codes/print')
def reports_codes_print():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.codes_report import api_print
    return api_print(request.args)

@reports_bp.route('/codes/analyze')
def codes_analyze():
    err = require_login()
    if err: return err
    from modules.reports.codes_report import api_analyze
    return jsonify(api_analyze(request.args))

# ====================  گزارش بحران ====================
@reports_bp.route('/crisis/data')
def reports_crisis_data():
    err = require_login()
    if err: return err
    from modules.reports.crisis_report import api_data
    return jsonify(api_data(request.args))

@reports_bp.route('/crisis/export')
def reports_crisis_export():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.crisis_report import api_export
    return api_export(request.args)

@reports_bp.route('/crisis/print')
def reports_crisis_print():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.crisis_report import api_print
    return api_print(request.args)

@reports_bp.route('/crisis/analyze')
def crisis_analyze():
    err = require_login()
    if err: return err
    from modules.reports.crisis_report import api_analyze
    return jsonify(api_analyze(request.args))

@reports_bp.route('/crisis/detail/<int:record_id>')
def crisis_detail(record_id):
    err = require_login()
    if err: return err
    from modules.reports.crisis_report import get_crisis_detail
    return jsonify(get_crisis_detail(record_id))


# ====================  گزارش حضور و غیاب ====================
# ====================  تحلیل حضور و غیاب ====================
@reports_bp.route('/attendance/analyze')
def reports_attendance_analyze():
    err = require_login()
    if err: return err
    from modules.reports.attendance_report import api_analyze
    return jsonify(api_analyze(request.args))


@reports_bp.route('/attendance/data')
def reports_attendance_data():
    err = require_login()
    if err: return err
    from modules.reports.attendance_report import api_data
    return jsonify(api_data(request.args))

@reports_bp.route('/attendance/export')
def reports_attendance_export():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.attendance_report import api_export
    return api_export(request.args)

@reports_bp.route('/attendance/print/shift')
def reports_attendance_print_shift():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.attendance_report import api_print_shift
    return api_print_shift(request.args)

@reports_bp.route('/attendance/print/person')
def reports_attendance_print_person():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.attendance_report import api_print_person
    return api_print_person(request.args)

# ====================  گردش کار گزارشات ====================

# ====================  تحلیل گردش کار ====================
@reports_bp.route('/workflow/analyze')
def reports_workflow_analyze():
    err = require_login()
    if err: return err
    from modules.reports.workflow_report import api_analyze
    return jsonify(api_analyze(request.args))

@reports_bp.route('/workflow/data')
def reports_workflow_data():
    err = require_login()
    if err: return err
    from modules.reports.workflow_report import api_data
    return jsonify(api_data(request.args))

@reports_bp.route('/workflow/detail/<int:report_id>')
def reports_workflow_detail(report_id):
    err = require_login()
    if err: return err
    from modules.reports.workflow_report import api_detail
    return jsonify(api_detail(report_id))

@reports_bp.route('/workflow/export')
def reports_workflow_export():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.workflow_report import api_export
    return api_export(request.args)

# ====================  گزارش راند و اعتباربخشی ====================
@reports_bp.route('/rounds/data')
def reports_rounds_data():
    err = require_login()
    if err: return err
    from modules.reports.rounds_report import api_data
    return jsonify(api_data(request.args))

@reports_bp.route('/rounds/export')
def reports_rounds_export():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.rounds_report import api_export
    return api_export(request.args)

@reports_bp.route('/rounds/print')
def reports_rounds_print():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.rounds_report import api_print
    return api_print(request.args)

@reports_bp.route('/rounds/analyze')
def rounds_analyze():
    err = require_login()
    if err: return err
    from modules.reports.rounds_report import api_analyze
    return jsonify(api_analyze(request.args))

# ====================  تحلیل آمار پایان شیفت ====================
@reports_bp.route('/stats/analyze')
def reports_stats_analyze():
    err = require_login()
    if err: return err
    from modules.reports.stats_report import api_analyze
    return jsonify(api_analyze(request.args))


@reports_bp.route('/stats/data')
def reports_stats_data():
    err = require_login()
    if err: return err
    from modules.reports.stats_report import api_data
    return jsonify(api_data(request.args))

@reports_bp.route('/stats/export')
def reports_stats_export():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.stats_report import api_export
    return api_export(request.args)

@reports_bp.route('/stats/print')
def reports_stats_print():
    if 'user' not in session:
        return 'دسترسی غیرمجاز', 401
    from modules.reports.stats_report import api_print
    return api_print(request.args)
    