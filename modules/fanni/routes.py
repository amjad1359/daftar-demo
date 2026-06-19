from flask import Blueprint, session, request, jsonify

fanni_bp = Blueprint('fanni', __name__, url_prefix='/module/fanni')

def require_login():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'لطفاً وارد شوید'})
    return None

@fanni_bp.route('/reports/list')
def fanni_reports_list():
    err = require_login()
    if err: return err
    from modules.fanni.reports_form import get_fanni_reports_list as func
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    return jsonify(func(search, status, page, per_page))

@fanni_bp.route('/reports/get/<int:report_id>')
def fanni_report_detail(report_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.fanni.reports_form import get_fanni_report_detail as func
    return jsonify(func(report_id))

@fanni_bp.route('/reports/opinion', methods=['POST'])
def fanni_save_opinion():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.fanni.reports_form import save_fanni_opinion as func
    return jsonify(func(session['user'], request.form))
    