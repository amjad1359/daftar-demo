"""
گزارش بحران‌ها و کدهای عمومی – نسخهٔ ارتقاء‌یافته
نمودارهای تعاملی Chart.js، تحلیل عمیق آماری، لود سریع
"""

from models.database import query
import json
import requests
from datetime import datetime as dt
from utils.formatters import format_date_display
import math


def get_crisis_report(user):
    """صفحه اصلی گزارش بحران"""

    import jdatetime
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    three_months_ago = (jdatetime.date.today() - jdatetime.timedelta(days=90)).strftime("%Y/%m/%d")

    # لود فیلترهای ثابت (سریع)
    code_list = query("SELECT ID_onvan_kod_o, nam_kod_o FROM tbl_onvan_kod_omomy ORDER BY nam_kod_o", fetch_all=True) or []
    location_list = query("SELECT DISTINCT nam_mahal FROM tbl_kod_omomy WHERE nam_mahal IS NOT NULL AND nam_mahal != '' ORDER BY nam_mahal", fetch_all=True) or []
    shift_list = query("SELECT DISTINCT s.ID_shift, s.tarkib FROM shift_namt s ORDER BY s.tarkib", fetch_all=True) or []

    code_opts = '<option value="">همه کدها</option>' + ''.join(f'<option value="{c["ID_onvan_kod_o"]}">{c["nam_kod_o"]}</option>' for c in code_list)
    loc_opts = '<option value="">همه مکان‌ها</option>' + ''.join(f'<option value="{l["nam_mahal"]}">{l["nam_mahal"]}</option>' for l in location_list)
    shift_opts = '<option value="">همه شیفت‌ها</option>' + ''.join(f'<option value="{s["ID_shift"]}">{s["tarkib"]}</option>' for s in shift_list)

    # آمار اولیه خالی
    stats = {'total': 0, 'avg_duration': 0, 'high_severity': 0, 'total_attendees': 0, 'unique_locations': 0}
    table_html = '<tr><td colspan="10" class="empty">در حال بارگذاری...</td></tr>'
    dash_html = '<div class="empty">در حال بارگذاری نمودارها...</div>'

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>گزارش بحران</title>
<script src="/static/js/chart.umd.min.js"></script>
<style>
    :root {{
        --orange: #ea580c; --orange-l: #f97316; --green: #10b981; --red: #ef4444; --yellow: #f59e0b;
        --gray: #64748b; --l-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9; --white: #fff; --r: 12px;
        --primary: #ea580c; --primary-light: #f97316; --dark: #1e293b; --light-gray: #94a3b8;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial; direction:rtl; background:var(--bg); color:#1e293b; }}
    .container {{ max-width:1400px; margin:0 auto; padding:16px; }}
    
    .header {{ background:linear-gradient(135deg,#ea580c,#c2410c); color:white; border-radius:var(--r); padding:18px 24px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 6px 20px rgba(234,88,12,.25); }}
    .header h2 {{ font-size:20px; }}
    .header a {{ color:white; text-decoration:none; padding:7px 14px; border:1.5px solid rgba(255,255,255,.4); border-radius:8px; font-size:12px; }}

    .kpi {{ display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:14px; }}
    .kpi-card {{ background:white; border-radius:10px; padding:15px; text-align:center; border:1px solid var(--border); }}
    .kpi-val {{ font-size:22px; font-weight:bold; }}
    .kpi-lbl {{ font-size:11px; color:var(--gray); margin-top:2px; }}

    .filters {{ background:white; border-radius:var(--r); padding:14px; border:1px solid var(--border); margin-bottom:14px; }}
    .f-row {{ display:flex; gap:8px; flex-wrap:wrap; align-items:flex-end; }}
    .f-row+.f-row {{ margin-top:8px; }}
    .f-grp {{ flex:1; min-width:100px; }}
    .f-grp label {{ display:block; font-size:10px; font-weight:600; color:var(--gray); margin-bottom:3px; }}
    .f-grp select, .f-grp input {{ width:100%; padding:7px 9px; border:2px solid var(--border); border-radius:6px; font-size:12px; font-family:inherit; }}
    .f-grp select:focus, .f-grp input:focus {{ border-color:var(--orange); outline:none; }}

    .btn {{ padding:7px 15px; border:none; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; font-family:inherit; white-space:nowrap; }}
    .btn-orange {{ background:var(--orange); color:white; }}
    .btn-grn {{ background:var(--green); color:white; }}
    .btn-amb {{ background:#f59e0b; color:white; }}
    .btn-xs {{ padding:5px 10px; font-size:10px; }}

    .tabs {{ display:flex; gap:4px; margin-bottom:12px; border-bottom:2px solid var(--border); }}
    .tab {{ padding:8px 16px; font-size:12px; font-weight:600; border:none; background:none; color:var(--l-gray); cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-2px; font-family:inherit; }}
    .tab.on {{ color:var(--orange); border-bottom-color:var(--orange); }}
    .pan {{ display:none; }}
    .pan.on {{ display:block; }}

    .tbl-wrap {{ background:white; border-radius:var(--r); border:1px solid var(--border); overflow:hidden; }}
    .tbl-scroll {{ overflow:auto; max-height:500px; }}
    table {{ width:100%; border-collapse:collapse; font-size:11px; }}
    th {{ background:var(--orange); color:white; padding:9px 5px; text-align:center; font-weight:600; position:sticky; top:0; z-index:5; }}
    td {{ padding:7px 5px; text-align:center; border-bottom:1px solid var(--border); }}
    tr:hover td {{ background:#fff7ed; }}
    tr[data-id] {{ cursor:pointer; }}

    .badge {{ padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; display:inline-block; color:white; }}
    .badge-h {{ background:var(--red); }}
    .badge-m {{ background:var(--yellow); }}
    .badge-l {{ background:var(--green); }}

    .charts {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
    .chart-box {{ background:white; border-radius:10px; padding:14px; border:1px solid var(--border); }}
    .chart-box h4 {{ margin-bottom:10px; font-size:13px; text-align:center; }}
    canvas {{ max-height:250px; }}

    .pagination {{ display:flex; justify-content:center; gap:10px; margin-top:15px; }}
    .bar {{ display:flex; gap:8px; justify-content:flex-end; margin-top:10px; }}
    .empty {{ text-align:center; padding:30px; color:var(--l-gray); }}

    .spinner {{
        width: 40px; height: 40px;
        border: 4px solid #e2e8f0;
        border-top-color: #ea580c;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin: 0 auto 10px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .ai-analysis-box {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        line-height: 2;
        font-size: 14px;
        white-space: pre-wrap;
    }}

    .detail-info p {{
        margin: 8px 0;
        line-height: 1.8;
        border-bottom: 1px dashed var(--border);
        padding-bottom: 6px;
    }}
    .detail-info strong {{
        display: inline-block;
        width: 100px;
        color: var(--primary);
    }}
    .file-item {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 10px 12px;
        margin-bottom: 8px;
        border-radius: 8px;
        border: 1px solid var(--border);
        transition: all 0.2s;
    }}
    .file-item:hover {{
        border-color: var(--primary-light);
        transform: translateX(-3px);
    }}
    .file-name {{
        font-size: 12px;
        color: var(--dark);
        word-break: break-all;
    }}
    .person-item {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: white;
        padding: 10px 12px;
        margin-bottom: 8px;
        border-radius: 8px;
        border: 1px solid var(--border);
    }}
    .person-avatar {{
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }}
    .person-info {{
        flex: 1;
    }}
    .person-name {{
        font-weight: bold;
        font-size: 13px;
    }}
    .person-contact {{
        font-size: 11px;
        color: var(--gray);
        margin-top: 3px;
    }}
    .person-contact span {{
        margin-left: 10px;
        direction: ltr;
        display: inline-block;
    }}

    @media (max-width:768px) {{ .kpi {{ grid-template-columns:repeat(2,1fr); }} .charts {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h2>🔥 مدیریت جامع بحران و پایش کدهای عمومی</h2>
        <a href="/module/reports">⬅️ بازگشت</a>
    </div>

    <div class="kpi">
        <div class="kpi-card"><div class="kpi-val" style="color:#ea580c;" id="k-total">{stats['total']}</div><div class="kpi-lbl">📋 کل رخدادها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#2563eb;" id="k-avg">{stats['avg_duration']}</div><div class="kpi-lbl">⏱ میانگین مدت (دقیقه)</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#ef4444;" id="k-high">{stats['high_severity']}</div><div class="kpi-lbl">🔴 شدت زیاد</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#8b5cf6;" id="k-attendees">{stats['total_attendees']}</div><div class="kpi-lbl">👥 افراد حاضر</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#10b981;" id="k-locs">{stats['unique_locations']}</div><div class="kpi-lbl">📍 مکان‌های درگیر</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ</label><input type="text" id="f-from" value="{three_months_ago}"></div>
            <div class="f-grp"><label>تا تاریخ</label><input type="text" id="f-to" value="{today_j}"></div>
            <div class="f-grp"><label>نوع کد/بحران</label><select id="f-code">{code_opts}</select></div>
            <div class="f-grp"><label>محل وقوع</label><select id="f-location">{loc_opts}</select></div>
            <div class="f-grp"><label>شیفت</label><select id="f-shift">{shift_opts}</select></div>
        </div>
        <div class="f-row">
            <div class="f-grp"><label>شدت بحران</label><select id="f-severity"><option value="">همه موارد</option><option value="high">🔴 زیاد</option><option value="medium">🟠 متوسط</option><option value="low">🟢 کم</option></select></div>
            <div class="f-grp" style="flex:2;"><label>جستجو در توضیحات</label><input type="text" id="f-search" placeholder="کلمه کلیدی..."></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-orange" onclick="refresh(1)">🔍 اعمال فیلتر</button></div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab on" data-tab="dash" onclick="switchTab('dash')">📊 داشبورد</button>
        <button class="tab" data-tab="list" onclick="switchTab('list')">📋 لیست رخدادها</button>
        <button class="tab" data-tab="detail" onclick="switchTab('detail')">📄 جزئیات کامل رخداد</button>
        <button class="tab" data-tab="ai" onclick="switchTab('ai')">🤖 تحلیل هوشمند</button>
    </div>

    <div id="pan-dash" class="pan on">{dash_html}</div>

    <div id="pan-list" class="pan">
        <div class="tbl-wrap"><div class="tbl-scroll"><table>
            <thead><tr><th>کد</th><th>تاریخ</th><th>نوع</th><th>محل</th><th>شیفت</th><th>شدت</th><th>شروع</th><th>مدت</th><th>نتیجه</th><th>حاضرین</th></tr></thead>
            <tbody id="tbl-body">{table_html}</tbody>
        </table></div></div>
        <div id="pagination" class="pagination"></div>
        <div class="bar">
            <button class="btn btn-grn btn-xs" onclick="doExport()">📥 Excel</button>
            <button class="btn btn-amb btn-xs" onclick="doPrint()">🖨️ چاپ</button>
        </div>
    </div>

    <div id="pan-detail" class="pan">
        <div class="card" id="detail-card" style="display:none;">
            <div class="detail-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; padding-bottom:15px; border-bottom:2px solid var(--border);">
                <h3 style="margin:0; color:var(--primary);">
                    <span id="detail-title">جزئیات رخداد</span>
                </h3>
                <button class="btn btn-sm" onclick="closeDetail()" style="background:#f1f5f9;">✖️ بستن</button>
            </div>
            
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;" id="detail-content">
                <!-- اطلاعات اصلی در سمت راست -->
                <div class="detail-info" style="background:var(--bg); border-radius:12px; padding:18px;">
                    <h4 style="margin-bottom:12px; color:var(--primary);">📋 اطلاعات رخداد</h4>
                    <div id="detail-info-text"></div>
                </div>
                
                <!-- اسناد و پرسنل در سمت چپ -->
                <div style="display:flex; flex-direction:column; gap:20px;">
                    <!-- اسناد -->
                    <div class="detail-files" style="background:var(--bg); border-radius:12px; padding:18px;">
                        <h4 style="margin-bottom:12px; color:var(--primary);">📎 اسناد و مدارک</h4>
                        <div id="detail-files-list" style="min-height:100px;"></div>
                    </div>
                    
                    <!-- پرسنل فراخوان -->
                    <div class="detail-personnel" style="background:var(--bg); border-radius:12px; padding:18px;">
                        <h4 style="margin-bottom:12px; color:var(--primary);">👥 پرسنل فراخوان شده</h4>
                        <div id="detail-personnel-list"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="detail-empty" class="card" style="text-align:center; padding:60px;">
            <div style="font-size:48px; margin-bottom:15px;">🔍</div>
            <h3 style="color:var(--gray);">جهت مشاهده جزئیات، روی یک رخداد کلیک کنید</h3>
            <p style="color:var(--light-gray); font-size:13px;">با کلیک روی هر ردیف در تب "لیست رخدادها"، اطلاعات کامل نمایش داده می‌شود</p>
        </div>
    </div>

    <div id="pan-ai" class="pan">
        <div class="card">
            <div class="card-title">🤖 تحلیل هوشمند بحران</div>
            <div class="row" style="margin-bottom:15px;">
                <div class="form-group" style="flex:2;">
                    <label>🔑 کلید API دیپ‌سیک (اختیاری)</label>
                    <input type="text" id="deepseek-key" class="form-input" placeholder="sk-...">
                    <small>با وارد کردن کلید، تحلیل عمیق‌تری دریافت می‌کنید</small>
                </div>
                <div class="form-group" style="flex:0 0 auto; align-self: flex-end;">
                    <button class="btn btn-orange" onclick="startAIAnalysis()">🔍 شروع تحلیل</button>
                </div>
            </div>
            <div id="ai-loading" style="display:none; text-align:center; padding:20px;">
                <div class="spinner"></div>
                <p>در حال تحلیل...</p>
            </div>
            <div id="ai-result" style="display:none;">
                <div class="notification info" id="ai-source"></div>
                <div class="ai-analysis-box" id="ai-text"></div>
            </div>
        </div>
    </div>
</div>

<script>
    let allData = [];
    let currentPage = 1;
    let totalPages = 1;

    function switchTab(t) {{
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.classList.toggle('on', tab.dataset.tab === t);
        }});
        document.querySelectorAll('.pan').forEach(p => p.classList.remove('on'));
        document.getElementById('pan-'+t).classList.add('on');
        if (t === 'dash') renderCharts(allData);
    }}

    async function refresh(page = 1) {{
        const p = new URLSearchParams({{
            from: (document.getElementById('f-from').value||'').replace(/\//g,''),
            to: (document.getElementById('f-to').value||'').replace(/\//g,''),
            code: document.getElementById('f-code').value,
            location: document.getElementById('f-location').value,
            shift: document.getElementById('f-shift').value,
            severity: document.getElementById('f-severity').value,
            search: document.getElementById('f-search').value,
            page: page,
            per_page: 15
        }});
        const r = await fetch('/module/reports/crisis/data?'+p.toString());
        const d = await r.json();
        allData = d.data || [];
        const s = d.stats || {{}};

        document.getElementById('k-total').textContent = s.total||0;
        document.getElementById('k-avg').textContent = s.avg_duration||0;
        document.getElementById('k-high').textContent = s.high_severity||0;
        document.getElementById('k-attendees').textContent = s.total_attendees||0;
        document.getElementById('k-locs').textContent = s.unique_locations||0;

        // اضافه کردن onclick برای هر ردیف
        document.getElementById('tbl-body').innerHTML = allData.length ? allData.map(r => {{
            const sev = (r.severity||'').includes('زیاد')||r.severity=='3' ? '<span class="badge badge-h">زیاد</span>' : (r.severity||'').includes('متوسط')||r.severity=='2' ? '<span class="badge badge-m">متوسط</span>' : '<span class="badge badge-l">کم</span>';
            return `<tr data-id="${{r.ID_kod_omomy}}" onclick="showDetail('${{r.ID_kod_omomy}}')">
                <td>${{r.ID_kod_omomy}}</td><td>${{r.date_display||''}}</td><td>${{r.code_title||''}}</td>
                <td>${{r.location||''}}</td><td>${{r.shift_name||''}}</td><td>${{sev}}</td>
                <td>${{(r.start_time||'').substring(0,5)}}</td><td>${{r.duration||0}}</td>
                <td>${{r.outcome||'-'}}</td><td>${{r.attendees_count||0}}</td>
            </tr>`;
        }}).join('') : '<tr><td colspan="10" class="empty">داده‌ای یافت نشد</td></tr>';

        if (d.available_shifts) populateShiftDropdown(d.available_shifts);

        currentPage = d.page || 1;
        totalPages = Math.ceil((d.total || 0) / 15);
        renderPagination();
        renderCharts(allData);
    }}

    // تابع نمایش جزئیات
    async function showDetail(recordId) {{
        const detailCard = document.getElementById('detail-card');
        const detailEmpty = document.getElementById('detail-empty');
        
        // نمایش حالت بارگذاری
        document.getElementById('detail-files-list').innerHTML = '<div style="text-align:center; padding:20px;">⏳ در حال بارگذاری...</div>';
        document.getElementById('detail-personnel-list').innerHTML = '';
        detailCard.style.display = 'block';
        detailEmpty.style.display = 'none';
        document.getElementById('detail-title').innerHTML = `رخداد #${{recordId}}`;
        
        try {{
            const res = await fetch(`/module/reports/crisis/detail/${{recordId}}`);
            const data = await res.json();
            
            if (!data.success) {{
                document.getElementById('detail-files-list').innerHTML = `<div class="empty-state">${{data.message}}</div>`;
                return;
            }}
            
            const r = data.record;
            
            // اطلاعات اصلی
            let infoHtml = `
                <p><strong>📅 تاریخ:</strong> ${{r.date_display || '-'}}</p>
                <p><strong>🕒 زمان شروع:</strong> ${{(r.time_saat_dagig_shoro || '').substring(0,5) || '-'}}</p>
                <p><strong>🏁 زمان پایان:</strong> ${{(r.time_sat_dagigeh_paian || '').substring(0,5) || '-'}}</p>
                <p><strong>📍 محل:</strong> ${{r.location || '-'}}</p>
                <p><strong>📈 شدت:</strong> ${{r.severity || '-'}}</p>
                <p><strong>🏥 شیفت:</strong> ${{r.shift_name || '-'}}</p>
                <p><strong>📝 نتیجه:</strong> ${{r.outcome || '-'}}</p>
                <p><strong>🛠️ اقدامات:</strong> ${{r.action_taken || '-'}}</p>
                <p><strong>📌 توضیحات:</strong> ${{r.description || '-'}}</p>
                <p><strong>👤 ثبت‌کننده:</strong> ${{r.registrar || '-'}}</p>
            `;
            document.getElementById('detail-info-text').innerHTML = infoHtml;
            
            // فایل‌ها
            let filesHtml = '';
            if (data.files && data.files.length > 0) {{
                data.files.forEach(file => {{
                    const fileName = file.split('/').pop();
                    filesHtml += `
                        <div class="file-item">
                            <span class="file-name">📄 ${{fileName}}</span>
                            <a href="/${{file}}" target="_blank" class="btn btn-sm" style="background:var(--primary-light); color:white; text-decoration:none;" download>📥 دانلود</a>
                        </div>
                    `;
                }});
            }} else {{
                filesHtml = '<div class="empty-state" style="padding:20px;">📭 هیچ سندی برای این رخداد ثبت نشده است</div>';
            }}
            document.getElementById('detail-files-list').innerHTML = filesHtml;
            
            // پرسنل
            let personnelHtml = '';
            if (data.personnel && data.personnel.length > 0) {{
                data.personnel.forEach((p, idx) => {{
                    const initial = (p.full_name || p.nam_person || '?').charAt(0);
                    personnelHtml += `
                        <div class="person-item">
                            <div class="person-avatar">${{initial}}</div>
                            <div class="person-info">
                                <div class="person-name">${{p.full_name || p.nam_person + ' ' + (p.fam_person || '')}}</div>
                                <div class="person-contact">
                                    ${{p.number_mobil ? `<span>📱 ${{p.number_mobil}}</span>` : ''}}
                                    ${{p.number_tel ? `<span>📞 ${{p.number_tel}}</span>` : ''}}
                                </div>
                                ${{p.adres ? `<div class="person-address" style="font-size:10px; color:var(--light-gray); margin-top:3px;">🏠 ${{p.adres.substring(0,50)}}</div>` : ''}}
                            </div>
                        </div>
                    `;
                }});
            }} else {{
                personnelHtml = '<div class="empty-state" style="padding:20px;">👥 هیچ پرسنلی برای این رخداد ثبت نشده است</div>';
            }}
            document.getElementById('detail-personnel-list').innerHTML = personnelHtml;
            
            // رفتن به تب جزئیات
            switchTab('detail');
            
        }} catch(e) {{
            console.error(e);
            document.getElementById('detail-files-list').innerHTML = '<div class="empty-state">خطا در دریافت اطلاعات</div>';
        }}
    }}

    function closeDetail() {{
        document.getElementById('detail-card').style.display = 'none';
        document.getElementById('detail-empty').style.display = 'block';
    }}

    function populateShiftDropdown(shifts) {{
        const sel = document.getElementById('f-shift');
        const cur = sel.value;
        sel.innerHTML = '<option value="">همه شیفت‌ها</option>';
        shifts.forEach(s => sel.innerHTML += `<option value="${{s[0]}}">${{s[1]}}</option>`);
        if (shifts.some(s => s[0] == cur)) sel.value = cur; else sel.value = '';
    }}

    function renderPagination() {{
        const container = document.getElementById('pagination');
        if (totalPages <= 1) {{ container.innerHTML = ''; return; }}
        let html = '';
        if (currentPage > 1) html += `<button class="btn btn-orange btn-xs" onclick="refresh(${{currentPage-1}})">« قبلی</button>`;
        html += `<span style="display:flex;align-items:center;font-size:13px;">صفحه ${{currentPage}} از ${{totalPages}}</span>`;
        if (currentPage < totalPages) html += `<button class="btn btn-orange btn-xs" onclick="refresh(${{currentPage+1}})">بعدی »</button>`;
        container.innerHTML = html;
    }}

    // نمودارها (بدون تغییر)
    function renderCharts(data) {{
        setTimeout(() => {{
            ['chart-codes','chart-severity','chart-locations','chart-trend','chart-duration'].forEach(id => {{
                const existing = Chart.getChart(id);
                if (existing) existing.destroy();
            }});

            if (!data.length) {{
                document.getElementById('pan-dash').innerHTML = '<div class="empty">داده‌ای نیست</div>';
                return;
            }}

            document.getElementById('pan-dash').innerHTML = `
                <div class="charts">
                    <div class="chart-box"><h4>🥧 توزیع فراوانی کدها</h4><canvas id="chart-codes"></canvas></div>
                    <div class="chart-box"><h4>📊 توزیع شدت بحران</h4><canvas id="chart-severity"></canvas></div>
                    <div class="chart-box"><h4>📍 پرتکرارترین مکان‌ها</h4><canvas id="chart-locations"></canvas></div>
                    <div class="chart-box"><h4>📈 روند روزانه بحران‌ها (۳۰ روز اخیر)</h4><canvas id="chart-trend"></canvas></div>
                    <div class="chart-box"><h4>⏱ توزیع مدت زمان (دقیقه)</h4><canvas id="chart-duration"></canvas></div>
                </div>
            `;

            const colors = ['#ea580c','#f97316','#fb923c','#fdba74','#fed7aa','#ffedd5'];
            const cm={{}};
            data.forEach(r => {{ const k=r.code_title||'نامشخص'; cm[k]=(cm[k]||0)+1; }});
            new Chart(document.getElementById('chart-codes'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(cm),
                    datasets: [{{ data: Object.values(cm), backgroundColor: colors.slice(0, Object.keys(cm).length) }}]
                }}
            }});

            const sm={{}};
            data.forEach(r => {{
                const k=(r.severity||'').includes('زیاد')||r.severity=='3'?'🔴 زیاد':(r.severity||'').includes('متوسط')||r.severity=='2'?'🟠 متوسط':'🟢 کم';
                sm[k]=(sm[k]||0)+1;
            }});
            new Chart(document.getElementById('chart-severity'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(sm),
                    datasets: [{{ data: Object.values(sm), backgroundColor: ['#ef4444','#f59e0b','#10b981'] }}]
                }},
                options: {{ responsive: true }}
            }});

            const lm={{}};
            data.forEach(r => {{ const k=r.location||'نامشخص'; lm[k]=(lm[k]||0)+1; }});
            const topLocs = Object.entries(lm).sort((a,b) => b[1]-a[1]).slice(0,8);
            new Chart(document.getElementById('chart-locations'), {{
                type: 'bar',
                data: {{
                    labels: topLocs.map(([k]) => k),
                    datasets: [{{ data: topLocs.map(([,v]) => v), backgroundColor: '#f97316' }}]
                }},
                options: {{ responsive: true, indexAxis: 'y' }}
            }});

            const daily={{}};
            data.forEach(r => {{ const d=r.date_display||''; daily[d]=(daily[d]||0)+1; }});
            const sortedDays = Object.entries(daily).sort((a,b) => a[0].localeCompare(b[0])).slice(-30);
            new Chart(document.getElementById('chart-trend'), {{
                type: 'line',
                data: {{
                    labels: sortedDays.map(([k]) => k.substring(5)),
                    datasets: [{{ label: 'تعداد بحران', data: sortedDays.map(([,v]) => v), borderColor: '#ea580c', tension: 0.3 }}]
                }},
                options: {{ responsive: true }}
            }});

            const bins = [0,10,20,30,45,60,90,120];
            const durData = {{}};
            bins.slice(0,-1).forEach((b,i) => {{
                const label = `${{b}}-${{bins[i+1]}}`;
                durData[label] = data.filter(r => (r.duration||0) >= b && (r.duration||0) < bins[i+1]).length;
            }});
            new Chart(document.getElementById('chart-duration'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(durData),
                    datasets: [{{ data: Object.values(durData), backgroundColor: '#dc2626' }}]
                }},
                options: {{ responsive: true }}
            }});
        }}, 50);
    }}

    // تحلیل هوشمند (بدون تغییر)
    async function startAIAnalysis() {{
        const loading = document.getElementById('ai-loading');
        const result = document.getElementById('ai-result');
        loading.style.display = 'block';
        result.style.display = 'none';
        const deepseekKey = document.getElementById('deepseek-key').value.trim();
        const params = new URLSearchParams({{
            from: (document.getElementById('f-from').value||'').replace(/\\//g,''),
            to: (document.getElementById('f-to').value||'').replace(/\\//g,''),
            code: document.getElementById('f-code').value,
            location: document.getElementById('f-location').value,
            shift: document.getElementById('f-shift').value,
            severity: document.getElementById('f-severity').value,
            search: document.getElementById('f-search').value,
            deepseek_key: deepseekKey
        }});
        try {{
            const res = await fetch('/module/reports/crisis/analyze?' + params.toString());
            const data = await res.json();
            loading.style.display = 'none';
            if (data.success) {{
                document.getElementById('ai-source').innerHTML = '✅ منبع تحلیل: <strong>' + data.source_name + '</strong>';
                document.getElementById('ai-text').innerHTML = data.analysis.replace(/\\n/g, '<br>');
                result.style.display = 'block';
            }}
        }} catch(e) {{ console.error(e); }}
    }}

    function doExport() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),code:document.getElementById('f-code').value,location:document.getElementById('f-location').value,shift:document.getElementById('f-shift').value,severity:document.getElementById('f-severity').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/crisis/export?'+p.toString(),'_blank');
    }}

    function doPrint() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),code:document.getElementById('f-code').value,location:document.getElementById('f-location').value,shift:document.getElementById('f-shift').value,severity:document.getElementById('f-severity').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/crisis/print?'+p.toString(),'_blank');
    }}

    document.addEventListener('DOMContentLoaded', () => refresh(1));
</script>
</body>
</html>'''
    return html


def _fetch_data(d_from='', d_to='', code='', location='', shift='', severity='', search='', page=1, per_page=15):
    offset = (page - 1) * per_page
    base_join = """FROM tbl_kod_omomy k
                    LEFT JOIN tbl_onvan_kod_omomy o ON k.onvan_kod_omomy = o.ID_onvan_kod_o
                    LEFT JOIN shift_namt s ON k.nam_shift = s.ID_shift
                    LEFT JOIN users u ON k.UserID = u.UserID
                    WHERE 1=1"""
    base_params = []

    if d_from: base_join += " AND k.dat_sabt >= %s"; base_params.append(d_from)
    if d_to: base_join += " AND k.dat_sabt <= %s"; base_params.append(d_to)
    if code: base_join += " AND k.onvan_kod_omomy = %s"; base_params.append(code)
    if location: base_join += " AND k.nam_mahal = %s"; base_params.append(location)
    if severity == 'high': base_join += " AND (k.shedat_bohran = '3' OR k.shedat_bohran LIKE '%زیاد%')"
    elif severity == 'medium': base_join += " AND (k.shedat_bohran = '2' OR k.shedat_bohran LIKE '%متوسط%')"
    elif severity == 'low': base_join += " AND (k.shedat_bohran = '1' OR k.shedat_bohran LIKE '%کم%')"
    if search: base_join += " AND k.tavzih LIKE %s"; base_params.append(f'%{search}%')

    data_sql = f"""SELECT k.ID_kod_omomy, k.dat_sabt, k.nam_mahal AS location, k.shedat_bohran AS severity,
                    k.time_saat_dagig_shoro AS start_time, k.time_sat_dagigeh_paian AS end_time,
                    k.eghdam AS action_taken, k.natijeh_amlit AS outcome, k.tavzih AS description,
                    o.nam_kod_o AS code_title, s.tarkib AS shift_name, s.ID_shift AS shift_id, u.FullName AS registrar {base_join}"""
    data_params = base_params.copy()
    if shift: data_sql += " AND k.nam_shift = %s"; data_params.append(shift)
    data_sql += " ORDER BY k.ID_kod_omomy DESC LIMIT %s OFFSET %s"; data_params.extend([per_page, offset])

    count_sql = f"SELECT COUNT(*) as total {base_join}"
    count_params = base_params.copy()
    if shift: count_sql += " AND k.nam_shift = %s"; count_params.append(shift)

    shifts_sql = f"SELECT DISTINCT s.ID_shift, s.tarkib {base_join} ORDER BY s.tarkib"
    shifts_params = base_params.copy()

    data = query(data_sql, data_params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0
    available_shifts = [(r['ID_shift'], r['tarkib']) for r in (query(shifts_sql, shifts_params, fetch_all=True) or [])]

    ids = [str(r['ID_kod_omomy']) for r in data]
    att_data = {}
    if ids:
        att_sql = f"""SELECT id_cod_omomi, COALESCE(p.nam,kp.nam_person) AS p_name, COALESCE(p.famil,kp.fam_person) AS p_family
                      FROM tbl_kod_omomy_person kp LEFT JOIN tbl_person p ON kp.preson_id=p.ID_person
                      WHERE kp.id_cod_omomi IN ({','.join(ids)})"""
        atts = query(att_sql, fetch_all=True) or []
        for a in atts:
            kid = str(a['id_cod_omomi'])
            if kid not in att_data: att_data[kid] = []
            att_data[kid].append(f"{a.get('p_name','')} {a.get('p_family','')}".strip())

    for row in data:
        row['date_display'] = format_date_display(row.get('dat_sabt'))
        s = str(row.get('start_time') or '')[:5]; e = str(row.get('end_time') or '')[:5]
        try:
            t1 = dt.strptime(s, "%H:%M") if s and ':' in s else dt(2000,1,1)
            t2 = dt.strptime(e, "%H:%M") if e and ':' in e else dt(2000,1,1)
            diff = (t2 - t1).total_seconds() / 60
            row['duration'] = int(diff) if diff >= 0 else int(diff + 1440)
        except: row['duration'] = 0
        kid = str(row['ID_kod_omomy'])
        att_list = att_data.get(kid, [])
        row['attendees'] = '، '.join(att_list) if att_list else 'بدون لیست حاضرین'
        row['attendees_count'] = len(att_list)

    avg_dur = int(sum(r.get('duration', 0) for r in data) / len(data)) if data else 0
    high_sev = sum(1 for r in data if 'زیاد' in str(r.get('severity','')) or str(r.get('severity')) == '3')
    total_att = sum(r.get('attendees_count', 0) for r in data)
    unique_locs = len(set(r.get('location', '') for r in data))

    return {
        'data': data,
        'stats': {'total': total, 'avg_duration': avg_dur, 'high_severity': high_sev, 'total_attendees': total_att, 'unique_locations': unique_locs},
        'total': total, 'page': page, 'per_page': per_page,
        'available_shifts': available_shifts
    }



def _build_table(data):
    if not data: return '<tr><td colspan="10" class="empty">داده‌ای یافت نشد</td></tr>'
    rows = []
    for r in data:
        sev = str(r.get('severity', ''))
        if 'زیاد' in sev or sev == '3': s = '<span class="badge badge-h">زیاد</span>'
        elif 'متوسط' in sev or sev == '2': s = '<span class="badge badge-m">متوسط</span>'
        else: s = '<span class="badge badge-l">کم</span>'
        rows.append(f"<tr><td>{r.get('ID_kod_omomy','')}</td><td>{r.get('date_display','')}</td><td>{r.get('code_title','')}</td><td>{r.get('location','')}</td><td>{r.get('shift_name','')}</td><td>{s}</td><td>{str(r.get('start_time',''))[:5]}</td><td>{r.get('duration',0)}</td><td>{r.get('outcome','-')}</td><td>{r.get('attendees_count',0)}</td></tr>")
    return ''.join(rows)


def _build_dashboard(data):
    return '<div class="empty">در حال بارگذاری نمودارها...</div>'


# ==================== تحلیل هوشمند (داخلی و DeepSeek) ====================

def _generate_ai_summary(data):
    """خلاصه آماری پیشرفته برای تحلیل هوشمند"""
    if not data: return {}
    total = len(data)
    avg_dur = round(sum(r.get('duration',0) for r in data) / total, 1) if total else 0

    daily_counts = {}
    for r in data:
        day = r.get('date_display','')[:10]
        daily_counts[day] = daily_counts.get(day, 0) + 1
    sorted_days = sorted(daily_counts.keys())
    values = [daily_counts[d] for d in sorted_days]

    moving_avg = []
    for i in range(len(values)):
        window = values[max(0, i-6):i+1]
        moving_avg.append(round(sum(window)/len(window), 1))

    mean_val = sum(values)/len(values) if values else 0
    std_val = math.sqrt(sum((v-mean_val)**2 for v in values)/len(values)) if len(values) > 1 else 0
    outliers = []
    for i, v in enumerate(values):
        if std_val > 0 and abs(v-mean_val)/std_val > 2:
            outliers.append({'date': sorted_days[i], 'value': v, 'z_score': round(abs(v-mean_val)/std_val, 2)})

    risk_scores = {}
    for r in data:
        code = r.get('code_title','نامشخص')
        if code not in risk_scores: risk_scores[code] = {'total':0, 'bad':0}
        risk_scores[code]['total'] += 1
        sev = str(r.get('severity',''))
        if 'زیاد' in sev or sev == '3':
            risk_scores[code]['bad'] += 1

    return {
        'total_events': total,
        'avg_duration': avg_dur,
        'code_types': {r.get('code_title','نامشخص'): data.count(r) for r in data},
        'locations': list(set(r.get('location','') for r in data)),
        'top_locations': sorted([(loc, sum(1 for r in data if r.get('location')==loc)) for loc in set(r.get('location','') for r in data)], key=lambda x: x[1], reverse=True)[:5],
        'severity_distribution': {r.get('severity','نامشخص'): data.count(r) for r in data},
        'shifts': {r.get('shift_name','نامشخص'): data.count(r) for r in data},
        'outcomes': {r.get('outcome','نامشخص'): data.count(r) for r in data},
        'total_attendees': sum(r.get('attendees_count',0) for r in data),
        'avg_attendees': round(sum(r.get('attendees_count',0) for r in data)/total, 1) if total else 0,
        'has_action': sum(1 for r in data if r.get('action_taken')),
        'moving_average': dict(zip(sorted_days[-10:], moving_avg[-10:])),
        'outliers': outliers,
        'risk_scores': {k: {'rate': round(v['bad']/v['total']*100, 1)} for k, v in risk_scores.items() if v['total']}
    }


def internal_crisis_analysis(summary):
    lines = []
    lines.append(f"🔢 **تعداد کل رخدادها:** {summary['total_events']}")
    lines.append(f"⏱ **میانگین مدت بحران:** {summary['avg_duration']} دقیقه")
    lines.append(f"👥 **مجموع افراد حاضر:** {summary['total_attendees']} (میانگین {summary['avg_attendees']} نفر)")
    if summary['top_locations']:
        lines.append("📍 **پرتکرارترین مکان‌ها:**")
        for loc, cnt in summary['top_locations']:
            lines.append(f"   - {loc}: {cnt} رخداد")
    if summary['code_types']:
        lines.append("📋 **فراوانی انواع کدها:**")
        for k, v in sorted(summary['code_types'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"   - {k}: {v}")
    if summary['severity_distribution']:
        lines.append("📈 **توزیع شدت:**")
        for k, v in summary['severity_distribution'].items():
            lines.append(f"   - {k}: {v}")
    if summary['outcomes']:
        lines.append("🏁 **نتایج عملیات:**")
        for k, v in summary['outcomes'].items():
            lines.append(f"   - {k}: {v}")
    if summary['shifts']:
        lines.append("🕒 **توزیع در شیفت‌ها:**")
        for k, v in summary['shifts'].items():
            lines.append(f"   - {k}: {v}")
    if summary.get('moving_average'):
        lines.append(f"📈 **میانگین متحرک ۷ روزه (۱۰ روز اخیر):** {list(summary['moving_average'].values())}")
    if summary.get('outliers'):
        lines.append(f"⚠️ **نقاط پرت (انحراف > ۲):** {len(summary['outliers'])} روز")
        for o in summary['outliers'][:3]:
            lines.append(f"   - {o['date']}: {o['value']} بحران (Z-score: {o['z_score']})")
    if summary.get('risk_scores'):
        lines.append("🚨 **امتیاز ریسک به تفکیک نوع کد (درصد با شدت زیاد):**")
        for k, v in sorted(summary['risk_scores'].items(), key=lambda x: x[1]['rate'], reverse=True):
            emoji = '🔴' if v['rate'] > 30 else '🟠' if v['rate'] > 15 else '🟢'
            lines.append(f"   {emoji} {k}: {v['rate']}%")

    lines.append("💡 **پیشنهادات:**")
    if summary['avg_duration'] > 30:
        lines.append("- زمان پاسخ‌دهی بالا؛ نیاز به بازنگری فرآیند فراخوان.")
    if summary['total_events'] > 0 and summary['has_action'] < summary['total_events']:
        lines.append("- برخی رخدادها فاقد شرح اقدام هستند؛ مستندسازی را تقویت کنید.")
    lines.append("- مکان‌های پرتکرار بحران را برای استقرار منابع بیشتر بررسی کنید.")
    lines.append("- برگزاری مانور بر اساس کدهای شایع و با ریسک بالا پیشنهاد می‌شود.")
    return "\n".join(lines)


def deepseek_analysis(api_key, summary):
    if not api_key or len(api_key.strip()) < 10: return None
    prompt = f"""شما یک تحلیلگر مدیریت بحران بیمارستانی هستید. این داده‌های گزارش بحران را تحلیل کنید و پاسخ کاملاً فارسی دهید:

{json.dumps(summary, indent=2, ensure_ascii=False)}

تحلیل باید شامل: خلاصه وضعیت، الگوها، نقاط پرت، امتیاز ریسک و پیشنهادات اجرایی (حداقل ۳ مورد)."""
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [
                {"role": "system", "content": "شما یک کارشناس ارشد مدیریت بحران بیمارستان هستید."},
                {"role": "user", "content": prompt}
            ], "temperature": 0.7, "max_tokens": 1500},
            timeout=20)
        if resp.status_code == 200: return resp.json()['choices'][0]['message']['content']
    except: pass
    return None


def api_data(request_args):
    return _fetch_data(
        request_args.get('from',''), request_args.get('to',''),
        request_args.get('code',''), request_args.get('location',''),
        request_args.get('shift',''), request_args.get('severity',''),
        request_args.get('search',''),
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 15, type=int)
    )


def api_analyze(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('code',''), request_args.get('location',''),
                    request_args.get('shift',''), request_args.get('severity',''),
                    request_args.get('search',''), page=1, per_page=9999)
    data = d['data']
    if not data: return {'success': False, 'message': 'داده‌ای برای تحلیل وجود ندارد'}
    summary = _generate_ai_summary(data)
    deepseek_key = request_args.get('deepseek_key', '').strip()
    if deepseek_key:
        analysis = deepseek_analysis(deepseek_key, summary)
        if analysis: return {'success': True, 'analysis': analysis, 'source_name': 'DeepSeek AI'}
    analysis = internal_crisis_analysis(summary)
    return {'success': True, 'analysis': analysis, 'source_name': 'تحلیل داخلی'}


def api_export(request_args):
    import io; from openpyxl import Workbook; from flask import send_file
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('code',''), request_args.get('location',''), request_args.get('shift',''), request_args.get('severity',''), request_args.get('search',''), page=1, per_page=9999)
    wb = Workbook(); ws = wb.active; ws.title = "گزارش بحران"
    ws.append(['کد','تاریخ','نوع','محل','شیفت','شدت','شروع','پایان','مدت','اقدام','نتیجه','توضیحات','حاضرین','ثبت‌کننده'])
    for r in d['data']: ws.append([r.get('ID_kod_omomy'),r.get('date_display'),r.get('code_title'),r.get('location'),r.get('shift_name'),r.get('severity'),str(r.get('start_time',''))[:5],str(r.get('end_time',''))[:5],r.get('duration'),r.get('action_taken',''),r.get('outcome',''),r.get('description',''),r.get('attendees',''),r.get('registrar','')])
    ws2 = wb.create_sheet("آمار"); ws2.append(['شاخص','مقدار']); s = d['stats']
    for k,v in [('کل رخدادها',s['total']),('میانگین مدت',f"{s['avg_duration']} دقیقه"),('شدت زیاد',s['high_severity']),('مجموع حاضرین',s['total_attendees']),('مکان‌ها',s['unique_locations'])]: ws2.append([k,v])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='crisis_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def api_print(request_args):
    import jdatetime
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('code',''), request_args.get('location',''), request_args.get('shift',''), request_args.get('severity',''), request_args.get('search',''), page=1, per_page=9999)
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    groups = {}
    for r in d['data']:
        k = r.get('code_title','نامشخص')
        if k not in groups: groups[k] = []
        groups[k].append(r)
    html = f'''<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><style>
        body{{font-family:Tahoma;padding:20px;}}h1{{text-align:center;color:#ea580c;}}
        .cg{{margin:20px 0;border:1px solid #ddd;border-radius:10px;overflow:hidden;}}
        .ch{{background:#ea580c;color:white;padding:10px 15px;font-weight:bold;}}
        table{{width:100%;border-collapse:collapse;}}th{{background:#fdba74;color:#7b341e;padding:8px;font-size:11px;}}
        td{{padding:7px;border-bottom:1px solid #eee;text-align:center;font-size:11px;}}
        .hh{{background:#ef4444;color:white;padding:2px 6px;border-radius:3px;font-size:10px;}}
        .mm{{background:#f59e0b;color:white;padding:2px 6px;border-radius:3px;font-size:10px;}}
        .ll{{background:#10b981;color:white;padding:2px 6px;border-radius:3px;font-size:10px;}}
        .detail-row td {{background:#f9fafb; font-size:10px; color:#555; text-align:right;}}
        @media print{{body{{padding:0;}}}}
    </style></head><body><h1>🔥 گزارش بحران - {today_j}</h1>'''
    for code, items in groups.items():
        html += f'<div class="cg"><div class="ch">⚠️ {code} - {len(items)} مورد</div><table><tr><th>تاریخ</th><th>محل</th><th>شیفت</th><th>شدت</th><th>شروع</th><th>مدت</th><th>نتیجه</th><th>حاضرین</th></tr>'
        for r in items:
            sev = str(r.get('severity',''))
            sc = 'hh' if 'زیاد' in sev or sev=='3' else ('mm' if 'متوسط' in sev or sev=='2' else 'll')
            st = 'زیاد' if 'زیاد' in sev or sev=='3' else ('متوسط' if 'متوسط' in sev or sev=='2' else 'کم')
            html += f'<tr><td>{r.get("date_display")}</td><td>{r.get("location","-")}</td><td>{r.get("shift_name","-")}</td><td><span class="{sc}">{st}</span></td><td>{str(r.get("start_time",""))[:5]}</td><td>{r.get("duration",0)}</td><td>{r.get("outcome","-")}</td><td>{r.get("attendees_count",0)}</td></tr>'
            action = r.get('action_taken', '') or '---'
            desc = r.get('description', '') or '---'
            html += f'<tr class="detail-row"><td colspan="8"><strong>🛠️ اقدامات:</strong> {action} &nbsp;&nbsp;&nbsp; <strong>📝 توضیحات:</strong> {desc}</td></tr>'
        html += '</table></div>'
    html += '<script>window.print();</script></body></html>'
    return html
    
    
    
def get_crisis_detail(record_id):
    """دریافت جزئیات کامل یک رخداد بحران شامل اسناد و پرسنل"""
    try:
        # اصلاح: انتخاب فیلدها با aliasهای متناسب با جاوااسکریپت
        record = query("""
            SELECT 
                k.ID_kod_omomy,
                k.dat_sabt,
                k.nam_mahal AS location,          -- alias برای نمایش محل
                k.shedat_bohran AS severity,      -- alias برای شدت
                k.time_saat_dagig_shoro,
                k.time_sat_dagigeh_paian,
                k.eghdam AS action_taken,         -- alias برای اقدامات
                k.natijeh_amlit AS outcome,       -- alias برای نتیجه
                k.tavzih AS description,          -- alias برای توضیحات
                o.nam_kod_o AS code_title,
                s.tarkib AS shift_name,
                u.FullName AS registrar,
                k.mostanad
            FROM tbl_kod_omomy k
            LEFT JOIN tbl_onvan_kod_omomy o ON k.onvan_kod_omomy = o.ID_onvan_kod_o
            LEFT JOIN shift_namt s ON k.nam_shift = s.ID_shift
            LEFT JOIN users u ON k.UserID = u.UserID
            WHERE k.ID_kod_omomy = %s
        """, (record_id,), fetch_one=True)
        
        if not record:
            return {'success': False, 'message': 'رخداد یافت نشد'}
        
        # دریافت لیست پرسنل فراخوان شده (بدون تغییر)
        personnel = query("""
            SELECT kp.*, 
                   CONCAT(COALESCE(kp.nam_person, ''), ' ', COALESCE(kp.fam_person, '')) as full_name
            FROM tbl_kod_omomy_person kp
            WHERE kp.id_cod_omomi = %s
        """, (record_id,), fetch_all=True) or []
        
        # پردازش فایل‌های اسناد (بدون تغییر)
        files = []
        if record.get('mostanad'):
            files = record['mostanad'].split(',') if record['mostanad'] else []
            files = [f for f in files if f.strip()]
        
        # تبدیل تاریخ (بدون تغییر)
        if record.get('dat_sabt'):
            d = str(record['dat_sabt'])
            record['date_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d
        
        # تبدیل bytearray به string (بدون تغییر)
        for key in list(record.keys()):
            if isinstance(record[key], (bytearray, bytes)):
                record[key] = record[key].decode('utf-8', errors='ignore')
        
        return {
            'success': True,
            'record': record,
            'personnel': personnel,
            'files': files
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}
        