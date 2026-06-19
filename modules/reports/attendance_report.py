"""
گزارش حضور و غیاب پرسنل (نسخه کامل با داشبورد و تحلیل هوشمند)
نسخه Flask با صفحه‌بندی، فیلتر شیفت وابسته به تاریخ، KPI و Export
+ اصلاح نمایش rizshift بر اساس shift_code از onvan_shift
"""

from models.database import query
import json
from utils.formatters import format_date_display
from datetime import datetime
import math

def get_attendance_report(user):
    """صفحه اصلی گزارش حضور و غیاب"""

    import jdatetime
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    yesterday_j = (jdatetime.date.today() - jdatetime.timedelta(days=1)).strftime("%Y/%m/%d")
    today_int = today_j.replace('/', '')
    yesterday_int = yesterday_j.replace('/', '')

    # بخش‌ها (ثابت)
    section_list = query("SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh", fetch_all=True) or []
    section_opts = '<option value="">همه بخش‌ها</option>' + ''.join(f'<option value="{s["ID_nam_bakhsh"]}">{s["nam_bakhsh"]}</option>' for s in section_list)

    # لود داده‌های اولیه (صفحه ۱)
    initial = _fetch_data(yesterday_int, today_int, page=1, per_page=15)
    stats = initial['stats']
    table_html = _build_table(initial['data'])

    # شیفت‌های موجود در بازهٔ اولیه (بر اساس tarkib اصلی)
    available_shifts = initial.get('available_shifts', [])
    shift_opts = '<option value="">همه شیفت‌ها</option>' + ''.join(
        f'<option value="{s}">{s}</option>' for s in available_shifts
    )

    # برای json.dumps، تمام اشیای datetime را در همان initial['data'] به رشته تبدیل می‌کنیم
    for row in initial['data']:
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.strftime('%Y-%m-%d %H:%M:%S')

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>گزارش حضور و غیاب</title>
<script src="/static/js/chart.umd.min.js"></script>
<style>
    :root {{ --primary: #1e3a8a; --green: #28a745; --red: #dc3545; --orange: #fd7e14; --yellow: #ffc107; --teal: #17a2b8; --gray: #64748b; --l-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9; --white: #fff; --r: 12px; }}
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
    .f-grp select:focus, .f-grp input:focus {{ border-color:var(--primary); outline:none; }}

    .btn {{ padding:7px 15px; border:none; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; font-family:inherit; white-space:nowrap; }}
    .btn-blue {{ background:var(--primary); color:white; }}
    .btn-grn {{ background:var(--green); color:white; }}
    .btn-amb {{ background:#f59e0b; color:white; }}
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
    tr:hover td {{ background:#f8fafc; }}

    .badge {{ padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; display:inline-block; color:white; }}
    .badge-present {{ background:var(--green); }}
    .badge-absent {{ background:var(--red); }}
    .badge-late {{ background:var(--yellow); color:#333; }}
    .badge-early {{ background:var(--orange); }}
    .badge-pass {{ background:var(--teal); }}

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
        <h2>📊 کارتابل هوشمند تردد پرسنل</h2>
        <a href="/module/reports">⬅️ بازگشت</a>
    </div>

    <div class="kpi">
        <div class="kpi-card"><div class="kpi-val" style="color:#28a745;" id="k-present">{stats['present']}</div><div class="kpi-lbl">✅ حاضرین</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#dc3545;" id="k-absent">{stats['absent']}</div><div class="kpi-lbl">❌ غایبین</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#ffc107;" id="k-late">{stats['late']}</div><div class="kpi-lbl">⏳ تاخیر</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#fd7e14;" id="k-early">{stats['early']}</div><div class="kpi-lbl">🏃 تعجیل</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#17a2b8;" id="k-pass">{stats['pass']}</div><div class="kpi-lbl">🎫 پاس ساعتی</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ</label><input type="text" id="f-from" value="{yesterday_j}"></div>
            <div class="f-grp"><label>تا تاریخ</label><input type="text" id="f-to" value="{today_j}"></div>
            <div class="f-grp"><label>شیفت</label><select id="f-shift">{shift_opts}</select></div>
            <div class="f-grp"><label>بخش</label><select id="f-section">{section_opts}</select></div>
            <div class="f-grp"><label>وضعیت</label><select id="f-status"><option value="">همه</option><option value="حاضر">✅ حاضر</option><option value="غایب">❌ غایب</option><option value="تاخیر">⏳ تاخیر</option><option value="تعجیل">🏃 تعجیل</option><option value="پاس ساعتی">🎫 پاس ساعتی</option></select></div>
        </div>
        <div class="f-row">
            <div class="f-grp" style="flex:2;"><label>جستجوی نام</label><input type="text" id="f-search" placeholder="نام پرسنل..."></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-blue" onclick="refresh(1)">🔍 نمایش گزارش</button></div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab on" onclick="switchTab('list')">📋 لیست</button>
        <button class="tab" onclick="switchTab('dash')">📊 داشبورد</button>
        <button class="tab" onclick="switchTab('ai')">🤖 تحلیل هوشمند</button>
        <button class="tab" onclick="switchTab('print-shift')">📄 چاپ (شیفت/بخش)</button>
        <button class="tab" onclick="switchTab('print-person')">👥 چاپ (پرسنل)</button>
    </div>

    <div id="pan-list" class="pan on">
        <div class="tbl-wrap"><div class="tbl-scroll"><table>
            <thead><tr><th>تاریخ</th><th>وضعیت</th><th>پرسنل</th><th>بخش</th><th>شیفت</th><th>ریز شیفت</th><th>زمان ثبت</th><th>توضیحات</th></tr></thead>
            <tbody id="tbl-body">{table_html}</tbody>
        </table></div></div>
        <div id="pagination" class="pagination"></div>
        <div class="bar">
            <button class="btn btn-grn btn-xs" onclick="doExport()">📥 Excel</button>
        </div>
    </div>

    <div id="pan-dash" class="pan">
        <div class="empty">در حال بارگذاری نمودارها...</div>
    </div>

    <div id="pan-ai" class="pan">
        <div class="card">
            <div class="card-title">🤖 تحلیل هوشمند حضور و غیاب</div>
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

    <div id="pan-print-shift" class="pan">
        <div style="text-align:center;padding:20px;">
            <p style="color:var(--gray);margin-bottom:10px;">نسخه چاپی گروه‌بندی شده بر اساس شیفت و بخش</p>
            <button class="btn btn-blue" onclick="doPrintShift()">🖨️ مشاهده و چاپ</button>
        </div>
    </div>

    <div id="pan-print-person" class="pan">
        <div style="text-align:center;padding:20px;">
            <p style="color:var(--gray);margin-bottom:10px;">نسخه چاپی گروه‌بندی شده بر اساس پرسنل</p>
            <button class="btn btn-blue" onclick="doPrintPerson()">🖨️ مشاهده و چاپ</button>
        </div>
    </div>
</div>

<script>
    let allData = {json.dumps(initial['data'], ensure_ascii=False)};
    var currentPage = 1;
    var totalPages = 1;

    function switchTab(t) {{
        document.querySelectorAll('.tab').forEach((x,i) => {{
            x.classList.toggle('on', (t==='list'&&i===0)||(t==='dash'&&i===1)||(t==='ai'&&i===2)||(t==='print-shift'&&i===3)||(t==='print-person'&&i===4));
        }});
        document.querySelectorAll('.pan').forEach(p => p.classList.remove('on'));
        document.getElementById('pan-'+t).classList.add('on');
        if (t === 'dash') renderCharts(allData);
    }}

    async function refresh(page = 1) {{
        const p = new URLSearchParams({{
            from: (document.getElementById('f-from').value||'').replace(/\//g,''),
            to: (document.getElementById('f-to').value||'').replace(/\//g,''),
            shift: document.getElementById('f-shift').value,
            section: document.getElementById('f-section').value,
            status: document.getElementById('f-status').value,
            search: document.getElementById('f-search').value,
            page: page,
            per_page: 15
        }});
        const r = await fetch('/module/reports/attendance/data?'+p.toString());
        const d = await r.json();
        allData = d.data || [];
        const s = d.stats || {{}};

        document.getElementById('k-present').textContent = s.present||0;
        document.getElementById('k-absent').textContent = s.absent||0;
        document.getElementById('k-late').textContent = s.late||0;
        document.getElementById('k-early').textContent = s.early||0;
        document.getElementById('k-pass').textContent = s.pass||0;

        document.getElementById('tbl-body').innerHTML = allData.length ? allData.map(r => {{
            const badges = {{'حاضر':'badge-present','غایب':'badge-absent','تاخیر':'badge-late','تعجیل':'badge-early','پاس ساعتی':'badge-pass'}};
            const b = badges[r.status] || 'badge-present';
            return `<tr><td>${{r.date_display||''}}</td><td><span class="badge ${{b}}">${{r.status}}</span></td><td>${{r.person_name||''}}</td><td>${{r.section_name||''}}</td><td>${{r.shift_name||''}}</td><td>${{r.rizshift_display||'-'}}</td><td>${{r.time_display||''}}</td><td>${{r.description||'-'}}</td></tr>`;
        }}).join('') : '<tr><td colspan="8" class="empty">داده‌ای یافت نشد</td></tr>';

        if (d.available_shifts) {{
            populateShiftDropdown(d.available_shifts);
        }}

        currentPage = d.page || 1;
        totalPages = Math.ceil((d.total || 0) / 15);
        renderPagination();

        if (document.getElementById('pan-dash').classList.contains('on')) {{
            renderCharts(allData);
        }}
    }}

    function populateShiftDropdown(shifts) {{
        const sel = document.getElementById('f-shift');
        const currentVal = sel.value;
        sel.innerHTML = '<option value="">همه شیفت‌ها</option>';
        shifts.forEach(s => {{ sel.innerHTML += `<option value="${{s}}">${{s}}</option>`; }});
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
            ['chart-status','chart-dept','chart-shift','chart-trend','chart-risk'].forEach(id => {{
                const existing = Chart.getChart(id);
                if (existing) existing.destroy();
            }});

            if (!data.length) {{
                document.getElementById('pan-dash').innerHTML = '<div class="empty">داده‌ای نیست</div>';
                return;
            }}

            document.getElementById('pan-dash').innerHTML = `
                <div class="charts">
                    <div class="chart-box"><h4>🥧 توزیع وضعیت‌ها</h4><canvas id="chart-status"></canvas></div>
                    <div class="chart-box"><h4>📊 حضور/غیاب به تفکیک بخش</h4><canvas id="chart-dept"></canvas></div>
                    <div class="chart-box"><h4>🕒 وضعیت‌ها در شیفت‌های مختلف</h4><canvas id="chart-shift"></canvas></div>
                    <div class="chart-box"><h4>📈 روند روزانه (۳۰ روز اخیر)</h4><canvas id="chart-trend"></canvas></div>
                    <div class="chart-box"><h4>🚨 ریسک بخش‌ها (درصد غیبت)</h4><canvas id="chart-risk"></canvas></div>
                </div>
            `;

            const colors = ['#28a745','#dc3545','#ffc107','#fd7e14','#17a2b8'];

            // وضعیت‌ها (pie)
            const sm={{}};
            data.forEach(r => {{ const k=r.status||'نامشخص'; sm[k]=(sm[k]||0)+1; }});
            new Chart(document.getElementById('chart-status'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(sm),
                    datasets: [{{ data: Object.values(sm), backgroundColor: colors.slice(0, Object.keys(sm).length) }}]
                }}
            }});

            // بخش‌ها (bar stacked: حاضر/غایب)
            const dm={{}};
            data.forEach(r => {{
                const k=r.section_name||'نامشخص';
                if(!dm[k]) dm[k]={{present:0,absent:0}};
                r.status==='حاضر' ? dm[k].present++ : dm[k].absent++;
            }});
            const deptLabels = Object.keys(dm);
            const presentData = deptLabels.map(k => dm[k].present);
            const absentData = deptLabels.map(k => dm[k].absent);
            new Chart(document.getElementById('chart-dept'), {{
                type: 'bar',
                data: {{
                    labels: deptLabels,
                    datasets: [
                        {{ label: 'حاضر', data: presentData, backgroundColor: '#28a745' }},
                        {{ label: 'غایب', data: absentData, backgroundColor: '#dc3545' }}
                    ]
                }},
                options: {{ responsive: true, scales: {{ x: {{ stacked: true }}, y: {{ stacked: true }} }} }}
            }});

            // شیفت‌ها (stacked bar با تفکیک وضعیت)
            const shiftMap={{}};
            const statuses = ['حاضر','غایب','تاخیر','تعجیل','پاس ساعتی'];
            data.forEach(r => {{
                const k=r.shift_name||'نامشخص';
                if(!shiftMap[k]) shiftMap[k]={{}};
                shiftMap[k][r.status]=(shiftMap[k][r.status]||0)+1;
            }});
            const shiftLabels = Object.keys(shiftMap);
            const datasets = statuses.map((st, i) => ({{
                label: st,
                data: shiftLabels.map(sh => shiftMap[sh][st]||0),
                backgroundColor: colors[i]
            }}));
            new Chart(document.getElementById('chart-shift'), {{
                type: 'bar',
                data: {{ labels: shiftLabels, datasets: datasets }},
                options: {{ responsive: true, scales: {{ x: {{ stacked: true }}, y: {{ stacked: true }} }} }}
            }});

            // روند روزانه (line)
            const daily={{}};
            data.forEach(r => {{ const d=r.date_display||''; daily[d]=(daily[d]||0)+1; }});
            const sortedDays = Object.entries(daily).sort((a,b) => a[0].localeCompare(b[0])).slice(-30);
            new Chart(document.getElementById('chart-trend'), {{
                type: 'line',
                data: {{
                    labels: sortedDays.map(([k]) => k.substring(5)),
                    datasets: [{{ label: 'تعداد رکورد', data: sortedDays.map(([,v]) => v), borderColor: '#1e3a8a', tension: 0.3 }}]
                }},
                options: {{ responsive: true }}
            }});

            // ریسک بخش‌ها (bar درصد غیرحاضر)
            const riskMap={{}};
            data.forEach(r => {{
                const k=r.section_name||'نامشخص';
                if(!riskMap[k]) riskMap[k]={{total:0,absent:0}};
                riskMap[k].total++;
                if(r.status!=='حاضر') riskMap[k].absent++;
            }});
            const riskLabels = Object.keys(riskMap);
            const riskData = riskLabels.map(k => {{
                const v=riskMap[k];
                return v.total ? Math.round((v.absent/v.total)*100) : 0;
            }});
            const riskColors = riskData.map(v => v>30?'#dc3545':v>15?'#ffc107':'#28a745');
            new Chart(document.getElementById('chart-risk'), {{
                type: 'bar',
                data: {{
                    labels: riskLabels,
                    datasets: [{{ data: riskData, backgroundColor: riskColors }}]
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
            shift: document.getElementById('f-shift').value,
            section: document.getElementById('f-section').value,
            status: document.getElementById('f-status').value,
            search: document.getElementById('f-search').value,
            deepseek_key: deepseekKey
        }});
        try {{
            const res = await fetch('/module/reports/attendance/analyze?' + params.toString());
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
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value,section:document.getElementById('f-section').value,status:document.getElementById('f-status').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/attendance/export?'+p.toString(),'_blank');
    }}

    function doPrintShift() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value,section:document.getElementById('f-section').value,status:document.getElementById('f-status').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/attendance/print/shift?'+p.toString(),'_blank');
    }}

    function doPrintPerson() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value,section:document.getElementById('f-section').value,status:document.getElementById('f-status').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/attendance/print/person?'+p.toString(),'_blank');
    }}

    document.addEventListener('DOMContentLoaded', function() {{
        renderCharts(allData);
    }});
</script>
</body>
</html>'''
    return html


def _fetch_data(d_from='', d_to='', shift='', section='', status='', search='', page=1, per_page=15):
    """واکشی داده از دیتابیس با صفحه‌بندی و فیلتر شیفت پویا"""

    # پاک‌سازی تاریخ‌ها
    d_from = ''.join(filter(str.isdigit, d_from)) if d_from else ''
    d_to = ''.join(filter(str.isdigit, d_to)) if d_to else ''

    data = []

    # حضور
    sql_h = """SELECT h.ID_hazer as id, h.dat_sabt, 'حاضر' as status, h.zaman_sabt,
               b.nam_bakhsh as section_name, p.nam as p_nam, p.famil as p_famil, h.id_person as person_id,
               s.tarkib AS shift_name, s.ID_shift as shift_id, '' as description,
               o.shift_code as rizshift_display
               FROM tbl_hozor h
               LEFT JOIN tbl_bakhsh b ON h.nam_bakhsh=b.ID_nam_bakhsh
               LEFT JOIN tbl_person p ON h.id_person=p.ID_person
               LEFT JOIN shift_namt s ON h.nam_shift=s.ID_shift
               LEFT JOIN onvan_shift o ON h.rizshift = o.ID_onvan_shift
               WHERE h.ispresent=1"""
    params_h = []
    if d_from: sql_h += " AND h.dat_sabt >= %s"; params_h.append(d_from)
    if d_to: sql_h += " AND h.dat_sabt <= %s"; params_h.append(d_to)
    if shift: sql_h += " AND s.tarkib = %s"; params_h.append(shift)
    if section: sql_h += " AND h.nam_bakhsh = %s"; params_h.append(section)
    if search: sql_h += " AND (p.nam LIKE %s OR p.famil LIKE %s)"; params_h.extend([f'%{search}%']*2)

    present_data = query(sql_h, params_h, fetch_all=True) or []

    # غیبت و ترددها
    types = [('غایب','ghaibat'),('تاخیر','takhir_saati'),('تعجیل','taajil_khoroj'),('پاس ساعتی','pas_saati')]
    g_data = []
    for status_name, col in types:
        sql_g = f"""SELECT g.ID_ghaibat as id, g.dat_sabt, '{status_name}' as status, g.zaman_sabt,
                    b.nam_bakhsh as section_name, p.nam as p_nam, p.famil as p_famil, g.nam_person as person_id,
                    s.tarkib AS shift_name, s.ID_shift as shift_id, g.tozihat as description,
                    o.shift_code as rizshift_display
                    FROM tbl_ghaybat g
                    LEFT JOIN tbl_bakhsh b ON g.nam_bakhsh=b.ID_nam_bakhsh
                    LEFT JOIN tbl_person p ON g.nam_person=p.ID_person
                    LEFT JOIN shift_namt s ON g.nam_shift=s.ID_shift
                    LEFT JOIN onvan_shift o ON g.rizshift = o.ID_onvan_shift
                    WHERE g.{col}=1"""
        params_g = []
        if d_from: sql_g += " AND g.dat_sabt >= %s"; params_g.append(d_from)
        if d_to: sql_g += " AND g.dat_sabt <= %s"; params_g.append(d_to)
        if shift: sql_g += " AND s.tarkib = %s"; params_g.append(shift)
        if section: sql_g += " AND g.nam_bakhsh = %s"; params_g.append(section)
        if search: sql_g += " AND (p.nam LIKE %s OR p.famil LIKE %s)"; params_g.extend([f'%{search}%']*2)
        g_data.extend(query(sql_g, params_g, fetch_all=True) or [])

    all_data = present_data + g_data

    # پردازش
    for row in all_data:
        row['date_display'] = format_date_display(row.get('dat_sabt'))
        t = str(row.get('zaman_sabt', ''))
        row['time_display'] = t.split(' ')[-1][:5] if ' ' in t else t[:5]
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        row['person_name'] = f"{row.get('p_nam','')} {row.get('p_famil','')}".strip() or str(row.get('person_id',''))
        row['section_name'] = row.get('section_name') or str(row.get('nam_bakhsh',''))
        # rizshift_display اکنون از JOIN گرفته شده، اگر NULL بود '-' بگذاریم
        row['rizshift_display'] = row.get('rizshift_display') or '-'

    # فیلتر وضعیت
    if status:
        all_data = [r for r in all_data if r.get('status') == status]

    # مرتب‌سازی کل
    all_data.sort(key=lambda r: (r.get('dat_sabt', 0), r.get('zaman_sabt', '')), reverse=True)

    # شیفت‌های یکتا
    shift_set = set()
    for r in all_data:
        sn = r.get('shift_name', '')
        if sn:
            shift_set.add(sn)
    available_shifts = sorted(shift_set)

    # آمار کلی
    stats = {
        'present': sum(1 for r in all_data if r.get('status') == 'حاضر'),
        'absent': sum(1 for r in all_data if r.get('status') == 'غایب'),
        'late': sum(1 for r in all_data if r.get('status') == 'تاخیر'),
        'early': sum(1 for r in all_data if r.get('status') == 'تعجیل'),
        'pass': sum(1 for r in all_data if r.get('status') == 'پاس ساعتی'),
    }

    total = len(all_data)
    offset = (page - 1) * per_page
    page_data = all_data[offset:offset+per_page]

    return {
        'data': page_data,
        'stats': stats,
        'total': total,
        'page': page,
        'per_page': per_page,
        'available_shifts': available_shifts
    }


def _build_table(data):
    if not data:
        return '<tr><td colspan="8" class="empty">داده‌ای یافت نشد</td></tr>'
    badges = {'حاضر': 'badge-present', 'غایب': 'badge-absent', 'تاخیر': 'badge-late', 'تعجیل': 'badge-early', 'پاس ساعتی': 'badge-pass'}
    rows = []
    for r in data:
        b = badges.get(r.get('status', ''), 'badge-present')
        rows.append(
            f"<tr><td>{r.get('date_display','')}</td>"
            f"<td><span class='badge {b}'>{r.get('status','')}</span></td>"
            f"<td>{r.get('person_name','')}</td>"
            f"<td>{r.get('section_name','')}</td>"
            f"<td>{r.get('shift_name','')}</td>"
            f"<td>{r.get('rizshift_display','-')}</td>"
            f"<td>{r.get('time_display','')}</td>"
            f"<td>{r.get('description','-')}</td></tr>"
        )
    return ''.join(rows)


def api_data(request_args):
    return _fetch_data(
        request_args.get('from',''), request_args.get('to',''),
        request_args.get('shift',''), request_args.get('section',''),
        request_args.get('status',''), request_args.get('search',''),
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 15, type=int)
    )


def api_export(request_args):
    import io; from openpyxl import Workbook; from flask import send_file
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('shift',''), request_args.get('section',''), request_args.get('status',''), request_args.get('search',''), page=1, per_page=9999)
    wb = Workbook(); ws = wb.active; ws.title = "حضور و غیاب"
    ws.append(['تاریخ', 'وضعیت', 'پرسنل', 'بخش', 'شیفت', 'شیفت جزئی', 'زمان', 'توضیحات'])
    for r in d['data']:
        ws.append([r.get('date_display'), r.get('status'), r.get('person_name'), r.get('section_name'), r.get('shift_name'), r.get('rizshift_display','-'), r.get('time_display'), r.get('description','')])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='attendance_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def api_print_shift(request_args):
    import jdatetime
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('shift',''), request_args.get('section',''), request_args.get('status',''), request_args.get('search',''), page=1, per_page=9999)
    today_j = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    data = d['data']

    groups = {}
    for r in data:
        sh = r.get('shift_name', 'نامشخص')
        sec = r.get('section_name', 'نامشخص')
        if sh not in groups: groups[sh] = {}
        if sec not in groups[sh]: groups[sh][sec] = []
        groups[sh][sec].append(r)

    html = f'''<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><style>body{{font-family:Tahoma;padding:25px;}}h1{{color:#1e3a8a;text-align:center;}}.sh{{background:#1e3a8a;color:white;padding:12px;margin-top:20px;border-radius:8px;font-size:16px;}}.sec{{background:#f8f9fa;padding:8px;border-right:5px solid #1e3a8a;margin:10px 0;font-weight:bold;color:#1e3a8a;}}table{{width:100%;border-collapse:collapse;margin-bottom:15px;}}th{{background:#e2e8f0;padding:8px;font-size:11px;}}td{{padding:7px;border:1px solid #ddd;text-align:center;font-size:11px;}}.g{{color:#28a745;font-weight:bold;}}.r{{color:#dc3545;font-weight:bold;}}@media print{{body{{padding:10px;}}}}</style></head><body><h1>📊 گزارش حضور و غیاب</h1><p style="text-align:center;">{today_j}</p>'''
    for sh, sections in groups.items():
        html += f'<div class="sh">🕒 {sh}</div>'
        for sec, items in sections.items():
            html += f'<div class="sec">🏥 بخش: {sec} ({len(items)} مورد)</div><table><tr><th>تاریخ</th><th>پرسنل</th><th>وضعیت</th><th>ریز شیفت</th><th>زمان</th><th>توضیحات</th></tr>'
            for r in items:
                sc = 'g' if r.get('status') == 'حاضر' else 'r'
                html += f'<tr><td>{r.get("date_display")}</td><td>{r.get("person_name")}</td><td class="{sc}">{r.get("status")}</td><td>{r.get("rizshift_display","-")}</td><td>{r.get("time_display")}</td><td>{r.get("description","-")}</td></tr>'
            html += '</table>'
    html += '<script>window.print();</script></body></html>'
    return html


def api_print_person(request_args):
    import jdatetime
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('shift',''), request_args.get('section',''), request_args.get('status',''), request_args.get('search',''), page=1, per_page=9999)
    today_j = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    data = d['data']

    groups = {}
    for r in data:
        pn = r.get('person_name', 'نامشخص')
        if pn not in groups: groups[pn] = []
        groups[pn].append(r)

    html = f'''<!DOCTYPE html><html dir="rtl">
<head><meta charset="UTF-8">
<style>
    body{{font-family:Tahoma; padding:25px;}}
    h1{{color:#1e3a8a; text-align:center;}}
    .ph{{background:#1e3a8a; color:white; padding:12px; margin-top:20px; border-radius:8px; font-size:16px; text-align:center;}}
    .summary{{display:flex; gap:10px; flex-wrap:wrap; padding:10px; background:#e8f4f8; border-radius:8px; margin:8px 0;}}
    .shift-summary{{display:flex; gap:10px; flex-wrap:wrap; padding:10px; background:#fff3cd; border-radius:8px; margin:8px 0;}}
    table{{width:100%; border-collapse:collapse; margin-bottom:15px;}}
    th{{background:#e2e8f0; padding:8px; font-size:11px;}}
    td{{padding:7px; border:1px solid #ddd; text-align:center; font-size:11px;}}
    .total-shifts{{background:#d4edda; padding:15px; margin:20px 0; border-radius:8px; border-right:5px solid #28a745;}}
    @media print{{
        body{{padding:10px;}}
        div[style*="page-break-after"]{{page-break-after:always;}}
    }}
</style></head>
<body>
<h1>👥 گزارش تفکیکی پرسنل</h1>
<p style="text-align:center;">{today_j}</p>
'''
    overall_shift_counts = {}
    for pn, items in groups.items():
        sc = {}
        shift_counts = {}
        for r in items:
            k = r.get('status',''); sc[k] = sc.get(k,0)+1
            sn = r.get('rizshift_display') or r.get('shift_name') or 'نامشخص'
            shift_counts[sn] = shift_counts.get(sn, 0) + 1

        for sn, cnt in shift_counts.items():
            overall_shift_counts[sn] = overall_shift_counts.get(sn, 0) + cnt

        html += f'<div class="ph">👤 {pn}</div>'
        html += '<div class="summary">'
        for k,v in sc.items():
            html += f'<span style="background:white;padding:5px 12px;border-radius:15px;border:1px solid #ddd;font-size:12px;"><strong>{k}:</strong> {v}</span>'
        html += '</div>'
        if shift_counts:
            html += '<div class="shift-summary"><strong style="color:#856404;">📋 انواع شیفت:</strong>'
            for sn, cnt in shift_counts.items():
                html += f'<span><strong>{sn}:</strong> {cnt}</span>'
            html += '</div>'
        html += '<table><tr><th>تاریخ</th><th>بخش</th><th>شیفت</th><th>وضعیت</th><th>زمان</th><th>توضیحات</th></tr>'
        for r in items:
            shift_display = r.get('rizshift_display') or r.get('shift_name')
            html += f'<tr><td>{r.get("date_display")}</td><td>{r.get("section_name")}</td><td>{shift_display}</td><td>{r.get("status")}</td><td>{r.get("time_display")}</td><td>{r.get("description","-")}</td></tr>'
        html += '</table><div style="page-break-after:always;"></div>'

    if overall_shift_counts:
        html += '<div class="total-shifts"><h3 style="color:#155724;margin-top:0;">📊 جمع‌بندی کلی شیفت‌ها</h3><div style="display:flex; gap:15px; flex-wrap:wrap;">'
        for sn, cnt in overall_shift_counts.items():
            html += f'<span style="background:white;padding:8px 15px;border-radius:20px;box-shadow:0 1px 4px rgba(0,0,0,0.1);"><strong>{sn}:</strong> <span style="font-size:18px;font-weight:bold;color:#28a745;">{cnt}</span></span>'
        html += '</div></div>'

    html += '<script>window.print();</script></body></html>'
    return html


def _generate_ai_summary(data):
    if not data:
        return {}
    total = len(data)
    status_counts = {}
    for r in data:
        st = r.get('status','')
        status_counts[st] = status_counts.get(st, 0) + 1

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

    dept_risk = {}
    for r in data:
        dept = r.get('section_name', 'نامشخص')
        if dept not in dept_risk: dept_risk[dept] = {'total':0, 'absent':0}
        dept_risk[dept]['total'] += 1
        if r.get('status') != 'حاضر':
            dept_risk[dept]['absent'] += 1

    shift_stats = {}
    for r in data:
        sh = r.get('shift_name', 'نامشخص')
        if sh not in shift_stats: shift_stats[sh] = {'total':0, 'absent':0}
        shift_stats[sh]['total'] += 1
        if r.get('status') != 'حاضر':
            shift_stats[sh]['absent'] += 1

    return {
        'total_records': total,
        'status_distribution': status_counts,
        'present_rate': round(status_counts.get('حاضر',0)/total*100,1) if total else 0,
        'moving_average': dict(zip(sorted_days[-10:], moving_avg[-10:])),
        'outliers': outliers,
        'dept_risk': {k: {'rate': round(v['absent']/v['total']*100,1)} for k,v in dept_risk.items() if v['total']},
        'shift_stats': shift_stats
    }


def internal_attendance_analysis(summary):
    lines = []
    lines.append(f"🔢 **تعداد کل رکوردها:** {summary['total_records']}")
    lines.append(f"📊 **نرخ حضور:** {summary['present_rate']}%")
    if summary.get('status_distribution'):
        lines.append("📋 **توزیع وضعیت‌ها:**")
        for k,v in summary['status_distribution'].items():
            lines.append(f"   - {k}: {v}")
    if summary.get('moving_average'):
        lines.append(f"📈 **میانگین متحرک ۷ روزه (۱۰ روز اخیر):** {list(summary['moving_average'].values())}")
    if summary.get('outliers'):
        lines.append(f"⚠️ **نقاط پرت (انحراف > ۲):** {len(summary['outliers'])} روز")
        for o in summary['outliers'][:3]:
            lines.append(f"   - {o['date']}: {o['value']} رکورد (Z-score: {o['z_score']})")
    if summary.get('dept_risk'):
        lines.append("🚨 **ریسک بخش‌ها (درصد غیرحاضر):**")
        for k,v in sorted(summary['dept_risk'].items(), key=lambda x: x[1]['rate'], reverse=True):
            emoji = '🔴' if v['rate']>30 else '🟠' if v['rate']>15 else '🟢'
            lines.append(f"   {emoji} {k}: {v['rate']}%")
    lines.append("💡 **پیشنهادات:**")
    if summary['present_rate'] < 85:
        lines.append("- نرخ حضور پایین است؛ بررسی علل غیبت ضروری است.")
    lines.append("- پایش روزهای پرت و تطبیق با رویدادها.")
    return "\n".join(lines)


def api_analyze(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('shift',''), request_args.get('section',''),
                    request_args.get('status',''), request_args.get('search',''),
                    page=1, per_page=9999)
    data = d['data']
    if not data:
        return {'success': False, 'message': 'داده‌ای برای تحلیل وجود ندارد'}
    summary = _generate_ai_summary(data)
    deepseek_key = request_args.get('deepseek_key', '').strip()
    if deepseek_key:
        pass
    analysis = internal_attendance_analysis(summary)
    return {'success': True, 'analysis': analysis, 'source_name': 'تحلیل داخلی'}
    
