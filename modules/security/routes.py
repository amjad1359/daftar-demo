from flask import Blueprint, session, request, jsonify

security_bp = Blueprint('security', __name__, url_prefix='/module/security')

def require_login():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'لطفاً وارد شوید'})
    return None

@security_bp.route('/change-password', methods=['POST'])
def security_change_password():
    err = require_login()
    if err: return err
    from modules.security.views import change_user_password
    return jsonify(change_user_password(session['user'], request.form))
    