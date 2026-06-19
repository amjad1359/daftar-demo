"""
گزارش آمار پایان شیفت – نسخهٔ نهایی با تفکیک هوشمند جریانی/موجودی
بر اساس فیلد is_inventory در tbl_amar_items
"""

from models.database import query
import json
from utils.formatters import format_date_display
import math
from datetime import datetime  # برای تبدیل فیلدهای datetime

def get_stats_report(user):
    """صفحه اصلی آمار پایان شیفت"""

    import jdatetime
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    yesterday_j = (jdatetime.date.today() - jdatetime.timedelta(days=1)).strftime("%Y/%m/%d")
    today_int = today_j.replace('/', '')
    yesterday_int = yesterday_j.replace('/', '')

    # بخش‌های فعال
    section_list = query("SELECT nam_bakhsh FROM tbl_bakhsh WHERE amar=1 ORDER BY nam_bakhsh", fetch_all=True) or []
    section_opts = '<option value="">همه بخش‌ها</option>' + ''.join(f'<option value="{s["nam_bakhsh"]}">{s["nam_bakhsh"]}</option>' for s in section_list)

    # لود اولیه
    initial = _fetch_data(yesterday_int, today_int, page=1, per_page=15)
    stats = initial['stats']
    chart_data = initial.get('chart_data', {})

    available_shifts = initial.get('available_shifts', [])
    shift_opts = '<option value="">همه شیفت‌ها</option>' + ''.join(f'<option value="{s}">{s}</option>' for s in available_shifts)

    table_html = _build_table(initial['data'])

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>آمار پایان شیفت</title>
<script src="/static/js/chart.umd.min.js"></script>
<style>
    :root {{ --primary: #1e3a8a; --green: #10b981; --blue: #3b82f6; --purple: #8b5cf6; --gray: #64748b; --l-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9; --white: #fff; --r: 12px; }}
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
    .f-grp {{ flex:1; min-width:100px; }}
    .f-grp label {{ display:block; font-size:10px; font-weight:600; color:var(--gray); margin-bottom:3px; }}
    .f-grp select, .f-grp input {{ width:100%; padding:7px 9px; border:2px solid var(--border); border-radius:6px; font-size:12px; font-family:inherit; }}

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
        <h2>📈 داشبورد و گزارشات آمار پایان شیفت</h2>
        <a href="/module/reports">⬅️ بازگشت</a>
    </div>

    <div class="kpi">
        <div class="kpi-card"><div class="kpi-val" style="color:#1e3a8a;" id="k-total">{stats['total']}</div><div class="kpi-lbl">📋 کل رکوردها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#3b82f6;" id="k-sum">{stats['sum']}</div><div class="kpi-lbl">🔢 مجموع جریانی</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#8b5cf6;" id="k-depts">{stats['depts']}</div><div class="kpi-lbl">🏥 بخش‌های فعال</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#10b981;" id="k-items">{stats['items']}</div><div class="kpi-lbl">📊 تنوع آیتم‌ها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#f59e0b;" id="k-max-inv">{stats['max_inventory']}</div><div class="kpi-lbl">⚠️ حداکثر موجودی</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ</label><input type="text" id="f-from" value="{yesterday_j}"></div>
            <div class="f-grp"><label>تا تاریخ</label><input type="text" id="f-to" value="{today_j}"></div>
            <div class="f-grp"><label>شیفت</label><select id="f-shift">{shift_opts}</select></div>
            <div class="f-grp"><label>بخش</label><select id="f-section">{section_opts}</select></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-blue" onclick="refresh(1)">🔍 اعمال فیلتر</button></div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab on" onclick="switchTab('dash')">📊 نمودارها</button>
        <button class="tab" onclick="switchTab('list')">📋 لیست داده‌ها</button>
        <button class="tab" onclick="switchTab('ai')">🤖 تحلیل هوشمند</button>
    </div>

    <div id="pan-dash" class="pan on">
        <div class="charts">
            <div class="chart-box"><h4>📊 سهم بخش‌ها (آیتم‌های جریانی)</h4><canvas id="chart-dept"></canvas></div>
            <div class="chart-box"><h4>📈 تراکم آیتم‌های جریانی</h4><canvas id="chart-item"></canvas></div>
            <div class="chart-box"><h4>📈 روند روزانه مجموع جریانی (۳۰ روز)</h4><canvas id="chart-trend"></canvas></div>
            <div class="chart-box"><h4>⭐ ۵ آیتم جریانی برتر</h4><canvas id="chart-top-items"></canvas></div>
            <div class="chart-box"><h4>🏥 آخرین موجودی به تفکیک بخش و شیفت</h4><canvas id="chart-inventory"></canvas></div>
        </div>
    </div>

    <div id="pan-list" class="pan">
        <div class="tbl-wrap"><div class="tbl-scroll"><table>
            <thead><tr><th>تاریخ</th><th>شیفت</th><th>بخش</th><th>آیتم</th><th>مقدار</th><th>ثبت‌کننده</th><th>ساعت</th><th>توضیحات</th></tr></thead>
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
            <div class="card-title">🤖 تحلیل هوشمند آمار پایان شیفت</div>
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

<script>
    let currentPage = 1;
    let totalPages = 1;

    renderCharts({json.dumps(chart_data, ensure_ascii=False)});

    function switchTab(t) {{
        document.querySelectorAll('.tab').forEach((x,i) => {{ x.classList.toggle('on', (t==='dash'&&i===0)||(t==='list'&&i===1)||(t==='ai'&&i===2)); }});
        document.querySelectorAll('.pan').forEach(p => p.classList.remove('on'));
        document.getElementById('pan-'+t).classList.add('on');
    }}

    async function refresh(page = 1) {{
        const p = new URLSearchParams({{
            from: (document.getElementById('f-from').value||'').replace(/\//g,''),
            to: (document.getElementById('f-to').value||'').replace(/\//g,''),
            shift: document.getElementById('f-shift').value,
            section: document.getElementById('f-section').value,
            page: page,
            per_page: 15
        }});
        const r = await fetch('/module/reports/stats/data?'+p.toString());
        const d = await r.json();
        const data = d.data || [];
        const s = d.stats || {{}};

        document.getElementById('k-total').textContent = s.total||0;
        document.getElementById('k-sum').textContent = s.sum||0;
        document.getElementById('k-depts').textContent = s.depts||0;
        document.getElementById('k-items').textContent = s.items||0;
        document.getElementById('k-max-inv').textContent = s.max_inventory||0;

        document.getElementById('tbl-body').innerHTML = data.length ? data.map(r => `<tr><td>${{r.date_display||''}}</td><td>${{r.nam_shift||''}}</td><td>${{r.nam_bakhsh||''}}</td><td>${{r.item_name||''}}</td><td style="color:#1e3a8a;font-weight:bold;">${{r.value||0}}</td><td>${{r.user_name||''}}</td><td>${{r.time_display||''}}</td><td>${{r.tozihat||'-'}}</td></tr>`).join('') : '<tr><td colspan="8" class="empty">داده‌ای یافت نشد</td></tr>';

        if (d.available_shifts) {{
            populateShiftDropdown(d.available_shifts);
        }}

        currentPage = d.page || 1;
        totalPages = Math.ceil((d.total || 0) / 15);
        renderPagination();

        if (d.chart_data) renderCharts(d.chart_data);
    }}

    function populateShiftDropdown(shifts) {{
        const sel = document.getElementById('f-shift');
        const currentVal = sel.value;
        sel.innerHTML = '<option value="">همه شیفت‌ها</option>';
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

    function renderCharts(cd) {{
        setTimeout(() => {{
            ['chart-dept','chart-item','chart-trend','chart-top-items','chart-inventory'].forEach(id => {{
                const existing = Chart.getChart(id);
                if (existing) existing.destroy();
            }});

            const dm = cd.dept_sums || [];
            if (dm.length) {{
                new Chart(document.getElementById('chart-dept'), {{
                    type: 'bar',
                    data: {{
                        labels: dm.map(d => d.name),
                        datasets: [{{ data: dm.map(d => d.sum), backgroundColor: '#3b82f6' }}]
                    }},
                    options: {{ responsive: true }}
                }});
            }}

            const im = cd.item_sums || [];
            if (im.length) {{
                new Chart(document.getElementById('chart-item'), {{
                    type: 'bar',
                    data: {{
                        labels: im.map(d => d.name),
                        datasets: [{{ data: im.map(d => d.sum), backgroundColor: '#8b5cf6' }}]
                    }},
                    options: {{ responsive: true }}
                }});
            }}

            const trend = cd.daily_trend || [];
            if (trend.length) {{
                new Chart(document.getElementById('chart-trend'), {{
                    type: 'line',
                    data: {{
                        labels: trend.map(d => d.date.substring(5)),
                        datasets: [{{ label: 'مجموع جریانی', data: trend.map(d => d.sum), borderColor: '#10b981', tension: 0.3 }}]
                    }},
                    options: {{ responsive: true }}
                }});
            }}

            const topItems = (cd.item_sums || []).sort((a,b) => b.sum - a.sum).slice(0,5);
            if (topItems.length) {{
                new Chart(document.getElementById('chart-top-items'), {{
                    type: 'bar',
                    data: {{
                        labels: topItems.map(d => d.name),
                        datasets: [{{ data: topItems.map(d => d.sum), backgroundColor: '#f59e0b' }}]
                    }},
                    options: {{ responsive: true, indexAxis: 'y' }}
                }});
            }}

            // نمودار آخرین موجودی به تفکیک بخش و شیفت
            const invData = cd.inventory_latest || [];
            if (invData.length) {{
                // گروه‌بندی بخش‌ها
                const deptSet = new Set(invData.map(d => d.dept));
                const shifts = [...new Set(invData.map(d => d.shift))];
                const datasets = shifts.map((shift, idx) => {{
                    const color = ['#f59e0b','#10b981','#3b82f6'][idx % 3];
                    const data = invData.filter(d => d.shift === shift).map(d => d.value);
                    return {{
                        label: shift,
                        data: data,
                        backgroundColor: color
                    }};
                }});
                new Chart(document.getElementById('chart-inventory'), {{
                    type: 'bar',
                    data: {{
                        labels: [...deptSet],
                        datasets: datasets
                    }},
                    options: {{ responsive: true, scales: {{ x: {{ stacked: false }}, y: {{ beginAtZero: true }} }} }}
                }});
            }}
        }}, 50);
    }}

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
            deepseek_key: deepseekKey
        }});
        try {{
            const res = await fetch('/module/reports/stats/analyze?' + params.toString());
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
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value,section:document.getElementById('f-section').value}});
        window.open('/module/reports/stats/export?'+p.toString(),'_blank');
    }}

    function doPrint() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),shift:document.getElementById('f-shift').value,section:document.getElementById('f-section').value}});
        window.open('/module/reports/stats/print?'+p.toString(),'_blank');
    }}
</script>
</body>
</html>'''
    return html


def _fetch_data(d_from='', d_to='', shift='', section='', page=1, per_page=15):
    offset = (page - 1) * per_page

    base_join = """FROM tbl_amar_data d
                    LEFT JOIN tbl_bakhsh b ON d.bakhsh_id = b.ID_nam_bakhsh
                    LEFT JOIN shift_namt s ON d.nam_shift = s.ID_shift
                    LEFT JOIN users u ON d.UserID = u.UserID
                    LEFT JOIN tbl_amar_items i ON d.item_id = i.ID_item
                    WHERE 1=1"""
    base_params = []

    if d_from:
        base_join += " AND d.dat_sabt >= %s"
        base_params.append(d_from)
    if d_to:
        base_join += " AND d.dat_sabt <= %s"
        base_params.append(d_to)
    if section:
        base_join += " AND b.nam_bakhsh = %s"
        base_params.append(section)

    # کوئری اصلی داده‌ها
    data_sql = f"SELECT d.ID_data, d.value, d.dat_sabt, d.zaman_sabt, d.tozihat, b.nam_bakhsh, s.tarkib AS nam_shift, u.FullName AS user_name, i.item_name, i.is_inventory {base_join}"
    data_params = base_params.copy()
    if shift:
        data_sql += " AND s.tarkib = %s"
        data_params.append(shift)
    data_sql += " ORDER BY d.dat_sabt DESC, d.zaman_sabt DESC LIMIT %s OFFSET %s"
    data_params.extend([per_page, offset])

    count_sql = f"SELECT COUNT(*) as total {base_join}"
    count_params = base_params.copy()
    if shift:
        count_sql += " AND s.tarkib = %s"
        count_params.append(shift)

    shifts_sql = f"SELECT DISTINCT s.tarkib {base_join} ORDER BY s.tarkib"
    shifts_params = base_params.copy()

    # کوئری‌های تجمیعی فقط برای آیتم‌های جریانی (is_inventory = 0)
    dept_sql = f"SELECT b.nam_bakhsh AS name, COALESCE(SUM(d.value),0) AS sum {base_join} AND i.is_inventory = 0"
    dept_params = base_params.copy()
    if shift:
        dept_sql += " AND s.tarkib = %s"
        dept_params.append(shift)
    dept_sql += " AND b.nam_bakhsh IS NOT NULL GROUP BY b.nam_bakhsh ORDER BY sum DESC LIMIT 10"

    item_sql = f"SELECT i.item_name AS name, COALESCE(SUM(d.value),0) AS sum {base_join} AND i.is_inventory = 0"
    item_params = base_params.copy()
    if shift:
        item_sql += " AND s.tarkib = %s"
        item_params.append(shift)
    item_sql += " AND i.item_name IS NOT NULL GROUP BY i.item_name ORDER BY sum DESC LIMIT 10"

    daily_sql = f"SELECT d.dat_sabt AS date, COALESCE(SUM(d.value),0) AS sum {base_join} AND i.is_inventory = 0"
    daily_params = base_params.copy()
    if shift:
        daily_sql += " AND s.tarkib = %s"
        daily_params.append(shift)
    daily_sql += " GROUP BY d.dat_sabt ORDER BY d.dat_sabt DESC LIMIT 30"

    # کوئری آخرین موجودی به تفکیک بخش و شیفت (آیتم‌های موجودی)
    inv_sql = f"""SELECT b.nam_bakhsh AS dept, s.tarkib AS shift, d.value, d.zaman_sabt, i.item_name
                  FROM tbl_amar_data d
                  JOIN tbl_bakhsh b ON d.bakhsh_id = b.ID_nam_bakhsh
                  JOIN shift_namt s ON d.nam_shift = s.ID_shift
                  JOIN tbl_amar_items i ON d.item_id = i.ID_item
                  WHERE i.is_inventory = 1 AND {base_join.split('WHERE')[1].strip().replace('WHERE 1=1','')}"""
    inv_params = base_params.copy()
    if shift:
        inv_sql += " AND s.tarkib = %s"
        inv_params.append(shift)
    # برای هر بخش و شیفت، آخرین رکورد از نظر dat_sabt و zaman_sabt را بگیریم
    inv_sql += " ORDER BY d.dat_sabt DESC, d.zaman_sabt DESC"

    data = query(data_sql, data_params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0
    available_shifts = [r['tarkib'] for r in (query(shifts_sql, shifts_params, fetch_all=True) or [])]
    dept_sums = query(dept_sql, dept_params, fetch_all=True) or []
    item_sums = query(item_sql, item_params, fetch_all=True) or []
    daily_trend = query(daily_sql, daily_params, fetch_all=True) or []
    inv_rows = query(inv_sql, inv_params, fetch_all=True) or []

    # پردازش داده‌های اصلی
    for row in data:
        row['date_display'] = format_date_display(row.get('dat_sabt'))
        t = row.get('zaman_sabt')
        if isinstance(t, datetime):
            row['time_display'] = t.strftime('%H:%M:%S')
            row['zaman_sabt'] = t.strftime('%Y-%m-%d %H:%M:%S')  # برای اطمینان از سریالایز JSON
        else:
            row['time_display'] = str(t).split(' ')[-1][:5] if t else ''
        # تبدیل سایر فیلدهای datetime احتمالی
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        try: row['value'] = int(float(row.get('value', 0)))
        except: row['value'] = 0

    daily_trend = [{'date': format_date_display(r['date']), 'sum': int(r['sum'])} for r in daily_trend]
    daily_trend.reverse()

    # حداکثر موجودی
    max_inv_sql = f"SELECT COALESCE(MAX(d.value),0) as mx {base_join} AND i.is_inventory = 1"
    max_inv_params = base_params.copy()
    if shift:
        max_inv_sql += " AND s.tarkib = %s"
        max_inv_params.append(shift)
    max_inv_row = query(max_inv_sql, max_inv_params, fetch_one=True)
    max_inventory = int(max_inv_row['mx']) if max_inv_row else 0

    # پردازش آخرین موجودی: فقط آخرین رکورد برای هر بخش-شیفت (با احتساب آیتم‌ها)
    # اما می‌خواهیم یک مقدار برای هر بخش-شیفت (مثلاً مجموع آخرین مقادیر آیتم‌ها) – برای سادگی آخرین مقدار اولین آیتم
    # روش بهتر: گروه‌بندی بر اساس بخش و شیفت و گرفتن اولین رکورد (جدیدترین)
    latest_inv_map = {}
    for row in inv_rows:
        key = (row['dept'], row['shift'])
        if key not in latest_inv_map:
            latest_inv_map[key] = row['value']
    inventory_latest = [{'dept': k[0], 'shift': k[1], 'value': v} for k, v in latest_inv_map.items()]

    chart_data = {
        'dept_sums': [{'name': r['name'], 'sum': int(r['sum'])} for r in dept_sums],
        'item_sums': [{'name': r['name'], 'sum': int(r['sum'])} for r in item_sums],
        'daily_trend': daily_trend,
        'inventory_latest': inventory_latest
    }

    return {
        'data': data,
        'total': total,
        'page': page,
        'per_page': per_page,
        'available_shifts': available_shifts,
        'chart_data': chart_data,
        'stats': {
            'total': total,
            'sum': sum(r['sum'] for r in dept_sums) if dept_sums else 0,
            'depts': len(dept_sums),
            'items': len(item_sums),
            'max_inventory': max_inventory
        }
    }


def _build_table(data):
    if not data: return '<tr><td colspan="8" class="empty">داده‌ای یافت نشد</td></tr>'
    return ''.join(f"<tr><td>{r.get('date_display','')}</td><td>{r.get('nam_shift','')}</td><td>{r.get('nam_bakhsh','')}</td><td>{r.get('item_name','')}</td><td style='color:#1e3a8a;font-weight:bold;'>{r.get('value',0)}</td><td>{r.get('user_name','')}</td><td>{r.get('time_display','')}</td><td>{r.get('tozihat','-')}</td></tr>" for r in data)


def api_data(request_args):
    return _fetch_data(
        request_args.get('from',''), request_args.get('to',''),
        request_args.get('shift',''), request_args.get('section',''),
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 15, type=int)
    )


def api_export(request_args):
    import io; from openpyxl import Workbook; from flask import send_file
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('shift',''), request_args.get('section',''), page=1, per_page=9999)
    wb = Workbook(); ws = wb.active; ws.title = "آمار"
    ws.append(['تاریخ','شیفت','بخش','آیتم','مقدار','ثبت‌کننده','ساعت','توضیحات'])
    for r in d['data']: ws.append([r.get('date_display'),r.get('nam_shift'),r.get('nam_bakhsh'),r.get('item_name'),r.get('value'),r.get('user_name'),r.get('time_display'),r.get('tozihat','')])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='stats_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def api_print(request_args):
    import jdatetime
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('shift',''), request_args.get('section',''), page=1, per_page=9999)
    today_j = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    data = d['data']

    groups = {}
    for r in data:
        sh = r.get('nam_shift', 'نامشخص')
        sec = r.get('nam_bakhsh', 'نامشخص')
        if sh not in groups: groups[sh] = {}
        if sec not in groups[sh]: groups[sh][sec] = []
        groups[sh][sec].append(r)

    html = f'''<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><style>body{{font-family:Tahoma;padding:20px;}}h1{{color:#1e3a8a;text-align:center;}}.sh{{background:#1e3a8a;color:white;padding:12px;margin-top:20px;border-radius:8px;font-size:16px;text-align:center;}}.sec{{margin:15px 0;border:1px solid #ccc;padding:12px;background:#f9f9f9;border-radius:8px;}}.shd{{font-weight:bold;color:#1e3a8a;border-bottom:2px solid #ddd;padding-bottom:8px;margin-bottom:10px;display:flex;justify-content:space-between;}}.cards{{display:flex;flex-wrap:wrap;gap:10px;}}.card{{background:white;border:1px solid #cbd5e1;padding:6px 14px;border-radius:20px;font-size:12px;}}.sum{{margin-top:10px;background:#f0fdf4;border:2px solid #22c55e;padding:12px;border-radius:8px;}}.sum-cards{{display:flex;flex-wrap:wrap;gap:10px;}}.sc{{background:white;padding:8px;border-radius:5px;text-align:center;min-width:100px;}}@media print{{body{{padding:10px;}}}}</style></head><body><h1>📊 گزارش آمار پایان شیفت</h1><p style="text-align:center;">{today_j}</p>'''
    for sh, sections in groups.items():
        html += f'<div class="sh">🌙 شیفت: {sh}</div>'
        shift_items = {}
        for sec, items in sections.items():
            desc = items[0].get('tozihat', 'بدون توضیح') if items else ''
            html += f'<div class="sec"><div class="shd"><span>🏥 {sec}</span><span>📝 {desc}</span></div><div class="cards">'
            for r in items:
                inv_mark = ' ⚠️' if r.get('is_inventory') == 1 else ''
                html += f'<div class="card"><span style="color:#64748b;">{r.get("item_name")}{inv_mark}:</span> <strong>{r.get("value",0)}</strong></div>'
                # تجمیع همه آیتم‌ها (چاپ پایان شیفت بدون تداخل)
                k = r.get('item_name', '')
                shift_items[k] = (shift_items.get(k, 0) + r.get('value', 0))
            html += '</div></div>'
        # جمع تجمعی شیفت (همه آیتم‌ها)
        html += '<div class="sum"><h4 style="color:#166534;">📊 جمع کل شیفت</h4><div class="sum-cards">'
        for k, v in shift_items.items():
            html += f'<div class="sc"><div style="font-size:10px;color:#166534;">{k}</div><div style="font-size:14px;font-weight:bold;color:#15803d;">{v}</div></div>'
        html += '</div></div>'
    html += '<script>window.print();</script></body></html>'
    return html


def _generate_ai_summary(chart_data):
    dept_sums = chart_data.get('dept_sums', [])
    item_sums = chart_data.get('item_sums', [])
    daily_trend = chart_data.get('daily_trend', [])

    total_sum = sum(d['sum'] for d in dept_sums)
    dept_count = len(dept_sums)
    item_count = len(item_sums)

    values = [d['sum'] for d in daily_trend]
    moving_avg = []
    for i in range(len(values)):
        window = values[max(0, i-6):i+1]
        moving_avg.append(round(sum(window)/len(window), 1))

    mean_val = sum(values)/len(values) if values else 0
    std_val = math.sqrt(sum((v-mean_val)**2 for v in values)/len(values)) if len(values) > 1 else 0
    outliers = []
    for i, v in enumerate(values):
        if std_val > 0 and abs(v-mean_val)/std_val > 2:
            outliers.append({'date': daily_trend[i]['date'], 'value': v, 'z_score': round(abs(v-mean_val)/std_val, 2)})

    return {
        'total_sum': total_sum,
        'dept_count': dept_count,
        'item_count': item_count,
        'top_dept': dept_sums[0]['name'] if dept_sums else '---',
        'top_item': item_sums[0]['name'] if item_sums else '---',
        'moving_average': dict(zip([d['date'] for d in daily_trend[-10:]], moving_avg[-10:])),
        'outliers': outliers
    }


def internal_stats_analysis(summary):
    lines = []
    lines.append(f"📊 **مجموع کل مقادیر جریانی:** {summary['total_sum']}")
    lines.append(f"🏥 **بخش‌های فعال:** {summary['dept_count']} بخش")
    lines.append(f"📋 **تنوع آیتم‌های جریانی:** {summary['item_count']} آیتم")
    lines.append(f"🥇 **بخش برتر:** {summary['top_dept']}")
    lines.append(f"⭐ **آیتم جریانی غالب:** {summary['top_item']}")
    if summary.get('moving_average'):
        lines.append(f"📈 **میانگین متحرک ۷ روزه (۱۰ روز اخیر):** {list(summary['moving_average'].values())}")
    if summary.get('outliers'):
        lines.append(f"⚠️ **نقاط پرت (انحراف > ۲):** {len(summary['outliers'])} روز")
        for o in summary['outliers'][:3]:
            lines.append(f"   - {o['date']}: {o['value']} (Z-score: {o['z_score']})")
    lines.append("💡 **پیشنهادات:**")
    if summary['total_sum'] > 0:
        lines.append("- پایش روزانه آیتم‌های پرمصرف جریانی برای مدیریت منابع.")
    return "\n".join(lines)


def api_analyze(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('shift',''), request_args.get('section',''),
                    page=1, per_page=9999)
    chart_data = d.get('chart_data', {})
    if not chart_data.get('dept_sums') and not chart_data.get('item_sums'):
        return {'success': False, 'message': 'داده‌ای برای تحلیل وجود ندارد'}
    summary = _generate_ai_summary(chart_data)
    analysis = internal_stats_analysis(summary)
    return {'success': True, 'analysis': analysis, 'source_name': 'تحلیل داخلی'}
    
    