"""
گزارش آنکالی پزشکان – نسخه ارتقاءیافته
نمودارهای تعاملی Chart.js، تحلیل عمیق آماری، لود سریع
"""

from models.database import query
import json
import requests
from datetime import datetime as dt
import jdatetime
from flask import send_file
import io
from openpyxl import Workbook
from utils.formatters import format_date_display
import math


def get_ankal_report(user):
    """صفحه اصلی گزارش آنکال پزشکان"""

    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    month_ago = (jdatetime.date.today() - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")

    # تخصص‌ها (سریع)
    specialties = query("""
        SELECT DISTINCT t.ID_onvan_takhasos, t.nam_takhasos
        FROM tbl_ankal a
        JOIN tbl_onvan_takhasos t ON a.nam_takhasos = t.ID_onvan_takhasos
        ORDER BY t.nam_takhasos
    """, fetch_all=True) or []
    spec_opts = '<option value="">همه تخصص‌ها</option>' + ''.join(
        f'<option value="{s["ID_onvan_takhasos"]}">{s["nam_takhasos"]}</option>' for s in specialties)

    # شیفت‌ها (سریع)
    shift_list = query("SELECT DISTINCT s.ID_shift, s.tarkib FROM shift_namt s ORDER BY s.tarkib", fetch_all=True) or []
    shift_opts = '<option value="">همه شیفت‌ها</option>' + ''.join(
        f'<option value="{s["ID_shift"]}">{s["tarkib"]}</option>' for s in shift_list)

    # آمار اولیه خالی
    stats = {'total': 0, 'responded': 0, 'no_response': 0, 'response_rate': 0}
    table_html = '<tr><td colspan="8" class="empty">در حال بارگذاری...</td></tr>'
    dash_html = '<div class="empty">در حال بارگذاری نمودارها...</div>'

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>گزارش آنکال پزشکان</title>
<script src="/static/js/chart.umd.min.js"></script>
<style>
    :root {{ --primary: #0f766e; --primary-light: #14b8a6; --green: #10b981; --red: #ef4444; --yellow: #f59e0b; --gray: #64748b; --l-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9; --white: #fff; --r: 12px; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial; direction:rtl; background:var(--bg); color:#1e293b; }}
    .container {{ max-width:1400px; margin:0 auto; padding:16px; }}
    
    .header {{ background:linear-gradient(135deg,#0f766e,#14b8a6); color:white; border-radius:var(--r); padding:18px 24px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 6px 20px rgba(15,118,110,.25); }}
    .header h2 {{ font-size:20px; }}
    .header a {{ color:white; text-decoration:none; padding:7px 14px; border:1.5px solid rgba(255,255,255,.4); border-radius:8px; font-size:12px; }}

    .kpi {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:14px; }}
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
    .btn-teal {{ background:var(--primary); color:white; }}
    .btn-grn {{ background:var(--green); color:white; }}
    .btn-amb {{ background:var(--yellow); color:white; }}
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
    tr:hover td {{ background:#f0fdfa; }}

    .badge {{ padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; display:inline-block; color:white; }}
    .badge-ok {{ background:var(--green); }}
    .badge-no {{ background:var(--red); }}

    .charts {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
    .chart-box {{ background:white; border-radius:10px; padding:14px; border:1px solid var(--border); }}
    .chart-box h4 {{ margin-bottom:10px; font-size:13px; text-align:center; }}
    canvas {{ max-height:250px; }}

    .pagination {{ display:flex; justify-content:center; gap:10px; margin-top:15px; }}
    .bar {{ display:flex; gap:8px; justify-content:flex-end; margin-top:10px; }}
    .empty {{ text-align:center; padding:30px; color:var(--l-gray); }}

    .spinner {{ width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #0f766e; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .ai-analysis-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; line-height: 2; font-size: 14px; white-space: pre-wrap; }}

    /* Modal */
    .modal-overlay {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:1000; justify-content:center; align-items:flex-start; padding:20px; }}
    .modal-overlay.show {{ display:flex; }}
    .modal-content {{ background:white; border-radius:16px; padding:25px; width:90%; max-width:500px; max-height:85vh; overflow-y:auto; box-shadow:0 20px 60px rgba(0,0,0,0.3); }}
    .modal-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; padding-bottom:12px; border-bottom:2px solid var(--border); }}
    .modal-close {{ background:none; border:none; font-size:20px; cursor:pointer; color:var(--gray); }}

    @media (max-width:768px) {{ .kpi {{ grid-template-columns:repeat(2,1fr); }} .charts {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h2>📞 پایش و مدیریت آنکال پزشکان</h2>
        <a href="/module/reports">⬅️ بازگشت</a>
    </div>

    <div class="kpi">
        <div class="kpi-card"><div class="kpi-val" style="color:#0f766e;" id="k-total">{stats['total']}</div><div class="kpi-lbl">📋 کل تماس‌ها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#10b981;" id="k-responded">{stats['responded']}</div><div class="kpi-lbl">✅ پاسخگو</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#ef4444;" id="k-noresp">{stats['no_response']}</div><div class="kpi-lbl">❌ عدم پاسخ</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#2563eb;" id="k-rate">{stats['response_rate']}%</div><div class="kpi-lbl">📊 نرخ پاسخگویی</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ</label><input type="text" id="f-from" value="{month_ago}"></div>
            <div class="f-grp"><label>تا تاریخ</label><input type="text" id="f-to" value="{today_j}"></div>
            <div class="f-grp"><label>شیفت</label><select id="f-shift">{shift_opts}</select></div>
            <div class="f-grp"><label>تخصص</label><select id="f-spec">{spec_opts}</select></div>
            <div class="f-grp"><label>وضعیت پاسخ</label><select id="f-status">
                <option value="">همه</option><option value="1">پاسخگو</option><option value="0">عدم پاسخ</option>
            </select></div>
        </div>
        <div class="f-row">
            <div class="f-grp" style="flex:2;"><label>جستجوی نام پزشک</label><input type="text" id="f-search" placeholder="نام پزشک..."></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-teal" onclick="refresh(1)">🔍 اعمال فیلتر</button></div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab on" onclick="switchTab('dash')">📊 داشبورد</button>
        <button class="tab" onclick="switchTab('list')">📋 لیست آنکال‌ها</button>
        <button class="tab" onclick="switchTab('ai')">🤖 تحلیل هوشمند</button>
    </div>

    <div id="pan-dash" class="pan on">{dash_html}</div>

    <div id="pan-list" class="pan">
        <div class="tbl-wrap"><div class="tbl-scroll"><table>
            <thead><tr><th>کد</th><th>تاریخ</th><th>پزشک</th><th>تخصص</th><th>شیفت</th><th>وضعیت</th><th>زمان ثبت</th><th>توضیحات</th></tr></thead>
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
            <div class="card-title">🤖 تحلیل هوشمند آنکال</div>
            <div class="row" style="margin-bottom:15px;">
                <div class="form-group" style="flex:2;">
                    <label>🔑 کلید API دیپ‌سیک (اختیاری)</label>
                    <input type="text" id="deepseek-key" class="form-input" placeholder="sk-...">
                </div>
                <div class="form-group" style="flex:0 0 auto; align-self: flex-end;">
                    <button class="btn btn-teal" onclick="startAIAnalysis()">🔍 شروع تحلیل</button>
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
<div class="modal-overlay" id="detailModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>جزئیات آنکال <span id="modal-id"></span></h3>
            <button class="modal-close" onclick="closeModal()">✕</button>
        </div>
        <div id="modal-body"></div>
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
            spec: document.getElementById('f-spec').value,
            status: document.getElementById('f-status').value,
            shift: document.getElementById('f-shift').value,
            search: document.getElementById('f-search').value,
            page: page,
            per_page: 15
        }});
        const r = await fetch('/module/reports/ankal/data?'+p.toString());
        const d = await r.json();
        allData = d.data || [];
        const s = d.stats || {{}};

        document.getElementById('k-total').textContent = s.total||0;
        document.getElementById('k-responded').textContent = s.responded||0;
        document.getElementById('k-noresp').textContent = s.no_response||0;
        document.getElementById('k-rate').textContent = (s.response_rate||0)+'%';

        let rows = '';
        if (allData.length) {{
            allData.forEach(r => {{
                const statusBadge = r.no_rispons ? '<span class="badge badge-no">❌ عدم پاسخ</span>' : '<span class="badge badge-ok">✅ پاسخگو</span>';
                rows += `<tr onclick="showDetail(${{r.ID_ankal}})" style="cursor:pointer;">
                    <td>${{r.ID_ankal}}</td><td>${{r.date_display||''}}</td><td>${{r.doctor_name||''}}</td>
                    <td>${{r.specialty_name||''}}</td><td>${{r.shift_name||''}}</td>
                    <td>${{statusBadge}}</td><td>${{(r.zaman_sabt||'').substring(0,5)}}</td>
                    <td>${{r.tozihat||'-'}}</td>
                </tr>`;
            }});
        }} else {{
            rows = '<tr><td colspan="8" class="empty">داده‌ای یافت نشد</td></tr>';
        }}
        document.getElementById('tbl-body').innerHTML = rows;

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
        const cur = sel.value;
        sel.innerHTML = '<option value="">همه شیفت‌ها</option>';
        shifts.forEach(s => sel.innerHTML += `<option value="${{s[0]}}">${{s[1]}}</option>`);
        if (shifts.some(s => s[0] == cur)) sel.value = cur; else sel.value = '';
    }}

    function renderPagination() {{
        const container = document.getElementById('pagination');
        if (totalPages <= 1) {{ container.innerHTML = ''; return; }}
        let h = '';
        if (currentPage > 1) h += `<button class="btn btn-teal btn-xs" onclick="refresh(${{currentPage-1}})">« قبلی</button>`;
        h += `<span style="display:flex;align-items:center;font-size:13px;">صفحه ${{currentPage}} از ${{totalPages}}</span>`;
        if (currentPage < totalPages) h += `<button class="btn btn-teal btn-xs" onclick="refresh(${{currentPage+1}})">بعدی »</button>`;
        container.innerHTML = h;
    }}

    // ==================== نمودارهای Chart.js ====================
    function renderCharts(data) {{
        setTimeout(() => {{
            ['chart-spec','chart-shift','chart-trend','chart-risk'].forEach(id => {{
                const existing = Chart.getChart(id);
                if (existing) existing.destroy();
            }});

            if (!data.length) {{
                document.getElementById('pan-dash').innerHTML = '<div class="empty">داده‌ای نیست</div>';
                return;
            }}

            document.getElementById('pan-dash').innerHTML = `
                <div class="charts">
                    <div class="chart-box"><h4>🥧 توزیع تخصص‌ها</h4><canvas id="chart-spec"></canvas></div>
                    <div class="chart-box"><h4>📊 پاسخگویی بر اساس شیفت</h4><canvas id="chart-shift"></canvas></div>
                    <div class="chart-box"><h4>📈 روند تماس‌ها (۳۰ روز اخیر)</h4><canvas id="chart-trend"></canvas></div>
                    <div class="chart-box"><h4>🚨 امتیاز ریسک تخصص‌ها (درصد عدم پاسخ)</h4><canvas id="chart-risk"></canvas></div>
                </div>
            `;

            const colors = ['#0f766e','#14b8a6','#2dd4bf','#5eead4','#99f6e4'];

            // تخصص‌ها (pie)
            const sm={{}};
            data.forEach(r => {{ const k=r.specialty_name||'نامشخص'; sm[k]=(sm[k]||0)+1; }});
            new Chart(document.getElementById('chart-spec'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(sm),
                    datasets: [{{ data: Object.values(sm), backgroundColor: colors.slice(0, Object.keys(sm).length) }}]
                }}
            }});

            // شیفت‌ها (stacked bar)
            const shiftMap={{}};
            data.forEach(r => {{
                const k=r.shift_name||'نامشخص';
                if(!shiftMap[k]) shiftMap[k]={{responded:0,noresp:0}};
                r.no_rispons ? shiftMap[k].noresp++ : shiftMap[k].responded++;
            }});
            const shiftLabels = Object.keys(shiftMap);
            const respondedData = shiftLabels.map(k => shiftMap[k].responded);
            const norespData = shiftLabels.map(k => shiftMap[k].noresp);
            new Chart(document.getElementById('chart-shift'), {{
                type: 'bar',
                data: {{
                    labels: shiftLabels,
                    datasets: [
                        {{ label: 'پاسخگو', data: respondedData, backgroundColor: '#10b981' }},
                        {{ label: 'عدم پاسخ', data: norespData, backgroundColor: '#ef4444' }}
                    ]
                }},
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
                    datasets: [{{ label: 'تعداد تماس', data: sortedDays.map(([,v]) => v), borderColor: '#0f766e', tension: 0.3 }}]
                }},
                options: {{ responsive: true }}
            }});

            // امتیاز ریسک تخصص‌ها (bar, درصد عدم پاسخ)
            const riskMap={{}};
            data.forEach(r => {{
                const k=r.specialty_name||'نامشخص';
                if(!riskMap[k]) riskMap[k]={{total:0,noresp:0}};
                riskMap[k].total++;
                if(r.no_rispons) riskMap[k].noresp++;
            }});
            const riskLabels = Object.keys(riskMap);
            const riskData = riskLabels.map(k => {{
                const v = riskMap[k];
                return v.total ? Math.round((v.noresp/v.total)*100) : 0;
            }});
            const riskColors = riskData.map(v => v>30?'#ef4444':v>15?'#f59e0b':'#10b981');
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

    // ==================== مودال جزئیات ====================
    async function showDetail(id) {{
        try {{
            const r = await fetch('/module/reports/ankal/detail/'+id);
            const d = await r.json();
            if (!d.success) return;
            const rec = d.record;
            document.getElementById('modal-id').textContent = '#'+rec.ID_ankal;
            let html = `<p><strong>پزشک:</strong> ${{rec.doctor_name}}</p>
                <p><strong>تخصص:</strong> ${{rec.specialty_name}}</p>
                <p><strong>شیفت:</strong> ${{rec.shift_name}}</p>
                <p><strong>تاریخ:</strong> ${{rec.date_display}}</p>
                <p><strong>زمان ثبت:</strong> ${{(rec.zaman_sabt||'').substring(0,5)}}</p>
                <p><strong>وضعیت:</strong> ${{rec.no_rispons ? '❌ عدم پاسخ' : '✅ پاسخگو'}}</p>
                <p><strong>توضیحات:</strong> ${{rec.tozihat||'-'}}</p>`;
            document.getElementById('modal-body').innerHTML = html;
            document.getElementById('detailModal').classList.add('show');
        }} catch(e) {{ console.error(e); }}
    }}

    function closeModal() {{ document.getElementById('detailModal').classList.remove('show'); }}
    document.getElementById('detailModal').addEventListener('click', function(e) {{ if(e.target===this) closeModal(); }});

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
            spec: document.getElementById('f-spec').value,
            status: document.getElementById('f-status').value,
            shift: document.getElementById('f-shift').value,
            search: document.getElementById('f-search').value,
            deepseek_key: deepseekKey
        }});
        try {{
            const res = await fetch('/module/reports/ankal/analyze?' + params.toString());
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
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),spec:document.getElementById('f-spec').value,status:document.getElementById('f-status').value,shift:document.getElementById('f-shift').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/ankal/export?'+p.toString(),'_blank');
    }}

    function doPrint() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value}});
        window.open('/module/reports/ankal/print?'+p.toString(),'_blank');
    }}

    document.addEventListener('DOMContentLoaded', () => refresh(1));
</script>
</body>
</html>'''
    return html


def _fetch_data(d_from='', d_to='', spec='', status='', shift='', search='', page=1, per_page=15):
    """واکشی داده با فیلترها و صفحه‌بندی"""
    offset = (page - 1) * per_page

    base_join = """FROM tbl_ankal a
                   JOIN tbl_onvan_takhasos t ON a.nam_takhasos = t.ID_onvan_takhasos
                   JOIN tbl_person p ON a.nam_pezshk = p.ID_person
                   LEFT JOIN shift_namt s ON a.nam_shift = s.ID_shift
                   WHERE 1=1"""
    base_params = []

    if d_from:
        base_join += " AND a.dat_sabt >= %s"
        base_params.append(d_from)
    if d_to:
        base_join += " AND a.dat_sabt <= %s"
        base_params.append(d_to)
    if spec:
        base_join += " AND a.nam_takhasos = %s"
        base_params.append(spec)
    if search:
        base_join += " AND (p.nam LIKE %s OR p.famil LIKE %s)"
        base_params.extend([f'%{search}%'] * 2)

    if status == '1':
        base_join += " AND a.no_rispons = 0"
    elif status == '0':
        base_join += " AND a.no_rispons = 1"

    # کوئری داده‌ها
    data_sql = f"""SELECT a.ID_ankal, a.dat_sabt, a.zaman_sabt, a.no_rispons, a.tozihat,
                    CONCAT(p.nam, ' ', p.famil) AS doctor_name,
                    t.nam_takhasos AS specialty_name,
                    s.tarkib AS shift_name, s.ID_shift AS shift_id
                    {base_join}"""
    data_params = base_params.copy()
    if shift:
        data_sql += " AND a.nam_shift = %s"
        data_params.append(shift)
    data_sql += " ORDER BY a.ID_ankal DESC LIMIT %s OFFSET %s"
    data_params.extend([per_page, offset])

    # شمارش کل
    count_sql = f"SELECT COUNT(*) as total {base_join}"
    count_params = base_params.copy()
    if shift:
        count_sql += " AND a.nam_shift = %s"
        count_params.append(shift)

    # شیفت‌های موجود
    shifts_sql = f"SELECT DISTINCT s.ID_shift, s.tarkib {base_join} ORDER BY s.tarkib"
    shifts_params = base_params.copy()

    data = query(data_sql, data_params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0
    available_shifts = [(r['ID_shift'], r['tarkib']) for r in (query(shifts_sql, shifts_params, fetch_all=True) or [])]

    for row in data:
        row['date_display'] = format_date_display(row.get('dat_sabt'))
        ts = str(row.get('zaman_sabt', ''))
        row['zaman_sabt'] = ts.split(' ')[-1][:5] if ' ' in ts else ts[:5]

    # محاسبه آمار کلی (بر اساس کل رکوردهای فیلترشده)
    responded = sum(1 for r in data if r.get('no_rispons') == 0)
    no_response = total - responded
    response_rate = round(responded / total * 100, 1) if total > 0 else 0

    stats = {
        'total': total,
        'responded': responded,
        'no_response': no_response,
        'response_rate': response_rate
    }

    # صفحه‌بندی
    page_data = data[offset:offset+per_page] if per_page else data

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
    rows = []
    for r in data:
        status_badge = '<span class="badge badge-no">❌ عدم پاسخ</span>' if r.get('no_rispons') else '<span class="badge badge-ok">✅ پاسخگو</span>'
        rows.append(f'''<tr onclick="showDetail({r['ID_ankal']})" style="cursor:pointer;">
            <td>{r['ID_ankal']}</td><td>{r.get('date_display','')}</td><td>{r.get('doctor_name','')}</td>
            <td>{r.get('specialty_name','')}</td><td>{r.get('shift_name','')}</td>
            <td>{status_badge}</td><td>{r.get('zaman_sabt','')}</td><td>{r.get('tozihat','-')}</td>
        </tr>''')
    return ''.join(rows)


def _build_dashboard(data):
    return '<div class="empty">در حال بارگذاری نمودارها...</div>'


# ==================== API Functions ====================

def api_data(request_args):
    return _fetch_data(
        request_args.get('from',''), request_args.get('to',''),
        request_args.get('spec',''), request_args.get('status',''),
        request_args.get('shift',''), request_args.get('search',''),
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 15, type=int)
    )


def api_export(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('spec',''), request_args.get('status',''),
                    request_args.get('shift',''), request_args.get('search',''),
                    page=1, per_page=9999)
    wb = Workbook()
    ws = wb.active
    ws.title = "گزارش آنکال"
    headers = ['کد', 'تاریخ', 'پزشک', 'تخصص', 'شیفت', 'وضعیت', 'زمان ثبت', 'توضیحات']
    ws.append(headers)
    for r in d['data']:
        ws.append([r['ID_ankal'], r.get('date_display',''), r.get('doctor_name',''),
                   r.get('specialty_name',''), r.get('shift_name',''),
                   'پاسخگو' if not r.get('no_rispons') else 'عدم پاسخ',
                   r.get('zaman_sabt',''), r.get('tozihat','')])
    ws2 = wb.create_sheet("آمار")
    ws2.append(['شاخص', 'مقدار'])
    s = d['stats']
    for k,v in [('کل تماس‌ها',s['total']), ('پاسخگو',s['responded']),
                ('عدم پاسخ',s['no_response']), ('نرخ پاسخگویی',f"{s['response_rate']}%")]:
        ws2.append([k,v])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='ankal_report.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def api_print(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    shift=request_args.get('shift',''), page=1, per_page=9999)
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    data = d['data']
    groups = {}
    for r in data:
        shift = r.get('shift_name','نامشخص')
        if shift not in groups:
            groups[shift] = []
        groups[shift].append(r)

    html = f'''<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><style>
        body{{font-family:Tahoma;padding:20px;}}h1{{color:#0f766e;text-align:center;}}
        .sg{{margin:20px 0;border:1px solid #ddd;border-radius:10px;overflow:hidden;}}
        .sh{{background:#0f766e;color:white;padding:10px;font-weight:bold;}}
        table{{width:100%;border-collapse:collapse;}}
        th{{background:#e2e8f0;padding:8px;}}td{{padding:6px;border:1px solid #ddd;text-align:center;font-size:11px;}}
        .ok{{color:#10b981;font-weight:bold;}} .no{{color:#ef4444;font-weight:bold;}}
        @media print{{body{{padding:0;}}}}
    </style></head><body><h1>📞 گزارش آنکال پزشکان - {today_j}</h1>'''
    for shift, items in groups.items():
        html += f'<div class="sg"><div class="sh">🕒 {shift} - {len(items)} مورد</div><table><tr><th>پزشک</th><th>تخصص</th><th>وضعیت</th><th>زمان</th><th>توضیحات</th></tr>'
        for r in items:
            status = '<span class="ok">✅ پاسخگو</span>' if not r['no_rispons'] else '<span class="no">❌ عدم پاسخ</span>'
            html += f"<tr><td>{r.get('doctor_name','')}</td><td>{r.get('specialty_name','')}</td><td>{status}</td><td>{r.get('zaman_sabt','')}</td><td>{r.get('tozihat','-')}</td></tr>"
        html += '</table></div>'
    html += '<script>window.print();</script></body></html>'
    return html


def api_detail(record_id):
    rec = query("""
        SELECT a.*, CONCAT(p.nam, ' ', p.famil) AS doctor_name,
               t.nam_takhasos AS specialty_name, s.tarkib AS shift_name
        FROM tbl_ankal a
        JOIN tbl_person p ON a.nam_pezshk = p.ID_person
        JOIN tbl_onvan_takhasos t ON a.nam_takhasos = t.ID_onvan_takhasos
        LEFT JOIN shift_namt s ON a.nam_shift = s.ID_shift
        WHERE a.ID_ankal = %s
    """, (record_id,), fetch_one=True)
    if not rec:
        return {'success': False}
    for k in list(rec.keys()):
        if isinstance(rec[k], bytearray):
            rec[k] = rec[k].decode('utf-8')
    d = str(rec.get('dat_sabt', ''))
    rec['date_display'] = f"{d[:4]}/{d[4:6]}/{d[6:]}" if len(d) == 8 else d
    return {'success': True, 'record': rec}


def _generate_ai_summary(data):
    """خلاصه آماری پیشرفته برای تحلیل هوشمند"""
    if not data:
        return {}
    total = len(data)
    responded = sum(1 for r in data if not r.get('no_rispons'))
    response_rate = round(responded / total * 100, 1) if total else 0

    specialties = {}
    for r in data:
        sp = r.get('specialty_name', 'نامشخص')
        specialties[sp] = specialties.get(sp, 0) + 1

    shifts = {}
    for r in data:
        sh = r.get('shift_name', 'نامشخص')
        if sh not in shifts:
            shifts[sh] = {'total': 0, 'noresp': 0}
        shifts[sh]['total'] += 1
        if r.get('no_rispons'):
            shifts[sh]['noresp'] += 1

    daily_counts = {}
    for r in data:
        day = r.get('date_display', '')[:10]
        daily_counts[day] = daily_counts.get(day, 0) + 1
    sorted_days = sorted(daily_counts.keys())
    values = [daily_counts[d] for d in sorted_days]

    moving_avg = []
    for i in range(len(values)):
        window = values[max(0, i-6):i+1]
        moving_avg.append(round(sum(window) / len(window), 1))

    mean_val = sum(values) / len(values) if values else 0
    std_val = math.sqrt(sum((v - mean_val) ** 2 for v in values) / len(values)) if len(values) > 1 else 0
    outliers = []
    for i, v in enumerate(values):
        if std_val > 0:
            z = abs(v - mean_val) / std_val
            if z > 2:
                outliers.append({'date': sorted_days[i], 'value': v, 'z_score': round(z, 2)})

    risk_scores = {}
    for r in data:
        sp = r.get('specialty_name', 'نامشخص')
        if sp not in risk_scores:
            risk_scores[sp] = {'total': 0, 'noresp': 0}
        risk_scores[sp]['total'] += 1
        if r.get('no_rispons'):
            risk_scores[sp]['noresp'] += 1

    return {
        'total_calls': total,
        'response_rate': response_rate,
        'specialties': specialties,
        'shifts': shifts,
        'no_response_count': total - responded,
        'moving_average': dict(zip(sorted_days[-10:], moving_avg[-10:])),
        'outliers': outliers,
        'risk_scores': {k: {'rate': round(v['noresp']/v['total']*100, 1)} for k, v in risk_scores.items() if v['total']}
    }


def internal_ankal_analysis(summary):
    lines = []
    lines.append(f"🔢 **تعداد کل تماس‌های آنکال:** {summary['total_calls']}")
    lines.append(f"📊 **نرخ پاسخگویی:** {summary['response_rate']}%")
    if summary.get('specialties'):
        lines.append("🩺 **فراوانی بر اساس تخصص:**")
        for k, v in sorted(summary['specialties'].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"   - {k}: {v}")
    if summary.get('shifts'):
        lines.append("🕒 **توزیع در شیفت‌ها:**")
        for k, v in summary['shifts'].items():
            rate = round((1 - v['noresp']/v['total'])*100, 1) if v['total'] else 0
            lines.append(f"   - {k}: {v['total']} تماس (پاسخگویی {rate}%)")
    if summary.get('moving_average'):
        lines.append(f"📈 **میانگین متحرک ۷ روزه (۱۰ روز اخیر):** {list(summary['moving_average'].values())}")
    if summary.get('outliers'):
        lines.append(f"⚠️ **نقاط پرت (انحراف بیش از ۲ برابر نرمال):** {len(summary['outliers'])} روز")
        for o in summary['outliers'][:3]:
            lines.append(f"   - {o['date']}: {o['value']} تماس (Z-score: {o['z_score']})")
    if summary.get('risk_scores'):
        lines.append("🚨 **امتیاز ریسک تخصص‌ها (نرخ عدم پاسخ):**")
        for k, v in sorted(summary['risk_scores'].items(), key=lambda x: x[1]['rate'], reverse=True):
            emoji = '🔴' if v['rate'] > 30 else '🟠' if v['rate'] > 15 else '🟢'
            lines.append(f"   {emoji} {k}: {v['rate']}%")
    lines.append("💡 **پیشنهادات اجرایی:**")
    if summary['response_rate'] < 80:
        lines.append("- نرخ پاسخگویی پایین است؛ بازنگری در سیستم فراخوان ضروری است.")
    if any(v['rate'] > 30 for v in summary.get('risk_scores', {}).values()):
        lines.append("- تخصص‌های با ریسک بالا نیاز به پشتیبان‌گیری فوری دارند.")
    lines.append("- پایش مستمر روزهای پرت و تطبیق با رویدادهای بیمارستان پیشنهاد می‌شود.")
    return "\n".join(lines)


def deepseek_ankal_analysis(api_key, summary):
    if not api_key or len(api_key.strip()) < 10:
        return None
    prompt = f"""شما یک مدیر بیمارستان هستید. این داده‌های آنکال پزشکان را تحلیل کنید و پاسخ کاملاً فارسی دهید:
{json.dumps(summary, indent=2, ensure_ascii=False)}
تحلیل شامل: وضعیت پاسخگویی، الگوها، نقاط پرت، امتیاز ریسک و پیشنهادات اجرایی (حداقل ۳ مورد)."""
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [
                {"role": "system", "content": "شما یک تحلیلگر مدیریت بیمارستان هستید."},
                {"role": "user", "content": prompt}
            ], "temperature": 0.7, "max_tokens": 1500},
            timeout=20)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except:
        pass
    return None


def api_analyze(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('spec',''), request_args.get('status',''),
                    request_args.get('shift',''), request_args.get('search',''),
                    page=1, per_page=9999)
    data = d['data']
    if not data:
        return {'success': False, 'message': 'داده‌ای برای تحلیل وجود ندارد'}
    summary = _generate_ai_summary(data)
    deepseek_key = request_args.get('deepseek_key', '').strip()
    if deepseek_key:
        analysis = deepseek_ankal_analysis(deepseek_key, summary)
        if analysis:
            return {'success': True, 'analysis': analysis, 'source_name': 'DeepSeek AI'}
    analysis = internal_ankal_analysis(summary)
    return {'success': True, 'analysis': analysis, 'source_name': 'تحلیل داخلی'}
    
    