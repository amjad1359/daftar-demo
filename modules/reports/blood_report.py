"""
گزارش هموویژولانس (تزریق خون و فرآورده‌ها) – نسخه ارتقاءیافته
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


def get_blood_report(user):
    """صفحه اصلی گزارش خون"""

    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    month_ago = (jdatetime.date.today() - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")

    blood_groups = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-", "Unknown"]
    bg_opts = '<option value="">همه گروه‌های خونی</option>' + ''.join(f'<option value="{bg}">{bg}</option>' for bg in blood_groups)

    product_types = query("SELECT DISTINCT nam_faravardeh FROM tbl_blood_faravardeh ORDER BY nam_faravardeh", fetch_all=True) or []
    prod_opts = '<option value="">همه فرآورده‌ها</option>' + ''.join(f'<option value="{p["nam_faravardeh"]}">{p["nam_faravardeh"]}</option>' for p in product_types)

    department_list = query("SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh", fetch_all=True) or []
    dept_opts = '<option value="">همه بخش‌ها</option>' + ''.join(f'<option value="{d["ID_nam_bakhsh"]}">{d["nam_bakhsh"]}</option>' for d in department_list)

    shift_list = query("SELECT DISTINCT s.ID_shift, s.tarkib FROM shift_namt s ORDER BY s.tarkib", fetch_all=True) or []
    shift_opts = '<option value="">همه شیفت‌ها</option>' + ''.join(f'<option value="{s["ID_shift"]}">{s["tarkib"]}</option>' for s in shift_list)

    # آمار اولیه خالی
    stats = {'total': 0, 'total_units': 0, 'unique_patients': 0, 'unique_depts': 0}
    table_html = '<tr><td colspan="10" class="empty">در حال بارگذاری...</td></tr>'
    dash_html = '<div class="empty">در حال بارگذاری نمودارها...</div>'

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>گزارش خون و فرآورده‌ها</title>
<script src="/static/js/chart.umd.min.js"></script>
<style>
    :root {{ --red: #b91c1c; --red-l: #dc2626; --green: #10b981; --gray: #64748b; --l-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9; --white: #fff; --r: 12px; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial; direction:rtl; background:var(--bg); color:#1e293b; }}
    .container {{ max-width:1400px; margin:0 auto; padding:16px; }}
    
    .header {{ background:linear-gradient(135deg,#991b1b,#dc2626); color:white; border-radius:var(--r); padding:18px 24px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 6px 20px rgba(153,27,27,.25); }}
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

    .spinner {{ width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #b91c1c; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .ai-analysis-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; line-height: 2; font-size: 14px; white-space: pre-wrap; }}

    /* Modal */
    .modal-overlay {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:1000; justify-content:center; align-items:flex-start; padding:20px; }}
    .modal-overlay.show {{ display:flex; }}
    .modal-content {{ background:white; border-radius:16px; padding:25px; width:90%; max-width:650px; max-height:85vh; overflow-y:auto; box-shadow:0 20px 60px rgba(0,0,0,0.3); }}
    .modal-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; padding-bottom:12px; border-bottom:2px solid var(--border); }}
    .modal-close {{ background:none; border:none; font-size:20px; cursor:pointer; color:var(--gray); }}

    @media (max-width:768px) {{ .kpi {{ grid-template-columns:repeat(2,1fr); }} .charts {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h2>🩸 سامانه جامع گزارشات هموویژولانس</h2>
        <a href="/module/reports">⬅️ بازگشت</a>
    </div>

    <div class="kpi">
        <div class="kpi-card"><div class="kpi-val" style="color:#b91c1c;" id="k-total">{stats['total']}</div><div class="kpi-lbl">📋 کل ترانسفوزیون‌ها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#2563eb;" id="k-units">{stats['total_units']}</div><div class="kpi-lbl">🩸 مجموع واحدها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#10b981;" id="k-patients">{stats['unique_patients']}</div><div class="kpi-lbl">👤 بیماران منحصربه‌فرد</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#f59e0b;" id="k-depts">{stats['unique_depts']}</div><div class="kpi-lbl">🏥 بخش‌های درگیر</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ</label><input type="text" id="f-from" value="{month_ago}"></div>
            <div class="f-grp"><label>تا تاریخ</label><input type="text" id="f-to" value="{today_j}"></div>
            <div class="f-grp"><label>شیفت</label><select id="f-shift">{shift_opts}</select></div>
            <div class="f-grp"><label>بخش</label><select id="f-dept">{dept_opts}</select></div>
            <div class="f-grp"><label>گروه خونی بیمار</label><select id="f-blood-group">{bg_opts}</select></div>
        </div>
        <div class="f-row">
            <div class="f-grp"><label>نوع فرآورده</label><select id="f-product">{prod_opts}</select></div>
            <div class="f-grp"><label>واکنش</label><select id="f-reaction"><option value="">همه</option><option value="1">دارای واکنش</option><option value="0">بدون واکنش</option></select></div>
            <div class="f-grp" style="flex:2;"><label>جستجو (نام بیمار / شماره پرونده)</label><input type="text" id="f-search" placeholder="جستجو..."></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-red" onclick="refresh(1)">🔍 اعمال فیلتر</button></div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab on" onclick="switchTab('dash')">📊 داشبورد</button>
        <button class="tab" onclick="switchTab('list')">📋 لیست ترانسفوزیون‌ها</button>
        <button class="tab" onclick="switchTab('ai')">🤖 تحلیل هوشمند</button>
    </div>

    <div id="pan-dash" class="pan on">{dash_html}</div>

    <div id="pan-list" class="pan">
        <div class="tbl-wrap"><div class="tbl-scroll"><table>
            <thead><tr><th>کد</th><th>تاریخ</th><th>بیمار</th><th>پرونده</th><th>بخش</th><th>شیفت</th><th>گروه خونی</th><th>تعداد فرآورده</th><th>واحد</th><th>واکنش</th></tr></thead>
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
            <div class="card-title">🤖 تحلیل هوشمند هموویژولانس</div>
            <div class="row" style="margin-bottom:15px;">
                <div class="form-group" style="flex:2;">
                    <label>🔑 کلید API دیپ‌سیک (اختیاری)</label>
                    <input type="text" id="deepseek-key" class="form-input" placeholder="sk-...">
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

<!-- مودال جزئیات -->
<div class="modal-overlay" id="detailModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3>جزئیات ترانسفوزیون <span id="modal-id"></span></h3>
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
            dept: document.getElementById('f-dept').value,
            blood_group: document.getElementById('f-blood-group').value,
            product: document.getElementById('f-product').value,
            reaction: document.getElementById('f-reaction').value,
            shift: document.getElementById('f-shift').value,
            search: document.getElementById('f-search').value,
            page: page,
            per_page: 15
        }});
        const r = await fetch('/module/reports/blood/data?'+p.toString());
        const d = await r.json();
        allData = d.data || [];
        const s = d.stats || {{}};

        document.getElementById('k-total').textContent = s.total||0;
        document.getElementById('k-units').textContent = s.total_units||0;
        document.getElementById('k-patients').textContent = s.unique_patients||0;
        document.getElementById('k-depts').textContent = s.unique_depts||0;

        let rows = '';
        if (allData.length) {{
            allData.forEach(r => {{
                rows += `<tr onclick="showDetail(${{r.ID_blood}})" style="cursor:pointer;">
                    <td>${{r.ID_blood}}</td><td>${{r.date_display||''}}</td><td>${{r.nam_bimar||''}}</td>
                    <td>${{r.shomar_parvandeh||''}}</td><td>${{r.dept_name||''}}</td><td>${{r.shift_name||''}}</td>
                    <td>${{r.groh_khoni_bimar||''}}</td><td>${{r.product_count||0}}</td>
                    <td>${{r.total_units||0}}</td><td>${{r.has_reaction ? '⚠️ دارد' : '✅ خیر'}}</td>
                </tr>`;
            }});
        }} else {{
            rows = '<tr><td colspan="10" class="empty">داده‌ای یافت نشد</td></tr>';
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
        if (currentPage > 1) h += `<button class="btn btn-red btn-xs" onclick="refresh(${{currentPage-1}})">« قبلی</button>`;
        h += `<span style="display:flex;align-items:center;font-size:13px;">صفحه ${{currentPage}} از ${{totalPages}}</span>`;
        if (currentPage < totalPages) h += `<button class="btn btn-red btn-xs" onclick="refresh(${{currentPage+1}})">بعدی »</button>`;
        container.innerHTML = h;
    }}

    // ==================== نمودارهای Chart.js ====================
    function renderCharts(data) {{
        setTimeout(() => {{
            ['chart-bg','chart-dept','chart-product','chart-reaction','chart-trend'].forEach(id => {{
                const existing = Chart.getChart(id);
                if (existing) existing.destroy();
            }});

            if (!data.length) {{
                document.getElementById('pan-dash').innerHTML = '<div class="empty">داده‌ای نیست</div>';
                return;
            }}

            document.getElementById('pan-dash').innerHTML = `
                <div class="charts">
                    <div class="chart-box"><h4>🥧 توزیع گروه‌های خونی</h4><canvas id="chart-bg"></canvas></div>
                    <div class="chart-box"><h4>📊 ترانسفوزیون به تفکیک بخش</h4><canvas id="chart-dept"></canvas></div>
                    <div class="chart-box"><h4>📦 مجموع واحدهای فرآورده</h4><canvas id="chart-product"></canvas></div>
                    <div class="chart-box"><h4>⚠️ وضعیت واکنش</h4><canvas id="chart-reaction"></canvas></div>
                    <div class="chart-box"><h4>📈 روند روزانه ترانسفوزیون (۳۰ روز)</h4><canvas id="chart-trend"></canvas></div>
                </div>
            `;

            const colors = ['#b91c1c','#dc2626','#f87171','#fca5a5','#fecaca'];

            // گروه خونی (pie)
            const bgm={{}};
            data.forEach(r => {{ const k=r.groh_khoni_bimar||'نامشخص'; bgm[k]=(bgm[k]||0)+1; }});
            new Chart(document.getElementById('chart-bg'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(bgm),
                    datasets: [{{ data: Object.values(bgm), backgroundColor: colors.slice(0, Object.keys(bgm).length) }}]
                }}
            }});

            // بخش‌ها (bar)
            const dm={{}};
            data.forEach(r => {{ const k=r.dept_name||'نامشخص'; dm[k]=(dm[k]||0)+1; }});
            new Chart(document.getElementById('chart-dept'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(dm),
                    datasets: [{{ data: Object.values(dm), backgroundColor: '#b91c1c' }}]
                }},
                options: {{ responsive: true }}
            }});

            // فرآورده‌ها (bar, مجموع واحد)
            const pm={{}};
            data.forEach(r => {{
                if(r.products) r.products.forEach(p => {{
                    const k=p.nam_faravardeh||'نامشخص';
                    pm[k]=(pm[k]||0)+(p.teda_vahed||1);
                }});
            }});
            new Chart(document.getElementById('chart-product'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(pm),
                    datasets: [{{ data: Object.values(pm), backgroundColor: '#dc2626' }}]
                }},
                options: {{ responsive: true }}
            }});

            // واکنش (doughnut)
            const rm={{}};
            data.forEach(r => {{ const k=r.has_reaction ? 'واکنش دارد' : 'بدون واکنش'; rm[k]=(rm[k]||0)+1; }});
            new Chart(document.getElementById('chart-reaction'), {{
                type: 'doughnut',
                data: {{
                    labels: Object.keys(rm),
                    datasets: [{{ data: Object.values(rm), backgroundColor: ['#ef4444','#10b981'] }}]
                }}
            }});

            // روند روزانه (line)
            const daily={{}};
            data.forEach(r => {{ const d=r.date_display||''; daily[d]=(daily[d]||0)+1; }});
            const sortedDays = Object.entries(daily).sort((a,b) => a[0].localeCompare(b[0])).slice(-30);
            new Chart(document.getElementById('chart-trend'), {{
                type: 'line',
                data: {{
                    labels: sortedDays.map(([k]) => k.substring(5)),
                    datasets: [{{ label: 'تعداد ترانسفوزیون', data: sortedDays.map(([,v]) => v), borderColor: '#b91c1c', tension: 0.3 }}]
                }},
                options: {{ responsive: true }}
            }});
        }}, 50);
    }}

    // ==================== مودال جزئیات ====================
    async function showDetail(id) {{
        try {{
            const r = await fetch('/module/reports/blood/detail/'+id);
            const d = await r.json();
            if (!d.success) return;
            const rec = d.record;
            document.getElementById('modal-id').textContent = '#'+rec.ID_blood;
            let html = `<p><strong>بیمار:</strong> ${{rec.nam_bimar}}</p>
                <p><strong>پرونده:</strong> ${{rec.shomar_parvandeh||'-'}}</p>
                <p><strong>بخش:</strong> ${{rec.dept_name}}</p>
                <p><strong>شیفت:</strong> ${{rec.shift_name}}</p>
                <p><strong>گروه خونی بیمار:</strong> ${{rec.groh_khoni_bimar}}</p>
                <p><strong>توضیحات واکنش:</strong> ${{rec.vakonsh_tavzih||'-'}}</p>
                <h4 style="margin-top:15px;">فرآورده‌ها</h4>
                <table style="width:100%;margin-top:8px;"><tr><th>فرآورده</th><th>گروه</th><th>واحد</th><th>واکنش</th></tr>`;
            if (rec.products) rec.products.forEach(p => {{
                html += `<tr><td>${{p.nam_faravardeh}}</td><td>${{p.groh_khoni_f}}</td><td>${{p.teda_vahed}}</td><td>${{p.vakonsh ? '⚠️ دارد' : '✅ خیر'}}</td></tr>`;
            }});
            html += '</table>';
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
            dept: document.getElementById('f-dept').value,
            blood_group: document.getElementById('f-blood-group').value,
            product: document.getElementById('f-product').value,
            reaction: document.getElementById('f-reaction').value,
            shift: document.getElementById('f-shift').value,
            search: document.getElementById('f-search').value,
            deepseek_key: deepseekKey
        }});
        try {{
            const res = await fetch('/module/reports/blood/analyze?' + params.toString());
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
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),dept:document.getElementById('f-dept').value,blood_group:document.getElementById('f-blood-group').value,product:document.getElementById('f-product').value,reaction:document.getElementById('f-reaction').value,shift:document.getElementById('f-shift').value,search:document.getElementById('f-search').value}});
        window.open('/module/reports/blood/export?'+p.toString(),'_blank');
    }}

    function doPrint() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value}});
        window.open('/module/reports/blood/print?'+p.toString(),'_blank');
    }}

    document.addEventListener('DOMContentLoaded', () => refresh(1));
</script>
</body>
</html>'''
    return html


def _fetch_data(d_from='', d_to='', dept='', blood_group='', product='', reaction='', shift='', search='', page=1, per_page=15):
    """واکشی داده با فیلترها و صفحه‌بندی"""
    offset = (page - 1) * per_page

    base_join = """FROM tbl_blood_trans t
                   LEFT JOIN shift_namt s ON t.nam_shift = s.ID_shift
                   LEFT JOIN tbl_bakhsh b ON t.nam_bakhsh = b.ID_nam_bakhsh
                   WHERE 1=1"""
    base_params = []

    if d_from:
        base_join += " AND t.dat_sabt >= %s"
        base_params.append(d_from)
    if d_to:
        base_join += " AND t.dat_sabt <= %s"
        base_params.append(d_to)
    if dept:
        base_join += " AND t.nam_bakhsh = %s"
        base_params.append(dept)
    if blood_group:
        base_join += " AND t.groh_khoni_bimar = %s"
        base_params.append(blood_group)
    if search:
        base_join += " AND (t.nam_bimar LIKE %s OR t.shomar_parvandeh LIKE %s)"
        base_params.extend([f'%{search}%'] * 2)

    if product:
        base_join += " AND EXISTS (SELECT 1 FROM tbl_blood_faravardeh fb WHERE fb.bloodT_key = t.ID_blood AND fb.nam_faravardeh = %s)"
        base_params.append(product)
    if reaction == '1':
        base_join += " AND EXISTS (SELECT 1 FROM tbl_blood_faravardeh fb WHERE fb.bloodT_key = t.ID_blood AND fb.vakonsh = 1)"
    elif reaction == '0':
        base_join += " AND NOT EXISTS (SELECT 1 FROM tbl_blood_faravardeh fb WHERE fb.bloodT_key = t.ID_blood AND fb.vakonsh = 1)"

    data_sql = f"""SELECT t.ID_blood, t.dat_sabt, t.nam_bimar, t.shomar_parvandeh, t.groh_khoni_bimar,
                    t.vakonsh_tavzih, b.nam_bakhsh as dept_name, s.tarkib as shift_name, s.ID_shift as shift_id
                    {base_join}"""
    data_params = base_params.copy()
    if shift:
        data_sql += " AND t.nam_shift = %s"
        data_params.append(shift)
    data_sql += " ORDER BY t.ID_blood DESC LIMIT %s OFFSET %s"
    data_params.extend([per_page, offset])

    count_sql = f"SELECT COUNT(*) as total {base_join}"
    count_params = base_params.copy()
    if shift:
        count_sql += " AND t.nam_shift = %s"
        count_params.append(shift)

    shifts_sql = f"SELECT DISTINCT s.ID_shift, s.tarkib {base_join} ORDER BY s.tarkib"
    shifts_params = base_params.copy()

    data = query(data_sql, data_params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0
    available_shifts = [(r['ID_shift'], r['tarkib']) for r in (query(shifts_sql, shifts_params, fetch_all=True) or [])]

    if data:
        ids = [str(r['ID_blood']) for r in data]
        products_sql = f"""SELECT bloodT_key, nam_faravardeh, groh_khoni_f, teda_vahed, vakonsh
                          FROM tbl_blood_faravardeh WHERE bloodT_key IN ({','.join(ids)})"""
        all_products = query(products_sql, fetch_all=True) or []
        prod_map = {}
        for p in all_products:
            key = p['bloodT_key']
            if key not in prod_map:
                prod_map[key] = []
            prod_map[key].append(p)

        for row in data:
            row['date_display'] = format_date_display(row.get('dat_sabt'))
            prods = prod_map.get(row['ID_blood'], [])
            row['products'] = prods
            row['product_count'] = len(prods)
            row['total_units'] = sum(p['teda_vahed'] for p in prods)
            row['has_reaction'] = any(p['vakonsh'] == 1 for p in prods)

    stats = _compute_stats(data)
    total = len(data)

    page_data = data[offset:offset+per_page] if per_page else data

    return {
        'data': page_data,
        'stats': stats,
        'total': total,
        'page': page,
        'per_page': per_page,
        'available_shifts': available_shifts
    }


def _compute_stats(data):
    if not data:
        return {'total':0, 'total_units':0, 'unique_patients':0, 'unique_depts':0}
    total = len(data)
    total_units = sum(r.get('total_units',0) for r in data)
    unique_patients = len(set(r.get('nam_bimar','') for r in data))
    unique_depts = len(set(r.get('dept_name','') for r in data))
    return {
        'total': total,
        'total_units': total_units,
        'unique_patients': unique_patients,
        'unique_depts': unique_depts
    }


def _build_table(data):
    if not data:
        return '<tr><td colspan="10" class="empty">داده‌ای یافت نشد</td></tr>'
    rows = []
    for r in data:
        rows.append(f'''<tr onclick="showDetail({r['ID_blood']})" style="cursor:pointer;">
            <td>{r['ID_blood']}</td><td>{r.get('date_display','')}</td><td>{r.get('nam_bimar','')}</td>
            <td>{r.get('shomar_parvandeh','')}</td><td>{r.get('dept_name','')}</td><td>{r.get('shift_name','')}</td>
            <td>{r.get('groh_khoni_bimar','')}</td><td>{r.get('product_count',0)}</td>
            <td>{r.get('total_units',0)}</td><td>{'⚠️ دارد' if r.get('has_reaction') else '✅ خیر'}</td>
        </tr>''')
    return ''.join(rows)


def _build_dashboard(data):
    return '<div class="empty">در حال بارگذاری نمودارها...</div>'


# ==================== API Functions ====================

def api_data(request_args):
    return _fetch_data(
        request_args.get('from',''), request_args.get('to',''),
        request_args.get('dept',''), request_args.get('blood_group',''),
        request_args.get('product',''), request_args.get('reaction',''),
        request_args.get('shift',''), request_args.get('search',''),
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 15, type=int)
    )


def api_export(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('dept',''), request_args.get('blood_group',''),
                    request_args.get('product',''), request_args.get('reaction',''),
                    request_args.get('shift',''), request_args.get('search',''),
                    page=1, per_page=9999)
    wb = Workbook()
    ws = wb.active
    ws.title = "گزارش خون"
    headers = ['کد', 'تاریخ', 'بیمار', 'پرونده', 'بخش', 'شیفت', 'گروه خونی',
               'تعداد فرآورده', 'مجموع واحدها', 'واکنش', 'توضیحات واکنش', 'فرآورده‌ها']
    ws.append(headers)
    for r in d['data']:
        prods = ' | '.join([f"{p['nam_faravardeh']}({p['groh_khoni_f']},{p['teda_vahed']}u)"
                            for p in r.get('products', [])])
        ws.append([r['ID_blood'], r.get('date_display',''), r.get('nam_bimar',''),
                   r.get('shomar_parvandeh',''), r.get('dept_name',''), r.get('shift_name',''),
                   r.get('groh_khoni_bimar',''), r.get('product_count',0), r.get('total_units',0),
                   'دارد' if r.get('has_reaction') else 'خیر',
                   r.get('vakonsh_tavzih', ''), prods])
    ws2 = wb.create_sheet("آمار")
    ws2.append(['شاخص', 'مقدار'])
    s = d['stats']
    for k,v in [('کل ترانسفوزیون‌ها',s['total']), ('مجموع واحدها',s['total_units']),
                ('بیماران یکتا',s['unique_patients']), ('بخش‌های درگیر',s['unique_depts'])]:
        ws2.append([k,v])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='blood_report.xlsx',
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
        body{{font-family:Tahoma;padding:20px;}}h1{{color:#b91c1c;text-align:center;}}
        .sg{{margin:20px 0;border:1px solid #ddd;border-radius:10px;overflow:hidden;}}
        .sh{{background:#b91c1c;color:white;padding:10px;font-weight:bold;}}
        table{{width:100%;border-collapse:collapse;}}
        th{{background:#e2e8f0;padding:8px;}}td{{padding:6px;border:1px solid #ddd;text-align:center;font-size:11px;}}
        @media print{{body{{padding:0;}}}}
    </style></head><body><h1>🩸 گزارش ترانسفوزیون - {today_j}</h1>'''
    for shift, items in groups.items():
        html += f'<div class="sg"><div class="sh">🕒 {shift} - {len(items)} مورد</div><table>'
        html += '<tr><th>بیمار</th><th>پرونده</th><th>بخش</th><th>گروه</th><th>فرآورده‌ها</th><th>واحد</th><th>واکنش</th><th>توضیحات واکنش</th></tr>'
        for r in items:
            prods = ', '.join([f"{p['nam_faravardeh']} ({p['groh_khoni_f']})" for p in r.get('products', [])])
            reaction_status = 'دارد' if r.get('has_reaction') else 'خیر'
            html += f"<tr><td>{r.get('nam_bimar','')}</td><td>{r.get('shomar_parvandeh','')}</td><td>{r.get('dept_name','')}</td><td>{r.get('groh_khoni_bimar','')}</td><td>{prods}</td><td>{r.get('total_units',0)}</td><td>{reaction_status}</td><td>{r.get('vakonsh_tavzih','')}</td></tr>"
        html += '</table></div>'
    html += '<script>window.print();</script></body></html>'
    return html


def api_detail(record_id):
    rec = query("""
        SELECT t.*, b.nam_bakhsh as dept_name, s.tarkib as shift_name
        FROM tbl_blood_trans t
        LEFT JOIN tbl_bakhsh b ON t.nam_bakhsh = b.ID_nam_bakhsh
        LEFT JOIN shift_namt s ON t.nam_shift = s.ID_shift
        WHERE t.ID_blood = %s
    """, (record_id,), fetch_one=True)
    if not rec:
        return {'success': False}
    prods = query("SELECT * FROM tbl_blood_faravardeh WHERE bloodT_key = %s", (record_id,), fetch_all=True) or []
    rec['products'] = prods
    for k in list(rec.keys()):
        if isinstance(rec[k], bytearray):
            rec[k] = rec[k].decode('utf-8')
    return {'success': True, 'record': rec}


def _generate_ai_summary(data):
    """خلاصه آماری پیشرفته برای تحلیل هوشمند"""
    if not data:
        return {}
    total = len(data)
    total_units = sum(r.get('total_units',0) for r in data)

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

    product_risk = {}
    for r in data:
        for p in r.get('products', []):
            name = p.get('nam_faravardeh','نامشخص')
            if name not in product_risk:
                product_risk[name] = {'total':0, 'reactions':0}
            product_risk[name]['total'] += 1
            if p.get('vakonsh'):
                product_risk[name]['reactions'] += 1

    return {
        'total_transfusions': total,
        'total_units': total_units,
        'avg_units_per_transfusion': round(total_units/total, 1) if total else 0,
        'unique_patients': len(set(r.get('nam_bimar','') for r in data)),
        'departments': list(set(r.get('dept_name','') for r in data)),
        'blood_groups': {r.get('groh_khoni_bimar','نامشخص'): sum(1 for x in data if x.get('groh_khoni_bimar')==r.get('groh_khoni_bimar')) for r in data},
        'reaction_count': sum(1 for r in data if r.get('has_reaction')),
        'moving_average': dict(zip(sorted_days[-10:], moving_avg[-10:])),
        'outliers': outliers,
        'product_risk': {k: {'rate': round(v['reactions']/v['total']*100, 1)} for k, v in product_risk.items() if v['total']}
    }


def internal_blood_analysis(summary):
    lines = []
    lines.append(f"🔢 **تعداد کل ترانسفوزیون‌ها:** {summary['total_transfusions']}")
    lines.append(f"🩸 **مجموع واحدهای تزریقی:** {summary['total_units']} (میانگین {summary['avg_units_per_transfusion']} واحد)")
    lines.append(f"👤 **بیماران منحصربه‌فرد:** {summary['unique_patients']}")
    if summary.get('departments'):
        lines.append(f"🏥 **بخش‌های دریافت‌کننده:** {', '.join(summary['departments'])}")
    if summary.get('blood_groups'):
        lines.append("🅰️ **توزیع گروه‌های خونی:**")
        for k,v in summary['blood_groups'].items():
            lines.append(f"   - {k}: {v}")
    lines.append(f"⚠️ **موارد دارای واکنش:** {summary['reaction_count']} ({(summary['reaction_count']/summary['total_transfusions']*100):.1f}%)")
    if summary.get('moving_average'):
        lines.append(f"📈 **میانگین متحرک ۷ روزه (۱۰ روز اخیر):** {list(summary['moving_average'].values())}")
    if summary.get('outliers'):
        lines.append(f"⚠️ **نقاط پرت (انحراف > ۲):** {len(summary['outliers'])} روز")
        for o in summary['outliers'][:3]:
            lines.append(f"   - {o['date']}: {o['value']} ترانسفوزیون (Z-score: {o['z_score']})")
    if summary.get('product_risk'):
        lines.append("🚨 **امتیاز ریسک فرآورده‌ها (درصد واکنش):**")
        for k, v in sorted(summary['product_risk'].items(), key=lambda x: x[1]['rate'], reverse=True):
            emoji = '🔴' if v['rate'] > 20 else '🟠' if v['rate'] > 10 else '🟢'
            lines.append(f"   {emoji} {k}: {v['rate']}%")
    lines.append("💡 **پیشنهادات:**")
    if summary['reaction_count'] > 0:
        lines.append("- بررسی دقیق علل واکنش‌های تزریق خون و مستندسازی کامل.")
    lines.append("- پایش مصرف فرآورده‌های خاص در بخش‌های پرخطر.")
    return "\n".join(lines)


def deepseek_blood_analysis(api_key, summary):
    if not api_key or len(api_key.strip()) < 10:
        return None
    prompt = f"""شما یک متخصص بانک خون هستید. این داده‌های هموویژولانس را تحلیل کنید و پاسخ کاملاً فارسی دهید:
{json.dumps(summary, indent=2, ensure_ascii=False)}
تحلیل شامل: وضعیت کلی، الگوهای مصرف، واکنش‌ها، نقاط پرت، امتیاز ریسک و پیشنهادات اجرایی (حداقل ۳ مورد)."""
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [
                {"role": "system", "content": "شما یک تحلیلگر ارشد بانک خون هستید."},
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
                    request_args.get('dept',''), request_args.get('blood_group',''),
                    request_args.get('product',''), request_args.get('reaction',''),
                    request_args.get('shift',''), request_args.get('search',''),
                    page=1, per_page=9999)
    data = d['data']
    if not data:
        return {'success': False, 'message': 'داده‌ای برای تحلیل وجود ندارد'}
    summary = _generate_ai_summary(data)
    deepseek_key = request_args.get('deepseek_key', '').strip()
    if deepseek_key:
        analysis = deepseek_blood_analysis(deepseek_key, summary)
        if analysis:
            return {'success': True, 'analysis': analysis, 'source_name': 'DeepSeek AI'}
    analysis = internal_blood_analysis(summary)
    return {'success': True, 'analysis': analysis, 'source_name': 'تحلیل داخلی'}
    
    