"""
گزارش راند و اعتباربخشی – نسخهٔ ارتقاءیافته
نمودارهای تعاملی Chart.js، تحلیل عمیق آماری، لود سریع
"""

from models.database import query
import json
from modules.reports.ai_engine import internal_analysis, deepseek_analysis
from utils.formatters import format_date_display
import math

def get_rounds_report(user):
    """صفحه اصلی گزارش راند"""

    import jdatetime
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    month_ago = (jdatetime.date.today() - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")

    # لود فیلترهای ثابت (سریع)
    dept_list = query("SELECT ID_nam_bakhsh, nam_bakhsh FROM tbl_bakhsh ORDER BY nam_bakhsh", fetch_all=True) or []
    title_list = query("SELECT ID_onvan_arziabi, nom_onvan FROM tbl_arzibi_onvan ORDER BY nom_onvan", fetch_all=True) or []
    shift_list = query("SELECT DISTINCT s.ID_shift, s.tarkib FROM shift_namt s ORDER BY s.tarkib", fetch_all=True) or []

    dept_opts = '<option value="">همه بخش‌ها</option>' + ''.join(
        f'<option value="{d["ID_nam_bakhsh"]}">{d["nam_bakhsh"]}</option>' for d in dept_list)
    title_opts = '<option value="">همه گروه‌ها</option>' + ''.join(
        f'<option value="{t["ID_onvan_arziabi"]}">{t["nom_onvan"]}</option>' for t in title_list)
    shift_opts = '<option value="">همه شیفت‌ها</option>' + ''.join(
        f'<option value="{s["ID_shift"]}">{s["tarkib"]}</option>' for s in shift_list)

    # آمار اولیه خالی
    stats = {'total': 0, 'earned': '0', 'percent': 0, 'level': '---'}
    table_html = '<tr><td colspan="13" class="empty">در حال بارگذاری...</td></tr>'
    dash_html = '<div class="empty">در حال بارگذاری نمودارها...</div>'

    html = f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>گزارش راند و اعتباربخشی</title>
<script src="/static/js/chart.umd.min.js"></script>
<style>
    :root {{ --primary: #1e3a8a; --green: #10b981; --red: #ef4444; --yellow: #f59e0b; --blue: #3b82f6; --gray: #64748b; --l-gray: #94a3b8; --border: #e2e8f0; --bg: #f1f5f9; --white: #fff; --r: 12px; }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family: Tahoma, Arial; direction:rtl; background:var(--bg); color:#1e293b; }}
    .container {{ max-width:1400px; margin:0 auto; padding:16px; }}
    
    .header {{ background:linear-gradient(135deg,#1e3a8a,#3b82f6); color:white; border-radius:var(--r); padding:18px 24px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 6px 20px rgba(30,58,138,.25); }}
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
    .badge-ex {{ background:#059669; }}
    .badge-gd {{ background:#2563eb; }}
    .badge-av {{ background:#b45309; }}
    .badge-pr {{ background:#b91c1c; }}

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
        <h2>📋 سامانه تحلیل و گزارش راندها</h2>
        <a href="/module/reports">⬅️ بازگشت</a>
    </div>

    <div class="kpi">
        <div class="kpi-card"><div class="kpi-val" style="color:#1e3a8a;" id="k-total">{stats['total']}</div><div class="kpi-lbl">📋 تعداد ارزیابی‌ها</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#059669;" id="k-score">{stats['earned']}</div><div class="kpi-lbl">⭐ امتیاز نهایی</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#2563eb;" id="k-percent">{stats['percent']}%</div><div class="kpi-lbl">📈 درصد تحقق</div></div>
        <div class="kpi-card"><div class="kpi-val" style="color:#b45309;" id="k-level">{stats['level']}</div><div class="kpi-lbl">🏆 سطح اعتباربخشی</div></div>
    </div>

    <div class="filters">
        <div class="f-row">
            <div class="f-grp"><label>از تاریخ</label><input type="text" id="f-from" value="{month_ago}"></div>
            <div class="f-grp"><label>تا تاریخ</label><input type="text" id="f-to" value="{today_j}"></div>
            <div class="f-grp"><label>بخش</label><select id="f-dept">{dept_opts}</select></div>
            <div class="f-grp"><label>گروه ارزیابی</label><select id="f-title">{title_opts}</select></div>
            <div class="f-grp"><label>شیفت</label><select id="f-shift">{shift_opts}</select></div>
        </div>
        <div class="f-row">
            <div class="f-grp"><label><input type="checkbox" id="f-safety" style="width:auto;"> فقط آیتم‌های ایمنی</label></div>
            <div class="f-grp"><label><input type="checkbox" id="f-hasdoc" style="width:auto;"> فقط دارای اسناد</label></div>
            <div class="f-grp" style="flex:2;"><label>جستجو</label><input type="text" id="f-search" placeholder="نام سنجه / توضیحات..."></div>
            <div class="f-grp" style="flex:0 0 auto;"><label>&nbsp;</label><button class="btn btn-blue" onclick="refresh(1)">🔍 اعمال فیلتر</button></div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab on" onclick="switchTab('dash')">📊 داشبورد</button>
        <button class="tab" onclick="switchTab('list')">📋 لیست ارزیابی‌ها</button>
        <button class="tab" onclick="switchTab('ai')">🤖 تحلیل هوشمند</button>
    </div>

    <div id="pan-dash" class="pan on">{dash_html}</div>

    <div id="pan-list" class="pan">
        <div class="tbl-wrap"><div class="tbl-scroll"><table>
            <thead><tr><th>کد</th><th>تاریخ</th><th>بخش</th><th>سطح</th><th>گروه</th><th>سنجه</th><th>امتیاز</th><th>نمره نهایی</th><th>حداکثر</th><th>درصد</th><th>کیفیت</th><th>ایمنی</th><th>اسناد</th></tr></thead>
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
            <div class="card-title">🤖 تحلیل هوشمند اعتباربخشی</div>
            <div class="row" style="margin-bottom:15px;">
                <div class="form-group" style="flex:2;">
                    <label>🔑 کلید API دیپ‌سیک (اختیاری)</label>
                    <input type="text" id="deepseek-key" class="form-input" placeholder="sk-...">
                    <small>با وارد کردن کلید، تحلیل عمیق‌تری دریافت می‌کنید</small>
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
            title: document.getElementById('f-title').value,
            shift: document.getElementById('f-shift').value,
            safety: document.getElementById('f-safety').checked ? '1' : '',
            hasdoc: document.getElementById('f-hasdoc').checked ? '1' : '',
            search: document.getElementById('f-search').value,
            page: page,
            per_page: 15
        }});
        const r = await fetch('/module/reports/rounds/data?'+p.toString());
        const d = await r.json();
        allData = d.data || [];
        const s = d.stats || {{}};

        document.getElementById('k-total').textContent = s.total||0;
        document.getElementById('k-score').textContent = s.earned||'0';
        document.getElementById('k-percent').textContent = (s.percent||0)+'%';
        document.getElementById('k-level').textContent = s.level||'-';



        document.getElementById('tbl-body').innerHTML = allData.length ? allData.map(r => {{
            const qb = r.quality_label||'متوسط';
            const qc = qb.includes('عالی')?'badge-ex':qb.includes('خوب')?'badge-gd':qb.includes('متوسط')?'badge-av':'badge-pr';
            
            // ساخت لینک دانلود برای فایل‌های پیوست
            let docDisplay = '<span style="color:#94a3b8;">ندارد</span>';
            if (r.has_document && r.sanad) {{
                const files = r.sanad.split(',').filter(f => f);
                if (files.length > 0) {{
                    let links = '';
                    files.forEach(file => {{
                        const fileName = file.split('/').pop();
                        links += `<a href="/${{file}}" target="_blank" class="btn btn-xs" style="background:#6366f1; color:white; text-decoration:none; margin:2px; display:inline-block;">📎 ${{fileName.substring(0,12)}}</a>`;
                    }});
                    docDisplay = `<div style="display:flex; flex-wrap:wrap; gap:3px; justify-content:center;">${{links}}</div>`;
                }} else {{
                    docDisplay = '<span class="badge" style="background:#6366f1;">📎 دارد</span>';
                }}
            }}
            
            return `<tr>
                <td>${{r.ID_arziabi_bakhsh}}</td>
                <td>${{r.date_display||''}}</td>
                <td>${{r.department||''}}</td>
                <td>${{r.level||''}}</td>
                <td>${{r.group_title||''}}</td>
                <td>${{(r.item_name||'').substring(0,50)}}</td>
                <td>${{r.emtiaz||0}}</td>
                <td>${{r.earned_score||0}}</td>
                <td>${{r.max_score||0}}</td>
                <td>${{r.achievement_percent||0}}%</td>
                <td><span class="badge ${{qc}}">${{qb}}</span></td>
                <td>${{r.is_safety==1?'🛡️':'📋'}}</td>
                <td>${{docDisplay}}</td>
            </tr>`;
        }}).join('') : '<tr><td colspan="13" class="empty">داده‌ای یافت نشد</td></tr>';


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
        sel.innerHTML = '<option value="">همه شیفت‌ها</option>';
        shifts.forEach(s => sel.innerHTML += `<option value="${{s[0]}}">${{s[1]}}</option>`);
        if (shifts.some(s => s[0] == currentVal)) sel.value = currentVal; else sel.value = '';
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
            ['chart-levels','chart-quality','chart-depts','chart-scores','chart-trend'].forEach(id => {{
                const existing = Chart.getChart(id);
                if (existing) existing.destroy();
            }});

            if (!data.length) {{
                document.getElementById('pan-dash').innerHTML = '<div class="empty">داده‌ای نیست</div>';
                return;
            }}

            document.getElementById('pan-dash').innerHTML = `
                <div class="charts">
                    <div class="chart-box"><h4>🥧 توزیع بر اساس سطح</h4><canvas id="chart-levels"></canvas></div>
                    <div class="chart-box"><h4>📊 توزیع سطوح کیفی</h4><canvas id="chart-quality"></canvas></div>
                    <div class="chart-box"><h4>📍 ارزیابی‌ها به تفکیک بخش</h4><canvas id="chart-depts"></canvas></div>
                    <div class="chart-box"><h4>⭐ مجموع امتیازات بخش‌ها</h4><canvas id="chart-scores"></canvas></div>
                    <div class="chart-box"><h4>📈 روند درصد تحقق (۳۰ روز اخیر)</h4><canvas id="chart-trend"></canvas></div>
                </div>
            `;

            const colors = ['#1e3a8a','#3b82f6','#6366f1','#818cf8','#a5b4fc'];

            // سطوح (pie)
            const lm={{}};
            data.forEach(r => {{ const k=r.level||'?'; lm[k]=(lm[k]||0)+1; }});
            new Chart(document.getElementById('chart-levels'), {{
                type: 'pie',
                data: {{
                    labels: Object.keys(lm),
                    datasets: [{{ data: Object.values(lm), backgroundColor: colors.slice(0, Object.keys(lm).length) }}]
                }}
            }});

            // کیفیت (bar)
            const qm={{}};
            data.forEach(r => {{ const k=r.quality_label||'متوسط'; qm[k]=(qm[k]||0)+1; }});
            const qColors = {{'عالی':'#059669','خوب':'#2563eb','متوسط':'#b45309','نیازمند بهبود':'#b91c1c'}};
            new Chart(document.getElementById('chart-quality'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(qm),
                    datasets: [{{ data: Object.values(qm), backgroundColor: Object.keys(qm).map(k => qColors[k]||'#94a3b8') }}]
                }},
                options: {{ responsive: true }}
            }});

            // بخش‌ها (bar)
            const dm={{}};
            data.forEach(r => {{ const k=r.department||'نامشخص'; dm[k]=(dm[k]||0)+1; }});
            const sortedDepts = Object.entries(dm).sort((a,b) => b[1]-a[1]).slice(0,10);
            new Chart(document.getElementById('chart-depts'), {{
                type: 'bar',
                data: {{
                    labels: sortedDepts.map(([k]) => k),
                    datasets: [{{ data: sortedDepts.map(([,v]) => v), backgroundColor: '#6366f1' }}]
                }},
                options: {{ responsive: true }}
            }});

            // امتیازات بخش‌ها (bar)
            const sc={{}};
            data.forEach(r => {{ const k=r.department||'نامشخص'; sc[k]=(sc[k]||0)+(r.earned_score||0); }});
            const sortedScores = Object.entries(sc).sort((a,b) => b[1]-a[1]).slice(0,10);
            new Chart(document.getElementById('chart-scores'), {{
                type: 'bar',
                data: {{
                    labels: sortedScores.map(([k]) => k),
                    datasets: [{{ data: sortedScores.map(([,v]) => v), backgroundColor: '#f59e0b' }}]
                }},
                options: {{ responsive: true }}
            }});

            // روند درصد تحقق (line)
            const dailyPct={{}};
            data.forEach(r => {{
                const d = r.date_display||'';
                if (!dailyPct[d]) dailyPct[d] = {{ sum:0, count:0 }};
                dailyPct[d].sum += r.achievement_percent||0;
                dailyPct[d].count++;
            }});
            const sortedDays = Object.keys(dailyPct).sort().slice(-30);
            const trendData = sortedDays.map(d => {{
                const v = dailyPct[d];
                return v.count ? Math.round(v.sum / v.count) : 0;
            }});
            new Chart(document.getElementById('chart-trend'), {{
                type: 'line',
                data: {{
                    labels: sortedDays.map(d => d.substring(5)),
                    datasets: [{{ label: 'میانگین درصد تحقق', data: trendData, borderColor: '#2563eb', tension: 0.3 }}]
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
            dept: document.getElementById('f-dept').value,
            title: document.getElementById('f-title').value,
            shift: document.getElementById('f-shift').value,
            safety: document.getElementById('f-safety').checked ? '1' : '',
            hasdoc: document.getElementById('f-hasdoc').checked ? '1' : '',
            search: document.getElementById('f-search').value,
            deepseek_key: deepseekKey
        }});
        try {{
            const res = await fetch('/module/reports/rounds/analyze?' + params.toString());
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
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),dept:document.getElementById('f-dept').value,title:document.getElementById('f-title').value,shift:document.getElementById('f-shift').value,safety:document.getElementById('f-safety').checked?'1':'',hasdoc:document.getElementById('f-hasdoc').checked?'1':'',search:document.getElementById('f-search').value}});
        window.open('/module/reports/rounds/export?'+p.toString(),'_blank');
    }}

    function doPrint() {{
        const p=new URLSearchParams({{from:(document.getElementById('f-from').value||'').replace(/\//g,''),to:(document.getElementById('f-to').value||'').replace(/\//g,''),dept:document.getElementById('f-dept').value,title:document.getElementById('f-title').value,shift:document.getElementById('f-shift').value,safety:document.getElementById('f-safety').checked?'1':'',hasdoc:document.getElementById('f-hasdoc').checked?'1':'',search:document.getElementById('f-search').value}});
        window.open('/module/reports/rounds/print?'+p.toString(),'_blank');
    }}

    document.addEventListener('DOMContentLoaded', () => refresh(1));
</script>
</body>
</html>'''
    return html


def _fetch_data(d_from='', d_to='', dept='', title='', shift='', safety='', hasdoc='', search='', page=1, per_page=15):
    """واکشی داده با صفحه‌بندی و فیلترهای پیشرفته"""
    offset = (page - 1) * per_page

    base_join = """FROM tbl_arziabi_bakhsh r
                   LEFT JOIN tbl_bakhsh b ON r.id_nam_bakhsh=b.ID_nam_bakhsh
                   LEFT JOIN tbl_arziabi_cheklist c ON r.id_ckeklist=c.ID_cheklist
                   LEFT JOIN tbl_arzibi_onvan t ON r.id_onvan_arziabi=t.ID_onvan_arziabi
                   LEFT JOIN shift_namt s ON r.id_shift=s.ID_shift
                   LEFT JOIN users u ON r.UserID=u.UserID
                   WHERE 1=1"""
    base_params = []

    if d_from: base_join += " AND r.dat_sabt >= %s"; base_params.append(d_from)
    if d_to: base_join += " AND r.dat_sabt <= %s"; base_params.append(d_to)
    if dept: base_join += " AND r.id_nam_bakhsh = %s"; base_params.append(dept)
    if title: base_join += " AND r.id_onvan_arziabi = %s"; base_params.append(title)
    if safety: base_join += " AND c.imani_chek = 1"
    if hasdoc: base_join += " AND r.sanad IS NOT NULL AND r.sanad != ''"
    if search: base_join += " AND (c.nam_item LIKE %s OR r.tozihat LIKE %s)"; base_params.extend([f'%{search}%']*2)

    data_sql = f"""SELECT r.ID_arziabi_bakhsh, r.dat_sabt, r.emtiaz, r.nomreh_kol AS earned_score,
                    r.nokat_manfi, r.nokhat_mosbat, r.tozihat, r.sanad,
                    b.nam_bakhsh AS department, t.nom_onvan AS group_title,
                    c.nam_item AS item_name, c.sath AS level, c.imani_chek AS is_safety,
                    c.kole_emtiaz AS max_score, c.adres_sanjeh, c.vazn_sanjeh, c.nomreh AS base_score,
                    s.tarkib AS shift_name, s.ID_shift AS shift_id, u.FullName AS assessor {base_join}"""
    data_params = base_params.copy()
    if shift: data_sql += " AND r.id_shift = %s"; data_params.append(shift)
    data_sql += " ORDER BY b.nam_bakhsh, c.sath, t.nom_onvan, c.nam_item LIMIT %s OFFSET %s"; data_params.extend([per_page, offset])

    count_sql = f"SELECT COUNT(*) as total {base_join}"
    count_params = base_params.copy()
    if shift: count_sql += " AND r.id_shift = %s"; count_params.append(shift)

    shifts_sql = f"SELECT DISTINCT s.ID_shift, s.tarkib {base_join} ORDER BY s.tarkib"
    shifts_params = base_params.copy()

    stats_sql = f"""SELECT COALESCE(SUM(r.nomreh_kol),0) as earned_sum, COALESCE(SUM(c.kole_emtiaz),0) as max_sum, COUNT(*) as cnt {base_join}"""
    stats_params = base_params.copy()
    if shift: stats_sql += " AND r.id_shift = %s"; stats_params.append(shift)

    data = query(data_sql, data_params, fetch_all=True) or []
    total = query(count_sql, count_params, fetch_one=True)['total'] if query(count_sql, count_params, fetch_one=True) else 0
    available_shifts = [(r['ID_shift'], r['tarkib']) for r in (query(shifts_sql, shifts_params, fetch_all=True) or [])]

    for row in data:
        row['date_display'] = format_date_display(row.get('dat_sabt'))
        try:
            es = float(row.get('earned_score') or 0)
            ms = float(row.get('max_score') or 0)
            row['earned_score'] = round(es, 2)
            row['max_score'] = round(ms, 2)
            row['achievement_percent'] = round((es/ms*100), 1) if ms > 0 else 0
        except: row['achievement_percent'] = 0
        pct = row.get('achievement_percent', 0)
        if pct >= 90: row['quality_label'] = 'عالی'
        elif pct >= 75: row['quality_label'] = 'خوب'
        elif pct >= 50: row['quality_label'] = 'متوسط'
        else: row['quality_label'] = 'نیازمند بهبود'
        row['has_document'] = bool(row.get('sanad') and str(row['sanad']).strip() not in ['', 'nan', 'None'])

    stats_row = query(stats_sql, stats_params, fetch_one=True)
    earned = round(float(stats_row['earned_sum'] or 0), 1)
    max_s = round(float(stats_row['max_sum'] or 0), 1)
    cnt = int(stats_row['cnt'] or 0)
    pct = round((earned/max_s*100), 1) if max_s > 0 else 0
    if pct >= 90: lvl = 'سطح یک (عالی)'
    elif pct >= 75: lvl = 'سطح دو (خوب)'
    elif pct >= 50: lvl = 'سطح سه (متوسط)'
    else: lvl = 'سطح چهار (نیازمند بهبود)'

    # داده‌های تکمیلی برای تحلیل هوشمند
    dept_scores = {}
    for r in data:
        dname = r.get('department', 'نامشخص')
        if dname not in dept_scores: dept_scores[dname] = {'earned': 0, 'max': 0}
        dept_scores[dname]['earned'] += float(r.get('earned_score', 0))
        dept_scores[dname]['max'] += float(r.get('max_score', 0))

    dept_percents = {}
    for d, v in dept_scores.items():
        dept_percents[d] = round((v['earned'] / v['max'] * 100), 1) if v['max'] > 0 else 0

    strong_items = list(set(r.get('item_name','') for r in data if r.get('achievement_percent', 0) >= 90))
    weak_items = list(set(r.get('item_name','') for r in data if r.get('achievement_percent', 0) < 50))

    ai_summary = {
        'total_items': total,
        'total_earned': earned,
        'total_max': max_s,
        'overall_percent': pct,
        'safety_items': sum(1 for r in data if r.get('is_safety') == 1),
        'doc_items': sum(1 for r in data if r.get('has_document')),
        'departments': list(set(r.get('department', '') for r in data)),
        'quality_dist': {k: sum(1 for r in data if r.get('quality_label') == k) for k in ['عالی', 'خوب', 'متوسط', 'نیازمند بهبود']},
        'dept_percents': dept_percents,
        'strong_items': strong_items,
        'weak_items': weak_items,
        'trend_30_days': _calculate_trend(data)
    }

    stats = {'total': total, 'earned': str(earned), 'percent': pct, 'level': lvl}

    return {
        'data': data,
        'stats': stats,
        'total': total,
        'page': page,
        'per_page': per_page,
        'available_shifts': available_shifts,
        'ai_summary': ai_summary
    }


def _calculate_trend(data):
    """محاسبه روند ۳۰ روزه درصد تحقق برای تحلیل"""
    daily = {}
    for r in data:
        day = r.get('date_display','')[:10]
        if day not in daily: daily[day] = {'sum':0, 'count':0}
        daily[day]['sum'] += r.get('achievement_percent', 0)
        daily[day]['count'] += 1
    sorted_days = sorted(daily.keys())[-30:]
    trend = []
    for day in sorted_days:
        v = daily[day]
        trend.append(round(v['sum']/v['count'], 1) if v['count'] else 0)
    return dict(zip(sorted_days, trend))


def _build_table(data):
    if not data: return '<tr><td colspan="13" class="empty">داده‌ای یافت نشد</td></tr>'
    rows = []
    for r in data:
        qb = r.get('quality_label', 'متوسط')
        qc = 'badge-ex' if 'عالی' in str(qb) else ('badge-gd' if 'خوب' in str(qb) else ('badge-av' if 'متوسط' in str(qb) else 'badge-pr'))
        doc_display = f'<span class="badge" style="background:#6366f1;">📎 دارد</span>' if r.get('has_document') else '<span style="color:#94a3b8;">ندارد</span>'
        rows.append(f"<tr><td>{r.get('ID_arziabi_bakhsh','')}</td><td>{r.get('date_display','')}</td><td>{r.get('department','')}</td><td>{r.get('level','')}</td><td>{r.get('group_title','')}</td><td>{(r.get('item_name','') or '')[:50]}</td><td>{r.get('emtiaz',0)}</td><td>{r.get('earned_score',0)}</td><td>{r.get('max_score',0)}</td><td>{r.get('achievement_percent',0)}%</td><td><span class='badge {qc}'>{qb}</span></td><td>{'🛡️' if r.get('is_safety')==1 else '📋'}</td><td>{doc_display}</td></tr>")
    return ''.join(rows)


def _build_dashboard(data):
    return '<div class="empty">در حال بارگذاری نمودارها...</div>'


def api_data(request_args):
    return _fetch_data(
        request_args.get('from',''), request_args.get('to',''),
        request_args.get('dept',''), request_args.get('title',''),
        request_args.get('shift',''), request_args.get('safety',''),
        request_args.get('hasdoc',''), request_args.get('search',''),
        page=request_args.get('page', 1, type=int),
        per_page=request_args.get('per_page', 15, type=int)
    )


def api_export(request_args):
    import io; from openpyxl import Workbook; from flask import send_file
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('dept',''), request_args.get('title',''), request_args.get('shift',''), request_args.get('safety',''), request_args.get('hasdoc',''), request_args.get('search',''), page=1, per_page=9999)
    wb = Workbook(); ws = wb.active; ws.title = "گزارش راند"
    ws.append(['کد','تاریخ','بخش','سطح','گروه','سنجه','امتیاز','نمره','حداکثر','درصد','کیفیت','ایمنی','نکات مثبت','نکات منفی','توضیحات','ارزیاب','اسناد'])
    for r in d['data']: ws.append([r.get('ID_arziabi_bakhsh'),r.get('date_display'),r.get('department'),r.get('level'),r.get('group_title'),r.get('item_name'),r.get('emtiaz'),r.get('earned_score'),r.get('max_score'),f"{r.get('achievement_percent',0)}%",r.get('quality_label'),'ایمنی' if r.get('is_safety')==1 else 'عادی',r.get('nokhat_mosbat',''),r.get('nokat_manfi',''),r.get('tozihat',''),r.get('assessor',''),r.get('sanad','')])
    ws2 = wb.create_sheet("آمار"); ws2.append(['شاخص','مقدار']); s = d['stats']
    for k,v in [('کل ارزیابی‌ها',s['total']),('امتیاز نهایی',s['earned']),('درصد تحقق',f"{s['percent']}%"),('سطح',s['level'])]: ws2.append([k,v])
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='rounds_report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def api_print(request_args):
    import jdatetime
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''), request_args.get('dept',''), request_args.get('title',''), request_args.get('shift',''), request_args.get('safety',''), request_args.get('hasdoc',''), request_args.get('search',''), page=1, per_page=9999)
    today_j = jdatetime.date.today().strftime("%Y/%m/%d")
    data = d['data']
    groups = {}
    for r in data:
        dept = r.get('department','نامشخص')
        lvl = r.get('level','?')
        grp = r.get('group_title','نامشخص')
        if dept not in groups: groups[dept] = {}
        if lvl not in groups[dept]: groups[dept][lvl] = {}
        if grp not in groups[dept][lvl]: groups[dept][lvl][grp] = []
        groups[dept][lvl][grp].append(r)

    html = f'''<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><style>
        body{{font-family:Tahoma; padding:20px;}}h1{{text-align:center; color:#1e3a8a;}}
        .dept{{border:2px solid #1e3a8a; margin:20px 0; border-radius:10px; overflow:hidden;}}
        .dh{{background:#1e3a8a; color:white; padding:12px; font-size:16px;}}
        .lh{{color:#f59e0b; padding:8px 15px; font-weight:bold; border-right:4px solid #f59e0b; margin:10px 0;}}
        .gh{{background:#f8f9fa; padding:8px; font-weight:bold;}}
        table{{width:100%; border-collapse:collapse; margin:10px 0;}}th{{background:#e0e7ff; padding:7px; font-size:10px;}}
        td{{padding:6px; border:1px solid #ddd; text-align:center; font-size:10px;}}
        .ex td{{background:#d1fae5;}}.gd td{{background:#dbeafe;}}.av td{{background:#fed7aa;}}.pr td{{background:#fee2e2;}}
        .detail-row td{{background:#f9fafb; font-size:9px; color:#555; text-align:right;}}
        @media print{{body{{padding:10px;}}}}
    </style></head><body><h1>📊 گزارش راند - {today_j}</h1>'''
    for dept, levels in groups.items():
        dept_score = sum(r.get('earned_score',0) for l in levels.values() for g in l.values() for r in g)
        dept_max = sum(r.get('max_score',0) for l in levels.values() for g in l.values() for r in g)
        dept_pct = round(dept_score/dept_max*100,1) if dept_max>0 else 0
        html += f'<div class="dept"><div class="dh">🏥 {dept} | ⭐ {dept_score:.1f}/{dept_max:.1f} ({dept_pct}%)</div>'
        for lvl, grps in levels.items():
            html += f'<div class="lh">🔸 سطح {lvl}</div>'
            for grp, items in grps.items():
                html += f'''<div class="gh">📑 {grp} ({len(items)} سنجه)</div><table>
                    <tr><th>سنجه</th><th>امتیاز</th><th>نمره</th><th>حداکثر</th><th>درصد</th><th>کیفیت</th><th>اسناد</th></tr>'''
                for r in items:
                    pct = r.get('achievement_percent',0)
                    rc = 'ex' if pct>=90 else ('gd' if pct>=75 else ('av' if pct>=50 else 'pr'))
                    doc_badge = '📎 دارد' if r.get('has_document') else 'ندارد'
                    html += f'''<tr class="{rc}"><td style="text-align:right;">{r.get("item_name","")[:60]}{'...' if len(r.get("item_name",""))>60 else ''}</td>
                    <td>{r.get("emtiaz",0)}</td><td>{r.get("earned_score",0)}</td><td>{r.get("max_score",0)}</td><td>{pct}%</td><td>{r.get("quality_label","")}</td><td>{doc_badge}</td></tr>'''
                    pos = r.get('nokhat_mosbat') or '-'
                    neg = r.get('nokat_manfi') or '-'
                    desc = r.get('tozihat') or '-'
                    html += f'''<tr class="detail-row"><td colspan="7"><strong>🟢 مثبت:</strong> {pos} &nbsp;&nbsp;&nbsp; <strong>🔴 منفی:</strong> {neg} &nbsp;&nbsp;&nbsp; <strong>📝 توضیحات:</strong> {desc}</td></tr>'''
                html += '</table>'
        html += '</div>'
    html += '<script>window.print();</script></body></html>'
    return html


def api_analyze(request_args):
    d = _fetch_data(request_args.get('from',''), request_args.get('to',''),
                    request_args.get('dept',''), request_args.get('title',''),
                    request_args.get('shift',''), request_args.get('safety',''),
                    request_args.get('hasdoc',''), request_args.get('search',''),
                    page=1, per_page=9999)
    
    ai_summary = d.get('ai_summary', {})
    if not ai_summary or not ai_summary.get('total_items'):
        return {'success': False, 'message': 'داده‌ای برای تحلیل وجود ندارد'}

    deepseek_key = request_args.get('deepseek_key', '').strip()
    if deepseek_key:
        analysis = deepseek_analysis(deepseek_key, ai_summary)
        if analysis:
            return {'success': True, 'analysis': analysis, 'source_name': 'DeepSeek AI'}

    # تحلیل داخلی (همان تابع internal_analysis از ai_engine.py)
    analysis = internal_analysis(ai_summary)
    return {'success': True, 'analysis': analysis, 'source_name': 'تحلیل داخلی'}
    