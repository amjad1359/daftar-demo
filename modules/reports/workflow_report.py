"""
گزارش گردش‌کار گزارشات – نسخهٔ ارتقاءیافته با نام تأییدکنندگان در خط سیر
نمودارهای تعاملی Chart.js، تحلیل هوشمند و لود سریع
"""

from models.database import query
import json
from utils.formatters import format_date_display
import math
from datetime import datetime

def get_workflow_report(user):
    """صفحه اصلی گردش‌کار گزارشات"""

    import jdatetime
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    month_ago = (jdatetime.date.today() - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")

    # المان‌های ثابت
    unit_list = query("SELECT DISTINCT nam_modiriat FROM tbl_nam_modiriat ORDER BY nam_modiriat", fetch_all=True) or []
    title_list = query("SELECT DISTINCT nam_onvan_gozaresh FROM tbl_onvan_gozaresh ORDER BY nam_onvan_gozaresh", fetch_all=True) or []
    shift_list = query("SELECT DISTINCT s.tarkib FROM shift_namt s ORDER BY s.tarkib", fetch_all=True) or []

    unit_opts = '<option value="">همه</option>' + ''.join(f'<option value="{u["nam_modiriat"]}">{u["nam_modiriat"]}</option>' for u in unit_list)
    title_opts = '<option value="">همه</option>' + ''.join(f'<option value="{t["nam_onvan_gozaresh"]}">{t["nam_onvan_gozaresh"]}</option>' for t in title_list)
    shift_opts = '<option value="">همه</option>' + ''.join(f'<option value="{s["tarkib"]}">{s["tarkib"]}</option>' for s in shift_list)

    # آمار اولیه خالی
    stats = {'total': 0, 'matron': 0, 'manager': 0, 'fanni': 0, 'raiss': 0}
    table_html = '<tr><td colspan="8" class="empty">در حال بارگذاری...</td></tr>'
    dash_html = '<div class="empty">در حال بارگذاری نمودارها...</div>'

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>گردش‌کار گزارشات</title>
<script src="/static/js/chart.umd.min.js"></script>
<style>
    :root {{ --primary: #1e3a8a; --green: #10b981; --red: #ef4444; --yellow: #f59e0b; --orange: #f97316; --blue: #3b82f6; --gray: #64748b; --l-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9; --white: #fff; --r: 12px; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial; direction:rtl; background:var(--bg); color:#1e293b; }}
    .container {{ max-width:1400px; margin:0 auto; padding:16px; }}
    
    .header {{ background:linear-gradient(135deg,#1e3a8a,#3b82f6); color:white; border-radius:var(--r); padding:18px 24px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 6px 20px rgba(30,58,138,.25); }}
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

    .btn {{ padding:7px 15px; border:none; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; font-family:inherit; white-space:nowrap; }}
    .btn-blue {{ background:var(--primary); color:white; }}
    .btn-grn {{ background:var(--green); color:white; }}
    .btn-xs {{ padding:5px 10px; font-size:10px; }}

    .tabs {{ display:flex; gap:4px; margin-bottom:12px; border-bottom:2px solid var(--border); }}
    .tab {{ padding:8px 16px; font-size:12px; font-weight:600; border:none; background:none; color:var(--l-gray); cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-2px; font-family:inherit; }}
    .tab.on {{ color:var(--primary); border-bottom-color:var(--primary); }}
    .pan {{ display:none; }}
    .pan.on {{ display:block; }}

    .tbl-wrap {{ background:white; border-radius:var(--r); border:1px solid var(--border); overflow:hidden; }}
    .tbl-scroll {{ overflow:auto; max-height:500px; }}
    table {{ width:100%; border-collapse:collapse; font-size:11px; }}
    th {{ background:var(--primary); color:white; padding:9px 5px; text-align:center; font-weight:600; position:sticky; top:0; z-index:5; }}
    td {{ padding:7px 5px; text-align:center; border-bottom:1px solid var(--border); }}
    tr:hover td {{ background:#f8fafc; cursor:pointer; }}

    .progress-bar {{ height:6px; background:#e5e7eb; border-radius:3px; overflow:hidden; }}
    .progress-fill {{ height:100%; border-radius:3px; }}
    .badge {{ padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; display:inline-block; color:white; }}

    .charts {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
    .chart-box {{ background:white; border-radius:10px; padding:14px; border:1px solid var(--border); }}
    .chart-box h4 {{ margin-bottom:10px; font-size:13px; text-align:center; }}
    canvas {{ max-height:250px; }}

    .detail-modal {{ display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:500; justify-content:center; align-items:center; }}
    .detail-modal.show {{ display:flex; }}
    .modal-content {{ background:white; border-radius:14px; padding:25px; width:90%; max-width:700px; max-height:85vh; overflow-y:auto; animation:fadeIn 0.3s ease; }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(20px); }} to {{ opacity:1; transform:translateY(0); }} }}

    .timeline {{ display:flex; gap:0; margin:15px 0; }}
    .timeline-step {{ flex:1; text-align:center; position:relative; padding:10px; }}
    .timeline-step::before {{ content:''; position:absolute; top:20px; left:0; right:0; height:3px; background:#e5e7eb; z-index:0; }}
    .timeline-step:first-child::before {{ left:50%; }}
    .timeline-step:last-child::before {{ right:50%; }}
    .timeline-dot {{ width:40px; height:40px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:18px; position:relative; z-index:1; }}
    .timeline-dot.done {{ background:#d1fae5; color:#065f46; }}
    .timeline-dot.pending {{ background:#fef3c7; color:#92400e; }}

    .pagination {{ display:flex; justify-content:center; gap:10px; margin-top:15px; }}
    .file-link {{ display:inline-block; margin:3px 5px; font-size:11px; }}
    .files-box {{ background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:12px; margin:10px 0; }}

    .bar {{ display:flex; gap:8px; justify-content:flex-end; margin-top:10px; }}
    .empty {{ text-align:center; padding:30px; color:var(--l-gray); }}

    .spinner {{
        width: 40px; height: 40px;
        border: 4px solid #e2e8f0;
        border-top-color: #1e3a8a;
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

    @media (max-width:768px) {{ .kpi {{ grid-template-columns:repeat(2,1fr); }} .charts {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h2>📋 کارتابل جامع پیگیری گزارشات</h2>
        <a href="/module/reports">⬅️ بازگشت</a>
    </div>

    <div class="kpi">
        <div class="kpi-card"><div class="kpi-val" style="color:#1e3a8a;" id="k-total">{stats['total']}</div><div class="kpi-lbl">📋 کل گزارشات</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#10b981;" id="k-matron">{stats['matron']}</div><div class="kpi-lbl">✅ آماده شروع فرایند</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#3b82f6;" id="k-manager">{stats['manager']}</div><div class="kpi-lbl">📝 پاسخ مدیر</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#f59e0b;" id="k-fanni">{stats['fanni']}</div><div class="kpi-lbl">🔧 نظر فنی</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#ef4444;" id="k-raiss">{stats['raiss']}</div><div class="kpi-lbl">👤 تایید ریاست</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ</label><input type="text" id="f-from" value="{month_ago}"></div>
            <div class="f-grp"><label>تا تاریخ</label><input type="text" id="f-to" value="{today_j}"></div>
            <div class="f-grp"><label>شیفت</label><select id="f-shift">{shift_opts}</select></div>
            <div class="f-grp"><label>واحد مدیریت</label><select id="f-unit">{unit_opts}</select></div>
            <div class="f-grp"><label>عنوان واقعه</label><select id="f-title">{title_opts}</select></div>
        </div>
        <div class="f-row">
            <div class="f-grp"><label>وضعیت</label><select id="f-status"><option value="">همه</option><option value="new">🔴 جدید</option><option value="matron">🟠 ارسال مترون</option><option value="manager">🟡 پاسخ مدیر</option><option value="review">🟢 در حال بررسی</option><option value="done">✅ تکمیل شده</option></select></div>
            <div class="f-grp" style="flex:2;"><label>جستجو</label><input type="text" id="f-search" placeholder="کلمه کلیدی..."></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-blue" onclick="refresh(1)">🔍 اعمال فیلتر</button></div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab on" onclick="switchTab('dash')">📊 داشبورد</button>
        <button class="tab" onclick="switchTab('list')">📋 لیست گزارشات</button>
        <button class="tab" onclick="switchTab('ai')">🤖 تحلیل هوشمند</button>
    </div>

    <div id="pan-dash" class="pan on">{dash_html}</div>

    <div id="pan-list" class="pan">
        <div class="tbl-wrap"><div class="tbl-scroll"><table>
            <thead><tr><th>کد</th><th>تاریخ</th><th>شیفت</th><th>واحد</th><th>عنوان</th><th>ثبت‌کننده</th><th>پیشرفت</th><th>وضعیت</th></tr></thead>
            <tbody id="tbl-body">{table_html}</tbody>
        </table></div></div>
        <div id="pagination" class="pagination"></div>
        <div class="bar">
            <button class="btn btn-grn btn-xs" onclick="doExport()">📥 Excel</button>
        </div>
    </div>

    <div id="pan-ai" class="pan">
        <div class="card">
            <div class="card-title">🤖 تحلیل هوشمند گردش‌کار</div>
            <div class="row" style="margin-bottom:15px;">
                <div class="form-group" style="flex:2;">
                    <label>🔑 کلید API دیپ‌سیک (اختیاری)</label>
                    <input type="text" id="deepseek-key" class="form-input" placeholder="sk-...">
                </div>
                <div class="form-group" style="flex:0 0 auto; align-self: flex-end;">
                    <button class="btn btn-blue" onclick="startAIAnalysis()">🔍 شروع تحلیل</button>
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

<!-- مودال جزئیات -->
<div class="detail-modal" id="detail-modal">
    <div class="modal-content" id="detail-content"></div>
</div>

<script>
    let allData = [];
    let currentPage = 1;
    let totalPages = 1;

    function switchTab(t) {{
        document.querySelectorAll('.tab').forEach((x,i) => {{ x.classList.toggle('on', (t==='dash'&&i===0)||(t==='list'&&i===1)||(t==='ai'&&i===2)); }});
        document.querySelectorAll('.pan').forEach(p => p.classList.remove('on'));
        document.getElementById('pan-'+t).classList.add('on');
        if (t === 'dash') renderCharts(allData);
    }}

    async function refresh(page = 1) {{
        const p = new URLSearchParams({{
            from: (document.getElementById('f-from').value||'').replace(/\//g,''),
            to: (document.getElementById('f-to').value||'').replace(/\//g,''),
            shift: document.getElementById('f-shift').value,
            unit: document.getElementById('f-unit').value,
            title: document.getElementById('f-title').value,
            status: document.getElementById('f-status').value,
            search: document.getElementById('f-search').value,
            page: page,
            per_page: 15
        }});
        const r = await fetch('/module/reports/workflow/data?'+p.toString());
        const d = await r.json();
        allData = d.data || [];
        const s = d.stats || {{}};

        document.getElementById('k-total').textContent = s.total||0;
        document.getElementById('k-matron').textContent = s.matron||0;
        document.getElementById('k-manager').textContent = s.manager||0;
        document.getElementById('k-fanni').textContent = s.fanni||0;
        document.getElementById('k-raiss').textContent = s.raiss||0;

        document.getElementById('tbl-body').innerHTML = allData.length ? allData.map(r => {{
            const pct = r.progress||0;
            const colors = ['#ef4444','#f97316','#f59e0b','#3b82f6','#10b981'];
            const ci = pct>=100?4:pct>=75?3:pct>=50?2:pct>=25?1:0;
            const statusLabels = ['🔴 جدید','🟠 ارسال مترون','🟡 پاسخ مدیر','🟢 در حال بررسی','✅ تکمیل شده'];
            const si = pct>=100?4:pct>=75?3:pct>=50?2:pct>=25?1:0;
            return `<tr onclick="showDetail(${{r.ID_gozaresh}})" style="cursor:pointer;">
                <td>${{r.ID_gozaresh}}</td><td>${{r.date_display||''}}</td><td>${{r.shift_name||''}}</td>
                <td>${{r.unit_name||''}}</td><td>${{r.title_name||''}}</td><td>${{r.registrar||''}}</td>
                <td><div class="progress-bar"><div class="progress-fill" style="width:${{pct}}%;background:${{colors[ci]}}"></div></div><small>${{pct}}%</small></td>
                <td><span class="badge" style="background:${{colors[si]}}">${{statusLabels[si]}}</span></td></tr>`;
        }}).join('') : '<tr><td colspan="8" class="empty">داده‌ای یافت نشد</td></tr>';

        if (d.available_shifts) {{
            populateShiftDropdown(d.available_shifts);
        }}

        currentPage = d.page || 1;
        totalPages = Math.ceil((d.total || 0) / 15);
        renderPagination();
        renderCharts(allData);
    }}

    function populateShiftDropdown(shifts) {{
        const sel = document.getElementById('f-shift');
        const currentVal = sel.value;
        sel.innerHTML = '<option value="">همه</option>';
        shifts.forEach(s => sel.innerHTML += `<option value="${{s}}">${{s}}</option>`);
        if (shifts.includes(currentVal)) sel.value = currentVal; else sel.value = '';
    }}

    function renderPagination() {{
        const container = document.getElementById('pagination');
        if (totalPages <= 1) {{ container.innerHTML = ''; return; }}
        let html = '';
        if (currentPage > 1) html += `<button class="btn btn-blue btn-xs" onclick="refresh(${{currentPage-1}})">« قبلی</button>`;
        html += `<span style="display:flex;align-items:center;font-size:13px;">صفحه ${{currentPage}} از ${{totalPages}}</span>`;
        if (currentPage < totalPages) html += `<button class="btn btn-blue btn-xs" onclick="refresh(${{currentPage+1}})">بعدی »</button>`;
        container.innerHTML = html;
    }}

    // ==================== نمودارهای Chart.js ====================
    function renderCharts(data) {{
        setTimeout(() => {{
            ['chart-status','chart-progress','chart-trend','chart-bottleneck'].forEach(id => {{
                const existing = Chart.getChart(id);
                if (existing) existing.destroy();
            }});

            if (!data.length) {{
                document.getElementById('pan-dash').innerHTML = '<div class="empty">داده‌ای نیست</div>';
                return;
            }}

            document.getElementById('pan-dash').innerHTML = `
                <div class="charts">
                    <div class="chart-box"><h4>🥧 توزیع وضعیت گزارشات</h4><canvas id="chart-status"></canvas></div>
                    <div class="chart-box"><h4>📊 توزیع درصد پیشرفت</h4><canvas id="chart-progress"></canvas></div>
                    <div class="chart-box"><h4>📈 روند ثبت گزارشات (۳۰ روز)</h4><canvas id="chart-trend"></canvas></div>
                    <div class="chart-box"><h4>🚨 گلوگاه‌ها (بیشترین توقف)</h4><canvas id="chart-bottleneck"></canvas></div>
                </div>
            `;

            const colors = ['#10b981','#3b82f6','#f59e0b','#f97316','#ef4444'];

            // وضعیت‌ها (pie)
            const sm={{}};
            data.forEach(r => {{
                const p = r.progress||0;
                const k = p>=100?'✅ تکمیل':p>=75?'🟢 بررسی':p>=50?'🟡 مدیر':p>=25?'🟠 مترون':'🔴 جدید';
                sm[k]=(sm[k]||0)+1;
            }});
            new Chart(document.getElementById('chart-status'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(sm),
                    datasets: [{{ data: Object.values(sm), backgroundColor: colors.slice(0, Object.keys(sm).length) }}]
                }}
            }});

            // توزیع پیشرفت (bar)
            const ranges = {{'0-25%':0,'26-50%':0,'51-75%':0,'76-100%':0}};
            data.forEach(r => {{
                const p = r.progress||0;
                if(p<=25) ranges['0-25%']++;
                else if(p<=50) ranges['26-50%']++;
                else if(p<=75) ranges['51-75%']++;
                else ranges['76-100%']++;
            }});
            new Chart(document.getElementById('chart-progress'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(ranges),
                    datasets: [{{ data: Object.values(ranges), backgroundColor: '#6366f1' }}]
                }},
                options: {{ responsive: true }}
            }});

            // روند روزانه (line)
            const daily={{}};
            data.forEach(r => {{ const d=r.date_display||''; daily[d]=(daily[d]||0)+1; }});
            const sortedDays = Object.entries(daily).sort((a,b) => a[0].localeCompare(b[0])).slice(-30);
            new Chart(document.getElementById('chart-trend'), {{
                type: 'line',
                data: {{
                    labels: sortedDays.map(([k]) => k.substring(5)),
                    datasets: [{{ label: 'تعداد گزارش', data: sortedDays.map(([,v]) => v), borderColor: '#1e3a8a', tension: 0.3 }}]
                }},
                options: {{ responsive: true }}
            }});

            // گلوگاه‌ها (bar)
            const bottleneck={{'مترون':0,'مدیر':0,'فنی':0,'ریاست':0}};
            data.forEach(r => {{
                if(r.matron_id && !r.manager_title) bottleneck['مدیر']++;
                else if(r.manager_title && !r.fanni_opinion) bottleneck['فنی']++;
                else if(r.fanni_opinion && !r.raiss_order) bottleneck['ریاست']++;
                else if(!r.matron_id) bottleneck['مترون']++;
            }});
            new Chart(document.getElementById('chart-bottleneck'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(bottleneck),
                    datasets: [{{ data: Object.values(bottleneck), backgroundColor: ['#ef4444','#f59e0b','#3b82f6','#10b981'] }}]
                }},
                options: {{ responsive: true }}
            }});
        }}, 50);
    }}

    // ==================== مودال جزئیات (با نام تأییدکنندگان) ====================
    async function showDetail(id) {{
        const r = await fetch('/module/reports/workflow/detail/'+id);
        const d = await r.json();
        if (!d.record) return;
        const rec = d.record;
        const pct = rec.progress||0;

        let html = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
            <h3>📋 گزارش کد ${{rec.ID_gozaresh}}</h3>
            <button class="btn btn-xs" onclick="closeDetail()" style="background:#e5e7eb;color:#333;">✕ بستن</button></div>`;

        html += `<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:15px;background:#f8fafc;padding:12px;border-radius:8px;">
            <div><strong>تاریخ:</strong> ${{rec.date_display}}</div><div><strong>شیفت:</strong> ${{rec.shift_name||'-'}}</div>
            <div><strong>واحد:</strong> ${{rec.unit_name||'-'}}</div><div><strong>ثبت‌کننده:</strong> ${{rec.registrar||'-'}}</div>
            <div><strong>عنوان:</strong> ${{rec.title_name||'-'}}</div><div><strong>وضعیت:</strong> ${{pct}}%</div></div>`;

        html += `<div style="margin-bottom:10px;"><strong>📝 شرح واقعه:</strong><div style="background:#f8fafc;padding:10px;border-radius:6px;margin-top:5px;">${{rec.mohtava_gozaresh||'---'}}</div></div>`;
        if (rec.eghdam_eslahi_avlieh) html += `<div style="margin-bottom:10px;"><strong>🔧 اقدام اصلاحی:</strong><div style="background:#fff7ed;padding:10px;border-radius:6px;margin-top:5px;">${{rec.eghdam_eslahi_avlieh}}</div></div>`;

        if (rec.mostanad) {{
            const files = rec.mostanad.split(',').filter(f => f.trim());
            if (files.length > 0) {{
                html += '<div class="files-box"><strong>📎 اسناد پیوست:</strong><div style="margin-top:8px;">';
                files.forEach(f => {{
                    const name = f.split('/').pop();
                    html += `<a href="/${{f}}" target="_blank" class="file-link">📄 ${{name}}</a>`;
                }});
                html += '</div></div>';
            }}
        }}

        html += `<div style="margin:20px 0;"><strong>⏱️ روند بررسی:</strong></div><div class="timeline">`;
        const steps = [
            {{label:'مترون', done:!!rec.matron_id, date:rec.matron_date, user:rec.matron_user_name}},
            {{label:'مدیر واحد', done:!!rec.manager_title, date:rec.manager_date, user:rec.manager_user_name}},
            {{label:'مسئول فنی', done:!!rec.fanni_opinion, date:rec.fanni_date, user:rec.fanni_user_name}},
            {{label:'ریاست', done:!!rec.raiss_order, date:rec.raiss_date, user:rec.raiss_user_name}}
        ];
        steps.forEach(s => {{
            html += `<div class="timeline-step"><div class="timeline-dot ${{s.done?'done':'pending'}}">${{s.done?'✅':'⏳'}}</div><div style="font-size:10px;margin-top:5px;">${{s.label}}</div>`;
            if (s.user) html += `<div style="font-size:9px;color:var(--gray);">${{s.user}}</div>`;
            html += `<div style="font-size:9px;color:var(--gray);">${{s.date||'-'}}</div></div>`;
        }});
        html += '</div>';

        if (rec.manager_response) html += `<div style="margin:10px 0;background:#f0f7ff;padding:10px;border-radius:6px;"><strong>💬 پاسخ مدیر:</strong> ${{rec.manager_title||''}}<br>${{rec.manager_response}}</div>`;
        if (rec.fanni_opinion) html += `<div style="margin:10px 0;background:#f0fdf4;padding:10px;border-radius:6px;"><strong>🔧 نظر فنی:</strong><br>${{rec.fanni_opinion}}</div>`;
        if (rec.raiss_order) html += `<div style="margin:10px 0;background:#fef3c7;padding:10px;border-radius:6px;"><strong>👤 دستور ریاست:</strong><br>${{rec.raiss_order}}</div>`;

        document.getElementById('detail-content').innerHTML = html;
        document.getElementById('detail-modal').classList.add('show');
    }}

    function closeDetail() {{ document.getElementById('detail-modal').classList.remove('show'); }}
    document.getElementById('detail-modal').addEventListener('click', function(e) {{ if(e.target===this)closeDetail(); }});

    // ==================== تحلیل هوشمند ====================
    async function startAIAnalysis() {{
        const loading = document.getElementById('ai-loading');
        const result = document.getElementById('ai-result');
        loading.style.display = 'block';
        result.style.display = 'none';
        const deepseekKey = document.getElementById('deepseek-key').value.trim();
        const params = new URLSearchParams({{
            from: (document.getElementById('f-from').value||'').replace(/\\//g,''),
            to: (document.getElementById('f-to').value||'').replace(/\\//g,''),
            shift: document.getElementById('f-shift').value,
            unit: document.getElementById('f-unit').value,
            title: document.getElementById('f-title').value,
            status: document.getElementById('f-status').value,
            search: document.getElementById('f-search').value,
            deepseek_key: deepseekKey
        }});
        try {{
            const res = await fetch('/module/reports/workflow/analyze?' + params.toString());
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
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value,unit:document.getElementById('f-unit').value,title:document.getElementById('f-title').value,status:document.getElementById('f-status').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/workflow/export?'+p.toString(),'_blank');
    }}

    document.addEventListener('DOMContentLoaded', () => refresh(1));
</script>
</body>
</html>'''
    return html


def _fetch_data(d_from='', d_to='', shift='', unit='', title='', status='', search='', page=1, per_page=15):
    """واکشی داده با صفحه‌بندی و برگرداندن شیفت‌های موجود در بازه"""
    offset = (page - 1) * per_page

    sql = """SELECT g.ID_gozaresh, g.dat_sabt, g.mohtava_gozaresh, g.eghdam_eslahi_avlieh,
             s.tarkib AS shift_name, m.nam_modiriat AS unit_name, o.nam_onvan_gozaresh AS title_name,
             u.FullName AS registrar,
             mp.ID_gozaresh_modir_parstati AS matron_id, mp.dat_sabt AS matron_date,
             pj.pasokh_onvan AS manager_title, pj.javab_sharh_kamel AS manager_response, pj.dat_sabt AS manager_date,
             nf.nazar_msol_fanni AS fanni_opinion, nf.dat_sabt AS fanni_date,
             nr.nazar_raiss AS raiss_order, nr.dat_sabt AS raiss_date
             FROM tbl_gozaresh g
             LEFT JOIN shift_namt s ON g.ID_shift=s.ID_shift
             LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit=m.ID_nam_modirit
             LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh=o.ID_onvan_gozaresh
             LEFT JOIN users u ON g.UserID=u.UserID
             LEFT JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh=mp.ID_gozaresh
             LEFT JOIN tbl_pasokh_modir_javab pj ON g.ID_gozaresh=pj.kod_gozaresh
             LEFT JOIN tbl_nazar_fanni nf ON g.ID_gozaresh=nf.kod_gozaresh
             LEFT JOIN tbl_nazar_raiis nr ON g.ID_gozaresh=nr.kod_gozaresh
             WHERE mp.taid_ersal=1"""
    params = []

    count_sql = """SELECT COUNT(*) as total FROM tbl_gozaresh g
             LEFT JOIN shift_namt s ON g.ID_shift=s.ID_shift
             LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit=m.ID_nam_modirit
             LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh=o.ID_onvan_gozaresh
             LEFT JOIN users u ON g.UserID=u.UserID
             LEFT JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh=mp.ID_gozaresh
             LEFT JOIN tbl_pasokh_modir_javab pj ON g.ID_gozaresh=pj.kod_gozaresh
             LEFT JOIN tbl_nazar_fanni nf ON g.ID_gozaresh=nf.kod_gozaresh
             LEFT JOIN tbl_nazar_raiis nr ON g.ID_gozaresh=nr.kod_gozaresh
             WHERE mp.taid_ersal=1"""
    count_params = []

    shifts_sql = """SELECT DISTINCT s.tarkib FROM tbl_gozaresh g
                    JOIN shift_namt s ON g.ID_shift = s.ID_shift
                    LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit = m.ID_nam_modirit
                    LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh = o.ID_onvan_gozaresh
                    LEFT JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh = mp.ID_gozaresh
                    WHERE mp.taid_ersal = 1"""
    shifts_params = []

    if d_from:
        sql += " AND g.dat_sabt >= %s"; params.append(d_from)
        count_sql += " AND g.dat_sabt >= %s"; count_params.append(d_from)
        shifts_sql += " AND g.dat_sabt >= %s"; shifts_params.append(d_from)
    if d_to:
        sql += " AND g.dat_sabt <= %s"; params.append(d_to)
        count_sql += " AND g.dat_sabt <= %s"; count_params.append(d_to)
        shifts_sql += " AND g.dat_sabt <= %s"; shifts_params.append(d_to)
    if unit:
        sql += " AND m.nam_modiriat = %s"; params.append(unit)
        count_sql += " AND m.nam_modiriat = %s"; count_params.append(unit)
        shifts_sql += " AND m.nam_modiriat = %s"; shifts_params.append(unit)
    if title:
        sql += " AND o.nam_onvan_gozaresh = %s"; params.append(title)
        count_sql += " AND o.nam_onvan_gozaresh = %s"; count_params.append(title)
        shifts_sql += " AND o.nam_onvan_gozaresh = %s"; shifts_params.append(title)
    if search:
        sql += " AND (g.mohtava_gozaresh LIKE %s OR g.eghdam_eslahi_avlieh LIKE %s OR o.nam_onvan_gozaresh LIKE %s)"
        params.extend([f'%{search}%']*3)
        count_sql += " AND (g.mohtava_gozaresh LIKE %s OR g.eghdam_eslahi_avlieh LIKE %s OR o.nam_onvan_gozaresh LIKE %s)"
        count_params.extend([f'%{search}%']*3)
        shifts_sql += " AND (g.mohtava_gozaresh LIKE %s OR g.eghdam_eslahi_avlieh LIKE %s OR o.nam_onvan_gozaresh LIKE %s)"
        shifts_params.extend([f'%{search}%']*3)

    if shift:
        sql += " AND s.tarkib = %s"; params.append(shift)
        count_sql += " AND s.tarkib = %s"; count_params.append(shift)

    shifts_sql += " ORDER BY s.tarkib"
    available_shifts = [row['tarkib'] for row in (query(shifts_sql, shifts_params, fetch_all=True) or [])]

    sql += " ORDER BY g.ID_gozaresh DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    data = query(sql, params, fetch_all=True) or []

    for row in data:
        row['date_display'] = format_date_display(row.get('dat_sabt'))
        for f in ['matron_date','manager_date','fanni_date','raiss_date']:
            row[f] = format_date_display(row.get(f))
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.strftime('%Y-%m-%d %H:%M:%S')

        progress = 0
        if row.get('matron_id'): progress += 25
        if row.get('manager_title'): progress += 25
        if row.get('fanni_opinion'): progress += 25
        if row.get('raiss_order'): progress += 25
        row['progress'] = progress

    if status == 'new': data = [r for r in data if r['progress'] < 25]
    elif status == 'matron': data = [r for r in data if 25 <= r['progress'] < 50]
    elif status == 'manager': data = [r for r in data if 50 <= r['progress'] < 75]
    elif status == 'review': data = [r for r in data if 75 <= r['progress'] < 100]
    elif status == 'done': data = [r for r in data if r['progress'] >= 100]

    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0

    stats = {
        'total': total,
        'matron': sum(1 for r in data if r.get('matron_id')),
        'manager': sum(1 for r in data if r.get('manager_title')),
        'fanni': sum(1 for r in data if r.get('fanni_opinion')),
        'raiss': sum(1 for r in data if r.get('raiss_order')),
    }

    return {
        'data': data,
        'stats': stats,
        'total': total,
        'page': page,
        'per_page': per_page,
        'available_shifts': available_shifts
    }


def _build_table(data):
    if not data: return '<tr><td colspan="8" class="empty">داده‌ای یافت نشد</td></tr>'
    rows = []
    colors = ['#ef4444','#f97316','#f59e0b','#3b82f6','#10b981']
    statusLabels = ['🔴 جدید','🟠 ارسال مترون','🟡 پاسخ مدیر','🟢 در حال بررسی','✅ تکمیل شده']
    for r in data:
        pct = r.get('progress', 0)
        ci = 4 if pct >= 100 else (3 if pct >= 75 else (2 if pct >= 50 else (1 if pct >= 25 else 0)))
        si = ci
        rows.append(f'''<tr onclick="showDetail({r.get('ID_gozaresh')})" style="cursor:pointer;">
            <td>{r.get('ID_gozaresh')}</td><td>{r.get('date_display','')}</td><td>{r.get('shift_name','')}</td>
            <td>{r.get('unit_name','')}</td><td>{r.get('title_name','')}</td><td>{r.get('registrar','')}</td>
            <td><div class="progress-bar"><div class="progress-fill" style="width:{pct}%;background:{colors[ci]}"></div></div><small>{pct}%</small></td>
            <td><span class="badge" style="background:{colors[si]}">{statusLabels[si]}</span></td></tr>''')
    return ''.join(rows)


def _build_dashboard(data):
    return '<div class="empty">در حال بارگذاری نمودارها...</div>'


def api_data(request_args):
    return _fetch_data(
        request_args.get('from',''), request_args.get('to',''),
        request_args.get('shift',''), request_args.get('unit',''),
        request_args.get('title',''), request_args.get('status',''),
        request_args.get('search',''),
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 15, type=int)
    )


def api_detail(report_id):
    sql = """SELECT g.*, s.tarkib AS shift_name, m.nam_modiriat AS unit_name, o.nam_onvan_gozaresh AS title_name,
             u.FullName AS registrar,
             mp.ID_gozaresh_modir_parstati AS matron_id, mp.dat_sabt AS matron_date,
             mu.FullName AS matron_user_name,
             pj.pasokh_onvan AS manager_title, pj.javab_sharh_kamel AS manager_response, pj.dat_sabt AS manager_date,
             pu.FullName AS manager_user_name,
             nf.nazar_msol_fanni AS fanni_opinion, nf.dat_sabt AS fanni_date,
             fu.FullName AS fanni_user_name,
             nr.nazar_raiss AS raiss_order, nr.dat_sabt AS raiss_date,
             ru.FullName AS raiss_user_name
             FROM tbl_gozaresh g
             LEFT JOIN shift_namt s ON g.ID_shift=s.ID_shift
             LEFT JOIN tbl_nam_modiriat m ON g.nam_modirit=m.ID_nam_modirit
             LEFT JOIN tbl_onvan_gozaresh o ON g.onvan_gozaresh=o.ID_onvan_gozaresh
             LEFT JOIN users u ON g.UserID=u.UserID
             LEFT JOIN tbl_gozaresh_modir_parastari mp ON g.ID_gozaresh=mp.ID_gozaresh
             LEFT JOIN users mu ON mp.UserID = mu.UserID
             LEFT JOIN tbl_pasokh_modir_javab pj ON g.ID_gozaresh=pj.kod_gozaresh
             LEFT JOIN users pu ON pj.UserID = pu.UserID
             LEFT JOIN tbl_nazar_fanni nf ON g.ID_gozaresh=nf.kod_gozaresh
             LEFT JOIN users fu ON nf.UserID = fu.UserID
             LEFT JOIN tbl_nazar_raiis nr ON g.ID_gozaresh=nr.kod_gozaresh
             LEFT JOIN users ru ON nr.UserID = ru.UserID
             WHERE g.ID_gozaresh=%s"""
    rec = query(sql, (report_id,), fetch_one=True)
    if rec:
        d = str(rec.get('dat_sabt', ''))
        rec['date_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d
        for f in ['matron_date','manager_date','fanni_date','raiss_date']:
            dv = str(rec.get(f, ''))
            rec[f] = f"{dv[:4]}/{dv[4:6]}/{dv[6:]}" if len(dv) == 8 else ''
        progress = 0
        if rec.get('matron_id'): progress += 25
        if rec.get('manager_title'): progress += 25
        if rec.get('fanni_opinion'): progress += 25
        if rec.get('raiss_order'): progress += 25
        rec['progress'] = progress

        for key in list(rec.keys()):
            if isinstance(rec[key], bytearray):
                rec[key] = rec[key].decode('utf-8')
            if isinstance(rec[key], datetime):
                rec[key] = rec[key].strftime('%Y-%m-%d %H:%M:%S')

        return {'record': rec}
    return {'record': None}


def api_export(request_args):
    import io; from openpyxl import Workbook; from flask import send_file
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('shift',''), request_args.get('unit',''), request_args.get('title',''), request_args.get('status',''), request_args.get('search',''), page=1, per_page=9999)
    wb = Workbook(); ws = wb.active; ws.title = "گردش‌کار"
    ws.append(['کد','تاریخ','شیفت','واحد','عنوان','ثبت‌کننده','پیشرفت','مترون','مدیر','فنی','ریاست'])
    for r in d['data']:
        ws.append([r.get('ID_gozaresh'),r.get('date_display'),r.get('shift_name'),r.get('unit_name'),r.get('title_name'),r.get('registrar'),f"{r.get('progress',0)}%",'✅' if r.get('matron_id') else '❌','✅' if r.get('manager_title') else '❌','✅' if r.get('fanni_opinion') else '❌','✅' if r.get('raiss_order') else '❌'])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='workflow_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def _generate_ai_summary(data):
    if not data: return {}
    total = len(data)
    completed = sum(1 for r in data if r.get('progress', 0) >= 100)
    avg_progress = round(sum(r.get('progress', 0) for r in data) / total, 1) if total else 0

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

    bottlenecks = {'مترون':0,'مدیر':0,'فنی':0,'ریاست':0}
    for r in data:
        if r.get('matron_id') and not r.get('manager_title'): bottlenecks['مدیر'] += 1
        elif r.get('manager_title') and not r.get('fanni_opinion'): bottlenecks['فنی'] += 1
        elif r.get('fanni_opinion') and not r.get('raiss_order'): bottlenecks['ریاست'] += 1
        elif not r.get('matron_id'): bottlenecks['مترون'] += 1

    return {
        'total_reports': total,
        'completed': completed,
        'completion_rate': round(completed/total*100, 1) if total else 0,
        'avg_progress': avg_progress,
        'bottlenecks': bottlenecks,
        'moving_average': dict(zip(sorted_days[-10:], moving_avg[-10:])),
        'outliers': outliers
    }


def internal_workflow_analysis(summary):
    lines = []
    lines.append(f"📋 **تعداد کل گزارشات:** {summary['total_reports']}")
    lines.append(f"✅ **تکمیل شده:** {summary['completed']} ({summary['completion_rate']}%)")
    lines.append(f"📊 **میانگین پیشرفت:** {summary['avg_progress']}%")
    if summary.get('bottlenecks'):
        lines.append("🚨 **گلوگاه‌های فرایند:**")
        for k, v in summary['bottlenecks'].items():
            lines.append(f"   - {k}: {v} گزارش در انتظار")
    if summary.get('moving_average'):
        lines.append(f"📈 **میانگین متحرک ۷ روزه (۱۰ روز اخیر):** {list(summary['moving_average'].values())}")
    if summary.get('outliers'):
        lines.append(f"⚠️ **نقاط پرت (انحراف > ۲):** {len(summary['outliers'])} روز")
        for o in summary['outliers'][:3]:
            lines.append(f"   - {o['date']}: {o['value']} گزارش (Z-score: {o['z_score']})")
    lines.append("💡 **پیشنهادات:**")
    if summary['completion_rate'] < 60:
        lines.append("- نرخ تکمیل پایین است؛ بازنگری در زمانبندی مراحل.")
    max_bottleneck = max(summary.get('bottlenecks', {}).items(), key=lambda x: x[1], default=(None, 0))
    if max_bottleneck[1] > 0:
        lines.append(f"- گلوگاه اصلی «{max_bottleneck[0]}» است؛ تخصیص منابع بیشتر.")
    return "\n".join(lines)


def api_analyze(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('shift',''), request_args.get('unit',''),
                    request_args.get('title',''), request_args.get('status',''),
                    request_args.get('search',''),
                    page=1, per_page=9999)
    data = d['data']
    if not data:
        return {'success': False, 'message': 'داده‌ای برای تحلیل وجود ندارد'}
    summary = _generate_ai_summary(data)
    analysis = internal_workflow_analysis(summary)
    return {'success': True, 'analysis': analysis, 'source_name': 'تحلیل داخلی'}
    
    