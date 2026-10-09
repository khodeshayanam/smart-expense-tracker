# 💰 Smart Expense & Habit Tracker

> یک سیستم کامل مدیریت هزینه و پیگیری عادت‌ها با تحلیل آماری، پیش‌بینی با یادگیری ماشین و داشبورد تعاملی زیبا.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?logo=scikitlearn)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ ویژگی‌ها

### مدیریت هزینه‌ها
- افزودن، ویرایش و حذف هزینه‌ها همراه با دسته‌بندی
- سیستم دسته‌بندی زیبا با آیکون و رنگ
- **پیشنهاد هوشمند دسته‌بندی** با استفاده از TF-IDF + Naive Bayes
- فیلتر کامل بر اساس بازه زمانی و دسته‌بندی

### پیگیری عادت‌ها
- ساخت عادت‌های روزانه و هفتگی
- ثبت سریع انجام عادت با یک کلیک
- نمایش **streak فعلی**، طولانی‌ترین streak و آمار کلی

### تحلیل‌های هوشمند
| ویژگی | تکنیک مورد استفاده |
|-------|---------------------|
| روند هزینه ماهانه | Aggregation + نمودارهای Plotly |
| پیش‌بینی ماه بعد | Linear Regression |
| الگوهای خرج کردن | قوانین آماری + تحلیل روز هفته و دسته‌بندی |
| دسته‌بندی خودکار | TF-IDF + Multinomial Naive Bayes |
| محاسبه Streak عادت‌ها | الگوریتم‌های توالی تاریخ |

### داشبورد
- متریک‌های لحظه‌ای
- نمودارهای تعاملی Plotly (میله‌ای + دونات)
- رابط کاربری تم تاریک و تمیز
- کاملاً واکنش‌گرا (Responsive)

---

## 🏗️ ساختار پروژه

```
smart-expense-tracker/
├── backend/                 # FastAPI REST API
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py        # مدل‌های SQLAlchemy
│   │   ├── schemas.py       # اسکیماهای Pydantic
│   │   ├── database.py
│   │   ├── routers/         # expenses, categories, habits, analytics
│   │   └── analysis/        # insights, prediction, ML
│   ├── seed_demo_data.py
│   └── requirements.txt
├── dashboard/               # فرانت‌اند Streamlit
│   ├── app.py
│   └── requirements.txt
└── README.md
```

**تکنولوژی‌ها**
- **Backend**: FastAPI + SQLAlchemy + SQLite (بدون نیاز به تنظیمات پیچیده)
- **Frontend**: Streamlit + Plotly
- **ML / Stats**: pandas, scikit-learn, numpy
- **مستندات API**: Swagger UI خودکار در آدرس `/docs`

---

## 🚀 راه‌اندازی سریع

### پیش‌نیاز
- پایتون ۳.۱۰ یا بالاتر

### ۱. Backend

```bash
cd backend
python -m venv venv

# ویندوز:
venv\Scripts\activate

# مک / لینوکس:
source venv/bin/activate

pip install -r requirements.txt

# وارد کردن داده‌های نمونه (۹۰ روز هزینه و عادت واقعی‌نما)
python seed_demo_data.py

# اجرای API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API در آدرس زیر در دسترس است:  
http://127.0.0.1:8000  

مستندات تعاملی:  
http://127.0.0.1:8000/docs

### ۲. Dashboard

یک ترمینال جدید باز کنید:

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

آدرس داشبورد معمولاً این است:  
http://localhost:8501

> اول Backend را اجرا کنید. آدرس API را می‌توانید از سایدبار داشبورد تغییر دهید.

---

## 📡 مهم‌ترین Endpointهای API

| متد | Endpoint | توضیح |
|-----|----------|--------|
| `POST` | `/api/categories/seed` | ساخت دسته‌بندی‌های پیش‌فرض |
| `GET`  | `/api/categories/` | لیست تمام دسته‌بندی‌ها |
| `POST` | `/api/expenses/` | ایجاد هزینه جدید |
| `GET`  | `/api/expenses/` | لیست / فیلتر هزینه‌ها |
| `GET`  | `/api/expenses/suggest-category/?description=...` | پیشنهاد هوشمند دسته‌بندی |
| `POST` | `/api/habits/` | ایجاد عادت |
| `POST` | `/api/habits/log` | ثبت انجام عادت |
| `GET`  | `/api/habits/{id}/streak` | آمار streak |
| `GET`  | `/api/analytics/overview` | شاخص‌های کلی |
| `GET`  | `/api/analytics/summary` | خلاصه ماهانه |
| `GET`  | `/api/analytics/predict` | پیش‌بینی ماه بعد |
| `GET`  | `/api/analytics/insights` | الگوهای شناسایی‌شده |

---

## 🧠 نحوه کار هوشمندی سیستم

1. **پیش‌بینی**  
   مجموع هزینه‌های ماهانه → Linear Regression → تخمین ماه بعد + میزان اطمینان (R²)

2. **شناسایی الگو**  
   - تشخیص ناهنجاری روزهای هفته  
   - تحلیل تمرکز روی دسته‌بندی‌ها  
   - مقایسه روند ماه‌به‌ماه  
   - تشخیص نقاط پرت (۹۵مین صدک)

3. **دسته‌بندی خودکار**  
   بعد از حدود ۱۵ هزینه، با TF-IDF + Multinomial Naive Bayes دسته‌بندی مناسب را از روی توضیح پیشنهاد می‌دهد.

---

## 🛠️ تغییر به PostgreSQL

فقط یک خط در فایل `backend/app/database.py` را تغییر دهید:

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/expense_tracker"
```

بقیه چیزها بدون تغییر کار می‌کند (SQLAlchemy خودش مدیریت می‌کند).

---

## 📦 ایده‌های آینده

- [ ] احراز هویت JWT + پشتیبانی چندکاربره
- [ ] خروجی Excel / گزارش PDF
- [ ] ربات تلگرام
- [ ] محدودیت بودجه + هشدار
- [ ] Docker Compose برای اجرای یک‌مرحله‌ای
- [ ] فرانت‌اند جایگزین با React

---

## 📄 لایسنس

MIT © 2026
