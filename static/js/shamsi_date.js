// static/js/shamsi_date.js

// اعتبارسنجی تاریخ شمسی
function isValidShamsiDate(dateStr) {
    if (!dateStr) return false;
    var parts = dateStr.split('/');
    if (parts.length !== 3) return false;
    var y = parseInt(parts[0], 10);
    var m = parseInt(parts[1], 10);
    var d = parseInt(parts[2], 10);
    if (isNaN(y) || isNaN(m) || isNaN(d)) return false;
    if (y < 1300 || y > 1500) return false;
    if (m < 1 || m > 12) return false;
    var maxDay;
    if (m <= 6) maxDay = 31;
    else if (m <= 11) maxDay = 30;
    else {
        // سال کبیسه شمسی: بخش‌پذیر بر 4، اما قاعده دقیق‌تر? (ساده شده)
        maxDay = (y % 4 === 0) ? 30 : 29;
    }
    return (d >= 1 && d <= maxDay);
}

// تبدیل خودکار ورودی به فرمت استاندارد (اضافه کردن صفر و جداساز)
function autoFormatShamsi(input) {
    var val = input.value.replace(/[^0-9]/g, '');
    if (val.length > 8) val = val.substring(0, 8);
    var formatted = '';
    if (val.length > 0) {
        formatted = val.substring(0, 4);
        if (val.length > 4) {
            formatted += '/' + val.substring(4, 6);
            if (val.length > 6) {
                formatted += '/' + val.substring(6, 8);
            }
        }
    }
    input.value = formatted;
}

// نصب رفتار روی تمام فیلدهای دارای کلاس shamsi-date
function initShamsiDateFields() {
    var fields = document.querySelectorAll('.shamsi-date');
    fields.forEach(function(field) {
        // فرمت خودکار هنگام تایپ
        field.addEventListener('input', function(e) {
            autoFormatShamsi(this);
        });
        // اعتبارسنجی هنگام خروج از فیلد
        field.addEventListener('blur', function() {
            var val = this.value.trim();
            if (val === '') return;
            if (!isValidShamsiDate(val)) {
                alert('تاریخ وارد شده نامعتبر است. فرمت صحیح: YYYY/MM/DD');
                this.value = '';
                this.focus();
            }
        });
    });
}

// اجرا هنگام بارگذاری صفحه
document.addEventListener('DOMContentLoaded', initShamsiDateFields);
