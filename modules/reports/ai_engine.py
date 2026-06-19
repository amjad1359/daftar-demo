"""
موتور تحلیل هوشمند گزارش راند و اعتباربخشی
تحلیل داخلی + اتصال به DeepSeek
"""

import json
import requests


def internal_analysis(summary):
    """
    تحلیل داخلی بر اساس داده‌های آماری
    summary شامل:
        - total_items, total_earned, total_max, overall_percent
        - safety_items, doc_items
        - departments: list
        - quality_dist: dict (عالی, خوب, متوسط, نیازمند بهبود)
        - dept_percents: dict {dept: percent}
        - weak_items: list of weak item names
        - strong_items: list of strong item names
    """
    lines = []
    overall = summary.get('overall_percent', 0)

    # سطح کلی
    if overall >= 90:
        level = "سطح یک (عالی) 🌟"
    elif overall >= 75:
        level = "سطح دو (خوب) ✅"
    elif overall >= 50:
        level = "سطح سه (متوسط) ⚠️"
    else:
        level = "سطح چهار (نیازمند بهبود) 🔴"

    lines.append(f"📊 **وضعیت کلی اعتباربخشی:** {level} با تحقق {overall}%")
    lines.append(f"🔢 تعداد ارزیابی‌ها: {summary['total_items']}")
    lines.append(f"⭐ امتیاز نهایی: {summary['total_earned']} از {summary['total_max']}")

    # ایمنی
    safety = summary.get('safety_items', 0)
    lines.append(f"🛡️ سنجه‌های ایمنی: {safety} مورد")

    # مستندات
    docs = summary.get('doc_items', 0)
    lines.append(f"📎 اسناد پیوست: {docs} مورد")

    # بخش‌ها
    depts = summary.get('departments', [])
    if depts:
        lines.append(f"🏥 بخش‌های ارزیابی شده: {', '.join(depts)}")

    # تحلیل عمقی بخش‌ها
    dept_percents = summary.get('dept_percents', {})
    if dept_percents:
        best = max(dept_percents, key=dept_percents.get)
        worst = min(dept_percents, key=dept_percents.get)
        lines.append(f"🌟 بهترین بخش: {best} ({dept_percents[best]}%)")
        lines.append(f"⚠️ بخش نیازمند بهبود: {worst} ({dept_percents[worst]}%)")

    # کیفیت
    qdist = summary.get('quality_dist', {})
    if qdist:
        lines.append("📈 توزیع کیفی:")
        for k, v in qdist.items():
            lines.append(f"   {k}: {v}")

    # نقاط قوت و ضعف
    strong = summary.get('strong_items', [])
    weak = summary.get('weak_items', [])
    if strong:
        lines.append(f"✨ نقاط قوت ({len(strong)} سنجه):")
        for item in strong[:5]:
            lines.append(f"   - {item}")
    if weak:
        lines.append(f"🔻 سنجه‌های نیازمند بهبود ({len(weak)} سنجه):")
        for item in weak[:5]:
            lines.append(f"   - {item}")

    # پیشنهادات
    lines.append("💡 **پیشنهادات بهبود:**")
    if overall < 75:
        lines.append("۱. برگزاری کارگاه‌های آموزشی برای پرسنل")
    if docs < summary.get('total_items', 1) * 0.5:
        lines.append("۲. افزایش مستندسازی و ضمیمه کردن اسناد ارزیابی")
    if weak:
        lines.append("۳. تمرکز ویژه بر سنجه‌های با امتیاز پایین با بازنگری فرآیندها")
    lines.append("۴. انجام ممیزی داخلی ماهانه برای پایش مستمر")

    return "\n".join(lines)


def deepseek_analysis(api_key, summary):
    """ارسال درخواست به DeepSeek API و دریافت تحلیل"""
    if not api_key or len(api_key.strip()) < 10:
        return None

    prompt = f"""شما یک کارشناس ارشد اعتباربخشی بیمارستانی هستید. این داده‌های ارزیابی را تحلیل کنید و پاسخ را کاملاً به فارسی بنویسید:

داده:
{json.dumps(summary, indent=2, ensure_ascii=False)}

تحلیل باید شامل:
۱. خلاصه وضعیت کلی
۲. نقاط قوت و ضعف
۳. تحلیل ایمنی بیمار
۴. وضعیت مستندسازی
۵. پیشنهادات اجرایی (حداقل ۳ مورد)
۶. مقایسه بخش‌ها و پیشنهاد برای ضعیف‌ترین بخش

لطفاً پاسخ را در قالب پاراگراف‌های منظم و حرفه‌ای بنویسید.
"""

    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "شما یک تحلیلگر حرفه‌ای حوزه سلامت هستید."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=20
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception:
        pass
    return None
    
    