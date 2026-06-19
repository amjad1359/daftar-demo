from flask import Blueprint, session, request, jsonify

riyasat_bp = Blueprint('riyasat', __name__, url_prefix='/module/riyasat')

def require_login():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'لطفاً وارد شوید'})
    return None

@riyasat_bp.route('/reports/list')
def riyasat_reports_list():
    err = require_login()
    if err: return err
    from modules.riyasat.reports_form import get_raiss_reports_list as func
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    return jsonify(func(search, status, page, per_page))

@riyasat_bp.route('/reports/get/<int:report_id>')
def riyasat_report_detail(report_id):
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.riyasat.reports_form import get_raiss_report_detail as func
    return jsonify(func(report_id))

@riyasat_bp.route('/reports/order', methods=['POST'])
def riyasat_save_order():
    err = require_login()
    if err: return jsonify({'success': False})
    from modules.riyasat.reports_form import save_raiss_order as func
    return jsonify(func(session['user'], request.form))
    
    