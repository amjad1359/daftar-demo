"""
گزارش کدهای عملیاتی بیمارمحور – نسخهٔ ارتقاء‌یافته
نمودارهای تعاملی Chart.js، تحلیل عمیق آماری، لود سریع
"""

from models.database import query
import json
import requests
from datetime import datetime as dt
from utils.formatters import format_date_display
import math

def get_codes_report(user):
    """صفحه اصلی گزارش کدها"""

    import jdatetime
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    month_ago = (jdatetime.date.today() - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")

    # لود فیلترهای ثابت (سریع)
    bakhsh_list = query("SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh", fetch_all=True) or []
    code_list = query("SELECT ID_onvan_kod, nam_kod FROM tbl_onvan_kod ORDER BY nam_kod", fetch_all=True) or []
    shift_list = query("SELECT DISTINCT s.ID_shift, s.tarkib FROM shift_namt s ORDER BY s.tarkib", fetch_all=True) or []

    bakhsh_opts = '<option value="">همه بخش‌ها</option>' + ''.join(
        f'<option value="{b["ID_nam_bakhsh"]}">{b["nam_bakhsh"]}</option>' for b in bakhsh_list)
    code_opts = '<option value="">همه کدها</option>' + ''.join(
        f'<option value="{c["ID_onvan_kod"]}">{c["nam_kod"]}</option>' for c in code_list)
    shift_opts = '<option value="">همه شیفت‌ها</option>' + ''.join(
        f'<option value="{s["ID_shift"]}">{s["tarkib"]}</option>' for s in shift_list)

    # آمار اولیه خالی
    stats = {'total': 0, 'avg_duration': 0, 'unique_codes': 0, 'total_team': 0, 'unique_shifts': 0}
    table_html = '<tr><td colspan="10" class="empty">در حال بارگذاری...</td></tr>'
    dash_html = '<div class="empty">در حال بارگذاری نمودارها...</div>'

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>گزارش کدهای عملیاتی</title>
<script src="/static/js/chart.umd.min.js"></script>
<style>
    :root {{ --red: #b91c1c; --red-l: #dc2626; --green: #10b981; --gray: #64748b; --l-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9; --white: #fff; --r: 12px; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial; direction:rtl; background:var(--bg); color:#1e293b; }}
    .container {{ max-width:1400px; margin:0 auto; padding:16px; }}
    
    .header {{ background:linear-gradient(135deg,#b91c1c,#dc2626); color:white; border-radius:var(--r); padding:18px 24px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 6px 20px rgba(185,28,28,.25); }}
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
    .f-grp select:focus, .f-grp input:focus {{ border-color:var(--red); outline:none; }}

    .btn {{ padding:7px 15px; border:none; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; font-family:inherit; white-space:nowrap; }}
    .btn-red {{ background:var(--red); color:white; }}
    .btn-grn {{ background:var(--green); color:white; }}
    .btn-amb {{ background:#f59e0b; color:white; }}
    .btn-xs {{ padding:5px 10px; font-size:10px; }}

    .tabs {{ display:flex; gap:4px; margin-bottom:12px; border-bottom:2px solid var(--border); }}
    .tab {{ padding:8px 16px; font-size:12px; font-weight:600; border:none; background:none; color:var(--l-gray); cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-2px; font-family:inherit; }}
    .tab.on {{ color:var(--red); border-bottom-color:var(--red); }}
    .pan {{ display:none; }}
    .pan.on {{ display:block; }}

    .tbl-wrap {{ background:white; border-radius:var(--r); border:1px solid var(--border); overflow:hidden; }}
    .tbl-scroll {{ overflow:auto; max-height:500px; }}
    table {{ width:100%; border-collapse:collapse; font-size:11px; }}
    th {{ background:var(--red); color:white; padding:9px 5px; text-align:center; font-weight:600; position:sticky; top:0; z-index:5; }}
    td {{ padding:7px 5px; text-align:center; border-bottom:1px solid var(--border); }}
    tr:hover td {{ background:#fef2f2; }}

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
        border-top-color: #b91c1c;
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
        <h2>🚑 سامانه هوشمند تحلیل کدهای اضطراری</h2>
        <a href="/module/reports">⬅️ بازگشت</a>
    </div>

    <div class="kpi">
        <div class="kpi-card"><div class="kpi-val" style="color:#b91c1c;" id="k-total">{stats['total']}</div><div class="kpi-lbl">📋 کل کدها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#2563eb;" id="k-avg">{stats['avg_duration']}</div><div class="kpi-lbl">⏱ میانگین مدت (دقیقه)</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#7c3aed;" id="k-codes">{stats['unique_codes']}</div><div class="kpi-lbl">🔀 تنوع کدها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#10b981;" id="k-team">{stats['total_team']}</div><div class="kpi-lbl">👥 اعضای تیم</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#f59e0b;" id="k-shifts">{stats['unique_shifts']}</div><div class="kpi-lbl">🕒 شیفت‌ها</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ</label><input type="text" id="f-from" value="{month_ago}"></div>
            <div class="f-grp"><label>تا تاریخ</label><input type="text" id="f-to" value="{today_j}"></div>
            <div class="f-grp"><label>بخش</label><select id="f-bakhsh">{bakhsh_opts}</select></div>
            <div class="f-grp"><label>نوع کد</label><select id="f-code">{code_opts}</select></div>
            <div class="f-grp"><label>شیفت</label><select id="f-shift">{shift_opts}</select></div>
        </div>
        <div class="f-row">
            <div class="f-grp" style="flex:2;"><label>جستجو</label><input type="text" id="f-search" placeholder="نام بیمار / تشخیص / توضیحات..."></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-red" onclick="refresh(1)">🔍 اعمال فیلتر</button></div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab on" onclick="switchTab('dash')">📊 داشبورد</button>
        <button class="tab" onclick="switchTab('list')">📋 لیست عملیات</button>
        <button class="tab" onclick="switchTab('ai')">🤖 تحلیل هوشمند</button>
    </div>

    <div id="pan-dash" class="pan on">{dash_html}</div>

    <div id="pan-list" class="pan">
        <div class="tbl-wrap"><div class="tbl-scroll"><table>
            <thead><tr><th>کد</th><th>تاریخ</th><th>نوع کد</th><th>بخش</th><th>شیفت</th><th>بیمار</th><th>سن</th><th>مدت</th><th>نتیجه</th><th>تیم</th></tr></thead>
            <tbody id="tbl-body">{table_html}</tbody>
        </table></div></div>
        <div id="pagination" class="pagination"></div>
        <div class="bar">
            <button class="btn btn-grn btn-xs" onclick="doExport()">📥 Excel</button>
            <button class="btn btn-amb btn-xs" onclick="doPrint()">🖨️ چاپ</button>
        </div>
    </div>

    <div id="pan-ai" class="pan">
        <div class="card">
            <div class="card-title">🤖 تحلیل هوشمند کدهای عملیاتی</div>
            <div class="row" style="margin-bottom:15px;">
                <div class="form-group" style="flex:2;">
                    <label>🔑 کلید API دیپ‌سیک (اختیاری)</label>
                    <input type="text" id="deepseek-key" class="form-input" placeholder="sk-...">
                    <small>با وارد کردن کلید، تحلیل عمیق‌تری دریافت می‌کنید</small>
                </div>
                <div class="form-group" style="flex:0 0 auto; align-self: flex-end;">
                    <button class="btn btn-red" onclick="startAIAnalysis()">🔍 شروع تحلیل</button>
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
        document.querySelectorAll('.tab').forEach((x,i) => {{
            x.classList.toggle('on', (t==='dash'&&i===0)||(t==='list'&&i===1)||(t==='ai'&&i===2));
        }});
        document.querySelectorAll('.pan').forEach(p => p.classList.remove('on'));
        document.getElementById('pan-'+t).classList.add('on');
        if (t === 'dash') renderCharts(allData);
    }}

    async function refresh(page = 1) {{
        const p = new URLSearchParams({{
            from: (document.getElementById('f-from').value||'').replace(/\//g,''),
            to: (document.getElementById('f-to').value||'').replace(/\//g,''),
            bakhsh: document.getElementById('f-bakhsh').value,
            code: document.getElementById('f-code').value,
            shift: document.getElementById('f-shift').value,
            search: document.getElementById('f-search').value,
            page: page,
            per_page: 15
        }});
        const r = await fetch('/module/reports/codes/data?'+p.toString());
        const d = await r.json();
        allData = d.data || [];
        const s = d.stats || {{}};

        document.getElementById('k-total').textContent = s.total||0;
        document.getElementById('k-avg').textContent = s.avg_duration||0;
        document.getElementById('k-codes').textContent = s.unique_codes||0;
        document.getElementById('k-team').textContent = s.total_team||0;
        document.getElementById('k-shifts').textContent = s.unique_shifts||0;

        document.getElementById('tbl-body').innerHTML = allData.length ? allData.map(r => `<tr><td>${{r.ID_kod}}</td><td>${{r.date_display||''}}</td><td>${{r.code_title||''}}</td><td>${{r.nam_bakhsh||''}}</td><td>${{r.shift_name||''}}</td><td>${{r.nam_biar||''}}</td><td>${{r.sen||0}}</td><td>${{r.duration_min||0}}</td><td>${{r.natijeh_amlit||'-'}}</td><td>${{r.team_count||0}}</td></tr>`).join('') : '<tr><td colspan="10" class="empty">داده‌ای یافت نشد</td></tr>';

        if (d.available_shifts) populateShiftDropdown(d.available_shifts);

        currentPage = d.page || 1;
        totalPages = Math.ceil((d.total || 0) / 15);
        renderPagination();
        renderCharts(allData);
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
        if (currentPage > 1) html += `<button class="btn btn-red btn-xs" onclick="refresh(${{currentPage-1}})">« قبلی</button>`;
        html += `<span style="display:flex;align-items:center;font-size:13px;">صفحه ${{currentPage}} از ${{totalPages}}</span>`;
        if (currentPage < totalPages) html += `<button class="btn btn-red btn-xs" onclick="refresh(${{currentPage+1}})">بعدی »</button>`;
        container.innerHTML = html;
    }}

    // ==================== نمودارهای Chart.js ====================
    function renderCharts(data) {{
        setTimeout(() => {{
            ['chart-outcome','chart-dept','chart-shift','chart-duration','chart-risk'].forEach(id => {{
                const existing = Chart.getChart(id);
                if (existing) existing.destroy();
            }});

            if (!data.length) {{
                document.getElementById('pan-dash').innerHTML = '<div class="empty">داده‌ای نیست</div>';
                return;
            }}

            document.getElementById('pan-dash').innerHTML = `
                <div class="charts">
                    <div class="chart-box"><h4>🥧 توزیع نتایج عملیات</h4><canvas id="chart-outcome"></canvas></div>
                    <div class="chart-box"><h4>📊 پراکندگی در بخش‌ها</h4><canvas id="chart-dept"></canvas></div>
                    <div class="chart-box"><h4>🕒 توزیع در شیفت‌ها</h4><canvas id="chart-shift"></canvas></div>
                    <div class="chart-box"><h4>⏱ توزیع مدت زمان (دقیقه)</h4><canvas id="chart-duration"></canvas></div>
                    <div class="chart-box"><h4>🚨 امتیاز ریسک به تفکیک نوع کد</h4><canvas id="chart-risk"></canvas></div>
                </div>
            `;

            // ۱. نتایج (pie)
            const rm={{}};
            data.forEach(r => {{ const k=r.natijeh_amlit||'نامشخص'; rm[k]=(rm[k]||0)+1; }});
            const outcomeLabels = Object.keys(rm);
            const outcomeData = Object.values(rm);
            const colors = ['#b91c1c','#dc2626','#f87171','#fca5a5','#fecaca','#fef2f2'];
            new Chart(document.getElementById('chart-outcome'), {{
                type: 'pie',
                data: {{
                    labels: outcomeLabels,
                    datasets: [{{ data: outcomeData, backgroundColor: colors.slice(0, outcomeLabels.length) }}]
                }}
            }});

            // ۲. بخش‌ها (bar)
            const dm={{}};
            data.forEach(r => {{ const k=r.nam_bakhsh||'نامشخص'; dm[k]=(dm[k]||0)+1; }});
            const sortedDepts = Object.entries(dm).sort((a,b) => b[1]-a[1]).slice(0,10);
            new Chart(document.getElementById('chart-dept'), {{
                type: 'bar',
                data: {{
                    labels: sortedDepts.map(([k]) => k),
                    datasets: [{{ data: sortedDepts.map(([,v]) => v), backgroundColor: '#b91c1c' }}]
                }},
                options: {{ responsive: true }}
            }});

            // ۳. شیفت‌ها (pie)
            const sm={{}};
            data.forEach(r => {{ const k=r.shift_name||'نامشخص'; sm[k]=(sm[k]||0)+1; }});
            const shiftLabels = Object.keys(sm);
            new Chart(document.getElementById('chart-shift'), {{
                type: 'pie',
                data: {{
                    labels: shiftLabels,
                    datasets: [{{ data: Object.values(sm), backgroundColor: colors.slice(0, shiftLabels.length) }}]
                }}
            }});

            // ۴. توزیع مدت زمان (bar stacked)
            const bins = [0,10,20,30,45,60,90,120];
            const durData = {{}};
            bins.slice(0,-1).forEach((b,i) => {{
                const label = `${{b}}-${{bins[i+1]}}`;
                durData[label] = data.filter(r => (r.duration_min||0) >= b && (r.duration_min||0) < bins[i+1]).length;
            }});
            new Chart(document.getElementById('chart-duration'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(durData),
                    datasets: [{{ data: Object.values(durData), backgroundColor: '#dc2626' }}]
                }},
                options: {{ responsive: true }}
            }});

            // ۵. امتیاز ریسک (bar)
            const riskMap = {{}};
            data.forEach(r => {{
                const k = r.code_title||'نامشخص';
                if (!riskMap[k]) riskMap[k] = {{total:0, noresp:0}};
                riskMap[k].total++;
                // فرض می‌کنیم natijeh_amlit شامل 'ناموفق' یا 'فوت' به‌عنوان پیامد منفی
                const outcome = r.natijeh_amlit||'';
                if (outcome.includes('ناموفق') || outcome.includes('فوت')) riskMap[k].noresp++;
            }});
            const riskLabels = Object.keys(riskMap);
            const riskScores = riskLabels.map(k => {{
                const v = riskMap[k];
                return v.total ? Math.round((v.noresp/v.total)*100) : 0;
            }});
            new Chart(document.getElementById('chart-risk'), {{
                type: 'bar',
                data: {{
                    labels: riskLabels,
                    datasets: [{{ data: riskScores, backgroundColor: riskScores.map(v => v>50?'#b91c1c':v>25?'#f59e0b':'#10b981') }}]
                }},
                options: {{ responsive: true }}
            }});
        }}, 50);
    }}

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
            bakhsh: document.getElementById('f-bakhsh').value,
            code: document.getElementById('f-code').value,
            shift: document.getElementById('f-shift').value,
            search: document.getElementById('f-search').value,
            deepseek_key: deepseekKey
        }});
        try {{
            const res = await fetch('/module/reports/codes/analyze?' + params.toString());
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
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),bakhsh:document.getElementById('f-bakhsh').value,code:document.getElementById('f-code').value,shift:document.getElementById('f-shift').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/codes/export?'+p.toString(),'_blank');
    }}

    function doPrint() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value}});
        window.open('/module/reports/codes/print?'+p.toString(),'_blank');
    }}

    // لود اولیه
    document.addEventListener('DOMContentLoaded', () => refresh(1));
</script>
</body>
</html>'''
    return html


# ==================== توابع کمکی (بدون تغییر در منطق، فقط بازآرایی جزئی) ====================

def _fetch_data(d_from='', d_to='', bakhsh='', code='', shift='', search='', page=1, per_page=15):
    offset = (page - 1) * per_page
    base_join = """FROM tbl_amliat_kod c
                    LEFT JOIN tbl_bakhsh b ON c.nam_bakhsh = b.ID_nam_bakhsh
                    LEFT JOIN tbl_onvan_kod o ON c.onvan_kod = o.ID_onvan_kod
                    LEFT JOIN shift_namt s ON c.nam_shift = s.ID_shift
                    LEFT JOIN users u ON c.UserID = u.UserID
                    WHERE 1=1"""
    base_params = []

    if d_from: base_join += " AND c.dat_sabt >= %s"; base_params.append(d_from)
    if d_to: base_join += " AND c.dat_sabt <= %s"; base_params.append(d_to)
    if bakhsh: base_join += " AND c.nam_bakhsh = %s"; base_params.append(bakhsh)
    if code: base_join += " AND c.onvan_kod = %s"; base_params.append(code)
    if search: base_join += " AND (c.nam_biar LIKE %s OR c.tashkhis_pezeshk LIKE %s OR c.tavzih LIKE %s)"; base_params.extend([f'%{search}%']*3)

    data_sql = f"""SELECT c.ID_kod, c.dat_sabt, c.nam_biar, c.sen, c.sen_mah, c.sen_roz, c.jens,
                    c.tashkhis_pezeshk, c.time_saat_dagig_shoro AS start_time,
                    c.time_sat_dagigeh_paian AS end_time, c.natijeh_amlit, c.tavzih,
                    c.nam_pezshk_lider, c.mavred1,
                    b.nam_bakhsh, o.nam_kod AS code_title, s.tarkib AS shift_name, s.ID_shift AS shift_id,
                    s.nam_super, u.FullName AS registrar {base_join}"""
    data_params = base_params.copy()
    if shift: data_sql += " AND c.nam_shift = %s"; data_params.append(shift)
    data_sql += " ORDER BY c.ID_kod DESC LIMIT %s OFFSET %s"; data_params.extend([per_page, offset])

    count_sql = f"SELECT COUNT(*) as total {base_join}"
    count_params = base_params.copy()
    if shift: count_sql += " AND c.nam_shift = %s"; count_params.append(shift)

    shifts_sql = f"SELECT DISTINCT s.ID_shift, s.tarkib {base_join} ORDER BY s.tarkib"
    shifts_params = base_params.copy()

    data = query(data_sql, data_params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0
    available_shifts = [(r['ID_shift'], r['tarkib']) for r in (query(shifts_sql, shifts_params, fetch_all=True) or [])]

    ids = [str(r['ID_kod']) for r in data]
    team_data = {}
    if ids:
        team_sql = f"""SELECT n.nam_kod AS ID_kod, CONCAT(p.nam,' ',p.famil) AS fullname, COALESCE(r.nam_naghsh_kod,'عضو') AS role
                       FROM tbl_naghsh_kod n LEFT JOIN tbl_person p ON n.id_person=p.ID_person LEFT JOIN tbl_onvan_naghsh r ON n.nam_nagsh=r.ID_onvan_naghsh_kod
                       WHERE n.nam_kod IN ({','.join(ids)})"""
        teams = query(team_sql, fetch_all=True) or []
        for t in teams:
            kid = str(t['ID_kod']); team_data.setdefault(kid, []).append(f"{t['role']}: {t['fullname']}")

    for row in data:
        row['date_display'] = format_date_display(row.get('dat_sabt'))
        s = str(row.get('start_time') or '')[:5]; e = str(row.get('end_time') or '')[:5]
        try:
            t1 = dt.strptime(s, "%H:%M") if s and ':' in s else dt(2000,1,1)
            t2 = dt.strptime(e, "%H:%M") if e and ':' in e else dt(2000,1,1)
            diff = (t2 - t1).total_seconds() / 60
            row['duration_min'] = int(diff) if diff >= 0 else int(diff + 1440)
        except: row['duration_min'] = 0
        row['team_members'] = ' | '.join(team_data.get(str(row['ID_kod']), []))
        row['team_count'] = len(team_data.get(str(row['ID_kod']), []))

    avg_dur = int(sum(r.get('duration_min', 0) for r in data) / len(data)) if data else 0
    unique_codes = len(set(r.get('code_title', '') for r in data))
    total_team = sum(r.get('team_count', 0) for r in data)
    unique_shifts = len(set(r.get('shift_name', '') for r in data))

    return {
        'data': data,
        'stats': {'total': total, 'avg_duration': avg_dur, 'unique_codes': unique_codes, 'total_team': total_team, 'unique_shifts': unique_shifts},
        'total': total,
        'page': page,
        'per_page': per_page,
        'available_shifts': available_shifts
    }


def _build_table(data):
    if not data: return '<tr><td colspan="10" class="empty">داده‌ای یافت نشد</td></tr>'
    return ''.join(f"<tr><td>{r.get('ID_kod','')}</td><td>{r.get('date_display','')}</td><td>{r.get('code_title','')}</td><td>{r.get('nam_bakhsh','')}</td><td>{r.get('shift_name','')}</td><td>{r.get('nam_biar','')}</td><td>{r.get('sen',0)}</td><td>{r.get('duration_min',0)}</td><td>{r.get('natijeh_amlit','-')}</td><td>{r.get('team_count',0)}</td></tr>" for r in data)


def _build_dashboard(data):
    """خالی – نمودارها با Chart.js ساخته می‌شوند"""
    return '<div class="empty">در حال بارگذاری نمودارها...</div>'


# ==================== تحلیل هوشمند ====================

def _generate_ai_summary(data):
    if not data: return {}
    total = len(data)
    avg_dur = int(sum(r.get('duration_min',0) for r in data) / total) if total else 0

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
    std_val = math.sqrt(sum((v-mean_val)**2 for v in values)/len(values)) if len(values)>1 else 0
    outliers = []
    for i, v in enumerate(values):
        if std_val > 0 and abs(v-mean_val)/std_val > 2:
            outliers.append({'date': sorted_days[i], 'value': v, 'z_score': round(abs(v-mean_val)/std_val, 2)})

    risk_scores = {}
    for r in data:
        code = r.get('code_title','نامشخص')
        if code not in risk_scores: risk_scores[code] = {'total':0, 'bad':0}
        risk_scores[code]['total'] += 1
        outcome = r.get('natijeh_amlit','')
        if 'ناموفق' in outcome or 'فوت' in outcome:
            risk_scores[code]['bad'] += 1

    return {
        'total_calls': total,
        'avg_duration': avg_dur,
        'code_types': {r.get('code_title','نامشخص'): data.count(r) for r in data},
        'departments': list(set(r.get('nam_bakhsh','') for r in data)),
        'outcomes': {r.get('natijeh_amlit','نامشخص'): data.count(r) for r in data},
        'shift_distribution': {r.get('shift_name','نامشخص'): data.count(r) for r in data},
        'team_avg': round(sum(r.get('team_count',0) for r in data)/total, 1) if total else 0,
        'max_team': max((r.get('team_count',0) for r in data), default=0),
        'moving_average': dict(zip(sorted_days[-10:], moving_avg[-10:])),
        'outliers': outliers,
        'risk_scores': {k: {'rate': round(v['bad']/v['total']*100, 1)} for k, v in risk_scores.items() if v['total']}
    }


def internal_codes_analysis(summary):
    lines = []
    lines.append(f"🔢 **تعداد کل عملیات‌ها:** {summary['total_calls']}")
    lines.append(f"⏱ **میانگین مدت عملیات:** {summary['avg_duration']} دقیقه")
    lines.append(f"👥 **میانگین اعضای تیم:** {summary['team_avg']} نفر (حداکثر {summary['max_team']})")

    if summary.get('code_types'):
        lines.append("📋 **فراوانی انواع کدها:**")
        for k, v in sorted(summary['code_types'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"   - {k}: {v}")

    if summary.get('outcomes'):
        lines.append("🏁 **توزیع نتایج:**")
        for k, v in summary['outcomes'].items():
            lines.append(f"   - {k}: {v}")

    if summary.get('shift_distribution'):
        lines.append("🕒 **توزیع در شیفت‌ها:**")
        for k, v in summary['shift_distribution'].items():
            lines.append(f"   - {k}: {v}")

    if summary.get('moving_average'):
        lines.append(f"📈 **میانگین متحرک ۷ روزه (۱۰ روز اخیر):** {list(summary['moving_average'].values())}")

    if summary.get('outliers'):
        lines.append(f"⚠️ **نقاط پرت (انحراف > ۲):** {len(summary['outliers'])} روز")
        for o in summary['outliers'][:3]:
            lines.append(f"   - {o['date']}: {o['value']} عملیات (Z-score: {o['z_score']})")

    if summary.get('risk_scores'):
        lines.append("🚨 **امتیاز ریسک به تفکیک نوع کد:**")
        for k, v in sorted(summary['risk_scores'].items(), key=lambda x: x[1]['rate'], reverse=True):
            emoji = '🔴' if v['rate'] > 30 else '🟠' if v['rate'] > 15 else '🟢'
            lines.append(f"   {emoji} {k}: {v['rate']}% پیامد منفی")

    lines.append("💡 **پیشنهادات:**")
    if summary['avg_duration'] > 30:
        lines.append("- میانگین زمان عملیات بالاست؛ بررسی فرآیندها ضروری است.")
    if summary['team_avg'] < 2:
        lines.append("- تیم‌های عملیاتی کوچک هستند؛ تقویت ترکیب تیم پیشنهاد می‌شود.")
    lines.append("- کدهای با ریسک بالا نیاز به بازنگری پروتکل‌ها دارند.")
    lines.append("- شبیه‌سازی دوره‌ای بر اساس کدهای پرتکرار اجرا شود.")
    return "\n".join(lines)


def deepseek_analysis(api_key, summary):
    if not api_key or len(api_key.strip()) < 10:
        return None
    prompt = f"""شما یک تحلیلگر عملیات‌های اضطراری بیمارستانی هستید. این داده‌های کدهای عملیاتی را تحلیل کنید و پاسخ کاملاً فارسی دهید:

{json.dumps(summary, indent=2, ensure_ascii=False)}

تحلیل باید شامل: خلاصه وضعیت، الگوها، نقاط پرت، امتیاز ریسک و پیشنهادات اجرایی (حداقل ۳ مورد)."""
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "شما یک کارشناس ارشد مدیریت بحران بیمارستان هستید."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7, "max_tokens": 1500
            },
            timeout=20)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except: pass
    return None


def api_data(request_args):
    return _fetch_data(
        request_args.get('from',''), request_args.get('to',''),
        request_args.get('bakhsh',''), request_args.get('code',''),
        request_args.get('shift',''), request_args.get('search',''),
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 15, type=int)
    )


def api_analyze(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('bakhsh',''), request_args.get('code',''),
                    request_args.get('shift',''), request_args.get('search',''),
                    page=1, per_page=9999)
    data = d['data']
    if not data:
        return {'success': False, 'message': 'داده‌ای برای تحلیل وجود ندارد'}
    summary = _generate_ai_summary(data)
    deepseek_key = request_args.get('deepseek_key', '').strip()
    if deepseek_key:
        analysis = deepseek_analysis(deepseek_key, summary)
        if analysis:
            return {'success': True, 'analysis': analysis, 'source_name': 'DeepSeek AI'}
    analysis = internal_codes_analysis(summary)
    return {'success': True, 'analysis': analysis, 'source_name': 'تحلیل داخلی'}


def api_export(request_args):
    import io; from openpyxl import Workbook; from flask import send_file
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('bakhsh',''), request_args.get('code',''), request_args.get('shift',''), request_args.get('search',''), page=1, per_page=9999)
    wb = Workbook(); ws = wb.active; ws.title = "گزارش کدها"
    ws.append(['کد','تاریخ','نوع کد','بخش','شیفت','سوپروایزر','بیمار','سن(سال)','سن(ماه)','سن(روز)','جنسیت','تشخیص','شروع','پایان','مدت','لیدر','نتیجه','تیم','توضیحات','ثبت‌کننده'])
    for r in d['data']: ws.append([r.get('ID_kod'),r.get('date_display'),r.get('code_title'),r.get('nam_bakhsh'),r.get('shift_name'),r.get('nam_super'),r.get('nam_biar'),r.get('sen'),r.get('sen_mah'),r.get('sen_roz'),r.get('jens'),r.get('tashkhis_pezeshk'),str(r.get('start_time',''))[:5],str(r.get('end_time',''))[:5],r.get('duration_min'),r.get('nam_pezshk_lider'),r.get('natijeh_amlit'),r.get('team_members',''),r.get('tavzih',''),r.get('registrar')])
    ws2 = wb.create_sheet("آمار"); ws2.append(['شاخص','مقدار']); s = d['stats']
    for k,v in [('کل کدها',s['total']),('میانگین مدت',f"{s['avg_duration']} دقیقه"),('تنوع کدها',s['unique_codes']),('مجموع اعضای تیم',s['total_team']),('شیفت‌ها',s['unique_shifts'])]: ws2.append([k,v])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='codes_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def api_print(request_args):
    import jdatetime
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), '', '', request_args.get('shift',''), page=1, per_page=9999)
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    shifts = {}
    for r in d['data']:
        s = r.get('shift_name','نامشخص')
        if s not in shifts: shifts[s] = []
        shifts[s].append(r)
    html = f'''<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><style>body{{font-family:Tahoma;padding:20px;}}h1{{text-align:center;color:#b91c1c;}}.sg{{margin:20px 0;border:1px solid #ddd;border-radius:10px;overflow:hidden;}}.sh{{background:#b91c1c;color:white;padding:10px 15px;font-weight:bold;}}table{{width:100%;border-collapse:collapse;}}th{{background:#e2e8f0;padding:8px;font-size:11px;}}td{{padding:7px;border-bottom:1px solid #eee;text-align:center;font-size:11px;}}@media print{{body{{padding:0;}}}}</style></head><body><h1>🚑 گزارش کدهای عملیاتی - {today_j}</h1>'''
    for shift, items in shifts.items():
        html += f'<div class="sg"><div class="sh">🕒 {shift} - {len(items)} مورد</div><table><tr><th>کد</th><th>تاریخ</th><th>نوع</th><th>بخش</th><th>بیمار</th><th>مدت</th><th>نتیجه</th><th>تیم</th></tr>'
        for r in items: html += f'<tr><td>{r.get("ID_kod")}</td><td>{r.get("date_display")}</td><td>{r.get("code_title")}</td><td>{r.get("nam_bakhsh")}</td><td>{r.get("nam_biar")}</td><td>{r.get("duration_min",0)}</td><td>{r.get("natijeh_amlit","-")}</td><td>{r.get("team_count",0)}</td></tr>'
        html += '</table></div>'
    html += '<script>window.print();</script></body></html>'
    return html
    
    