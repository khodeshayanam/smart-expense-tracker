# 💰 مدیریت هزینه و عادت هوشمند

نسخه ۱.۱ — یک سیستم شخصی برای ثبت هزینه‌ها، پیگیری عادت‌ها، تحلیل آماری و پیش‌بینی هزینه ماه بعد.

**رابط کاربری کاملاً فارسی + تم تاریک**

---

## ویژگی‌ها

- ثبت و مدیریت هزینه‌ها با دسته‌بندی
- پیشنهاد هوشمند دسته‌بندی (یادگیری ماشین)
- پیگیری عادت‌ها با محاسبه streak
- نمودارهای تعاملی روند هزینه
- پیش‌بینی هزینه ماه بعد
- رابط کاربری فارسی و راست‌چین

---

## ساختار پروژه

```
smart-expense-tracker/
├── backend/                  ← سرور API
│   ├── start-backend.bat     ← دوبار کلیک = اجرای سرور
│   ├── app/
│   ├── requirements.txt
│   └── seed_demo_data.py
├── dashboard/                ← رابط کاربری
│   ├── start-dashboard.bat   ← دوبار کلیک = اجرای داشبورد
│   ├── app.py
│   └── requirements.txt
└── README.md
```

---

## راه‌اندازی (فقط بار اول)

### پیش‌نیاز
پایتون ۳.۱۰ یا بالاتر نصب باشد.

### ۱. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # ویندوز
pip install -r requirements.txt
python seed_demo_data.py
```

### ۲. Dashboard

```bash
cd dashboard
pip install -r requirements.txt
```

---

## اجرای روزمره (خیلی ساده)

از این به بعد فقط این دو کار را انجام بده:

1. فایل **`backend/start-backend.bat`** را دوبار کلیک کن
2. فایل **`dashboard/start-dashboard.bat`** را دوبار کلیک کن

داشبورد در آدرس زیر باز می‌شود:  
**http://localhost:8501**

---

## نکات مهم

- اول Backend را روشن کن، بعد Dashboard
- اگر پیام «سرور روشن نیست» دیدی، یعنی Backend اجرا نشده
- داده‌های نمونه با دستور `python seed_demo_data.py` وارد می‌شوند

---

## تکنولوژی‌ها

- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: Streamlit + Plotly
- یادگیری ماشین: scikit-learn (Naive Bayes + Linear Regression)

---

## لایسنس

MIT
