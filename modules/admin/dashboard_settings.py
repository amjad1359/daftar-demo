"""
مدیریت محتوای داشبورد - پنل ادمین
CMS ساده برای مدیریت اسلایدر، اخبار و لینک‌های سریع
"""

from models.database import query, get_connection
import jdatetime
from datetime import datetime
import json
from utils.auto_log import log_crud

def get_dashboard_settings_form(user):
    """صفحه مدیریت محتوای داشبورد در پنل ادمین"""
    
    user_id = user.get('UserID', 0)
    full_name = user.get('FullName', '')
    
    # ========== دریافت محتوای فعلی ==========
    contents = query("""
        SELECT * FROM dashboard_content 
        ORDER BY content_type, sort_order
    """, fetch_all=True) or []
    
    # ========== دسته‌بندی محتوا ==========
    sliders = [c for c in contents if c['content_type'] == 'slider']
    news_items = [c for c in contents if c['content_type'] == 'news']
    quick_links = [c for c in contents if c['content_type'] == 'quick_link']
    welcome_msg = next((c for c in contents if c['content_type'] == 'welcome_message'), None)
    banners = [c for c in contents if c['content_type'] == 'banner']
    
    # ========== تابع کمکی برای ساخت لیست ==========
    def build_list_html(items):
        if not items:
            return '<div class="empty">📭 هیچ آیتمی وجود ندارد</div>'
        
        html = ''
        today = int(jdatetime.date.today().strftime("%Y%m%d"))
        
        for item in items:
            is_expired = item.get('expiry_date') and int(str(item.get('expiry_date', 0))) < today
            status_class = 'status-expired' if is_expired else ('status-active' if item.get('is_active') == 1 else 'status-inactive')
            status_text = '⏰ منقضی' if is_expired else ('✅ فعال' if item.get('is_active') == 1 else '❌ غیرفعال')
            
            # escape کردن کاراکترهای خاص
            title = str(item.get('title', '')).replace("'", "\\'").replace('"', '&quot;')
            desc = str(item.get('description', '')).replace("'", "\\'").replace('"', '&quot;')
            
            html += f'''
            <div class="content-item">
                <span class="item-order">#{item.get('sort_order', 1)}</span>
                <div class="item-info">
                    <div class="item-title">
                        {title[:50]}
                        <span class="status-badge {status_class}">{status_text}</span>
                    </div>
                    <div class="item-desc">{desc[:80]}{"..." if len(desc) > 80 else ""}</div>
                </div>
                <div class="item-actions">
                    <button class="btn btn-sm btn-primary" onclick="editContent({item['id']}, '{item['content_type']}')">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteContent({item['id']})">🗑️</button>
                </div>
            </div>
            '''
        return html
    
    # ========== ساخت HTML ==========
    html = f'''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مدیریت محتوای داشبورد</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {{
                --primary: #1e3a8a;
                --success: #10b981;
                --danger: #ef4444;
                --warning: #f59e0b;
                --dark: #1e293b;
                --gray: #64748b;
                --light-gray: #94a3b8;
                --border: #e2e8f0;
                --bg: #f1f5f9;
                --white: #fff;
                --radius: 14px;
                --transition: 0.2s ease;
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; background: var(--bg); color: var(--dark); }}
            
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            
            .page-header {{
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
                border-radius: var(--radius);
                padding: 25px 30px;
                margin-bottom: 25px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 8px 30px rgba(99, 102, 241, 0.25);
            }}
            
            .page-header h2 {{ font-size: 22px; margin: 0; }}
            .back-btn {{
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border: 1.5px solid rgba(255,255,255,0.4);
                border-radius: 8px;
                font-size: 13px;
                transition: var(--transition);
            }}
            .back-btn:hover {{ background: rgba(255,255,255,0.15); }}
            
            .tabs {{
                display: flex;
                gap: 5px;
                margin-bottom: 25px;
                border-bottom: 2px solid var(--border);
                flex-wrap: wrap;
            }}
            .tab {{
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                background: none;
                color: var(--light-gray);
                cursor: pointer;
                border-bottom: 2px solid transparent;
                margin-bottom: -2px;
                transition: var(--transition);
                font-family: inherit;
            }}
            .tab:hover {{ color: var(--dark); }}
            .tab.active {{ color: #6366f1; border-bottom-color: #6366f1; }}
            .tab-content {{ display: none; animation: fadeIn 0.3s ease; }}
            .tab-content.active {{ display: block; }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .card {{
                background: var(--white);
                border-radius: var(--radius);
                padding: 25px;
                border: 1px solid var(--border);
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                margin-bottom: 20px;
            }}
            
            .card-title {{
                font-size: 16px;
                font-weight: bold;
                color: var(--dark);
                margin-bottom: 20px;
                padding-bottom: 12px;
                border-bottom: 2px solid var(--border);
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .form-group {{ margin-bottom: 16px; }}
            .form-group label {{
                display: block;
                font-size: 13px;
                font-weight: 600;
                color: var(--gray);
                margin-bottom: 6px;
            }}
            
            .form-input, .form-select, .form-textarea {{
                width: 100%;
                padding: 12px 14px;
                border: 2px solid var(--border);
                border-radius: 10px;
                font-size: 14px;
                font-family: inherit;
                transition: var(--transition);
                background: var(--white);
            }}
            
            .form-input:focus, .form-select:focus, .form-textarea:focus {{
                border-color: #6366f1;
                outline: none;
                box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
            }}
            
            .form-textarea {{ min-height: 80px; resize: vertical; }}
            
            .btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                font-family: inherit;
                transition: var(--transition);
                text-decoration: none;
            }}
            .btn-primary {{
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
            }}
            .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(99,102,241,0.3); }}
            .btn-danger {{ background: var(--danger); color: white; }}
            .btn-danger:hover {{ background: #dc2626; }}
            .btn-sm {{ padding: 6px 12px; font-size: 12px; }}
            .btn-xs {{ padding: 4px 8px; font-size: 11px; border-radius: 6px; }}
            
            .row {{ display: flex; gap: 10px; flex-wrap: wrap; }}
            .row .form-group {{ flex: 1; min-width: 200px; }}
            
            .content-item {{
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                background: var(--bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                margin-bottom: 8px;
                transition: var(--transition);
            }}
            .content-item:hover {{ border-color: #6366f1; }}
            .content-item .item-order {{ font-weight: bold; color: var(--primary); font-size: 14px; min-width: 30px; }}
            .content-item .item-info {{ flex: 1; }}
            .content-item .item-title {{ font-weight: 600; color: var(--dark); }}
            .content-item .item-desc {{ font-size: 12px; color: var(--gray); margin-top: 3px; }}
            .content-item .item-actions {{ display: flex; gap: 5px; }}
            
            .status-badge {{
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            .status-active {{ background: #d1fae5; color: #065f46; }}
            .status-inactive {{ background: #fee2e2; color: #991b1b; }}
            .status-expired {{ background: #fef3c7; color: #92400e; }}
            
            .toast-box {{
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 8px;
                pointer-events: none;
            }}
            .toast {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 18px;
                border-radius: 10px;
                color: white;
                font-size: 13px;
                font-weight: 600;
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
                animation: slideDown 0.4s ease;
                pointer-events: auto;
            }}
            .toast.ok {{ background: var(--success); }}
            .toast.err {{ background: var(--danger); }}
            @keyframes slideDown {{
                from {{ opacity: 0; transform: translateY(-25px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .empty {{ text-align: center; padding: 40px; color: var(--light-gray); }}
        </style>
    </head>
    <body>
    <div class="toast-box" id="toastBox"></div>
    
    <div class="container">
        <div class="page-header">
            <h2>🎨 مدیریت محتوای داشبورد اصلی</h2>
            <a href="/module/admin" class="back-btn">⬅️ بازگشت</a>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('welcome')">👋 پیام خوش‌آمد</button>
            <button class="tab" onclick="switchTab('sliders')">🎠 اسلایدرها</button>
            <button class="tab" onclick="switchTab('news')">📰 اخبار</button>
            <button class="tab" onclick="switchTab('links')">🔗 لینک‌های سریع</button>
            <button class="tab" onclick="switchTab('banners')">🎯 بنرها</button>
        </div>
        
        <!-- تب پیام خوش‌آمد -->
        <div id="tab-welcome" class="tab-content active">
            <div class="card">
                <div class="card-title">👋 پیام خوش‌آمدگویی</div>
                <form id="welcomeForm">
                    <input type="hidden" name="content_type" value="welcome_message">
                    <input type="hidden" name="id" value="{welcome_msg['id'] if welcome_msg else ''}">
                    
                    <div class="form-group">
                        <label>متن پیام</label>
                        <textarea name="description" class="form-textarea" rows="3" required id="welcome-desc">{welcome_msg['description'] if welcome_msg else ''}</textarea>
                    </div>
                    
                    <button type="button" class="btn btn-primary" onclick="saveContent('welcomeForm')">
                        💾 ذخیره پیام
                    </button>
                </form>
            </div>
        </div>
        
        <!-- تب اسلایدر -->
        <div id="tab-sliders" class="tab-content">
            <div class="card">
                <div class="card-title">🎠 مدیریت اسلایدرها</div>
                
                <form id="sliderForm">
                    <input type="hidden" name="content_type" value="slider">
                    <input type="hidden" name="id" id="edit-id" value="">
                    
                    <div class="row">
                        <div class="form-group">
                            <label>عنوان اسلایدر</label>
                            <input type="text" name="title" id="edit-title" class="form-input" placeholder="عنوان...">
                        </div>
                        <div class="form-group">
                            <label>لینک تصویر (URL)</label>
                            <input type="text" name="image_url" id="edit-image" class="form-input" placeholder="https://...">
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="form-group">
                            <label>متن توضیح</label>
                            <input type="text" name="description" id="edit-desc" class="form-input" placeholder="توضیح کوتاه...">
                        </div>
                        <div class="form-group">
                            <label>لینک مقصد (اختیاری)</label>
                            <input type="text" name="link_url" id="edit-link" class="form-input" placeholder="/module/...">
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="form-group">
                            <label>رنگ پس‌زمینه</label>
                            <input type="color" name="bg_color" id="edit-bg" value="#6366f1" style="height: 40px; width: 80px;">
                        </div>
                        <div class="form-group">
                            <label>ترتیب</label>
                            <input type="number" name="sort_order" id="edit-order" class="form-input" value="1" min="1">
                        </div>
                        <div class="form-group">
                            <label>وضعیت</label>
                            <select name="is_active" id="edit-active" class="form-select">
                                <option value="1">✅ فعال</option>
                                <option value="0">❌ غیرفعال</option>
                            </select>
                        </div>
                    </div>
                    
                    <button type="button" class="btn btn-primary" onclick="saveContent('sliderForm')">
                        💾 ذخیره
                    </button>
                    <button type="button" class="btn btn-sm" onclick="resetForm('sliderForm')" style="margin-right: 10px;">
                        🆕 فرم جدید
                    </button>
                </form>
                
                <div style="margin-top: 20px;">
                    {build_list_html(sliders)}
                </div>
            </div>
        </div>
        
        <!-- تب اخبار -->
        <div id="tab-news" class="tab-content">
            <div class="card">
                <div class="card-title">📰 مدیریت اخبار</div>
                
                <form id="newsForm">
                    <input type="hidden" name="content_type" value="news">
                    <input type="hidden" name="id" id="news-edit-id" value="">
                    
                    <div class="form-group">
                        <label>عنوان خبر</label>
                        <input type="text" name="title" id="news-title" class="form-input" placeholder="عنوان خبر..." required>
                    </div>
                    <div class="form-group">
                        <label>متن خبر</label>
                        <textarea name="description" id="news-desc" class="form-textarea" rows="3"></textarea>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <label>رنگ پس‌زمینه</label>
                            <input type="color" name="bg_color" id="news-bg" value="#3b82f6" style="height: 40px; width: 80px;">
                        </div>
                        <div class="form-group">
                            <label>وضعیت</label>
                            <select name="is_active" id="news-active" class="form-select">
                                <option value="1">✅ فعال</option>
                                <option value="0">❌ غیرفعال</option>
                            </select>
                        </div>
                    </div>
                    
                    <button type="button" class="btn btn-primary" onclick="saveContent('newsForm')">
                        💾 ذخیره خبر
                    </button>
                </form>
                
                <div style="margin-top: 20px;">
                    {build_list_html(news_items)}
                </div>
            </div>
        </div>
        
        <!-- تب لینک‌های سریع -->
        <div id="tab-links" class="tab-content">
            <div class="card">
                <div class="card-title">🔗 مدیریت لینک‌های سریع</div>
                
                <form id="linkForm">
                    <input type="hidden" name="content_type" value="quick_link">
                    <input type="hidden" name="id" id="link-edit-id" value="">
                    
                    <div class="row">
                        <div class="form-group">
                            <label>عنوان لینک</label>
                            <input type="text" name="title" id="link-title" class="form-input" placeholder="متن نمایشی..." required>
                        </div>
                        <div class="form-group">
                            <label>آدرس مقصد</label>
                            <input type="text" name="link_url" id="link-url" class="form-input" placeholder="/module/..." required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <label>آیکون (Emoji)</label>
                            <input type="text" name="description" id="link-icon" class="form-input" placeholder="📊" maxlength="5">
                        </div>
                        <div class="form-group">
                            <label>رنگ پس‌زمینه</label>
                            <input type="color" name="bg_color" id="link-bg" value="#3b82f6" style="height: 40px; width: 80px;">
                        </div>
                        <div class="form-group">
                            <label>ترتیب</label>
                            <input type="number" name="sort_order" id="link-order" class="form-input" value="1" min="1">
                        </div>
                    </div>
                    
                    <button type="button" class="btn btn-primary" onclick="saveContent('linkForm')">
                        💾 ذخیره لینک
                    </button>
                </form>
                
                <div style="margin-top: 20px;">
                    {build_list_html(quick_links)}
                </div>
            </div>
        </div>
        
        <!-- تب بنرها -->
        <div id="tab-banners" class="tab-content">
            <div class="card">
                <div class="card-title">🎯 مدیریت بنرها</div>
                
                <form id="bannerForm">
                    <input type="hidden" name="content_type" value="banner">
                    <input type="hidden" name="id" id="banner-edit-id" value="">
                    
                    <div class="form-group">
                        <label>متن بنر</label>
                        <input type="text" name="title" id="banner-title" class="form-input" placeholder="متن بنر..." required>
                    </div>
                    <div class="form-group">
                        <label>توضیح (اختیاری)</label>
                        <input type="text" name="description" id="banner-desc" class="form-input" placeholder="توضیح کوتاه...">
                    </div>
                    <div class="row">
                        <div class="form-group">
                            <label>رنگ پس‌زمینه</label>
                            <input type="color" name="bg_color" id="banner-bg" value="#6366f1" style="height: 40px; width: 80px;">
                        </div>
                        <div class="form-group">
                            <label>رنگ متن</label>
                            <input type="color" name="text_color" id="banner-text" value="#ffffff" style="height: 40px; width: 80px;">
                        </div>
                    </div>
                    
                    <button type="button" class="btn btn-primary" onclick="saveContent('bannerForm')">
                        💾 ذخیره بنر
                    </button>
                </form>
                
                <div style="margin-top: 20px;">
                    {build_list_html(banners)}
                </div>
            </div>
        </div>
   


       

        <!-- راهنمای جامع -->
        <div class="card" style="margin-top: 30px; border: 2px solid #6366f1;">
            <div class="help-toggle" onclick="toggleHelp()" style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; padding: 15px 0;">
                <div class="card-title" style="margin-bottom: 0; padding-bottom: 0; border-bottom: none;">
                    <span>📖 راهنمای کامل مدیریت محتوای داشبورد</span>
                    <span style="font-size: 12px; color: var(--gray); font-weight: normal; margin-right: 10px;">
                        کلیک کنید تا باز شود
                    </span>
                </div>
                <span id="helpArrow" style="font-size: 20px; transition: transform 0.3s ease;">▼</span>
            </div>
            
            <div id="helpContent" style="display: none; padding-top: 10px; border-top: 1px solid var(--border);">
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    
                    <!-- ستون راست -->
                    <div>
                        <div style="background: #f0f9ff; border-right: 4px solid #3b82f6; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <h4 style="color: #1e3a8a; margin-top: 0;">👋 پیام خوش‌آمدگویی</h4>
                            <ul style="padding-right: 20px; line-height: 2; color: #475569;">
                                <li><strong>متن پیام:</strong> متنی که در بالای داشبورد اصلی نمایش داده می‌شود</li>
                                <li><strong>وضعیت:</strong> فعال/غیرفعال کردن پیام</li>
                                <li><strong>نکته:</strong> فقط یک پیام خوش‌آمدگویی می‌تواند فعال باشد</li>
                                <li><strong>محل نمایش:</strong> بالای صفحه داشبورد اصلی</li>
                            </ul>
                        </div>
                        
                        <div style="background: #fdf2f8; border-right: 4px solid #ec4899; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <h4 style="color: #9d174d; margin-top: 0;">🎠 اسلایدرها</h4>
                            <ul style="padding-right: 20px; line-height: 2; color: #475569;">
                                <li><strong>عنوان:</strong> متن بزرگ نمایش داده شده روی اسلایدر</li>
                                <li><strong>لینک تصویر:</strong> آدرس اینترنتی تصویر پس‌زمینه (اختیاری)</li>
                                <li><strong>متن توضیح:</strong> توضیح کوتاه زیر عنوان</li>
                                <li><strong>لینک مقصد:</strong> کاربر با کلیک به این آدرس هدایت می‌شود</li>
                                <li><strong>رنگ پس‌زمینه:</strong> اگر تصویر ندارید، رنگ پس‌زمینه را تنظیم کنید</li>
                                <li><strong>ترتیب:</strong> شماره ترتیب نمایش (۱ = اول)</li>
                                <li><strong>تاریخ انقضا:</strong> بعد از این تاریخ، اسلایدر مخفی می‌شود</li>
                                <li><strong>محل نمایش:</strong> بالای داشبورد، زیر پیام خوش‌آمد</li>
                            </ul>
                        </div>
                    </div>
                    
                    <!-- ستون چپ -->
                    <div>
                        <div style="background: #fef3c7; border-right: 4px solid #f59e0b; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <h4 style="color: #92400e; margin-top: 0;">📰 اخبار و اطلاعیه‌ها</h4>
                            <ul style="padding-right: 20px; line-height: 2; color: #475569;">
                                <li><strong>عنوان خبر:</strong> تیتر اطلاعیه (bold نمایش داده می‌شود)</li>
                                <li><strong>متن خبر:</strong> توضیحات تکمیلی (اختیاری)</li>
                                <li><strong>رنگ پس‌زمینه:</strong> رنگ نوار خبر - می‌توانید از رنگ‌های مختلف استفاده کنید:
                                    <br>🔴 قرمز: هشدارها | 🟡 زرد: اطلاعیه‌های مهم | 🟢 سبز: اخبار خوب | 🔵 آبی: عمومی
                                </li>
                                <li><strong>تاریخ انقضا:</strong> خبر بعد از این تاریخ مخفی می‌شود</li>
                                <li><strong>محل نمایش:</strong> زیر لینک‌های سریع در داشبورد</li>
                            </ul>
                        </div>
                        
                        <div style="background: #d1fae5; border-right: 4px solid #10b981; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <h4 style="color: #065f46; margin-top: 0;">🔗 لینک‌های سریع</h4>
                            <ul style="padding-right: 20px; line-height: 2; color: #475569;">
                                <li><strong>عنوان لینک:</strong> متن نمایشی روی کارت</li>
                                <li><strong>آدرس مقصد:</strong> مسیر در سیستم (مثال: <code>/module/supervisor/shift</code>)</li>
                                <li><strong>آیکون (Emoji):</strong> یک ایموجی برای نمایش روی کارت (مثال: 📊 👥 📅)</li>
                                <li><strong>رنگ:</strong> رنگ hover کارت (وقتی موس روی آن می‌رود)</li>
                                <li><strong>ترتیب:</strong> موقعیت نمایش (۱ = اول از راست)</li>
                                <li><strong>محل نمایش:</strong> زیر کارت‌های آمار KPI</li>
                                <li><strong>پیشنهاد:</strong> ۴ تا ۸ لینک پرکاربرد اضافه کنید</li>
                            </ul>
                        </div>
                        
                        <div style="background: #ede9fe; border-right: 4px solid #8b5cf6; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                            <h4 style="color: #5b21b6; margin-top: 0;">🎯 بنرها</h4>
                            <ul style="padding-right: 20px; line-height: 2; color: #475569;">
                                <li><strong>متن بنر:</strong> عنوان اصلی بنر (بزرگ و bold)</li>
                                <li><strong>توضیح:</strong> متن تکمیلی (اختیاری)</li>
                                <li><strong>لینک:</strong> آدرس مقصد (اختیاری - اگر خالی باشد، بنر قابل کلیک نیست)</li>
                                <li><strong>رنگ پس‌زمینه:</strong> رنگ کل بنر</li>
                                <li><strong>رنگ متن:</strong> رنگ نوشته‌ها (معمولاً سفید)</li>
                                <li><strong>محل نمایش:</strong> انتهای داشبورد</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- نکات کلی -->
                <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; border-radius: 12px; margin-top: 20px;">
                    <h3 style="margin-top: 0; text-align: center;">💡 نکات طلایی برای مدیریت بهتر</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 15px;">
                        <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 28px;">🎯</div>
                            <strong>قانون سه‌ثانیه</strong>
                            <p style="font-size: 12px; margin: 5px 0 0 0; opacity: 0.9;">محتوا باید در ۳ ثانیه اول توجه کاربر را جلب کند</p>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 28px;">📱</div>
                            <strong>موبایل فرندلی</strong>
                            <p style="font-size: 12px; margin: 5px 0 0 0; opacity: 0.9;">همه محتواها در موبایل هم بهینه نمایش داده می‌شوند</p>
                        </div>
                        <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 28px;">⏰</div>
                            <strong>تاریخ انقضا</strong>
                            <p style="font-size: 12px; margin: 5px 0 0 0; opacity: 0.9;">حتماً برای محتواهای موقت تاریخ انقضا تنظیم کنید</p>
                        </div>
                    </div>
                </div>
                
                <!-- مثال‌های آماده -->
                <div style="margin-top: 20px;">
                    <h4 style="color: #1e293b;">🎨 مثال‌های آماده برای کپی کردن:</h4>
                    
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-top: 10px;">
                        <p style="font-weight: bold; margin-top: 0;">📰 خبر فوری:</p>
                        <div style="background: #ef4444; color: white; padding: 10px 15px; border-radius: 8px; margin-bottom: 10px;">
                            <strong>⚠️ اطلاعیه مهم</strong>
                            <p style="margin: 5px 0 0 0;">امروز بازرسی وزارت بهداشت ساعت ۱۰ صبح</p>
                        </div>
                        
                        <p style="font-weight: bold;">🔗 لینک پرکاربرد:</p>
                        <div style="display: flex; gap: 10px;">
                            <div style="background: white; border: 2px solid #3b82f6; border-radius: 10px; padding: 10px 15px; text-align: center; font-size: 13px;">
                                <span style="font-size: 20px;">📅</span><br>
                                <strong>ثبت شیفت</strong>
                            </div>
                            <div style="background: white; border: 2px solid #10b981; border-radius: 10px; padding: 10px 15px; text-align: center; font-size: 13px;">
                                <span style="font-size: 20px;">📊</span><br>
                                <strong>گزارشات</strong>
                            </div>
                            <div style="background: white; border: 2px solid #8b5cf6; border-radius: 10px; padding: 10px 15px; text-align: center; font-size: 13px;">
                                <span style="font-size: 20px;">👥</span><br>
                                <strong>پرسنل</strong>
                            </div>
                        </div>
                    </div>
                </div>
                
            </div>
        </div>

        <script>
            function toggleHelp() {{
                const content = document.getElementById('helpContent');
                const arrow = document.getElementById('helpArrow');
                
                if (content.style.display === 'none') {{
                    content.style.display = 'block';
                    arrow.style.transform = 'rotate(180deg)';
                }} else {{
                    content.style.display = 'none';
                    arrow.style.transform = 'rotate(0deg)';
                }}
            }}
        </script>







   </div>
    
    <script>
        function switchTab(tab) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            const tabMap = {{'welcome': 0, 'sliders': 1, 'news': 2, 'links': 3, 'banners': 4}};
            document.querySelectorAll('.tab')[tabMap[tab]].classList.add('active');
            document.getElementById('tab-' + tab).classList.add('active');
        }}
        
        function toast(msg, type) {{
            const box = document.getElementById('toastBox');
            const t = document.createElement('div');
            t.className = 'toast ' + (type === 'ok' ? 'ok' : 'err');
            t.innerHTML = '<span>' + (type === 'ok' ? '✅' : '❌') + '</span><span>' + msg + '</span>';
            box.appendChild(t);
            setTimeout(() => t.remove(), 3000);
        }}
        
        async function saveContent(formId) {{
            const form = document.getElementById(formId);
            const formData = new FormData(form);
            
            try {{
                const res = await fetch('/module/admin/dashboard/save', {{
                    method: 'POST',
                    body: formData
                }});
                const data = await res.json();
                
                if (data.success) {{
                    toast(data.message, 'ok');
                    setTimeout(() => location.reload(), 1000);
                }} else {{
                    toast(data.message, 'err');
                }}
            }} catch(e) {{
                toast('خطا در ارتباط با سرور', 'err');
            }}
        }}
        
        async function editContent(id, type) {{
            try {{
                const res = await fetch('/module/admin/dashboard/get/' + id);
                const data = await res.json();
                
                if (data.success) {{
                    const item = data.item;
                    const prefix = type === 'slider' ? 'edit' : type === 'news' ? 'news' : type === 'quick_link' ? 'link' : 'banner';
                    
                    // تنظیم شناسه
                    const idField = document.getElementById(prefix + '-edit-id');
                    if (idField) idField.value = item.id;
                    
                    // تنظیم فیلدها
                    if (document.getElementById(prefix + '-title')) document.getElementById(prefix + '-title').value = item.title || '';
                    if (document.getElementById(prefix + '-desc')) document.getElementById(prefix + '-desc').value = item.description || '';
                    if (document.getElementById(prefix + '-image')) document.getElementById(prefix + '-image').value = item.image_url || '';
                    if (document.getElementById(prefix + '-link')) document.getElementById(prefix + '-link').value = item.link_url || '';
                    if (document.getElementById(prefix + '-bg')) document.getElementById(prefix + '-bg').value = item.bg_color || '#6366f1';
                    if (document.getElementById(prefix + '-text')) document.getElementById(prefix + '-text').value = item.text_color || '#ffffff';
                    if (document.getElementById(prefix + '-order')) document.getElementById(prefix + '-order').value = item.sort_order || 1;
                    if (document.getElementById(prefix + '-active')) document.getElementById(prefix + '-active').value = item.is_active ? '1' : '0';
                    if (document.getElementById(prefix + '-icon')) document.getElementById(prefix + '-icon').value = item.description || '';
                    
                    // سوییچ به تب مربوطه
                    const tabMap = {{'slider': 'sliders', 'news': 'news', 'quick_link': 'links', 'banner': 'banners'}};
                    switchTab(tabMap[type] || 'sliders');
                    window.scrollTo(0, 0);
                }}
            }} catch(e) {{
                toast('خطا در دریافت اطلاعات', 'err');
            }}
        }}
        
        async function deleteContent(id) {{
            if (!confirm('آیا از حذف این آیتم اطمینان دارید؟')) return;
            
            try {{
                const formData = new FormData();
                formData.append('id', id);
                
                const res = await fetch('/module/admin/dashboard/delete', {{
                    method: 'POST',
                    body: formData
                }});
                const data = await res.json();
                
                if (data.success) {{
                    toast(data.message, 'ok');
                    setTimeout(() => location.reload(), 1000);
                }} else {{
                    toast(data.message, 'err');
                }}
            }} catch(e) {{
                toast('خطا در ارتباط با سرور', 'err');
            }}
        }}
        
        function resetForm(formId) {{
            const form = document.getElementById(formId);
            const idField = form.querySelector('input[name="id"]');
            if (idField) idField.value = '';
            form.reset();
        }}
    </script>
    </body>
    </html>
    '''
    
    return html


# ==================== API Functions ====================

def save_dashboard_content(user, form_data):
    user_id = user.get('UserID', 0)
    content_id = form_data.get('id')
    content_type = form_data.get('content_type')
    title = form_data.get('title', '')
    description = form_data.get('description', '')
    image_url = form_data.get('image_url', '')
    link_url = form_data.get('link_url', '')
    link_text = form_data.get('link_text', '')
    bg_color = form_data.get('bg_color', '#3b82f6')
    text_color = form_data.get('text_color', '#ffffff')
    sort_order = int(form_data.get('sort_order', 1))
    is_active = int(form_data.get('is_active', 1))
    expiry_date = form_data.get('expiry_date', None)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if content_id and content_id.strip():
            # ---- ویرایش ----
            old_record = query("SELECT * FROM dashboard_content WHERE id = %s", (content_id,), fetch_one=True)
            cursor.execute("""
                UPDATE dashboard_content SET
                    title=%s, description=%s, image_url=%s, link_url=%s, link_text=%s,
                    bg_color=%s, text_color=%s, sort_order=%s, is_active=%s, expiry_date=%s
                WHERE id=%s
            """, (title, description, image_url, link_url, link_text, bg_color, text_color,
                  sort_order, is_active, expiry_date if expiry_date else None, int(content_id)))
            conn.commit()

            log_crud('save_dashboard', user_id, key_value=int(content_id),
                     old_value=json.dumps(old_record, ensure_ascii=False, default=str),
                     new_value=json.dumps({
                         "type": content_type, "title": title, "desc": description,
                         "link": link_url, "active": is_active
                     }, ensure_ascii=False))
            return {'success': True, 'message': '✅ محتوا با موفقیت بروزرسانی شد'}
        else:
            # ---- ثبت جدید ----
            cursor.execute("""
                INSERT INTO dashboard_content
                (content_type, title, description, image_url, link_url, link_text,
                 bg_color, text_color, sort_order, is_active, expiry_date, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """, (content_type, title, description, image_url, link_url, link_text,
                  bg_color, text_color, sort_order, is_active, expiry_date if expiry_date else None))
            conn.commit()
            new_id = cursor.lastrowid

            log_crud('save_dashboard', user_id, key_value=new_id,
                     new_value=json.dumps({
                         "type": content_type, "title": title, "desc": description,
                         "link": link_url, "active": is_active
                     }, ensure_ascii=False))
            return {'success': True, 'message': '✅ محتوا با موفقیت ذخیره شد'}
    except Exception as e:
        return {'success': False, 'message': f'⛔ خطا: {str(e)}'}
    finally:
        conn.close()



def get_content_by_id(content_id):
    """دریافت یک آیتم محتوا با شناسه"""
    try:
        item = query("SELECT * FROM dashboard_content WHERE id = %s", params=(content_id,), fetch_one=True)
        if item:
            # تبدیل bytearray به string
            for key in item:
                if isinstance(item[key], (bytearray, bytes)):
                    item[key] = item[key].decode('utf-8', errors='ignore')
            return {'success': True, 'item': item}
        return {'success': False, 'message': 'آیتم یافت نشد'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def delete_dashboard_content(user, form_data):
    user_id = user.get('UserID', 0)
    content_id = form_data.get('id')
    if not content_id:
        return {'success': False, 'message': 'شناسه نامعتبر است'}

    try:
        old_record = query("SELECT * FROM dashboard_content WHERE id = %s", (content_id,), fetch_one=True)
        query("DELETE FROM dashboard_content WHERE id = %s", params=(content_id,), commit=True)
        log_crud('delete_dashboard', user_id, key_value=int(content_id),
                 old_value=json.dumps(old_record, ensure_ascii=False, default=str))
        return {'success': True, 'message': '✅ آیتم با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'⛔ خطا: {str(e)}'}



def get_dashboard_content(content_type=None, active_only=True):
    """دریافت محتوای داشبورد برای نمایش در صفحه اصلی"""
    sql = "SELECT * FROM dashboard_content WHERE 1=1"
    params = []
    
    if content_type:
        sql += " AND content_type = %s"
        params.append(content_type)
    
    if active_only:
        today = int(jdatetime.date.today().strftime("%Y%m%d"))
        sql += " AND is_active = 1 AND (expiry_date IS NULL OR expiry_date >= %s)"
        params.append(today)
    
    sql += " ORDER BY sort_order ASC"
    
    return query(sql, params=params, fetch_all=True) or []
    