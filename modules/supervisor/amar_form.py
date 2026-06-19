"""
فرم آمار پایان شیفت - سوپروایزر
نسخه کامل با Toast Notification و AJAX
"""

from models.database import query
import jdatetime
from datetime import datetime
import json
from utils.auto_log import log_crud

# ==========================================
# ۱. تابع اصلی نمایش فرم آمار
# ==========================================

def get_amar_form(user, message=None, error=None):
    """فرم ثبت آمار بخش‌ها - نسخه کامل"""
    
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')
    
    # ========== دریافت شیفت فعال ==========
    active_shift = query(
        "SELECT ID_shift, tarkib, nam_shift FROM shift_namt ORDER BY ID_shift DESC LIMIT 1",
        fetch_one=True
    )
    
    if not active_shift:
        return '''
        <div class="content-card fade-in">
            <div style="text-align:center;padding:60px 20px;">
                <div style="font-size:64px;margin-bottom:15px;">⚠️</div>
                <h3 style="color:#1e293b;">شیفت فعالی یافت نشد</h3>
                <p style="color:#94a3b8;margin-bottom:25px;">لطفاً ابتدا یک شیفت ثبت کنید سپس آمار را وارد نمایید</p>
                <a href="/module/supervisor/shift" class="btn btn-primary btn-lg">📅 ثبت شیفت جدید</a>
            </div>
        </div>
        '''
    
    shift_id = active_shift['ID_shift']
    shift_name = active_shift['tarkib'] or active_shift.get('nam_shift', '---')
    shift_type = active_shift.get('nam_shift', '')
    
    # ========== دریافت آمار کلی شیفت (همه بخش‌ها) ==========
    totals = query("""
        SELECT i.item_name, SUM(d.value) as total_val
        FROM tbl_amar_data d
        JOIN tbl_amar_items i ON d.item_id = i.ID_item
        WHERE d.nam_shift = %s
        GROUP BY i.item_name
        HAVING total_val > 0
        ORDER BY total_val DESC
    """, params=(str(shift_id),), fetch_all=True)
    
    # ========== ساخت کارت‌های آمار کلی ==========
    if totals:
        total_cards = ''
        for idx, t in enumerate(totals):
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
            color = colors[idx % len(colors)]
            total_cards += f'''
            <div class="summary-stat-card" style="border-top: 3px solid {color};">
                <div class="summary-stat-value" style="color: {color};">{int(t['total_val']):,}</div>
                <div class="summary-stat-label">{t['item_name']}</div>
            </div>
            '''
    else:
        total_cards = '<div class="empty-summary">📭 هنوز آماری ثبت نشده است</div>'
    
    # ========== دریافت بخش‌های دارای آمار ==========
    wards = query("""
        SELECT ID_nam_bakhsh, nam_bakhsh, amar 
        FROM tbl_bakhsh 
        WHERE amar > 0 
        ORDER BY nam_bakhsh
    """, fetch_all=True)
    
    if not wards:
        wards = []
    
    # ========== لیست بخش‌های ثبت شده در این شیفت ==========
    submitted = query("""
        SELECT DISTINCT d.bakhsh_id, b.nam_bakhsh
        FROM tbl_amar_data d
        JOIN tbl_bakhsh b ON d.bakhsh_id = b.ID_nam_bakhsh
        WHERE d.nam_shift = %s
        ORDER BY d.ID_data DESC
    """, params=(str(shift_id),), fetch_all=True)
    
    # ========== ساخت لیست بخش‌های ثبت شده ==========
    if submitted:
        submitted_list = ''
        for s in submitted:
            submitted_list += f'''
            <div class="submitted-ward-item" onclick="selectWard('{s['bakhsh_id']}', '{s['nam_bakhsh']}')">
                <span>📝</span>
                <span>{s['nam_bakhsh']}</span>
                <span class="submitted-badge">ثبت شده</span>
            </div>
            '''
    else:
        submitted_list = '<div class="empty-submitted">هنوز بخشی ثبت نشده</div>'
    
    # ========== ساخت option های بخش‌ها ==========
    ward_options = ''
    for w in wards:
        ward_options += f'<option value="{w["ID_nam_bakhsh"]}">{w["nam_bakhsh"]}</option>'
    
    # ========== ساخت JSON داده‌های بخش‌ها ==========
    wards_json = _build_wards_json(wards, shift_id)
    
    # ========== آمار کلی ==========
    total_wards = len(wards)
    submitted_count = len(submitted) if submitted else 0
    remaining = total_wards - submitted_count
    
    # ========== HTML ==========
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --primary: #1e3a8a;
                --primary-light: #3b82f6;
                --success: #10b981;
                --danger: #ef4444;
                --warning: #f59e0b;
                --dark: #1e293b;
                --gray: #64748b;
                --light-gray: #94a3b8;
                --border: #e2e8f0;
                --bg-light: #f8fafc;
                --radius: 12px;
                --transition: 0.2s ease;
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: Tahoma, Arial, sans-serif;
                direction: rtl;
                background: #f1f5f9;
                color: var(--dark);
            }}
            
            .fade-in {{ animation: fadeIn 0.4s ease; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            .content-card {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            /* ==================== هدر صفحه ==================== */
            .amar-header {{
                background: linear-gradient(135deg, var(--primary), #2563eb);
                color: white;
                padding: 25px 30px;
                border-radius: 16px;
                margin-bottom: 25px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 8px 30px rgba(30, 58, 138, 0.2);
            }}
            
            .amar-header-left h2 {{
                font-size: 22px;
                margin: 0 0 5px 0;
            }}
            
            .amar-header-left p {{
                opacity: 0.85;
                font-size: 13px;
                margin: 0;
            }}
            
            .amar-header-right {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .shift-info-badge {{
                background: rgba(255,255,255,0.15);
                backdrop-filter: blur(10px);
                padding: 10px 20px;
                border-radius: 30px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid rgba(255,255,255,0.2);
            }}
            
            .back-link {{
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                font-size: 13px;
                transition: var(--transition);
            }}
            
            .back-link:hover {{
                background: rgba(255,255,255,0.15);
            }}
            
            /* ==================== کارت‌های KPI ==================== */
            .kpi-row {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 25px;
            }}
            
            .kpi-card {{
                background: white;
                border-radius: 14px;
                padding: 20px;
                text-align: center;
                border: 1px solid var(--border);
                transition: var(--transition);
            }}
            
            .kpi-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            }}
            
            .kpi-icon {{
                font-size: 28px;
                margin-bottom: 8px;
            }}
            
            .kpi-value {{
                font-size: 28px;
                font-weight: bold;
                color: var(--primary);
            }}
            
            .kpi-label {{
                font-size: 12px;
                color: var(--gray);
                margin-top: 4px;
            }}
            
            /* ==================== کارت‌های آمار تجمعی ==================== */
            .summary-section {{
                background: white;
                border-radius: 14px;
                padding: 20px;
                margin-bottom: 25px;
                border: 1px solid var(--border);
            }}
            
            .summary-section h3 {{
                margin: 0 0 15px 0;
                font-size: 16px;
                color: var(--dark);
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .summary-stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 12px;
            }}
            
            .summary-stat-card {{
                background: var(--bg-light);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                transition: var(--transition);
            }}
            
            .summary-stat-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }}
            
            .summary-stat-value {{
                font-size: 24px;
                font-weight: bold;
            }}
            
            .summary-stat-label {{
                font-size: 11px;
                color: var(--gray);
                margin-top: 4px;
            }}
            
            .empty-summary {{
                text-align: center;
                color: var(--light-gray);
                padding: 30px;
                font-size: 14px;
            }}
            
            /* ==================== چیدمان اصلی ==================== */
            .main-grid {{
                display: grid;
                grid-template-columns: 280px 1fr;
                gap: 25px;
            }}
            
            /* ==================== پنل راست ==================== */
            .side-panel {{
                background: white;
                border-radius: 14px;
                padding: 20px;
                border: 1px solid var(--border);
            }}
            
            .side-panel-title {{
                font-size: 15px;
                font-weight: bold;
                color: var(--dark);
                margin-bottom: 15px;
                padding-bottom: 12px;
                border-bottom: 2px solid var(--border);
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .side-panel-counter {{
                background: var(--primary);
                color: white;
                font-size: 11px;
                padding: 2px 10px;
                border-radius: 15px;
                font-weight: normal;
            }}
            
            .submitted-ward-item {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 12px;
                margin-bottom: 5px;
                border-radius: 8px;
                cursor: pointer;
                transition: var(--transition);
                font-size: 13px;
                border: 1px solid transparent;
            }}
            
            .submitted-ward-item:hover {{
                background: #dbeafe;
                border-color: var(--primary-light);
            }}
            
            .submitted-badge {{
                margin-right: auto;
                background: #d1fae5;
                color: #065f46;
                font-size: 10px;
                padding: 2px 8px;
                border-radius: 10px;
            }}
            
            .empty-submitted {{
                text-align: center;
                color: var(--light-gray);
                font-size: 13px;
                padding: 20px;
            }}
            
            /* ==================== پنل چپ - فرم ==================== */
            .form-panel {{
                background: white;
                border-radius: 14px;
                padding: 25px;
                border: 1px solid var(--border);
            }}
            
            .form-panel-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid var(--border);
            }}
            
            .form-panel-header h4 {{
                font-size: 16px;
                color: var(--dark);
                margin: 0;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .edit-mode-badge {{
                background: #fef3c7;
                color: #92400e;
                font-size: 12px;
                padding: 5px 14px;
                border-radius: 15px;
                display: none;
                animation: pulse 1.5s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.6; }}
            }}
            
            /* ==================== فیلدهای آمار ==================== */
            .ward-select {{
                width: 100%;
                padding: 12px 16px;
                border: 2px solid var(--border);
                border-radius: 10px;
                font-size: 14px;
                font-family: Tahoma;
                background: white;
                margin-bottom: 20px;
                transition: var(--transition);
                cursor: pointer;
            }}
            
            .ward-select:focus {{
                border-color: var(--primary-light);
                outline: none;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }}
            
            .items-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }}
            
            .item-card {{
                background: var(--bg-light);
                border: 1px solid var(--border);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                transition: var(--transition);
            }}
            
            .item-card:hover {{
                border-color: var(--primary-light);
                box-shadow: 0 2px 10px rgba(59, 130, 246, 0.1);
            }}
            
            .item-card label {{
                display: block;
                font-size: 12px;
                font-weight: 600;
                color: var(--gray);
                margin-bottom: 8px;
            }}
            
            .item-card input {{
                width: 80px;
                padding: 10px;
                border: 2px solid var(--border);
                border-radius: 8px;
                font-size: 16px;
                text-align: center;
                font-family: Tahoma;
                transition: var(--transition);
            }}
            
            .item-card input:focus {{
                border-color: var(--primary-light);
                outline: none;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }}
            
            .item-card .unit {{
                display: block;
                font-size: 10px;
                color: var(--light-gray);
                margin-top: 4px;
            }}
            
            .empty-form {{
                text-align: center;
                padding: 50px 20px;
                color: var(--light-gray);
            }}
            
            .empty-form .icon {{
                font-size: 48px;
                margin-bottom: 15px;
            }}
            
            /* ==================== فرم‌های ورودی ==================== */
            .form-group {{
                margin-bottom: 18px;
            }}
            
            .form-group label {{
                display: block;
                font-size: 13px;
                font-weight: 600;
                color: var(--gray);
                margin-bottom: 6px;
            }}
            
            .form-textarea {{
                width: 100%;
                padding: 12px;
                border: 2px solid var(--border);
                border-radius: 10px;
                font-size: 13px;
                font-family: Tahoma;
                resize: vertical;
                min-height: 70px;
                transition: var(--transition);
            }}
            
            .form-textarea:focus {{
                border-color: var(--primary-light);
                outline: none;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }}
            
            /* ==================== دکمه‌ها ==================== */
            .btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 12px 24px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                font-family: Tahoma;
                transition: var(--transition);
                text-decoration: none;
                white-space: nowrap;
            }}
            
            .btn-lg {{
                padding: 14px 28px;
                font-size: 16px;
            }}
            
            .btn-primary {{
                background: linear-gradient(135deg, var(--primary), var(--primary-light));
                color: white;
                box-shadow: 0 4px 15px rgba(30, 58, 138, 0.2);
            }}
            
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(30, 58, 138, 0.3);
            }}
            
            .btn-primary:active {{
                transform: translateY(0);
            }}
            
            .btn-secondary {{
                background: var(--bg-light);
                color: var(--gray);
                border: 2px solid var(--border);
            }}
            
            .btn-secondary:hover {{
                background: #fee2e2;
                color: var(--danger);
                border-color: var(--danger);
            }}
            
            .btn-refresh {{
                background: white;
                color: var(--primary-light);
                border: 2px solid var(--primary-light);
                font-size: 12px;
                padding: 6px 14px;
            }}
            
            .btn-refresh:hover {{
                background: var(--primary-light);
                color: white;
            }}
            
            .form-actions {{
                display: flex;
                gap: 12px;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid var(--border);
            }}
            
            .form-actions.hidden {{
                display: none;
            }}
            
            .note-group.hidden {{
                display: none;
            }}
            
            /* ==================== Toast Notification ==================== */
            .toast-container {{
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
            }}
            
            .toast {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 24px;
                border-radius: 14px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                animation: slideDown 0.4s ease;
                pointer-events: auto;
                min-width: 300px;
                max-width: 500px;
            }}
            
            .toast.success {{
                background: linear-gradient(135deg, #059669, #10b981);
            }}
            
            .toast.error {{
                background: linear-gradient(135deg, #dc2626, #ef4444);
            }}
            
            .toast.info {{
                background: linear-gradient(135deg, #2563eb, #3b82f6);
            }}
            
            .toast .toast-icon {{
                font-size: 24px;
                flex-shrink: 0;
            }}
            
            .toast .toast-close {{
                margin-right: auto;
                cursor: pointer;
                opacity: 0.7;
                font-size: 18px;
                transition: var(--transition);
            }}
            
            .toast .toast-close:hover {{
                opacity: 1;
            }}
            
            @keyframes slideDown {{
                from {{ opacity: 0; transform: translateY(-30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            @keyframes slideUp {{
                from {{ opacity: 1; transform: translateY(0); }}
                to {{ opacity: 0; transform: translateY(-30px); }}
            }}
            
            /* ==================== رسپانسیو ==================== */
            @media (max-width: 992px) {{
                .main-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .kpi-row {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                
                .items-grid {{
                    grid-template-columns: repeat(3, 1fr);
                }}
            }}
            
            @media (max-width: 576px) {{
                .items-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                
                .kpi-row {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                
                .summary-stats-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                
                .amar-header {{
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                }}
            }}
        </style>
    </head>
    <body>
        
        <!-- ==================== Toast Container ==================== -->
        <div class="toast-container" id="toast-container"></div>
        
        <!-- ==================== محتوای اصلی ==================== -->
        <div class="content-card fade-in">
            
            <!-- هدر -->
            <div class="amar-header">
                <div class="amar-header-left">
                    <h2>📊 پنل ثبت آمار پایان شیفت</h2>
                    <p>ثبت و مدیریت آمار بخش‌ها در شیفت جاری</p>
                </div>
                <div class="amar-header-right">
                    <span class="shift-info-badge">🕒 شیفت: {shift_name}</span>
                    <a href="/module/supervisor" class="back-link">⬅️ بازگشت به منو</a>
                </div>
            </div>
            
            <!-- ==================== کارت‌های KPI ==================== -->
            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-icon">🏥</div>
                    <div class="kpi-value">{total_wards}</div>
                    <div class="kpi-label">کل بخش‌ها</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">✅</div>
                    <div class="kpi-value" style="color:#10b981;">{submitted_count}</div>
                    <div class="kpi-label">ثبت شده</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">⏳</div>
                    <div class="kpi-value" style="color:#f59e0b;">{remaining}</div>
                    <div class="kpi-label">در انتظار ثبت</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">📈</div>
                    <div class="kpi-value">{int(submitted_count/total_wards*100) if total_wards > 0 else 0}%</div>
                    <div class="kpi-label">پیشرفت</div>
                </div>
            </div>
            
            <!-- ==================== آمار تجمعی ==================== -->
            <div class="summary-section">
                <h3>
                    📈 آمار تجمعی شیفت {shift_name}
                    <button class="btn btn-refresh" onclick="location.reload()">🔄 بروزرسانی</button>
                </h3>
                <div class="summary-stats-grid">
                    {total_cards}
                </div>
            </div>
            
            <!-- ==================== چیدمان اصلی ==================== -->
            <div class="main-grid">
                
                <!-- پنل راست: لیست بخش‌های ثبت شده -->
                <div class="side-panel">
                    <div class="side-panel-title">
                        📋 بخش‌های ثبت شده
                        <span class="side-panel-counter">{submitted_count}</span>
                    </div>
                    {submitted_list}
                </div>
                
                <!-- پنل چپ: فرم ثبت -->
                <div class="form-panel" id="form-panel">
                    <div class="form-panel-header">
                        <h4>🏥 ثبت آمار بخش</h4>
                        <span class="edit-mode-badge" id="edit-badge">🔄 حالت ویرایش</span>
                    </div>
                    
                    <form id="amar-form">
                        <input type="hidden" name="shift_id" value="{shift_id}" id="shift-id-input">
                        
                        <select name="ward_id" id="ward-select" class="ward-select" onchange="loadWardData()">
                            <option value="">--- انتخاب بخش ---</option>
                            {ward_options}
                        </select>
                        
                        <div id="ward-items-container">
                            <div class="empty-form">
                                <div class="icon">📋</div>
                                <p>لطفاً یک بخش را از لیست بالا انتخاب کنید</p>
                                <p style="font-size:12px;margin-top:5px;">آیتم‌های آماری بخش نمایش داده خواهد شد</p>
                            </div>
                        </div>
                        
                        <div class="note-group hidden" id="note-group">
                            <div class="form-group">
                                <label>📝 توضیحات</label>
                                <textarea name="note" id="note-input" class="form-textarea" placeholder="توضیحات تکمیلی برای این بخش..."></textarea>
                            </div>
                        </div>
                        
                        <div class="form-actions hidden" id="form-actions">
                            <button type="submit" class="btn btn-primary btn-lg" id="save-btn">
                                <span id="save-btn-text">💾 ثبت نهایی</span>
                                <span id="save-btn-loading" style="display:none;">⏳ در حال ذخیره...</span>
                            </button>
                            <button type="button" class="btn btn-secondary" onclick="resetWard()">
                                ❌ انصراف
                            </button>
                        </div>
                        
                    </form>
                </div>
                
            </div>
            
        </div>
        
        <!-- ==================== اسکریپت‌ها ==================== -->
        <script>
            // ========== داده‌های بخش‌ها ==========
            var wardsData = {wards_json};
            
            // ========== توابع Toast ==========
            function showToast(message, type) {{
                type = type || 'info';
                var container = document.getElementById('toast-container');
                
                var icons = {{
                    success: '✅',
                    error: '❌',
                    info: 'ℹ️'
                }};
                
                var toast = document.createElement('div');
                toast.className = 'toast ' + type;
                toast.innerHTML = 
                    '<span class="toast-icon">' + (icons[type] || '') + '</span>' +
                    '<span>' + message + '</span>' +
                    '<span class="toast-close" onclick="this.parentElement.remove()">✕</span>';
                
                container.appendChild(toast);
                
                // حذف خودکار بعد از ۴ ثانیه
                setTimeout(function() {{
                    if (toast.parentElement) {{
                        toast.style.animation = 'slideUp 0.3s ease forwards';
                        setTimeout(function() {{ toast.remove(); }}, 300);
                    }}
                }}, 4000);
            }}
            
            // ========== لود داده‌های بخش ==========
            function loadWardData() {{
                var wardId = document.getElementById('ward-select').value;
                var container = document.getElementById('ward-items-container');
                var noteGroup = document.getElementById('note-group');
                var formActions = document.getElementById('form-actions');
                var editBadge = document.getElementById('edit-badge');
                
                if (!wardId) {{
                    container.innerHTML = '<div class="empty-form"><div class="icon">📋</div><p>لطفاً یک بخش را انتخاب کنید</p></div>';
                    noteGroup.classList.add('hidden');
                    formActions.classList.add('hidden');
                    editBadge.style.display = 'none';
                    return;
                }}
                
                var data = wardsData[wardId];
                if (!data) {{
                    container.innerHTML = '<div class="empty-form"><div class="icon">⚠️</div><p style="color:#ef4444;">خطا در بارگذاری اطلاعات بخش</p></div>';
                    return;
                }}
                
                var items = data.items;
                var existing = data.existing || {{}};
                var isEdit = Object.keys(existing).length > 0;
                
                if (items.length === 0) {{
                    container.innerHTML = '<div class="empty-form"><div class="icon">📭</div><p>این بخش آیتم آماری ندارد</p><p style="font-size:12px;">از پنل ادمین آیتم تعریف کنید</p></div>';
                    noteGroup.classList.add('hidden');
                    formActions.classList.add('hidden');
                    editBadge.style.display = 'none';
                    return;
                }}
                
                // نمایش/مخفی کردن نشان ویرایش
                editBadge.style.display = isEdit ? 'inline-block' : 'none';
                
                // ساخت فیلدها
                var html = '<div class="items-grid">';
                
                items.forEach(function(item) {{
                    var val = existing[item.ID_item] || 0;
                    html += '<div class="item-card">';
                    html += '<label>' + item.item_name + '</label>';
                    html += '<input type="number" name="item_' + item.ID_item + '" value="' + val + '" min="0" step="1" id="item-' + item.ID_item + '">';
                    if (item.unit) {{
                        html += '<span class="unit">' + item.unit + '</span>';
                    }}
                    html += '</div>';
                }});
                
                html += '</div>';
                container.innerHTML = html;
                noteGroup.classList.remove('hidden');
                formActions.classList.remove('hidden');
                
                // مقدار توضیحات قبلی
                document.getElementById('note-input').value = existing._note || '';
                
                // فوکوس روی اولین فیلد
                setTimeout(function() {{
                    var firstInput = container.querySelector('input[type="number"]');
                    if (firstInput) firstInput.focus();
                }}, 200);
            }}
            
            // ========== انتخاب از لیست ==========
            function selectWard(wardId, wardName) {{
                document.getElementById('ward-select').value = wardId;
                loadWardData();
                // اسکرول به بالای فرم
                document.getElementById('form-panel').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
            
            // ========== ریست فرم ==========
            function resetWard() {{
                document.getElementById('ward-select').value = '';
                loadWardData();
            }}
            
            // ========== ارسال با AJAX ==========
            document.getElementById('amar-form').addEventListener('submit', function(e) {{
                e.preventDefault();
                
                var wardId = document.getElementById('ward-select').value;
                if (!wardId) {{
                    showToast('⛔ لطفاً یک بخش را انتخاب کنید', 'error');
                    return;
                }}
                
                var formData = new FormData(this);
                
                // نمایش لودینگ
                document.getElementById('save-btn-text').style.display = 'none';
                document.getElementById('save-btn-loading').style.display = 'inline';
                document.getElementById('save-btn').disabled = true;
                
                fetch('/module/supervisor/amar/save', {{
                    method: 'POST',
                    body: formData
                }})
                .then(function(response) {{
                    return response.json();
                }})
                .then(function(data) {{
                    // مخفی کردن لودینگ
                    document.getElementById('save-btn-text').style.display = 'inline';
                    document.getElementById('save-btn-loading').style.display = 'none';
                    document.getElementById('save-btn').disabled = false;
                    
                    if (data.success) {{
                        showToast('✅ ' + data.message, 'success');
                        
                        // بروزرسانی داده‌ها بدون رفرش صفحه
                        updateWardsData(wardId, data.saved_values || {{}});
                        
                        // افزودن به لیست بخش‌های ثبت شده
                        addToSubmittedList(wardId, data.ward_name || '');
                        
                        // نمایش نشان ویرایش
                        document.getElementById('edit-badge').style.display = 'inline-block';
                    }} else {{
                        showToast('⛔ ' + data.message, 'error');
                    }}
                }})
                .catch(function(error) {{
                    document.getElementById('save-btn-text').style.display = 'inline';
                    document.getElementById('save-btn-loading').style.display = 'none';
                    document.getElementById('save-btn').disabled = false;
                    showToast('⛔ خطا در ارتباط با سرور', 'error');
                }});
            }});
            
            // ========== بروزرسانی داده‌ها در memory ==========
            function updateWardsData(wardId, savedValues) {{
                if (!wardsData[wardId]) return;
                
                wardsData[wardId].existing = savedValues;
                
                // بروزرسانی مقادیر فیلدها
                if (savedValues) {{
                    Object.keys(savedValues).forEach(function(key) {{
                        if (key === '_note') {{
                            document.getElementById('note-input').value = savedValues[key];
                        }} else {{
                            var input = document.getElementById('item-' + key);
                            if (input) input.value = savedValues[key];
                        }}
                    }});
                }}
            }}
            
            // ========== افزودن به لیست ثبت شده‌ها ==========
            function addToSubmittedList(wardId, wardName) {{
                var sidePanel = document.querySelector('.side-panel');
                var emptyMsg = sidePanel.querySelector('.empty-submitted');
                
                if (emptyMsg) {{
                    emptyMsg.remove();
                }}
                
                // بررسی تکراری نبودن
                var existingItems = sidePanel.querySelectorAll('.submitted-ward-item');
                for (var i = 0; i < existingItems.length; i++) {{
                    if (existingItems[i].textContent.includes(wardName)) {{
                        return; // قبلاً وجود دارد
                    }}
                }}
                
                var newItem = document.createElement('div');
                newItem.className = 'submitted-ward-item';
                newItem.onclick = function() {{ selectWard(wardId, wardName); }};
                newItem.innerHTML = '<span>📝</span><span>' + wardName + '</span><span class="submitted-badge">ثبت شده</span>';
                
                var firstItem = sidePanel.querySelector('.submitted-ward-item');
                if (firstItem) {{
                    sidePanel.insertBefore(newItem, firstItem);
                }} else {{
                    var titleEl = sidePanel.querySelector('.side-panel-title');
                    titleEl.insertAdjacentElement('afterend', newItem);
                }}
            }}
            
            // ========== راهنمای سریع ==========
            console.log('📊 پنل آمار آماده است');
            console.log('   - بخش مورد نظر را انتخاب کنید');
            console.log('   - مقادیر را وارد کنید');
            console.log('   - دکمه ذخیره را بزنید');
            console.log('   - پیام موفقیت به صورت Toast نمایش داده می‌شود');
        </script>
    </body>
    </html>
    '''
    
    return html


# ==========================================
# ۲. تابع کمکی - ساخت JSON داده‌ها
# ==========================================

def _build_wards_json(wards, shift_id):
    """ساخت JSON داده‌های بخش‌ها برای JavaScript"""
    
    data = {}
    for w in wards:
        ward_id = w['ID_nam_bakhsh']
        
        # آیتم‌های آماری بخش
        items = query("""
            SELECT items.ID_item, items.item_name, items.unit
            FROM tbl_bakhsh_amar_config AS config
            JOIN tbl_amar_items AS items ON config.item_id = items.ID_item
            WHERE config.bakhsh_id = %s
            ORDER BY items.item_name
        """, params=(ward_id,), fetch_all=True)
        
        # مقادیر قبلی ثبت شده
        existing = {}
        existing_rows = query("""
            SELECT item_id, value, tozihat 
            FROM tbl_amar_data 
            WHERE bakhsh_id = %s AND nam_shift = %s
        """, params=(ward_id, str(shift_id)), fetch_all=True)
        
        if existing_rows:
            for row in existing_rows:
                existing[row['item_id']] = int(row['value'])
            existing['_note'] = existing_rows[0].get('tozihat', '')
        
        data[str(ward_id)] = {
            'items': items if items else [],
            'existing': existing
        }
    
    return json.dumps(data, ensure_ascii=False)


# ==========================================
# ۳. ذخیره آمار (با خروجی JSON)
# ==========================================

def save_amar(user, form_data):
    """
    ذخیره آمار بخش
    Returns: dict با success و message
    """
    
    user_id = user.get('UserID', 0)
    shift_id = form_data.get('shift_id', '')
    ward_id = form_data.get('ward_id', '')
    note = form_data.get('note', '')
    
    if not ward_id:
        return {'success': False, 'message': 'لطفاً یک بخش را انتخاب کنید'}
    
    # دریافت نام بخش
    ward_info = query(
        "SELECT nam_bakhsh FROM tbl_bakhsh WHERE ID_nam_bakhsh = %s",
        params=(ward_id,),
        fetch_one=True
    )
    ward_name = ward_info['nam_bakhsh'] if ward_info else ''
    
    # دریافت آیتم‌های این بخش
    items = query("""
        SELECT items.ID_item, items.item_name
        FROM tbl_bakhsh_amar_config AS config
        JOIN tbl_amar_items AS items ON config.item_id = items.ID_item
        WHERE config.bakhsh_id = %s
        ORDER BY items.item_name
    """, params=(ward_id,), fetch_all=True)
    
    if not items:
        return {'success': False, 'message': 'این بخش آیتم آماری ندارد'}
    
    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    now = datetime.now().strftime("%H:%M:%S")
    
    saved_values = {'_note': note}
    
    try:
        # حذف داده‌های قبلی این بخش در این شیفت
        query(
            "DELETE FROM tbl_amar_data WHERE bakhsh_id = %s AND nam_shift = %s",
            params=(ward_id, str(shift_id)),
            commit=True
        )
        
        # ثبت داده‌های جدید
        for item in items:
            value = form_data.get(f'item_{item["ID_item"]}', '0')
            value = int(value) if value and str(value).isdigit() else 0
            saved_values[str(item['ID_item'])] = value
            
            query("""
                INSERT INTO tbl_amar_data 
                (bakhsh_id, item_id, value, nam_shift, dat_sabt, zaman_sabt, UserID, tozihat)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, params=(ward_id, item['ID_item'], value, str(shift_id), today, now, user_id, note),
                commit=True
            )
                # ثبت لاگ
        log_crud('save_amar', user_id, key_value=ward_id,
                 new_value=f"شیفت:{shift_id}, بخش:{ward_id}, توضیحات:{note}")
        return {
            'success': True, 
            'message': f'آمار بخش {ward_name} با موفقیت ثبت شد',
            'ward_name': ward_name,
            'saved_values': saved_values
        }
        
    except Exception as e:
            # ثبت لاگ
        log_crud('save_amar', user_id, key_value=ward_id,
                 new_value=f"شیفت:{shift_id}, بخش:{ward_id}, توضیحات:{note}")
        return {'success': False, 'message': f'خطا: {str(e)}'}