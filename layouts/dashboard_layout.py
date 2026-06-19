"""
داشبورد اصلی - با محتوای داینامیک از پنل ادمین
نمایش اسلایدر، اخبار، لینک‌های سریع، بنرها و پیام خوش‌آمد
"""

from models.database import query
import jdatetime


def get_dashboard_content(content_type=None):
    """دریافت محتوای فعال داشبورد از دیتابیس"""
    sql = "SELECT * FROM dashboard_content WHERE is_active = 1"
    params = []
    
    if content_type:
        sql += " AND content_type = %s"
        params.append(content_type)
    
    # بررسی تاریخ انقضا
    today = int(jdatetime.date.today().strftime("%Y%m%d"))
    sql += " AND (expiry_date IS NULL OR expiry_date >= %s)"
    params.append(today)
    
    sql += " ORDER BY sort_order ASC"
    
    return query(sql, params=params, fetch_all=True) or []


def get_active_shift_info():
    """دریافت اطلاعات شیفت فعال"""
    sql = "SELECT ID_shift, tarkib, nam_shift FROM shift_namt ORDER BY ID_shift DESC LIMIT 1"
    return query(sql, fetch_one=True)


def get_dashboard_stats():
    """دریافت آمار کلی برای کارت‌های KPI"""
    stats = {
        'shift': '---',
        'present': '---',
        'reports': '---',
        'critical': '---'
    }
    
    try:
        # شیفت فعال
        shift = get_active_shift_info()
        if shift:
            stats['shift'] = shift.get('tarkib', '---')
        
        # تعداد پرسنل حاضر
        if shift:
            present = query(
                "SELECT COUNT(*) as cnt FROM tbl_hozor WHERE nam_shift = %s AND ispresent = 1",
                params=(str(shift['ID_shift']),),
                fetch_one=True
            )
            if present:
                stats['present'] = str(present['cnt'])
        
        # گزارشات امروز
        today = int(jdatetime.date.today().strftime("%Y%m%d"))
        reports = query(
            "SELECT COUNT(*) as cnt FROM tbl_gozaresh WHERE dat_sabt = %s",
            params=(today,),
            fetch_one=True
        )
        if reports:
            stats['reports'] = str(reports['cnt'])
        
        # موارد بحرانی (کدهای عملیاتی امروز)
        crisis = query(
            "SELECT COUNT(*) as cnt FROM tbl_amliat_kod WHERE dat_sabt = %s",
            params=(today,),
            fetch_one=True
        )
        if crisis:
            stats['critical'] = str(crisis['cnt'])
            
    except Exception as e:
        print(f"[DASHBOARD STATS ERROR] {e}")
    
    return stats


def get_dashboard_html():
    """
    تولید HTML محتوای داشبورد اصلی با محتوای داینامیک
    
    Returns:
        str: HTML محتوای داشبورد (فقط body، بدون html/head)
    """
    
    # ========== دریافت محتوا از دیتابیس ==========
    welcome_msg = get_dashboard_content('welcome_message')
    sliders = get_dashboard_content('slider')
    news_items = get_dashboard_content('news')
    quick_links = get_dashboard_content('quick_link')
    banners = get_dashboard_content('banner')
    
    # ========== آمار KPI ==========
    stats = get_dashboard_stats()
    
    # ========== استایل‌های مخصوص داشبورد ==========
    css = '''
    <style>
        /* هدر داشبورد */
        .dashboard-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
        }
        .dashboard-header h1 { margin: 0; font-size: 1.8rem; font-weight: 700; }
        .dashboard-header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1rem; }
        
        /* اسلایدر */
        .slider-wrapper {
            position: relative;
            overflow: hidden;
            border-radius: 1rem;
            margin-bottom: 2rem;
            height: 220px;
        }
        .slider-track {
            display: flex;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
        }
        .slider-slide {
            min-width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            text-decoration: none;
            color: white;
            text-align: center;
        }
        .slider-slide h3 { font-size: 1.4rem; margin-bottom: 0.5rem; }
        .slider-slide p { font-size: 0.95rem; opacity: 0.9; }
        
        .slider-dots {
            position: absolute;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 8px;
            z-index: 10;
        }
        .slider-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: rgba(255,255,255,0.4);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .slider-dot.active {
            background: white;
            width: 12px;
            height: 12px;
        }
        
        /* کارت‌های آمار KPI */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: white;
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 25px rgba(0,0,0,0.1);
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 4px;
            height: 100%;
        }
        .stat-card:nth-child(1)::before { background: #3b82f6; }
        .stat-card:nth-child(2)::before { background: #10b981; }
        .stat-card:nth-child(3)::before { background: #8b5cf6; }
        .stat-card:nth-child(4)::before { background: #f59e0b; }
        
        .stat-card-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            margin-bottom: 1rem;
        }
        .stat-card:nth-child(1) .stat-card-icon { background: #dbeafe; color: #3b82f6; }
        .stat-card:nth-child(2) .stat-card-icon { background: #d1fae5; color: #10b981; }
        .stat-card:nth-child(3) .stat-card-icon { background: #ede9fe; color: #8b5cf6; }
        .stat-card:nth-child(4) .stat-card-icon { background: #fef3c7; color: #f59e0b; }
        
        .stat-card-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.25rem;
        }
        .stat-card-label { color: #64748b; font-size: 0.875rem; }
        
        /* لینک‌های سریع */
        .section-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .quick-links-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .quick-link-card {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
            text-decoration: none;
            transition: all 0.3s ease;
            color: inherit;
            display: block;
        }
        .quick-link-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-color: var(--hover-color, #3b82f6);
        }
        .quick-link-icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .quick-link-title { font-weight: 600; font-size: 0.9rem; color: #1e293b; }
        
        /* اخبار */
        .news-section { margin-bottom: 2rem; }
        .news-item {
            padding: 1rem 1.25rem;
            border-radius: 0.75rem;
            color: white;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }
        .news-item:hover { transform: translateX(-5px); }
        .news-item strong { font-size: 0.95rem; }
        .news-item p { margin: 0.25rem 0 0 0; font-size: 0.85rem; opacity: 0.95; }
        
        /* بنرها */
        .banner-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .banner-card {
            padding: 1.5rem;
            border-radius: 1rem;
            text-decoration: none;
            transition: all 0.3s ease;
            display: block;
        }
        .banner-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .banner-card h3 { font-size: 1.1rem; margin: 0 0 0.5rem 0; }
        .banner-card p { font-size: 0.9rem; margin: 0; opacity: 0.9; }
        .banner-btn {
            display: inline-block;
            margin-top: 0.75rem;
            padding: 0.4rem 1.2rem;
            background: rgba(255,255,255,0.25);
            border-radius: 2rem;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        /* رسپانسیو */
        @media (max-width: 768px) {
            .slider-wrapper { height: 180px; }
            .quick-links-grid { grid-template-columns: repeat(2, 1fr); }
            .banner-grid { grid-template-columns: 1fr; }
        }
    </style>
    '''
    
    # ========== ساخت اسلایدر ==========
    slider_html = ''
    if sliders:
        slides = ''
        dots = ''
        for i, slide in enumerate(sliders):
            bg = slide.get('bg_color', '#6366f1')
            link = slide.get('link_url', '')
            title = slide.get('title', '')
            desc = slide.get('description', '')
            
            content = f'<h3>{title}</h3><p>{desc}</p>'
            
            if link:
                slides += f'<a href="{link}" class="slider-slide" style="background: {bg};">{content}</a>'
            else:
                slides += f'<div class="slider-slide" style="background: {bg};">{content}</div>'
            
            dots += f'<span class="slider-dot {"active" if i == 0 else ""}" onclick="goToSlide({i})"></span>'
        
        slider_html = f'''
        <div class="slider-wrapper">
            <div class="slider-track" id="sliderTrack">
                {slides}
            </div>
            <div class="slider-dots">
                {dots}
            </div>
        </div>
        '''
    
    # ========== ساخت هدر خوش‌آمد ==========
    welcome_text = 'به سامانه جامع دفتر پرستاری خوش آمدید'
    if welcome_msg and len(welcome_msg) > 0:
        welcome_text = welcome_msg[0].get('description', welcome_text)
    
    welcome_html = f'''
    <div class="dashboard-header">
        <h1>🎯 داشبورد اصلی</h1>
        <p>{welcome_text}</p>
    </div>
    '''
    
    # ========== کارت‌های KPI ==========
    kpi_html = f'''
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-card-icon">📅</div>
            <div class="stat-card-value">{stats['shift']}</div>
            <div class="stat-card-label">شیفت فعال</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-icon">👥</div>
            <div class="stat-card-value">{stats['present']}</div>
            <div class="stat-card-label">پرسنل حاضر</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-icon">📋</div>
            <div class="stat-card-value">{stats['reports']}</div>
            <div class="stat-card-label">گزارشات امروز</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-icon">⚠️</div>
            <div class="stat-card-value">{stats['critical']}</div>
            <div class="stat-card-label">کدهای عملیاتی</div>
        </div>
    </div>
    '''
    
    # ========== لینک‌های سریع ==========
    links_html = ''
    if quick_links:
        links_html = '<h3 class="section-title">🔗 دسترسی سریع</h3><div class="quick-links-grid">'
        for link in quick_links:
            bg = link.get('bg_color', '#3b82f6')
            icon = link.get('description', '🔗')
            title = link.get('title', '')
            url = link.get('link_url', '#')
            
            links_html += f'''
            <a href="{url}" class="quick-link-card" style="--hover-color: {bg};">
                <div class="quick-link-icon">{icon}</div>
                <div class="quick-link-title">{title}</div>
            </a>
            '''
        links_html += '</div>'
    
    # ========== اخبار ==========
    news_html = ''
    if news_items:
        news_html = '<div class="news-section"><h3 class="section-title">📰 اطلاعیه‌ها و اخبار</h3>'
        for news in news_items:
            bg = news.get('bg_color', '#3b82f6')
            title = news.get('title', '')
            desc = news.get('description', '')
            news_html += f'''
            <div class="news-item" style="background: {bg};">
                <strong>{title}</strong>
                {f'<p>{desc}</p>' if desc else ''}
            </div>
            '''
        news_html += '</div>'
    
    # ========== بنرها ==========
    banners_html = ''
    if banners:
        banners_html = '<h3 class="section-title">🎯 اطلاعیه‌های ویژه</h3><div class="banner-grid">'
        for banner in banners:
            bg = banner.get('bg_color', '#6366f1')
            text_color = banner.get('text_color', '#ffffff')
            title = banner.get('title', '')
            desc = banner.get('description', '')
            link = banner.get('link_url', '')
            link_text = banner.get('link_text', 'مشاهده')
            
            inner = f'''
            <h3 style="color: {text_color};">{title}</h3>
            {f'<p style="color: {text_color};">{desc}</p>' if desc else ''}
            <span class="banner-btn" style="color: {text_color};">{link_text} →</span>
            '''
            
            if link:
                banners_html += f'<a href="{link}" class="banner-card" style="background: {bg};">{inner}</a>'
            else:
                banners_html += f'<div class="banner-card" style="background: {bg};">{inner}</div>'
        
        banners_html += '</div>'
    
    # ========== اسکریپت اسلایدر ==========
    slider_script = ''
    if sliders and len(sliders) > 1:
        slider_script = f'''
        <script>
            let currentSlide = 0;
            const totalSlides = {len(sliders)};
            
            function goToSlide(index) {{
                currentSlide = index;
                const track = document.getElementById('sliderTrack');
                track.style.transform = 'translateX(' + (currentSlide * 100) + '%)';
                
                document.querySelectorAll('.slider-dot').forEach((dot, i) => {{
                    dot.classList.toggle('active', i === currentSlide);
                }});
            }}
            
            // حرکت خودکار
            setInterval(function() {{
                currentSlide = (currentSlide + 1) % totalSlides;
                goToSlide(currentSlide);
            }}, 4000);
        </script>
        '''
    
    # ========== مونتاژ نهایی محتوا ==========
    content_html = f'''
    {css}
    {welcome_html}
    {slider_html}
    {slider_script}
    {kpi_html}
    {links_html}
    {news_html}
    {banners_html}
    '''
    
    return content_html