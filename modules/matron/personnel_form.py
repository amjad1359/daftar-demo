"""
modules/matron/personnel_form.py — نسخه v3 (بهبودیافته با لیست‌های کشویی هوشمند)
"""

import os, json, jdatetime, re, io, html as html_module
from datetime import datetime
from models.database import query, get_connection
from openpyxl import Workbook
from flask import send_file
import pandas as pd
from utils.auto_log import log_crud
from utils.cache import cached_query

GROUP_OPTIONS = [
    'درمانی', 'پاراکلینیکی', 'خدماتی پشتیبانی', 'اداری',
    'موقت', 'سرپایی', 'تخصصی', 'فوق تخصصی', 'سایر'
]

PERSIAN_COLUMNS = {
    'ID_person': 'کد پرسنلی', 'nam': 'نام', 'famil': 'نام خانوادگی',
    'father_nam': 'نام پدر', 'kod_meli': 'کد ملی',
    'shenase_personli': 'شناسه پرسنلی', 'shom_shenasnameh': 'شماره شناسنامه',
    'jens': 'جنسیت', 'dat_tavalod': 'تاریخ تولد', 'mob_number': 'موبایل',
    'hom_number1': 'تلفن ثابت', 'other_number2': 'تلفن دیگر', 'adress': 'آدرس',
    'madrak': 'مقطع تحصیلی', 'madrak_nam': 'رشته تحصیلی',
    'vazit_khedmat': 'وضعیت استخدام', 'isActiv': 'فعال', 'list_pezeshk': 'پزشک',
    'specialty_id': 'کد تخصص', 'UserID': 'کاربر ثبت‌کننده',
    'dat_sabt': 'تاریخ ثبت', 'zaman_sabt': 'زمان ثبت',
    'nam_bakhsh': 'بخش', 'nam_shogl': 'عنوان شغلی',
    'takhasos': 'تخصص', 'nezam_pezeshki': 'شماره نظام پزشکی',
}

_SAFE_DEP_TABLES = {
    "tbl_hozor": "id_person",
    "tbl_ghaybat": "nam_person",
    "tbl_ankal": "nam_pezshk",
    "tbl_naghsh_kod": "id_person",
    "tbl_chart_bohran": "id_person",
    "tbl_sazema_person": "nam_person",
    "tbl_gozaresh": "UserID",
    "tbl_amliat_kod": "UserID",
    "tbl_blood_trans": "UserID",
    "tbl_blood_faravardeh": "UserID",
}

_SAFE_ORG_DEP_TABLES = {
    "tbl_hozor": "id_person",
    "tbl_ghaybat": "nam_person",
    "tbl_ankal": "nam_pezshk",
    "tbl_naghsh_kod": "id_person",
    "tbl_chart_bohran": "id_person",
}


def _esc(v):
    return html_module.escape(str(v or ''))


def format_date_display(d):
    if not d: return ''
    s = str(d)
    return f"{s[:4]}/{s[4:6]}/{s[6:]}" if len(s) == 8 else s


def format_date_int(s):
    if not s: return None
    s = re.sub(r'[^0-9]', '', s)
    return int(s) if len(s) == 8 else None


def _row_to_log_dict(row):
    if not row: return {}
    skip_keys = {'zaman_sabt', 'CreatedDate', 'UserID', 'dat_sabt'}
    log_row = {}
    for k, v in row.items():
        if k in skip_keys: continue
        if k in ('dat_tavalod', 'dat_vorod', 'dat_shoro', 'dat_payan', 'start_date', 'end_date', 'dat_sabt'):
            log_row[k] = format_date_display(v)
        else:
            log_row[k] = v
    return log_row


def _get_changed_fields(old_dict, new_dict):
    changes = {}
    for key, new_val in new_dict.items():
        if key == 'ID_person': continue
        old_val = old_dict.get(key)
        if str(old_val) != str(new_val):
            changes[key] = {"old": old_val, "new": new_val}
    return changes


# ══════════════════════════════════════════════════════════
# توابع کش
# ══════════════════════════════════════════════════════════

def _fetch_departments():
    return query("SELECT ID_nam_bakhsh, nam_bakhsh, grop FROM tbl_bakhsh ORDER BY nam_bakhsh", fetch_all=True) or []

def _fetch_job_titles():
    return query("SELECT ID_shoghl, nam_shogl FROM tbl_onvan_shoghl ORDER BY nam_shogl", fetch_all=True) or []

def _fetch_specialties():
    return query("SELECT ID_onvan_takhasos, nam_takhasos FROM tbl_onvan_takhasos ORDER BY nam_takhasos", fetch_all=True) or []

def _fetch_employment():
    return query("SELECT DISTINCT vazit_khedmat FROM tbl_person WHERE vazit_khedmat IS NOT NULL AND vazit_khedmat!='' ORDER BY vazit_khedmat", fetch_all=True) or []

def _fetch_degrees():
    rows = query("SELECT DISTINCT madrak FROM tbl_person WHERE madrak IS NOT NULL AND madrak!='' ORDER BY madrak", fetch_all=True) or []
    if rows: return rows
    return [{'madrak': d} for d in ["سیکل","دیپلم","کاردانی","کارشناسی","ارشد","دکترا","تخصص"]]

def _fetch_fields():
    return query("SELECT DISTINCT madrak_nam FROM tbl_person WHERE madrak_nam IS NOT NULL AND madrak_nam!='' ORDER BY madrak_nam", fetch_all=True) or []


# ══════════════════════════════════════════════════════════
# تولید HTML صفحه اصلی
# ══════════════════════════════════════════════════════════

def get_personnel_form(user):
    user_id   = user.get('UserID', 0)
    full_name = user.get('FullName', '')
    today_shamsi = jdatetime.date.today().strftime("%Y/%m/%d")

    departments    = cached_query('departments_list',  _fetch_departments,  ttl=600)
    job_titles     = cached_query('job_titles_list',   _fetch_job_titles,   ttl=600)
    specialties    = cached_query('specialties_list',  _fetch_specialties,  ttl=600)
    employment_list= cached_query('employment_list',   _fetch_employment,   ttl=600)
    degree_list    = cached_query('degree_list',       _fetch_degrees,      ttl=600)
    field_list     = cached_query('field_list',        _fetch_fields,       ttl=600)

    dept_options = '<option value="">--- انتخاب ---</option>' + ''.join(
        f'<option value="{_esc(d["ID_nam_bakhsh"])}">{_esc(d["nam_bakhsh"])}</option>' for d in departments)
    job_options = '<option value="">--- انتخاب ---</option>' + ''.join(
        f'<option value="{_esc(j["ID_shoghl"])}">{_esc(j["nam_shogl"])}</option>' for j in job_titles)
    spec_options = '<option value="">--- انتخاب ---</option>' + ''.join(
        f'<option value="{_esc(s["ID_onvan_takhasos"])}">{_esc(s["nam_takhasos"])}</option>' for s in specialties)
    degree_labels = ["", "سیکل", "دیپلم", "کاردانی", "کارشناسی", "ارشد", "دکترا", "تخصص"]
    degrees_html  = ''.join(f'<option value="{_esc(d)}">{d if d else "---"}</option>' for d in degree_labels)

    # تبدیل ایمن JSON
    depts_json   = json.dumps([{'id': str(d['ID_nam_bakhsh']), 'label': d['nam_bakhsh']} for d in departments], ensure_ascii=False).replace("<", "\\u003c")
    groups_json  = json.dumps([{'id': g, 'label': g} for g in GROUP_OPTIONS], ensure_ascii=False).replace("<", "\\u003c")
    specs_json   = json.dumps([{'id': str(s['ID_onvan_takhasos']), 'label': s['nam_takhasos']} for s in specialties], ensure_ascii=False).replace("<", "\\u003c")
    employs_json = json.dumps([{'id': e['vazit_khedmat'], 'label': e['vazit_khedmat']} for e in employment_list], ensure_ascii=False).replace("<", "\\u003c")
    degrees_json = json.dumps([{'id': d['madrak'], 'label': d['madrak']} for d in degree_list], ensure_ascii=False).replace("<", "\\u003c")
    fields_json  = json.dumps([{'id': f['madrak_nam'], 'label': f['madrak_nam']} for f in field_list], ensure_ascii=False).replace("<", "\\u003c")

    return f'''<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>مدیریت پرسنل</title>
<style>{_CSS}</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="container fade-in">

  <div class="personnel-header">
    <div><h2>👥 مدیریت جامع پرسنل</h2><p>👤 {_esc(full_name)}</p></div>
    <a href="/module/matron" class="back-btn">⬅️ بازگشت</a>
  </div>

  <div class="tabs">
    <button class="tab active"  onclick="switchTab('tab1')">📋 مدیریت پرسنل</button>
    <button class="tab"         onclick="switchTab('tab2')">🏥 پرسنل بر اساس بخش</button>
    <button class="tab"         onclick="switchTab('tab3')">👨‍⚕️ لیست پزشکان</button>
  </div>

  <div id="tab1" class="tab-content active">
    <div class="row" style="align-items:flex-start;gap:16px;">

      <div class="card" style="flex:0 0 310px;padding:15px;">
        <div style="display:flex;gap:8px;margin-bottom:10px;">
          <input type="text" id="person-search" class="form-input"
            placeholder="🔍 نام، خانوادگی یا کدملی..." oninput="debouncedSearch(1)" style="flex:1;">
        </div>
        <div style="display:flex;gap:8px;margin-bottom:10px;">
          <select id="person-status-filter" class="form-select" onchange="loadPersonList(1)" style="flex:1;">
            <option value="all">همه</option>
            <option value="active">فعال</option>
            <option value="inactive">غیرفعال</option>
          </select>
          <label class="check-label">
            <input type="checkbox" id="doctor-filter" onchange="loadPersonList(1)"> پزشکان
          </label>
        </div>
        <div class="person-list-wrapper" id="person-list">
          <div class="spinner-wrap"><div class="spinner"></div></div>
        </div>
        <div id="tab1-pagination" class="pagination"></div>
        <div class="count-info" id="person-count-info"></div>
        <button class="btn btn-primary" style="width:100%;margin-top:10px;" onclick="newPerson()">
          ➕ پرسنل جدید
        </button>
      </div>

      <div class="card" style="flex:1;min-width:0;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
          <h3 id="form-title" style="margin:0;font-size:16px;">📝 فرم پرسنل</h3>
          <div style="display:flex;align-items:center;gap:12px;">
            <div class="active-toggle-label">
              <span style="font-size:13px;">وضعیت:</span>
              <label class="toggle-switch">
                <input type="checkbox" id="isActivToggle" checked onchange="updateActiveHidden()">
                <span class="slider"></span>
              </label>
              <span id="active-status-text" style="font-size:13px;font-weight:600;">فعال</span>
            </div>
            <button class="btn btn-danger btn-sm" id="delete-person-btn"
              style="display:none;" onclick="deleteCurrentPerson()">🗑️ حذف</button>
          </div>
        </div>

        <form id="person-form" autocomplete="off">
          <input type="hidden" id="person-id" name="person_id" value="">
          <input type="hidden" id="isActivHidden" name="isActiv" value="1">

          <div class="inner-card">
            <div class="inner-card-title">📌 اطلاعات هویتی</div>
            <div class="row">
              <div class="form-group" style="flex:1;"><label>نام <span class="req">*</span></label>
                <input type="text" id="nam" name="nam" class="form-input" required autocomplete="off"></div>
              <div class="form-group" style="flex:1;"><label>نام خانوادگی <span class="req">*</span></label>
                <input type="text" id="famil" name="famil" class="form-input" required autocomplete="off"></div>
              <div class="form-group" style="flex:1;"><label>نام پدر</label>
                <input type="text" id="father_nam" name="father_nam" class="form-input"></div>
            </div>
            <div class="row">
              <div class="form-group" style="flex:1;">
                <label>کد ملی</label>
                <input type="text" id="kod_meli" name="kod_meli" class="form-input"
                  maxlength="10" inputmode="numeric" oninput="this.value=this.value.replace(/[^0-9]/g,'')"
                  onblur="validateNationalId(this)">
                <span class="field-hint" id="kod_meli_hint"></span>
              </div>
              <div class="form-group" style="flex:1;"><label>ش. شناسنامه</label>
                <input type="text" id="shom_shenasnameh" name="shom_shenasnameh" class="form-input"></div>
              <div class="form-group" style="flex:1;"><label>شناسه پرسنلی</label>
                <input type="text" id="shenase_personli" name="shenase_personli" class="form-input"></div>
            </div>
            <div class="row">
              <div class="form-group" style="flex:1;"><label>جنسیت</label>
                <select id="jens" name="jens" class="form-select">
                  <option value="مرد">مرد</option><option value="زن">زن</option>
                </select>
              </div>
              <div class="form-group" style="flex:1;"><label>تاریخ تولد</label>
                <input type="text" id="dat_tavalod" name="dat_tavalod"
                  class="form-input date-mask" placeholder="1370/01/01"></div>
              <div class="form-group" style="flex:1;"><label>تاریخ ورود</label>
                <input type="text" id="dat_vorod" name="dat_vorod"
                  class="form-input date-mask" value="{today_shamsi}"></div>
            </div>
          </div>

          <div class="inner-card">
            <div class="inner-card-title">📞 اطلاعات تماس</div>
            <div class="row">
              <div class="form-group" style="flex:1;"><label>موبایل</label>
                <input type="text" id="mob_number" name="mob_number" class="form-input"
                  maxlength="11" inputmode="numeric" oninput="this.value=this.value.replace(/[^0-9]/g,'')"></div>
              <div class="form-group" style="flex:1;"><label>تلفن ثابت</label>
                <input type="text" id="hom_number1" name="hom_number1" class="form-input"></div>
              <div class="form-group" style="flex:1;"><label>تلفن دیگر</label>
                <input type="text" id="other_number2" name="other_number2" class="form-input"></div>
            </div>
            <div class="form-group">
              <label>آدرس</label>
              <textarea id="adress" name="adress" class="form-textarea" rows="2"></textarea>
            </div>
          </div>

          <div class="inner-card">
            <div class="inner-card-title">🎓 تحصیلات و وضعیت شغلی</div>
            <div class="row">
              <div class="form-group" style="flex:1;"><label>مقطع تحصیلی</label>
                <select id="madrak" name="madrak" class="form-select">{degrees_html}</select>
              </div>
              <div class="form-group" style="flex:2;">
                <label>رشته تحصیلی</label>
                <div style="display:flex;gap:8px;">
                  <select id="madrak_nam_select" class="form-select" style="flex:1;" onchange="handleMajorSelect()">
                    <option value="">--- انتخاب ---</option>
                  </select>
                  <input type="text" id="madrak_nam_new" name="madrak_nam_new"
                    class="form-input" style="flex:1;display:none;" placeholder="رشته جدید...">
                </div>
              </div>
              <div class="form-group" style="flex:1;"><label>وضعیت استخدام</label>
                <select id="vazit_khedmat" name="vazit_khedmat" class="form-select">
                  <option value="رسمی">رسمی</option><option value="پیمانی">پیمانی</option>
                  <option value="قراردادی">قراردادی</option><option value="شرکتی">شرکتی</option>
                  <option value="طرحی">طرحی</option><option value="سایر">سایر</option>
                </select>
              </div>
            </div>
          </div>

          <div class="inner-card">
            <div class="inner-card-title">👨‍⚕️ وضعیت پزشک</div>
            <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
              <label class="check-label" style="font-size:14px;font-weight:600;">
                <input type="checkbox" id="list_pezeshk" name="list_pezeshk" onchange="toggleSpecialty()">
                پزشک است
              </label>
              <div class="form-group" id="specialty-group" style="flex:1;display:none;margin:0;">
                <label>تخصص</label>
                <select id="specialty_id" name="specialty_id" class="form-select">{spec_options}</select>
              </div>
            </div>
          </div>

          <div style="display:flex;gap:10px;margin-top:4px;">
            <button type="button" class="btn btn-primary" onclick="savePerson()">
              <span id="save-text">💾 ذخیره</span>
              <span id="save-loading" style="display:none;">⏳ در حال ذخیره...</span>
            </button>
            <button type="button" class="btn btn-outline" onclick="newPerson()">🔄 پرسنل جدید</button>
          </div>
        </form>
      </div>
    </div>

    <div class="card" id="org-section" style="display:none;">
      <div class="card-title">🏢 سوابق واحدها و سمت‌ها</div>
      <div class="org-form-row">
        <div class="form-group" style="flex:2;">
          <label>بخش</label>
          <select id="org-dept" class="form-select">{dept_options}</select>
        </div>
        <div class="form-group" style="flex:2;">
          <label>سمت / عنوان شغلی</label>
          <select id="org-job" class="form-select">{job_options}</select>
        </div>
        <div class="form-group" style="flex:1;">
          <label>تاریخ شروع</label>
          <input type="text" id="org-start" class="form-input date-mask" placeholder="1400/01/01">
        </div>
        <div class="form-group" style="flex:1;">
          <label>تاریخ پایان</label>
          <input type="text" id="org-end" class="form-input date-mask" placeholder="---">
        </div>
        <div class="form-group" style="flex:0;align-self:flex-end;padding-bottom:4px;">
          <label class="check-label">
            <input type="checkbox" id="org-finished" onchange="toggleOrgFinished()"> تایید پایانی
          </label>
        </div>
        <div style="align-self:flex-end;padding-bottom:2px;">
          <button class="btn btn-success btn-sm" onclick="saveOrgRecord()">💾 ذخیره</button>
          <button class="btn btn-outline btn-sm" onclick="clearOrgForm()" style="margin-right:6px;">✕ لغو</button>
        </div>
      </div>
      <input type="hidden" id="org-edit-id" value="">
      <div id="org-list"></div>
    </div>
  </div>

  <div id="tab2" class="tab-content">
    <div class="card">
      <div class="filter-bar">
        <div class="filter-bar-top">
          <span class="filter-bar-title">🔽 فیلترها</span>
          <button class="filter-toggle-btn" onclick="toggleFilterPanel('t2fp')">
            <span id="t2fp-badge" class="filter-badge" style="display:none;">0</span>
            نمایش / پنهان
          </button>
          <input type="text" id="tab2-search" class="form-input" style="flex:1;max-width:260px;"
            placeholder="🔍 جستجوی نام یا کد ملی..." oninput="debouncedTab2Search()">
          <select id="tab2-status-filter" class="form-select" style="width:130px;" onchange="loadTab2(1)">
            <option value="all">همه وضعیت‌ها</option>
            <option value="active">فعال</option>
            <option value="inactive">غیرفعال</option>
          </select>
          <button class="btn btn-primary btn-sm" onclick="loadTab2(1)">🔍 اعمال</button>
          <button class="btn btn-outline btn-sm" onclick="clearTab2Filters()">↺ پاک‌سازی</button>
          <button class="btn btn-success btn-sm" onclick="exportTab2Excel()">📥 Excel</button>
        </div>

        <div id="t2fp" class="filter-panel">
          
          <div class="filter-section">
            <div class="filter-section-label">🏥 بخش</div>
            <div class="ms-wrap" id="wrap-t2-dept">
              <div class="ms-box" id="box-t2-dept" tabindex="0">
                <span id="ph-t2-dept" class="ms-placeholder">انتخاب بخش...</span>
              </div>
              <div class="ms-drop" id="drop-t2-dept">
                <input class="ms-search" id="search-t2-dept" placeholder="جستجو...">
                <div id="list-t2-dept"></div>
              </div>
            </div>
          </div>

          <div class="filter-section">
            <div class="filter-section-label">🗂 گروه بخش</div>
            <div class="ms-wrap" id="wrap-t2-group">
              <div class="ms-box" id="box-t2-group" tabindex="0">
                <span id="ph-t2-group" class="ms-placeholder">انتخاب گروه...</span>
              </div>
              <div class="ms-drop" id="drop-t2-group">
                <input class="ms-search" id="search-t2-group" placeholder="جستجو...">
                <div id="list-t2-group"></div>
              </div>
            </div>
          </div>

          <div class="filter-section">
            <div class="filter-section-label">💼 وضعیت استخدام</div>
            <div class="ms-wrap" id="wrap-t2-employ">
              <div class="ms-box" id="box-t2-employ" tabindex="0">
                <span id="ph-t2-employ" class="ms-placeholder">انتخاب وضعیت...</span>
              </div>
              <div class="ms-drop" id="drop-t2-employ">
                <input class="ms-search" id="search-t2-employ" placeholder="جستجو...">
                <div id="list-t2-employ"></div>
              </div>
            </div>
          </div>

          <div class="filter-section">
            <div class="filter-section-label">🎓 مقطع تحصیلی</div>
            <div class="ms-wrap" id="wrap-t2-degree">
              <div class="ms-box" id="box-t2-degree" tabindex="0">
                <span id="ph-t2-degree" class="ms-placeholder">انتخاب مقطع...</span>
              </div>
              <div class="ms-drop" id="drop-t2-degree">
                <input class="ms-search" id="search-t2-degree" placeholder="جستجو...">
                <div id="list-t2-degree"></div>
              </div>
            </div>
          </div>

          <div class="filter-section">
            <div class="filter-section-label">📚 رشته تحصیلی</div>
            <div class="ms-wrap" id="wrap-t2-field">
              <div class="ms-box" id="box-t2-field" tabindex="0">
                <span id="ph-t2-field" class="ms-placeholder">انتخاب رشته...</span>
              </div>
              <div class="ms-drop" id="drop-t2-field">
                <input class="ms-search" id="search-t2-field" placeholder="جستجو...">
                <div id="list-t2-field"></div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <div id="tab2-stats" class="stats-grid"></div>

      <div class="table-wrapper">
        <table class="data-table" id="tab2-table">
          <thead><tr>
            <th>#</th><th>نام و نام خانوادگی</th><th>بخش</th>
            <th>سمت</th><th>مدرک</th><th>موبایل</th><th>وضعیت</th>
          </tr></thead>
          <tbody id="tab2-tbody"></tbody>
        </table>
      </div>
      <div id="tab2-pagination" class="pagination"></div>
      <div class="count-info" id="tab2-count-info"></div>
    </div>
  </div>

  <div id="tab3" class="tab-content">
    <div class="card">
      <div class="filter-bar">
        <div class="filter-bar-top">
          <span class="filter-bar-title">🔽 فیلترها</span>
          <button class="filter-toggle-btn" onclick="toggleFilterPanel('t3fp')">
            <span id="t3fp-badge" class="filter-badge" style="display:none;">0</span>
            نمایش / پنهان
          </button>
          <input type="text" id="tab3-search" class="form-input" style="flex:1;max-width:260px;"
            placeholder="🔍 نام پزشک یا کد ملی..." oninput="debouncedTab3Search()">
          <select id="tab3-status-filter" class="form-select" style="width:130px;" onchange="loadTab3(1)">
            <option value="all">همه وضعیت‌ها</option>
            <option value="active">فعال</option>
            <option value="inactive">غیرفعال</option>
          </select>
          <button class="btn btn-primary btn-sm" onclick="loadTab3(1)">🔍 اعمال</button>
          <button class="btn btn-outline btn-sm" onclick="clearTab3Filters()">↺ پاک‌سازی</button>
          <button class="btn btn-success btn-sm" onclick="exportTab3Excel()">📥 Excel</button>
        </div>
        
        <div id="t3fp" class="filter-panel">
          <div class="filter-section">
            <div class="filter-section-label">🩺 تخصص</div>
            <div class="ms-wrap" id="wrap-t3-spec">
              <div class="ms-box" id="box-t3-spec" tabindex="0">
                <span id="ph-t3-spec" class="ms-placeholder">انتخاب تخصص...</span>
              </div>
              <div class="ms-drop" id="drop-t3-spec">
                <input class="ms-search" id="search-t3-spec" placeholder="جستجو...">
                <div id="list-t3-spec"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div id="tab3-stats" class="stats-grid"></div>
      <div class="table-wrapper">
        <table class="data-table" id="tab3-table">
          <thead><tr>
            <th>#</th><th>نام پزشک</th><th>تخصص</th>
            <th>ش. نظام پزشکی</th><th>موبایل</th><th>وضعیت</th>
          </tr></thead>
          <tbody id="tab3-tbody"></tbody>
        </table>
      </div>
      <div id="tab3-pagination" class="pagination"></div>
      <div class="count-info" id="tab3-count-info"></div>
    </div>
  </div>

</div>

<script>
const todayShamsi = "{today_shamsi}";
let currentPersonId = null, currentMajors = [];
let tab1Page = 1, tab2Page = 1, tab3Page = 1;

// دیتاهای مربوط به منوهای کشویی
const MULTI_SELECTS = {{
  't2-dept':   {{ data: {depts_json},   sel: new Set(), badge: 't2fp-badge', onChange: () => loadTab2(1) }},
  't2-group':  {{ data: {groups_json},  sel: new Set(), badge: 't2fp-badge', onChange: () => loadTab2(1) }},
  't2-employ': {{ data: {employs_json}, sel: new Set(), badge: 't2fp-badge', onChange: () => loadTab2(1) }},
  't2-degree': {{ data: {degrees_json}, sel: new Set(), badge: 't2fp-badge', onChange: () => loadTab2(1) }},
  't2-field':  {{ data: {fields_json},  sel: new Set(), badge: 't2fp-badge', onChange: () => loadTab2(1) }},
  't3-spec':   {{ data: {specs_json},   sel: new Set(), badge: 't3fp-badge', onChange: () => loadTab3(1) }}
}};

function escapeHtml(text) {{
    const map = {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;' }};
    return String(text).replace(/[&<>"']/g, m => map[m]);
}}

/* ════════════════════════════════════════
   سیستم منوی کشویی چندگانه (Dropdown)
════════════════════════════════════════ */
function renderMsTags(k) {{
    const conf = MULTI_SELECTS[k];
    const box = document.getElementById('box-' + k);
    const ph = document.getElementById('ph-' + k);
    box.querySelectorAll('.ms-tag').forEach(t => t.remove());

    if (conf.sel.size === 0) {{
        ph.style.display = 'inline';
        return;
    }}
    ph.style.display = 'none';

    conf.sel.forEach(id => {{
        const item = conf.data.find(d => d.id === id);
        if (!item) return;
        const tag = document.createElement('div');
        tag.className = 'ms-tag';
        tag.innerHTML = escapeHtml(item.label) + '<span class="rm">×</span>';
        tag.querySelector('.rm').onclick = (e) => {{
            e.stopPropagation();
            conf.sel.delete(id);
            renderMsTags(k);
            renderMsDrop(k);
            updateBadge(conf.badge);
            conf.onChange();
        }};
        box.insertBefore(tag, ph);
    }});
}}

function toggleMsItem(k, id) {{
    const conf = MULTI_SELECTS[k];
    if (conf.sel.has(id)) conf.sel.delete(id);
    else conf.sel.add(id);
    renderMsTags(k);
    renderMsDrop(k);
    updateBadge(conf.badge);
    conf.onChange();
}}

function renderMsDrop(k) {{
    const conf = MULTI_SELECTS[k];
    const listEl = document.getElementById('list-' + k);
    const searchEl = document.getElementById('search-' + k);
    const q = (searchEl.value || "").trim().toLowerCase();
    const filtered = conf.data.filter(d => d.label.toLowerCase().includes(q));

    listEl.innerHTML = "";

    if (filtered.length > 0) {{
        const selectAllDiv = document.createElement("div");
        selectAllDiv.className = "ms-item";
        const isAllSelected = filtered.every(d => conf.sel.has(d.id));
        selectAllDiv.innerHTML = isAllSelected ? "❌ <strong>لغو انتخاب همه موارد</strong>" : "✅ <strong>انتخاب همه موارد این لیست</strong>";
        selectAllDiv.style.borderBottom = "1px dashed var(--border)";
        selectAllDiv.style.background = "#f8fafc";
        selectAllDiv.style.color = isAllSelected ? "var(--danger)" : "var(--primary)";

        selectAllDiv.onclick = (e) => {{
            e.stopPropagation();
            if (isAllSelected) {{
                filtered.forEach(d => conf.sel.delete(d.id));
            }} else {{
                filtered.forEach(d => conf.sel.add(d.id));
            }}
            renderMsTags(k);
            renderMsDrop(k);
            updateBadge(conf.badge);
            conf.onChange();
        }};
        listEl.appendChild(selectAllDiv);
    }}

    filtered.forEach(d => {{
        const div = document.createElement("div");
        div.className = "ms-item" + (conf.sel.has(d.id) ? " sel" : "");
        div.textContent = (conf.sel.has(d.id) ? "✅ " : "") + d.label;
        div.onclick = (e) => {{ e.stopPropagation(); toggleMsItem(k, d.id); }};
        listEl.appendChild(div);
    }});
}}

function openMsDrop(k) {{
    const drop = document.getElementById('drop-' + k);
    Object.keys(MULTI_SELECTS).forEach(otherK => {{
        if (otherK !== k) document.getElementById('drop-' + otherK).classList.remove('open');
    }});
    const isOpen = !drop.classList.contains('open');
    drop.classList.toggle('open', isOpen);
    if (isOpen) {{
        renderMsDrop(k);
        document.getElementById('search-' + k).focus();
    }}
}}

document.addEventListener("click", (e) => {{
    if (!e.target.closest(".ms-wrap")) {{
        document.querySelectorAll(".ms-drop").forEach(d => d.classList.remove("open"));
    }}
}});

function updateBadge(badgeId) {{
    let total = 0;
    if (badgeId === 't2fp-badge') {{
        total = MULTI_SELECTS['t2-dept'].sel.size + MULTI_SELECTS['t2-group'].sel.size + 
                MULTI_SELECTS['t2-employ'].sel.size + MULTI_SELECTS['t2-degree'].sel.size + MULTI_SELECTS['t2-field'].sel.size;
    }} else {{
        total = MULTI_SELECTS['t3-spec'].sel.size;
    }}
    const el = document.getElementById(badgeId);
    if (!el) return;
    if (total > 0) {{ el.textContent = total; el.style.display = 'inline-flex'; }}
    else           {{ el.style.display = 'none'; }}
}}

function toggleFilterPanel(id) {{
  const el = document.getElementById(id);
  if (el) el.classList.toggle('open');
}}

function clearTab2Filters() {{
  ['t2-dept', 't2-group', 't2-employ', 't2-degree', 't2-field'].forEach(k => {{
      MULTI_SELECTS[k].sel.clear();
      renderMsTags(k);
  }});
  document.getElementById('tab2-search').value = '';
  document.getElementById('tab2-status-filter').value = 'all';
  updateBadge('t2fp-badge');
  loadTab2(1);
}}

function clearTab3Filters() {{
  MULTI_SELECTS['t3-spec'].sel.clear();
  renderMsTags('t3-spec');
  document.getElementById('tab3-search').value = '';
  document.getElementById('tab3-status-filter').value = 'all';
  updateBadge('t3fp-badge');
  loadTab3(1);
}}

let t1Timer, t2Timer, t3Timer;
function debouncedSearch()     {{ clearTimeout(t1Timer); t1Timer = setTimeout(() => loadPersonList(1), 380); }}
function debouncedTab2Search() {{ clearTimeout(t2Timer); t2Timer = setTimeout(() => loadTab2(1), 380); }}
function debouncedTab3Search() {{ clearTimeout(t3Timer); t3Timer = setTimeout(() => loadTab3(1), 380); }}

function validateNationalId(inp) {{
  const v = inp.value.trim();
  const hint = document.getElementById('kod_meli_hint');
  if (!v) {{ inp.style.borderColor = ''; if(hint) hint.textContent=''; return; }}
  if (v.length !== 10 || /^(\\d)\\1{{9}}$/.test(v)) {{
    inp.style.borderColor = 'var(--danger)';
    if(hint) {{ hint.textContent = '⚠️ کد ملی نامعتبر'; hint.style.color='var(--danger)'; }}
    return;
  }}
  let s = 0;
  for (let i = 0; i < 9; i++) s += +v[i] * (10 - i);
  const r = s % 11, d = +v[9];
  const ok = (r < 2 && d === r) || (r >= 2 && d === 11 - r);
  inp.style.borderColor = ok ? 'var(--success)' : 'var(--danger)';
  if (hint) {{
    hint.textContent = ok ? '✅ معتبر' : '⚠️ کد ملی نامعتبر';
    hint.style.color = ok ? 'var(--success)' : 'var(--danger)';
  }}
}}

function validateShamsiDate(str) {{
  if (!str) return {{ valid:true, message:'' }};
  const parts = str.split('/');
  if (parts.length !== 3) return {{ valid:false, message:'فرمت: YYYY/MM/DD' }};
  const [y,m,d] = parts.map(Number);
  if (isNaN(y)||isNaN(m)||isNaN(d)) return {{ valid:false, message:'فقط عدد مجاز' }};
  if (y<1300||y>1500) return {{ valid:false, message:'سال ۱۳۰۰ تا ۱۵۰۰' }};
  if (m<1||m>12) return {{ valid:false, message:'ماه ۱ تا ۱۲' }};
  if (d<1||d>31) return {{ valid:false, message:'روز ۱ تا ۳۱' }};
  if (m>6&&m<12&&d>30) return {{ valid:false, message:'ماه‌های ۷-۱۱ حداکثر ۳۰ روز' }};
  return {{ valid:true, message:'' }};
}}

function applyDateMask(input) {{
  input.addEventListener('input', function() {{
    let v = this.value.replace(/[^0-9]/g,'').substring(0,8);
    let r = v.substring(0,4);
    if (v.length>4) r += '/' + v.substring(4,6);
    if (v.length>6) r += '/' + v.substring(6,8);
    this.value = r;
  }});
  input.addEventListener('blur', function() {{
    const res = validateShamsiDate(this.value.trim());
    this.style.borderColor = (!this.value||res.valid) ? '' : 'var(--danger)';
    if (!res.valid && this.value) showToast('⚠️ ' + res.message, 'error');
  }});
}}

function showToast(msg, type) {{
  const c = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = 'toast ' + (type === 'success' ? 'success' : 'error');
  t.innerHTML = `<span>${{type==='success'?'✅':'❌'}}</span><span>${{msg}}</span>
    <span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
  c.appendChild(t);
  setTimeout(() => {{ if(t.parentElement){{ t.style.opacity='0'; setTimeout(()=>t.remove(),300); }} }}, 4500);
}}

function switchTab(id) {{
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
  document.querySelector(`.tab[onclick*="'${{id}}'"]`)?.classList.add('active');
  document.getElementById(id)?.classList.add('active');
  if (id==='tab1') loadPersonList(tab1Page);
  else if(id==='tab2') loadTab2(tab2Page);
  else if(id==='tab3') loadTab3(tab3Page);
}}

function renderPagination(containerId, page, pages, cb) {{
  const c = document.getElementById(containerId);
  if (!c || pages<=1) {{ if(c) c.innerHTML=''; return; }}
  let h='';
  if(page>1) h+=`<button data-page="${{page-1}}">« قبل</button>`;
  let s=Math.max(1,page-2), e=Math.min(pages,page+2);
  for(let i=s;i<=e;i++) h+=`<button data-page="${{i}}" class="${{i===page?'active':''}}">${{i}}</button>`;
  if(page<pages) h+=`<button data-page="${{page+1}}">بعد »</button>`;
  c.innerHTML=h;
  c.onclick=ev=>{{ const b=ev.target.closest('button[data-page]'); if(b) cb(+b.dataset.page); }};
}}

function updateActiveHidden() {{
  const on = document.getElementById('isActivToggle').checked;
  document.getElementById('isActivHidden').value = on ? '1' : '0';
  document.getElementById('active-status-text').innerText = on ? 'فعال' : 'غیرفعال';
}}

async function loadPersonList(page) {{
  tab1Page = page || 1;
  const search = document.getElementById('person-search').value.trim();
  const status = document.getElementById('person-status-filter').value;
  const doctor = document.getElementById('doctor-filter').checked ? 1 : 0;
  document.getElementById('person-list').innerHTML = '<div class="spinner-wrap"><div class="spinner"></div></div>';
  try {{
    const res  = await fetch(`/module/matron/personnel/list?search=${{encodeURIComponent(search)}}&status=${{status}}&doctor=${{doctor}}&page=${{tab1Page}}&per_page=50`);
    if (!res.ok) throw new Error('خطای شبکه');
    const data = await res.json();
    const div  = document.getElementById('person-list');
    if (!data.records?.length) {{
      div.innerHTML = '<p class="empty-msg">پرسنلی یافت نشد</p>';
      document.getElementById('tab1-pagination').innerHTML = '';
      document.getElementById('person-count-info').innerText = 'تعداد: 0';
    }} else {{
      div.innerHTML = data.records.map(p => `
        <div class="person-card ${{currentPersonId==p.ID_person?'active':''}}" onclick="editPerson(${{p.ID_person}})">
          <div class="p-info">
            <span class="p-name">${{p.nam}} ${{p.famil}}</span>
            ${{p.list_pezeshk ? '<span class="badge badge-doctor">پزشک</span>' : ''}}
          </div>
          <div style="display:flex;gap:6px;align-items:center;">
            <span class="badge ${{p.isActiv?'badge-active':'badge-inactive'}}">${{p.isActiv?'فعال':'غیرفعال'}}</span>
            <small style="color:var(--light-gray);">${{p.kod_meli||''}}</small>
          </div>
        </div>`).join('');
      document.getElementById('person-count-info').innerText =
        `صفحه ${{data.page}} از ${{data.pages}} · کل: ${{data.total}}`;
      renderPagination('tab1-pagination', data.page, data.pages, loadPersonList);
    }}
    if(currentPersonId) document.getElementById('org-section').style.display='block';
  }} catch(e) {{ showToast('خطا در بارگذاری لیست', 'error'); }}
}}

async function newPerson() {{
  currentPersonId = null;
  document.getElementById('person-id').value = '';
  document.getElementById('form-title').innerText = '🆕 ثبت پرسنل جدید';
  document.getElementById('person-form').reset();
  document.getElementById('dat_vorod').value = todayShamsi;
  document.getElementById('isActivToggle').checked = true;
  updateActiveHidden();
  document.getElementById('specialty-group').style.display = 'none';
  document.getElementById('delete-person-btn').style.display = 'none';
  document.getElementById('org-section').style.display = 'none';
  document.getElementById('kod_meli_hint').textContent = '';
  clearOrgForm();
  await loadMajorDropdown();
  loadPersonList(tab1Page);
}}

async function editPerson(id) {{
  currentPersonId = id;
  clearOrgForm();
  try {{
    const res  = await fetch('/module/matron/personnel/get/' + id);
    const data = await res.json();
    if (!data.success) {{ showToast('خطا در دریافت اطلاعات', 'error'); return; }}
    const p = data.person;
    const set = (eid, val) => {{ const el=document.getElementById(eid); if(el) el.value=val||''; }};
    const setChk = (eid, val) => {{ const el=document.getElementById(eid); if(el) el.checked=!!val; }};
    set('person-id', p.ID_person);
    set('nam', p.nam); set('famil', p.famil); set('father_nam', p.father_nam);
    set('kod_meli', p.kod_meli); set('shom_shenasnameh', p.shom_shenasnameh);
    set('shenase_personli', p.shenase_personli); set('jens', p.jens||'مرد');
    set('dat_tavalod', p.dat_tavalod); set('dat_vorod', p.dat_vorod||todayShamsi);
    set('mob_number', p.mob_number); set('hom_number1', p.hom_number1);
    set('other_number2', p.other_number2); set('adress', p.adress);
    set('madrak', p.madrak); set('vazit_khedmat', p.vazit_khedmat||'رسمی');
    set('specialty_id', p.specialty_id);
    setChk('list_pezeshk', p.list_pezeshk==1);
    setChk('isActivToggle', p.isActiv==1);
    updateActiveHidden();
    document.getElementById('specialty-group').style.display = p.list_pezeshk?'block':'none';
    document.getElementById('delete-person-btn').style.display = 'inline-flex';
    document.getElementById('form-title').innerText = `✏️ ${{p.nam}} ${{p.famil}}`;
    document.getElementById('kod_meli_hint').textContent = '';
    await loadMajorDropdown(p.madrak_nam);
    document.getElementById('org-section').style.display = 'block';
    loadOrgHistory(id);
    loadPersonList(tab1Page);
  }} catch(e) {{ showToast('خطا در ارتباط با سرور', 'error'); }}
}}

async function loadMajorDropdown(sel=null) {{
  try {{
    const d = await (await fetch('/module/matron/personnel/majors')).json();
    currentMajors = d.majors||[];
    const s = document.getElementById('madrak_nam_select');
    s.innerHTML = '<option value="">--- انتخاب ---</option>' +
      currentMajors.map(m=>`<option value="${{m}}">${{m}}</option>`).join('') +
      '<option value="__new__">➕ مورد جدید...</option>';
    if (sel) {{
      s.value = currentMajors.includes(sel) ? sel : '__new__';
      document.getElementById('madrak_nam_new').style.display = s.value==='__new__' ? 'block':'none';
      if (s.value==='__new__') document.getElementById('madrak_nam_new').value = sel;
    }}
  }} catch(e) {{ showToast('خطا در بارگذاری رشته‌ها','error'); }}
}}

function handleMajorSelect() {{
  document.getElementById('madrak_nam_new').style.display =
    document.getElementById('madrak_nam_select').value==='__new__' ? 'block':'none';
}}

async function savePerson() {{
  for (const fid of ['dat_tavalod','dat_vorod']) {{
    const inp = document.getElementById(fid);
    if (inp.value) {{
      const r = validateShamsiDate(inp.value.trim());
      if (!r.valid) {{ showToast('⛔ '+r.message, 'error'); inp.focus(); return; }}
    }}
  }}
  const km = document.getElementById('kod_meli').value.trim();
  if (km && km.length!==10) {{ showToast('⛔ کد ملی باید ۱۰ رقم باشد','error'); return; }}

  const form = document.getElementById('person-form');
  const fd   = new FormData(form);
  const selMajor = document.getElementById('madrak_nam_select').value;
  fd.set('madrak_nam', selMajor==='__new__' ? document.getElementById('madrak_nam_new').value : selMajor);
  fd.set('list_pezeshk', document.getElementById('list_pezeshk').checked ? '1':'0');

  document.getElementById('save-text').style.display    = 'none';
  document.getElementById('save-loading').style.display = 'inline';
  try {{
    const res  = await fetch('/module/matron/personnel/save', {{method:'POST',body:fd}});
    const data = await res.json();
    if (data.success) {{
      showToast('✅ ذخیره شد','success');
      if (data.person_id) {{ currentPersonId=data.person_id; await editPerson(data.person_id); }}
    }} else showToast('⛔ '+data.message,'error');
  }} catch(e) {{ showToast('خطا در ذخیره','error'); }}
  finally {{
    document.getElementById('save-text').style.display    = 'inline';
    document.getElementById('save-loading').style.display = 'none';
  }}
}}

function toggleSpecialty() {{
  document.getElementById('specialty-group').style.display =
    document.getElementById('list_pezeshk').checked ? 'block':'none';
}}

async function deleteCurrentPerson() {{
  if (!currentPersonId) return;
  if (!confirm('آیا از حذف کامل این پرسنل اطمینان دارید؟\\nاین عمل غیرقابل بازگشت است.')) return;
  try {{
    const d = await (await fetch('/module/matron/personnel/delete/'+currentPersonId,{{method:'POST'}})).json();
    if (d.success) {{ showToast('✅ پرسنل حذف شد','success'); newPerson(); }}
    else showToast('⛔ '+d.message,'error');
  }} catch(e) {{ showToast('خطا','error'); }}
}}

async function loadOrgHistory(pid) {{
  try {{
    const d = await (await fetch('/module/matron/personnel/org_history/'+pid)).json();
    if (!d.records?.length) {{
      document.getElementById('org-list').innerHTML = '<p class="empty-msg" style="margin:12px 0;">بدون سابقه سازمانی</p>';
      return;
    }}
    document.getElementById('org-list').innerHTML = d.records.map(r => `
      <div class="org-record ${{r.payani_sazmandehi?'org-record-finished':''}}">
        <span class="org-col" style="min-width:160px;font-weight:600;">${{r.nam_bakhsh||'---'}}</span>
        <span class="org-col" style="min-width:130px;">${{r.nam_shogl||'---'}}</span>
        <span class="org-col" style="color:var(--gray);font-size:12px;">
          ${{r.start_display||''}} ${{r.end_display ? '← '+r.end_display : r.payani_sazmandehi?'(پایان)':'(در جریان)'}}
        </span>
        ${{r.payani_sazmandehi?'<span class="badge badge-inactive" style="flex:0;">پایان یافته</span>':
          '<span class="badge badge-active" style="flex:0;">فعال</span>'}}
        <div class="org-actions">
          <button class="btn btn-primary btn-xs" onclick="editOrgRecord(${{r.ID_sazman_person}})">✏️</button>
          <button class="btn btn-danger btn-xs" onclick="deleteOrgRecord(${{r.ID_sazman_person}})">🗑️</button>
          <button class="btn btn-xs" style="background:#8b5cf6;color:white;"
            onclick="openIntroLetter(${{r.ID_sazman_person}})">📄 معرفی‌نامه</button>
        </div>
      </div>`).join('');
  }} catch(e) {{ showToast('خطا در بارگذاری سوابق','error'); }}
}}

function clearOrgForm() {{
  ['org-dept','org-job','org-start','org-end'].forEach(id => {{ const el=document.getElementById(id); if(el) el.value=''; }});
  document.getElementById('org-finished').checked = false;
  document.getElementById('org-edit-id').value = '';
}}

function toggleOrgFinished() {{
  document.getElementById('org-end').value =
    document.getElementById('org-finished').checked ? todayShamsi : '';
}}

async function saveOrgRecord() {{
  const pid = document.getElementById('person-id').value;
  if (!pid) {{ showToast('ابتدا پرسنل را ذخیره کنید','error'); return; }}
  const start = document.getElementById('org-start').value;
  if (start) {{
    const r = validateShamsiDate(start);
    if (!r.valid) {{ showToast('تاریخ شروع: '+r.message,'error'); return; }}
  }}
  const fd = new FormData();
  fd.append('person_id', pid);
  fd.append('dept_id', document.getElementById('org-dept').value);
  fd.append('job_id', document.getElementById('org-job').value);
  fd.append('start_date', start);
  fd.append('end_date', document.getElementById('org-end').value);
  fd.append('finished', document.getElementById('org-finished').checked?'1':'0');
  const eid = document.getElementById('org-edit-id').value;
  if (eid) fd.append('org_id', eid);
  try {{
    const d = await (await fetch('/module/matron/personnel/save_org',{{method:'POST',body:fd}})).json();
    if (d.success) {{ showToast('✅ ذخیره شد','success'); clearOrgForm(); loadOrgHistory(currentPersonId); }}
    else showToast(d.message,'error');
  }} catch(e) {{ showToast('خطا','error'); }}
}}

async function editOrgRecord(orgId) {{
  try {{
    const d = await (await fetch('/module/matron/personnel/get_org/'+orgId)).json();
    if (d.success) {{
      const r = d.record;
      document.getElementById('org-edit-id').value   = r.ID_sazman_person;
      document.getElementById('org-dept').value      = r.nam_bakhsh;
      document.getElementById('org-job').value       = r.shoghl;
      document.getElementById('org-start').value     = r.start_display||'';
      document.getElementById('org-end').value       = r.end_display||(r.payani_sazmandehi?todayShamsi:'');
      document.getElementById('org-finished').checked= r.payani_sazmandehi==1;
    }} else showToast('خطا','error');
  }} catch(e) {{ showToast('خطا','error'); }}
}}

async function deleteOrgRecord(orgId) {{
  if (!confirm('این سابقه حذف شود؟')) return;
  try {{
    const d = await (await fetch('/module/matron/personnel/delete_org/'+orgId,{{method:'POST'}})).json();
    if (d.success) {{ showToast('✅ حذف شد','success'); loadOrgHistory(currentPersonId); }}
    else showToast(d.message,'error');
  }} catch(e) {{ showToast('خطا','error'); }}
}}

function openIntroLetter(orgId) {{ window.open('/module/matron/personnel/intro_letter/'+orgId,'_blank'); }}

async function loadTab2(page) {{
  tab2Page = page||1;
  const p = new URLSearchParams();
  MULTI_SELECTS['t2-dept'].sel.forEach(v => p.append('dept', v));
  MULTI_SELECTS['t2-group'].sel.forEach(v => p.append('grop', v));
  MULTI_SELECTS['t2-employ'].sel.forEach(v => p.append('employment', v));
  MULTI_SELECTS['t2-degree'].sel.forEach(v => p.append('degree', v));
  MULTI_SELECTS['t2-field'].sel.forEach(v => p.append('field', v));
  p.append('status',  document.getElementById('tab2-status-filter').value);
  p.append('search',  document.getElementById('tab2-search').value.trim());
  p.append('page',    tab2Page);
  p.append('per_page', 20);

  const tbody = document.getElementById('tab2-tbody');
  tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:24px;"><div class="spinner" style="margin:auto;"></div></td></tr>';
  try {{
    const data = await (await fetch('/module/matron/personnel/tab2?'+p)).json();
    renderStats('tab2-stats', data, ['without_dept','duplicate_count'],
      ['بدون بخش','تکرار در چند بخش']);
    if (!data.records?.length) {{
      tbody.innerHTML = '<tr><td colspan="7" class="empty-msg">موردی یافت نشد</td></tr>';
    }} else {{
      let i = (tab2Page-1)*20;
      tbody.innerHTML = data.records.map(r => `
        <tr>
          <td style="color:var(--light-gray);width:38px;">${{++i}}</td>
          <td style="font-weight:600;">${{r.FullName}}</td>
          <td><span class="tbl-badge dept">${{r.nam_bakhsh}}</span></td>
          <td>${{r.nam_shogl}}</td>
          <td>${{r.madrak||''}}</td>
          <td dir="ltr" style="font-size:12px;">${{r.Mobile||''}}</td>
          <td><span class="badge ${{r.is_active?'badge-active':'badge-inactive'}}">${{r.is_active?'فعال':'غیرفعال'}}</span></td>
        </tr>`).join('');
    }}
    document.getElementById('tab2-count-info').innerText =
      `صفحه ${{data.page}} از ${{data.pages}} · کل: ${{data.total}}`;
    renderPagination('tab2-pagination', data.page, data.pages, loadTab2);
  }} catch(e) {{ showToast('خطا در بارگذاری','error'); }}
}}

function exportTab2Excel() {{
  const p = new URLSearchParams();
  MULTI_SELECTS['t2-dept'].sel.forEach(v => p.append('dept', v));
  MULTI_SELECTS['t2-group'].sel.forEach(v => p.append('grop', v));
  MULTI_SELECTS['t2-employ'].sel.forEach(v => p.append('employment', v));
  MULTI_SELECTS['t2-degree'].sel.forEach(v => p.append('degree', v));
  MULTI_SELECTS['t2-field'].sel.forEach(v => p.append('field', v));
  p.append('status', document.getElementById('tab2-status-filter').value);
  p.append('search', document.getElementById('tab2-search').value);
  window.open('/module/matron/personnel/excel/tab2?'+p,'_blank');
}}

async function loadTab3(page) {{
  tab3Page = page||1;
  const p = new URLSearchParams();
  MULTI_SELECTS['t3-spec'].sel.forEach(v => p.append('spec', v));
  p.append('status',   document.getElementById('tab3-status-filter').value);
  p.append('search',   document.getElementById('tab3-search').value.trim());
  p.append('page',     tab3Page);
  p.append('per_page', 20);

  const tbody = document.getElementById('tab3-tbody');
  tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:24px;"><div class="spinner" style="margin:auto;"></div></td></tr>';
  try {{
    const data = await (await fetch('/module/matron/personnel/tab3?'+p)).json();
    renderStats('tab3-stats', data, [], []);
    if (!data.records?.length) {{
      tbody.innerHTML = '<tr><td colspan="6" class="empty-msg">موردی یافت نشد</td></tr>';
    }} else {{
      let i = (tab3Page-1)*20;
      tbody.innerHTML = data.records.map(r => `
        <tr>
          <td style="color:var(--light-gray);width:38px;">${{++i}}</td>
          <td style="font-weight:600;">${{r.nam_doctor}}</td>
          <td><span class="tbl-badge spec">${{r.takhasos}}</span></td>
          <td dir="ltr">${{r.nezam_pezeshki||''}}</td>
          <td dir="ltr" style="font-size:12px;">${{r.Mobile||''}}</td>
          <td><span class="badge ${{r.is_active?'badge-active':'badge-inactive'}}">${{r.is_active?'فعال':'غیرفعال'}}</span></td>
        </tr>`).join('');
    }}
    document.getElementById('tab3-count-info').innerText =
      `صفحه ${{data.page}} از ${{data.pages}} · کل: ${{data.total}}`;
    renderPagination('tab3-pagination', data.page, data.pages, loadTab3);
  }} catch(e) {{ showToast('خطا در بارگذاری','error'); }}
}}

function exportTab3Excel() {{
  const p = new URLSearchParams();
  MULTI_SELECTS['t3-spec'].sel.forEach(v => p.append('spec', v));
  p.append('status', document.getElementById('tab3-status-filter').value);
  p.append('search', document.getElementById('tab3-search').value);
  window.open('/module/matron/personnel/excel/tab3?'+p,'_blank');
}}

function renderStats(containerId, data, extraKeys, extraLabels) {{
  const el = document.getElementById(containerId);
  if (!el) return;
  const cards = [
    {{v: data.total,    l: 'کل', color:'var(--primary)'}},
    {{v: data.active,   l: 'فعال', color:'var(--success)'}},
    {{v: data.inactive, l: 'غیرفعال', color:'var(--danger)'}},
    ...extraKeys.map((k,i) => ({{v: data[k]||0, l: extraLabels[i], color:'var(--warning)'}}))
  ];
  el.innerHTML = cards.map(c =>
    `<div class="stat-card">
       <div class="stat-value" style="color:${{c.color}}">${{c.v}}</div>
       <div class="stat-label">${{c.l}}</div>
     </div>`).join('');
}}

document.addEventListener('DOMContentLoaded', () => {{
  document.querySelectorAll('.date-mask').forEach(applyDateMask);
  const os = document.getElementById('org-start');
  if (os) os.addEventListener('focus', () => {{ if(!os.value) os.value=todayShamsi; }});

  // راه‌اندازی منوهای کشویی
  Object.keys(MULTI_SELECTS).forEach(k => {{
      const box = document.getElementById('box-' + k);
      if (box) box.onclick = (e) => {{ e.stopPropagation(); openMsDrop(k); }};
      
      const search = document.getElementById('search-' + k);
      if (search) search.oninput = () => renderMsDrop(k);
      
      renderMsTags(k);
  }});

  loadPersonList(1);
  loadMajorDropdown();
}});
</script>
</body></html>'''


# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════

_CSS = """
@font-face{font-family:'Vazirmatn';src:url('/static/fonts/vazirmatn/Vazirmatn-Regular.woff2') format('woff2');font-weight:normal;}
:root{
  --primary:#1e3a8a;--primary-light:#3b82f6;--primary-soft:#eef2ff;
  --success:#10b981;--danger:#ef4444;--warning:#f59e0b;
  --dark:#1e293b;--gray:#64748b;--light-gray:#94a3b8;
  --border:#e2e8f0;--bg:#f1f5f9;--white:#fff;
  --radius:14px;--tr:0.22s cubic-bezier(.4,0,.2,1);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Vazirmatn','Segoe UI',Tahoma,sans-serif;direction:rtl;background:var(--bg);color:var(--dark);line-height:1.6;min-height:100vh;}

.fade-in{animation:fadeIn .4s ease both;}
@keyframes fadeIn{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}

.container{max-width:1500px;margin:0 auto;padding:16px 20px;}

.personnel-header{background:linear-gradient(135deg,#0f766e,#14b8a6);color:white;border-radius:20px;
  padding:20px 28px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;
  box-shadow:0 8px 28px rgba(15,118,110,.28);}
.personnel-header h2{font-size:22px;font-weight:700;margin:0;}
.personnel-header p{font-size:12px;opacity:.85;margin:2px 0 0;}
.back-btn{background:rgba(255,255,255,.12);color:white;text-decoration:none;padding:9px 18px;
  border:1px solid rgba(255,255,255,.25);border-radius:10px;font-size:13px;font-weight:600;
  backdrop-filter:blur(4px);transition:var(--tr);}
.back-btn:hover{background:rgba(255,255,255,.22);}

.tabs{display:flex;gap:4px;margin-bottom:20px;border-bottom:2px solid var(--border);}
.tab{padding:11px 22px;font-weight:600;border:none;background:none;color:var(--light-gray);
  cursor:pointer;border-bottom:3px solid transparent;transition:var(--tr);font-family:inherit;font-size:14px;}
.tab:hover{color:var(--dark);}
.tab.active{color:var(--primary)!important;border-bottom-color:var(--primary)!important;
  background:rgba(30,58,138,.05);font-weight:700;}
.tab-content{display:none;}
.tab-content.active{display:block;animation:fadeIn .3s ease;}

.card{background:rgba(255,255,255,.9);backdrop-filter:blur(10px);border-radius:var(--radius);
  padding:20px 22px;border:1px solid rgba(226,232,240,.8);
  box-shadow:0 4px 16px rgba(0,0,0,.04);margin-bottom:20px;}
.card-title{font-weight:700;color:var(--dark);margin-bottom:16px;padding-bottom:10px;
  border-bottom:2px solid var(--border);font-size:15px;}
.inner-card{background:#f8fafc;border:1px solid var(--border);border-radius:10px;
  padding:14px 16px;margin-bottom:14px;}
.inner-card-title{font-weight:700;font-size:13px;color:var(--gray);margin-bottom:12px;
  padding-bottom:8px;border-bottom:1px solid var(--border);}

.row{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap;}
.form-group{margin-bottom:14px;min-width:0;}
.form-group label{display:block;font-size:12px;font-weight:600;color:var(--gray);margin-bottom:4px;}
.form-select,.form-input,.form-textarea{
  width:100%;padding:9px 13px;border:2px solid var(--border);border-radius:10px;
  font-size:13px;font-family:inherit;transition:var(--tr);background:var(--white);}
.form-select:focus,.form-input:focus,.form-textarea:focus{
  border-color:var(--primary-light);outline:none;box-shadow:0 0 0 3px rgba(59,130,246,.1);}
.form-textarea{min-height:72px;resize:vertical;}
.req{color:var(--danger);margin-right:2px;}
.field-hint{font-size:11px;font-weight:600;display:block;margin-top:3px;}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:9px 17px;
  border:none;border-radius:10px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;
  transition:all .2s;white-space:nowrap;}
.btn:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.1);}
.btn:active{transform:translateY(0);}
.btn-primary{background:var(--primary);color:white;}
.btn-success{background:var(--success);color:white;}
.btn-danger{background:var(--danger);color:white;}
.btn-outline{background:white;color:var(--dark);border:2px solid var(--border);}
.btn-outline:hover{border-color:var(--primary-light);color:var(--primary);}
.btn-sm{padding:7px 13px;font-size:12px;}
.btn-xs{padding:4px 9px;font-size:11px;border-radius:6px;}

.check-label{display:inline-flex;align-items:center;gap:7px;cursor:pointer;font-weight:600;font-size:13px;white-space:nowrap;}
.check-label input{width:16px;height:16px;cursor:pointer;accent-color:var(--primary);}

.toggle-switch{position:relative;display:inline-block;width:50px;height:25px;}
.toggle-switch input{opacity:0;width:0;height:0;}
.slider{position:absolute;cursor:pointer;inset:0;background:#cbd5e1;transition:.35s;border-radius:25px;}
.slider:before{position:absolute;content:"";height:19px;width:19px;left:3px;bottom:3px;
  background:white;transition:.35s;border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,.2);}
input:checked+.slider{background:var(--success);}
input:checked+.slider:before{transform:translateX(25px);}
.active-toggle-label{display:flex;align-items:center;gap:8px;}

.person-list-wrapper{min-height:280px;max-height:480px;overflow-y:auto;padding-right:2px;}
.person-list-wrapper::-webkit-scrollbar{width:5px;}
.person-list-wrapper::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px;}
.person-card{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;
  background:white;border:1.5px solid var(--border);border-radius:10px;margin-bottom:7px;
  cursor:pointer;transition:var(--tr);}
.person-card:hover,.person-card.active{border-color:var(--primary);background:var(--primary-soft);transform:translateX(-2px);}
.p-info{flex:1;}
.p-name{font-weight:700;font-size:13px;}

.badge{padding:2px 9px;border-radius:20px;font-size:11px;font-weight:600;display:inline-block;}
.badge-active{background:#d1fae5;color:#065f46;}
.badge-inactive{background:#fee2e2;color:#991b1b;}
.badge-doctor{background:#dbeafe;color:#1e40af;}
.tbl-badge{padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;}
.tbl-badge.dept{background:#ede9fe;color:#5b21b6;}
.tbl-badge.spec{background:#d1fae5;color:#065f46;}

.org-form-row{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;margin-bottom:14px;
  background:#f8fafc;border:1px solid var(--border);border-radius:10px;padding:14px;}
.org-record{display:flex;align-items:center;gap:10px;padding:10px 14px;
  border-bottom:1px solid var(--border);flex-wrap:wrap;}
.org-record:last-child{border-bottom:none;}
.org-col{flex:1;}
.org-actions{display:flex;gap:6px;flex-shrink:0;}
.org-record-finished{background:#fafafa;opacity:.8;}
.org-record-finished .org-col{text-decoration:line-through;color:var(--light-gray);}

/* ══════════ پنل فیلترها و لیست‌های کشویی ══════════ */
.filter-bar{background:#f8fafc;border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:16px;}
.filter-bar-top{display:flex;gap:10px;align-items:center;flex-wrap:wrap;}
.filter-bar-title{font-weight:700;font-size:14px;white-space:nowrap;color:var(--dark);}
.filter-toggle-btn{display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border:2px solid var(--border);border-radius:8px;background:white;cursor:pointer;font-family:inherit;font-size:13px;font-weight:600;transition:var(--tr);position:relative;}
.filter-toggle-btn:hover{border-color:var(--primary-light);color:var(--primary);}
.filter-badge{background:var(--danger);color:white;border-radius:20px;padding:1px 7px;font-size:11px;font-weight:700;min-width:20px;text-align:center;}

.filter-panel{display:none;margin-top:14px;border-top:1px solid var(--border);padding-top:14px;display:grid;grid-template-columns:repeat(auto-fill, minmax(220px, 1fr));gap:14px;}
.filter-panel.open{display:grid;}
.filter-section{display:flex;flex-direction:column;gap:6px;}
.filter-section-label{font-size:12px;font-weight:700;color:var(--gray);}

/* استایل لیست‌های کشویی هوشمند */
.ms-wrap{position:relative;}
.ms-box{border:2px solid var(--border);border-radius:8px;padding:5px;min-height:42px;display:flex;flex-wrap:wrap;gap:5px;cursor:text;transition:var(--tr);background:var(--white);}
.ms-box:focus-within{border-color:var(--primary-light);box-shadow:0 0 0 3px rgba(59,130,246,.15);}
.ms-placeholder{color:var(--light-gray);font-size:12px;padding:4px;}
.ms-tag{display:inline-flex;align-items:center;gap:4px;background:#dbeafe;color:#1e40af;border-radius:6px;padding:3px 8px;font-size:12px;font-weight:600;}
.ms-tag .rm{cursor:pointer;color:#3b82f6;font-size:14px;line-height:1;}
.ms-tag .rm:hover{color:#1e3a8a;}
.ms-drop{position:absolute;z-index:100;background:var(--white);border:2px solid var(--primary-light);border-radius:8px;max-height:220px;overflow-y:auto;min-width:100%;top:100%;margin-top:4px;box-shadow:0 8px 24px rgba(0,0,0,.12);display:none;}
.ms-drop.open{display:block;}
.ms-search{width:100%;padding:8px 12px;border:none;border-bottom:1px solid var(--border);font-size:13px;outline:none;font-family:inherit;}
.ms-item{padding:9px 12px;cursor:pointer;font-size:12px;display:flex;align-items:center;gap:8px;border-bottom:1px solid #f8fafc;}
.ms-item:hover{background:#eff6ff;}
.ms-item.sel{background:#dbeafe;color:#1e40af;font-weight:600;}

/* ══════════ جدول و آمار ══════════ */
.table-wrapper{overflow-x:auto;border-radius:10px;border:1px solid var(--border);}
.data-table{width:100%;border-collapse:collapse;}
.data-table thead th{background:var(--primary);color:white;padding:10px 12px;text-align:center;font-size:13px;position:sticky;top:0;z-index:1;font-weight:700;}
.data-table tbody tr{transition:background .15s;}
.data-table tbody tr:nth-child(even){background:#f8fafc;}
.data-table tbody tr:hover{background:var(--primary-soft);}
.data-table td{padding:8px 12px;text-align:center;border-bottom:1px solid var(--border);font-size:13px;}
.data-table .empty-msg{text-align:center;color:var(--light-gray);padding:32px;}

.stats-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:12px;margin-bottom:16px;}
.stat-card{background:white;border-radius:10px;padding:14px;text-align:center;border:1px solid var(--border);box-shadow:0 2px 6px rgba(0,0,0,.03);transition:var(--tr);}
.stat-card:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.07);}
.stat-value{font-size:24px;font-weight:800;line-height:1.2;}
.stat-label{font-size:11px;color:var(--gray);margin-top:3px;font-weight:600;}

.pagination{display:flex;gap:5px;justify-content:center;margin-top:12px;flex-wrap:wrap;}
.pagination button{padding:5px 11px;border:1.5px solid var(--border);border-radius:7px;background:white;cursor:pointer;font-family:inherit;font-size:13px;font-weight:600;transition:var(--tr);}
.pagination button:hover{border-color:var(--primary-light);color:var(--primary);}
.pagination button.active{background:var(--primary);color:white;border-color:var(--primary);}
.pagination button:disabled{opacity:.4;cursor:default;}
.count-info{text-align:center;margin-top:8px;font-size:12px;color:var(--gray);}

/* ══════════ توست و متفرقه ══════════ */
.toast-container{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:100000;display:flex;flex-direction:column;gap:10px;pointer-events:none;align-items:center;}
.toast{display:flex;align-items:center;gap:12px;padding:14px 24px;border-radius:12px;color:white;font-size:14px;font-weight:600;box-shadow:0 12px 40px rgba(0,0,0,.3);animation:toastPop .4s cubic-bezier(.68,-.55,.27,1.55);pointer-events:auto;min-width:260px;}
.toast.success{background:linear-gradient(135deg,#059669,#10b981);}
.toast.error{background:linear-gradient(135deg,#dc2626,#ef4444);}
.toast-close{margin-right:auto;cursor:pointer;opacity:.8;font-size:16px;}
.toast-close:hover{opacity:1;}
@keyframes toastPop{0%{opacity:0;transform:scale(.7);}80%{transform:scale(1.04);}100%{opacity:1;transform:scale(1);}}

.spinner-wrap{display:flex;justify-content:center;align-items:center;padding:32px;}
.spinner{width:30px;height:30px;border:3px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin .7s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}
.empty-msg{color:var(--light-gray);text-align:center;padding:20px;font-size:14px;}

@media(max-width:768px){
  .personnel-header{flex-direction:column;gap:12px;text-align:center;}
  .stats-grid{grid-template-columns:repeat(2,1fr);}
  .filter-bar-top{flex-direction:column;align-items:stretch;}
  .org-form-row{flex-direction:column;}
  .filter-panel{grid-template-columns:1fr;}
}
"""


# ══════════════════════════════════════════════════════════
# API — لیست پرسنل
# ══════════════════════════════════════════════════════════

def get_personnel_list_api(search, status, doctor_only, page=1, per_page=50):
    page     = max(1, int(page or 1))
    per_page = max(1, min(200, int(per_page or 50)))
    offset   = (page - 1) * per_page

    base_sql = "FROM tbl_person WHERE 1=1"
    params   = []

    if status == 'active':
        base_sql += " AND isActiv = 1"
    elif status == 'inactive':
        base_sql += " AND (isActiv = 0 OR isActiv IS NULL)"
    if str(doctor_only) == '1':
        base_sql += " AND list_pezeshk = 1"
    if search:
        base_sql += " AND (nam LIKE %s OR famil LIKE %s OR kod_meli LIKE %s)"
        s = f'%{search}%'
        params.extend([s, s, s])

    total_row = query(f"SELECT COUNT(*) as cnt {base_sql}", params, fetch_one=True)
    total     = total_row['cnt'] if total_row else 0
    records   = query(
        f"SELECT ID_person, nam, famil, kod_meli, isActiv, list_pezeshk {base_sql}"
        f" ORDER BY famil, nam LIMIT %s OFFSET %s",
        params + [per_page, offset], fetch_all=True
    ) or []
    pages = max(1, (total + per_page - 1) // per_page)
    return {'records': records, 'total': total, 'page': page, 'pages': pages}


def get_person_detail(person_id):
    try:
        person_id = int(person_id)
    except (TypeError, ValueError):
        return {'success': False, 'message': 'شناسه نامعتبر'}
    rec = query("SELECT * FROM tbl_person WHERE ID_person = %s", (person_id,), fetch_one=True)
    if not rec:
        return {'success': False, 'message': 'پرسنل یافت نشد'}
    for f in ['dat_tavalod', 'dat_vorod']:
        v = rec.get(f)
        rec[f] = format_date_display(v) if v not in [0, None, ''] else ''
    for k in list(rec.keys()):
        if isinstance(rec[k], bytearray):
            rec[k] = rec[k].decode('utf-8')
    return {'success': True, 'person': rec}


def save_personnel(user, form_data):
    user_id   = user.get('UserID', 0)
    person_id = form_data.get('person_id') or None

    nam   = (form_data.get('nam', '') or '').strip()
    famil = (form_data.get('famil', '') or '').strip()
    if not nam or not famil:
        return {'success': False, 'message': 'نام و نام خانوادگی الزامی است'}

    data = {
        'nam':              nam,
        'famil':            famil,
        'father_nam':       (form_data.get('father_nam', '') or '').strip(),
        'kod_meli':         (form_data.get('kod_meli', '') or '').strip() or None,
        'shom_shenasnameh': (form_data.get('shom_shenasnameh', '') or '').strip() or '',
        'shenase_personli': (form_data.get('shenase_personli', '') or '').strip() or None,
        'jens':             form_data.get('jens', 'مرد'),
        'dat_tavalod':      format_date_int(form_data.get('dat_tavalod')),
        'dat_vorod':        format_date_int(form_data.get('dat_vorod')),
        'mob_number':       (form_data.get('mob_number', '') or '').strip() or None,
        'hom_number1':      (form_data.get('hom_number1', '') or '').strip() or '',
        'other_number2':    (form_data.get('other_number2', '') or '').strip() or '',
        'adress':           (form_data.get('adress', '') or '').strip() or '',
        'madrak':           form_data.get('madrak', ''),
        'madrak_nam':       (form_data.get('madrak_nam', '') or '').strip(),
        'vazit_khedmat':    form_data.get('vazit_khedmat', 'رسمی'),
        'isActiv':          1 if form_data.get('isActiv') == '1' else 0,
        'list_pezeshk':     1 if form_data.get('list_pezeshk') == '1' else 0,
        'specialty_id':     form_data.get('specialty_id') or None,
    }

    if data['kod_meli']:
        km = data['kod_meli']
        if len(km) != 10 or not km.isdigit():
            return {'success': False, 'message': 'کد ملی باید دقیقاً ۱۰ رقم عددی باشد'}
        dup = query("SELECT ID_person FROM tbl_person WHERE kod_meli=%s", (km,), fetch_one=True)
        if dup and (not person_id or dup['ID_person'] != int(person_id)):
            return {'success': False, 'message': 'کد ملی در سیستم تکراری است'}

    if data['shenase_personli']:
        dup = query("SELECT ID_person FROM tbl_person WHERE shenase_personli=%s",
                    (data['shenase_personli'],), fetch_one=True)
        if dup and (not person_id or dup['ID_person'] != int(person_id)):
            return {'success': False, 'message': 'شناسه پرسنلی در سیستم تکراری است'}

    if data['isActiv'] == 0 and person_id:
        a = query(
            "SELECT COUNT(*) as cnt FROM tbl_sazema_person WHERE nam_person=%s AND payani_sazmandehi=0",
            (person_id,), fetch_one=True)
        if a and a['cnt'] > 0:
            return {'success': False, 'message': 'این پرسنل دارای سوابق فعال است. ابتدا تایید پایانی ثبت کنید'}

    conn = get_connection()
    new_id = None
    try:
        cursor = conn.cursor()
        if person_id:
            cursor.execute("""
                UPDATE tbl_person SET nam=%s,famil=%s,father_nam=%s,kod_meli=%s,
                shenase_personli=%s,shom_shenasnameh=%s,dat_tavalod=%s,dat_vorod=%s,
                jens=%s,mob_number=%s,hom_number1=%s,other_number2=%s,adress=%s,
                madrak=%s,madrak_nam=%s,vazit_khedmat=%s,isActiv=%s,list_pezeshk=%s,
                specialty_id=%s WHERE ID_person=%s
            """, (data['nam'], data['famil'], data['father_nam'], data['kod_meli'],
                  data['shenase_personli'], data['shom_shenasnameh'], data['dat_tavalod'],
                  data['dat_vorod'], data['jens'], data['mob_number'], data['hom_number1'],
                  data['other_number2'], data['adress'], data['madrak'], data['madrak_nam'],
                  data['vazit_khedmat'], data['isActiv'], data['list_pezeshk'],
                  data['specialty_id'], person_id))
            conn.commit()
            new_id = int(person_id)
        else:
            d_sabt = int(jdatetime.date.today().strftime("%Y%m%d"))
            cursor.execute("""
                INSERT INTO tbl_person
                (nam,famil,father_nam,kod_meli,shenase_personli,shom_shenasnameh,
                 dat_tavalod,dat_vorod,jens,mob_number,hom_number1,other_number2,
                 adress,madrak,madrak_nam,vazit_khedmat,isActiv,list_pezeshk,
                 specialty_id,UserID,dat_sabt,zaman_sabt)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (data['nam'], data['famil'], data['father_nam'], data['kod_meli'],
                  data['shenase_personli'], data['shom_shenasnameh'], data['dat_tavalod'],
                  data['dat_vorod'], data['jens'], data['mob_number'], data['hom_number1'],
                  data['other_number2'], data['adress'], data['madrak'], data['madrak_nam'],
                  data['vazit_khedmat'], data['isActiv'], data['list_pezeshk'],
                  data['specialty_id'], user_id, d_sabt, datetime.now()))
            conn.commit()
            new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        log_crud('save_person', user_id, key_value=new_id,
                 new_value=json.dumps(data, ensure_ascii=False, default=str))
        return {'success': True, 'person_id': new_id}
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return {'success': False, 'message': f'خطا در ذخیره: {str(e)}'}


def delete_personnel_api(user, person_id):
    user_id = user.get('UserID', 0)
    try:
        person_id = int(person_id)
    except (TypeError, ValueError):
        return {'success': False, 'message': 'شناسه نامعتبر'}

    person = query("SELECT * FROM tbl_person WHERE ID_person=%s", (person_id,), fetch_one=True)
    if not person:
        return {'success': False, 'message': 'پرسنل یافت نشد'}

    for table, column in _SAFE_DEP_TABLES.items():
        row = query(
            f"SELECT COUNT(*) AS cnt FROM `{table}` WHERE `{column}`=%s",
            (person_id,), fetch_one=True)
        if row and row['cnt'] > 0:
            return {'success': False,
                    'message': f'پرسنل در جدول {table} رکورد فعال دارد و قابل حذف نیست'}

    try:
        query("DELETE FROM tbl_person WHERE ID_person=%s", (person_id,), commit=True)
        log_crud('delete_personnel', user_id, key_value=person_id,
                 old_value=json.dumps(person, ensure_ascii=False, default=str))
        return {'success': True, 'message': 'پرسنل با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا در حذف: {str(e)}'}


def get_majors_api():
    rows = query(
        "SELECT DISTINCT madrak_nam FROM tbl_person"
        " WHERE madrak_nam IS NOT NULL AND madrak_nam != '' ORDER BY madrak_nam",
        fetch_all=True) or []
    return {'majors': [r['madrak_nam'] for r in rows]}


def get_org_history_api(person_id):
    try:
        person_id = int(person_id)
    except (TypeError, ValueError):
        return {'records': []}
    rows = query("""
        SELECT s.ID_sazman_person, s.nam_bakhsh, s.shoghl,
               s.dat_shoro, s.dat_payan, s.payani_sazmandehi,
               b.nam_bakhsh, o.nam_shogl
        FROM   tbl_sazema_person s
        LEFT JOIN tbl_bakhsh b       ON s.nam_bakhsh = b.ID_nam_bakhsh
        LEFT JOIN tbl_onvan_shoghl o ON s.shoghl = o.ID_shoghl
        WHERE  s.nam_person = %s
        ORDER  BY s.dat_shoro DESC
    """, (person_id,), fetch_all=True) or []
    for r in rows:
        r['start_display'] = format_date_display(r['dat_shoro'])
        r['end_display']   = format_date_display(r['dat_payan']) if r['payani_sazmandehi'] else ''
    return {'records': rows}


def get_org_record_api(org_id):
    try:
        org_id = int(org_id)
    except (TypeError, ValueError):
        return {'success': False}
    r = query("SELECT * FROM tbl_sazema_person WHERE ID_sazman_person=%s", (org_id,), fetch_one=True)
    if not r:
        return {'success': False}
    r['start_display'] = format_date_display(r['dat_shoro'])
    r['end_display']   = format_date_display(r['dat_payan'])
    return {'success': True, 'record': r}


def save_org_record_api(user, form_data):
    user_id   = user.get('UserID', 0)
    org_id    = form_data.get('org_id') or None
    person_id = form_data.get('person_id')
    dept      = form_data.get('dept_id')
    job       = form_data.get('job_id')
    finished  = 1 if form_data.get('finished') == '1' else 0
    start     = format_date_int(form_data.get('start_date'))
    end       = format_date_int(form_data.get('end_date')) if finished else None
    if finished and not end:
        end = int(jdatetime.date.today().strftime("%Y%m%d"))
    if not person_id or not dept or not job:
        return {'success': False, 'message': 'بخش و سمت سازمانی الزامی است'}

    conn = get_connection()
    try:
        cursor = conn.cursor()
        if org_id:
            old = query("SELECT * FROM tbl_sazema_person WHERE ID_sazman_person=%s",
                        params=(org_id,), fetch_one=True)
            cursor.execute("""
                UPDATE tbl_sazema_person
                SET nam_bakhsh=%s, shoghl=%s, dat_shoro=%s,
                    dat_payan=%s, payani_sazmandehi=%s
                WHERE ID_sazman_person=%s
            """, (dept, job, start, end, finished, org_id))
            conn.commit()
            cursor.close()
            conn.close()
            log_crud('save_org_record', user_id, key_value=org_id,
                     old_value=json.dumps(old, ensure_ascii=False, default=str))
        else:
            cursor.execute(
                "SELECT 1 FROM tbl_sazema_person"
                " WHERE nam_person=%s AND nam_bakhsh=%s AND shoghl=%s AND payani_sazmandehi=0",
                (person_id, dept, job))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return {'success': False, 'message': 'این سابقه سازمانی فعال قبلاً ثبت شده است'}
            d_sabt = int(jdatetime.date.today().strftime("%Y%m%d"))
            cursor.execute("""
                INSERT INTO tbl_sazema_person
                (nam_person,nam_bakhsh,shoghl,dat_shoro,dat_payan,
                 payani_sazmandehi,UserID,dat_sabt,zaman_sabt)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (person_id, dept, job, start, end, finished, user_id, d_sabt, datetime.now()))
            conn.commit()
            new_org_id = cursor.lastrowid
            cursor.close()
            conn.close()
            log_crud('save_org_record', user_id, key_value=new_org_id,
                     new_value=json.dumps(
                         {'person_id': person_id, 'dept': dept, 'job': job,
                          'start': start, 'finished': finished},
                         ensure_ascii=False))
        return {'success': True}
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
        return {'success': False, 'message': str(e)}


def delete_org_record_api(user, org_id):
    user_id = user.get('UserID', 0)
    try:
        org_id = int(org_id)
    except (TypeError, ValueError):
        return {'success': False, 'message': 'شناسه نامعتبر'}

    old = query("SELECT * FROM tbl_sazema_person WHERE ID_sazman_person=%s",
                params=(org_id,), fetch_one=True)
    if not old:
        return {'success': False, 'message': 'سابقه مورد نظر یافت نشد'}

    person_id = old['nam_person']
    for table, column in _SAFE_ORG_DEP_TABLES.items():
        row = query(
            f"SELECT COUNT(*) AS cnt FROM `{table}` WHERE `{column}`=%s",
            (person_id,), fetch_one=True)
        if row and row['cnt'] > 0:
            return {'success': False,
                    'message': f'این پرسنل در جدول {table} رکورد دارد؛ سابقه قابل حذف نیست'}
    try:
        query("DELETE FROM tbl_sazema_person WHERE ID_sazman_person=%s", (org_id,), commit=True)
        log_crud('delete_org_record', user_id, key_value=org_id,
                 old_value=json.dumps(old, ensure_ascii=False, default=str))
        return {'success': True, 'message': 'سابقه با موفقیت حذف شد'}
    except Exception as e:
        return {'success': False, 'message': f'خطا: {str(e)}'}


# ══════════════════════════════════════════════════════════
# API — تب ۲ (پرسنل بر اساس بخش)
# ══════════════════════════════════════════════════════════

def _build_tab2_filters(dept, grop, status, search, employment, degree, field):
    dept  = [d for d in (dept or [])  if d]
    grop  = [g for g in (grop or [])  if g]
    params, filters = [], []

    if dept:
        filters.append(f" AND s.nam_bakhsh IN ({','.join(['%s']*len(dept))})")
        params.extend(dept)
    if grop:
        filters.append(f" AND b.grop IN ({','.join(['%s']*len(grop))})")
        params.extend(grop)
    if status == 'active':
        filters.append(" AND p.isActiv = 1")
    elif status == 'inactive':
        filters.append(" AND (p.isActiv = 0 OR p.isActiv IS NULL)")
    if search:
        filters.append(" AND (p.nam LIKE %s OR p.famil LIKE %s OR p.kod_meli LIKE %s)")
        s = f'%{search}%'
        params.extend([s, s, s])
    if employment:
        filters.append(" AND p.vazit_khedmat = %s")
        params.append(employment)
    if degree:
        filters.append(" AND p.madrak = %s")
        params.append(degree)
    if field:
        filters.append(" AND p.madrak_nam = %s")
        params.append(field)

    return "".join(filters), params


_TAB2_FROM = """FROM tbl_person p
        LEFT JOIN tbl_sazema_person s
            ON p.ID_person = s.nam_person
           AND (s.payani_sazmandehi = 0 OR s.payani_sazmandehi IS NULL)
        LEFT JOIN tbl_bakhsh b       ON s.nam_bakhsh = b.ID_nam_bakhsh
        LEFT JOIN tbl_onvan_shoghl o ON s.shoghl = o.ID_shoghl
        WHERE p.list_pezeshk = 0"""


def get_tab2_data(dept=None, grop=None, status='', search='',
                  employment='', degree='', field='', page=1, per_page=20):
    page, per_page = int(page), int(per_page)
    offset = (page - 1) * per_page

    filter_sql, params = _build_tab2_filters(dept, grop, status, search, employment, degree, field)

    total_r  = query(f"SELECT COUNT(DISTINCT p.ID_person) cnt {_TAB2_FROM}{filter_sql}", params, fetch_one=True)
    total    = total_r['cnt'] if total_r else 0

    active_r = query(f"SELECT COUNT(DISTINCT p.ID_person) cnt {_TAB2_FROM}{filter_sql} AND p.isActiv=1", params, fetch_one=True)
    active   = active_r['cnt'] if active_r else 0

    dup_r = query(
        f"SELECT COUNT(*) cnt FROM ("
        f"  SELECT p.ID_person {_TAB2_FROM}{filter_sql}"
        f"  GROUP BY p.ID_person HAVING COUNT(s.ID_sazman_person)>1"
        f") _t",
        params, fetch_one=True)
    dup_count = dup_r['cnt'] if dup_r else 0

    without_dept = 0
    if not [d for d in (dept or []) if d] and not [g for g in (grop or []) if g]:
        _, base_params = _build_tab2_filters([], [], status, search, employment, degree, field)
        base_filter    = _build_tab2_filters([], [], status, search, employment, degree, field)[0]
        wo_r = query(
            f"SELECT COUNT(DISTINCT p.ID_person) cnt"
            f" FROM tbl_person p"
            f" WHERE p.list_pezeshk=0{base_filter}"
            f" AND NOT EXISTS("
            f"   SELECT 1 FROM tbl_sazema_person s2"
            f"   WHERE s2.nam_person=p.ID_person"
            f"   AND (s2.payani_sazmandehi=0 OR s2.payani_sazmandehi IS NULL))",
            base_params, fetch_one=True)
        without_dept = wo_r['cnt'] if wo_r else 0

    records = query(
        f"SELECT p.ID_person, CONCAT(p.nam,' ',p.famil) FullName,"
        f"       p.kod_meli, p.mob_number Mobile, p.madrak,"
        f"       p.isActiv is_active, b.nam_bakhsh, o.nam_shogl"
        f" {_TAB2_FROM}{filter_sql}"
        f" ORDER BY b.nam_bakhsh, p.famil LIMIT %s OFFSET %s",
        params + [per_page, offset], fetch_all=True) or []

    for r in records:
        r['nam_bakhsh'] = r['nam_bakhsh'] or 'ثبت نشده'
        r['nam_shogl']  = r['nam_shogl']  or 'ثبت نشده'
        r['Mobile']     = r['Mobile']     or ''
        r['madrak']     = r['madrak']     or ''

    return {
        'records':         records,
        'total':           total,
        'active':          active,
        'inactive':        total - active,
        'without_dept':    without_dept,
        'duplicate_count': dup_count,
        'page':            page,
        'pages':           max(1, (total + per_page - 1) // per_page),
    }


def get_tab2_full_data(dept=None, grop=None, status='', search='',
                       employment='', degree='', field=''):
    filter_sql, params = _build_tab2_filters(dept, grop, status, search, employment, degree, field)
    records = query(
        f"SELECT p.*, b.nam_bakhsh, o.nam_shogl"
        f" {_TAB2_FROM}{filter_sql}"
        f" ORDER BY b.nam_bakhsh, p.famil",
        params, fetch_all=True) or []
    for r in records:
        for f in ['dat_tavalod', 'dat_vorod', 'dat_sabt']:
            r[f] = format_date_display(r.get(f))
        for k in list(r.keys()):
            if isinstance(r[k], bytearray):
                r[k] = r[k].decode('utf-8')
    return records


def export_tab2_excel(dept=None, grop=None, status='', search='',
                      employment='', degree='', field=''):
    return _to_excel(
        get_tab2_full_data(dept, grop, status, search, employment, degree, field),
        'پرسنل', 'personnel_by_dept.xlsx')


# ══════════════════════════════════════════════════════════
# API — تب ۳ (پزشکان)
# ══════════════════════════════════════════════════════════

_TAB3_FROM = ("FROM tbl_person p"
              " LEFT JOIN tbl_onvan_takhasos t ON p.specialty_id=t.ID_onvan_takhasos"
              " WHERE p.list_pezeshk=1")


def _build_tab3_filters(spec, status, search):
    spec   = [s for s in (spec or []) if s]
    params, filters = [], []
    if spec:
        filters.append(f" AND p.specialty_id IN ({','.join(['%s']*len(spec))})")
        params.extend(spec)
    if status == 'active':
        filters.append(" AND p.isActiv=1")
    elif status == 'inactive':
        filters.append(" AND (p.isActiv=0 OR p.isActiv IS NULL)")
    if search:
        filters.append(" AND (p.nam LIKE %s OR p.famil LIKE %s OR p.kod_meli LIKE %s OR t.nam_takhasos LIKE %s)")
        s = f'%{search}%'
        params.extend([s, s, s, s])
    return "".join(filters), params


def get_tab3_data(spec=None, status='', search='', page=1, per_page=20):
    page, per_page = int(page), int(per_page)
    offset = (page - 1) * per_page
    filter_sql, params = _build_tab3_filters(spec, status, search)

    total_r  = query(f"SELECT COUNT(*) cnt {_TAB3_FROM}{filter_sql}", params, fetch_one=True)
    total    = total_r['cnt'] if total_r else 0
    active_r = query(f"SELECT COUNT(*) cnt {_TAB3_FROM}{filter_sql} AND p.isActiv=1", params, fetch_one=True)
    active   = active_r['cnt'] if active_r else 0

    records = query(
        f"SELECT p.ID_person,"
        f"       CONCAT(p.nam,' ',p.famil) nam_doctor,"
        f"       p.kod_meli, p.mob_number Mobile,"
        f"       p.isActiv is_active,"
        f"       t.nam_takhasos takhasos,"
        f"       p.shom_shenasnameh nezam_pezeshki"
        f" {_TAB3_FROM}{filter_sql}"
        f" ORDER BY p.famil LIMIT %s OFFSET %s",
        params + [per_page, offset], fetch_all=True) or []
    for r in records:
        r['takhasos']       = r['takhasos']       or 'ثبت نشده'
        r['Mobile']         = r['Mobile']         or ''
        r['nezam_pezeshki'] = r['nezam_pezeshki'] or ''

    return {
        'records':  records,
        'total':    total,
        'active':   active,
        'inactive': total - active,
        'page':     page,
        'pages':    max(1, (total + per_page - 1) // per_page),
    }


def get_tab3_full_data(spec=None, status='', search=''):
    filter_sql, params = _build_tab3_filters(spec, status, search)
    records = query(
        f"SELECT p.*, t.nam_takhasos AS takhasos,"
        f"       p.shom_shenasnameh AS nezam_pezeshki"
        f" {_TAB3_FROM}{filter_sql}"
        f" ORDER BY p.famil",
        params, fetch_all=True) or []
    for r in records:
        for f in ['dat_tavalod', 'dat_vorod', 'dat_sabt']:
            r[f] = format_date_display(r.get(f))
        for k in list(r.keys()):
            if isinstance(r[k], bytearray):
                r[k] = r[k].decode('utf-8')
    return records


def export_tab3_excel(spec=None, status='', search=''):
    return _to_excel(get_tab3_full_data(spec, status, search), 'پزشکان', 'doctors.xlsx')


# ══════════════════════════════════════════════════════════
# کمکی Excel
# ══════════════════════════════════════════════════════════

def _to_excel(records, sheet_name, download_name):
    if not records:
        df = pd.DataFrame(columns=['نام', 'نام خانوادگی'])
    else:
        df = pd.DataFrame(records)
        cols = [c for c in PERSIAN_COLUMNS if c in df.columns]
        df   = df[cols].copy().rename(columns=PERSIAN_COLUMNS)
        if 'فعال' in df.columns:
            df['فعال'] = df['فعال'].apply(lambda x: 'فعال' if x == 1 else 'غیرفعال')
        if 'پزشک' in df.columns:
            df['پزشک'] = df['پزشک'].apply(lambda x: 'بله' if x == 1 else 'خیر')
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=download_name)


# ══════════════════════════════════════════════════════════
# معرفی‌نامه
# ══════════════════════════════════════════════════════════

def get_intro_letter_html(org_id):
    org = query("""
        SELECT s.*, s.nam_bakhsh AS dept_id, b.nam_bakhsh, o.nam_shogl
        FROM   tbl_sazema_person s
        LEFT JOIN tbl_bakhsh b       ON s.nam_bakhsh = b.ID_nam_bakhsh
        LEFT JOIN tbl_onvan_shoghl o ON s.shoghl = o.ID_shoghl
        WHERE  s.ID_sazman_person = %s
    """, (org_id,), fetch_one=True)
    if not org:
        return "<h2>سابقه مورد نظر یافت نشد</h2>"

    person = query("SELECT * FROM tbl_person WHERE ID_person=%s",
                   (org['nam_person'],), fetch_one=True)
    if not person:
        return "<h2>اطلاعات پرسنل یافت نشد</h2>"

    logo_res       = query("SELECT setting_value FROM site_settings WHERE setting_key='hospital_logo'",   fetch_one=True)
    center_res     = query("SELECT setting_value FROM site_settings WHERE setting_key='center_name'",     fetch_one=True)
    sub_center_res = query("SELECT setting_value FROM site_settings WHERE setting_key='sub_center_name'", fetch_one=True)

    logo_src        = f"/{logo_res['setting_value']}"      if logo_res       and logo_res['setting_value']       else ''
    center_name     = center_res['setting_value']           if center_res     and center_res['setting_value']     else 'نام مرکز اصلی'
    sub_center_name = sub_center_res['setting_value']       if sub_center_res and sub_center_res['setting_value'] else 'نام بیمارستان'

    today_j       = jdatetime.date.today()
    today_shamsi  = today_j.strftime("%Y/%m/%d")
    month_day     = today_j.strftime("%m%d")
    letter_number = f"{person['ID_person']}/{org['dept_id']}/{month_day}"
    full_name     = f"{person['nam']} {person['famil']}"
    gender        = person.get('jens', 'مرد')
    intro_title   = 'خواهر' if gender == 'زن' else 'برادر'
    start_date    = format_date_display(org['dat_shoro']) if org.get('dat_shoro') else ''
    logo_html     = f'<img src="{_esc(logo_src)}" style="height:70px;" alt="لوگو">' if logo_src else ''

    return f'''<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<title>معرفی‌نامه پرسنل</title>
<style>
@page {{ size:A5; margin:15mm; }}
body {{ font-family:Tahoma,Arial,sans-serif; direction:rtl; background:white; color:#1e293b; margin:0; padding:0; }}
.letter {{ width:100%; }}
.header {{ display:flex; justify-content:space-between; align-items:center;
           border-bottom:2px solid #1e3a8a; padding-bottom:10px; margin-bottom:20px; }}
.center-names {{ flex:1; text-align:center; }}
.center-names .main {{ font-size:16px; font-weight:bold; color:#1e3a8a; }}
.center-names .sub  {{ font-size:14px; color:#475569; margin-top:3px; }}
.header-left {{ font-size:13px; color:#334155; line-height:2; text-align:left; }}
.content {{ font-size:14px; line-height:2; text-align:justify; }}
.details-table {{ width:100%; border-collapse:collapse; margin:15px 0; font-size:13px; }}
.details-table td {{ padding:6px 10px; border:1px solid #94a3b8; }}
.details-table td:first-child {{ background:#f1f5f9; font-weight:bold; width:35%; }}
.signature {{ margin-top:30px; text-align:center; }}
.sig-line  {{ border-top:1px dashed #64748b; width:180px; margin:40px auto 10px; }}
@media print {{ body {{ margin:0; padding:0; }} }}
</style>
</head>
<body>
<div class="letter">
  <div class="header">
    <div>{logo_html}</div>
    <div class="center-names">
      <div class="main">{_esc(center_name)}</div>
      <div class="sub">{_esc(sub_center_name)}</div>
    </div>
    <div class="header-left">
      <div>تاریخ: {today_shamsi}</div>
      <div>شماره: {letter_number}</div>
    </div>
  </div>
  <div class="content">
    <p><strong>به: مسئول محترم بخش {_esc(org.get("nam_bakhsh", ""))}</strong></p>
    <p><strong>از: مدیریت خدمات پرستاری</strong></p>
    <p>با صلوات بر محمد و آل محمد (ص) و با احترام، بدین‌وسیله {intro_title}
       <strong>{_esc(full_name)}</strong> فرزند {_esc(person.get("father_nam", "---"))}
       با مشخصات زیر برای ادامه خدمت از تاریخ
       <strong>{start_date}</strong> به حضورتان معرفی می‌گردد.</p>
    <table class="details-table">
      <tr><td>وضعیت استخدام</td><td>{_esc(person.get("vazit_khedmat", "---"))}</td></tr>
      <tr><td>مقطع تحصیلی</td> <td>{_esc(person.get("madrak", "---"))}</td></tr>
      <tr><td>رشته تحصیلی</td> <td>{_esc(person.get("madrak_nam", "---"))}</td></tr>
      <tr><td>کد ملی</td>       <td>{_esc(person.get("kod_meli", "---"))}</td></tr>
      <tr><td>عنوان شغلی</td>   <td>{_esc(org.get("nam_shogl", "---"))}</td></tr>
    </table>
  </div>
  <div class="signature">
    <div class="sig-line"></div>
    <strong>مدیریت خدمات پرستاری</strong>
  </div>
</div>
<script>window.print();</script>
</body>
</html>'''

