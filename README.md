# 💰 مدیریت هزینه و عادت هوشمند

نسخه ۲.۰ — یک اپ وب واقعی برای ثبت هزینه‌ها، پیگیری عادت‌ها، تحلیل آماری، پیش‌بینی هزینه ماه بعد و **دستیار هوش مصنوعی** که با زبان طبیعی فارسی درباره وضعیت مالی‌ات صحبت می‌کند.

**رابط کاربری React + تم تاریک + کاملاً فارسی و راست‌چین**

---

## ویژگی‌ها

- ثبت و مدیریت هزینه‌ها با دسته‌بندی
- پیشنهاد هوشمند دسته‌بندی (یادگیری ماشین — scikit-learn)
- پیگیری عادت‌ها با محاسبه streak
- نمودارهای تعاملی روند هزینه (recharts)
- پیش‌بینی آماری هزینه ماه بعد (رگرسیون خطی)
- **دستیار هوش مصنوعی مولد (Gemini، رایگان):** تحلیل متنی خودکار وضعیت مالی + چت آزاد درباره هزینه‌ها
- رابط کاربری وب واقعی، مستقل از بک‌اند — پایه مناسب برای تبدیل بعدی به اپ اندروید

---

## ساختار پروژه

```
smart-expense-tracker/
├── backend/                  ← سرور API (FastAPI)
│   ├── app/
│   │   ├── routers/ai.py     ← اندپوینت‌های هوش مصنوعی
│   │   └── ...
│   ├── requirements.txt
│   ├── .env.example          ← کپی کن به .env و کلید AI را بگذار
│   └── seed_demo_data.py
├── frontend/                 ← وب‌اپ جدید (React + Vite + Tailwind)
│   ├── src/
│   │   ├── pages/             (Dashboard, Expenses, Habits, Categories, AIInsights)
│   │   ├── components/
│   │   └── lib/api.js
│   └── package.json
├── dashboard/                 ← داشبورد قدیمی Streamlit (اختیاری، دیگر لازم نیست)
└── README.md
```

---

## راه‌اندازی (فقط بار اول)

### پیش‌نیاز
پایتون ۳.۱۰+ و Node.js ۱۸+ نصب باشد.

### ۱. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # ویندوز   (یا source venv/bin/activate در مک/لینوکس)
pip install -r requirements.txt
python seed_demo_data.py
```

### ۲. فعال‌سازی دستیار هوش مصنوعی (اختیاری ولی توصیه می‌شود)

1. یک کلید رایگان از **https://aistudio.google.com/apikey** بگیر (نیاز به اکانت گوگل)
2. فایل `backend/.env.example` را کپی کن و نامش را بگذار `backend/.env`
3. داخلش بنویس:
   ```
   GEMINI_API_KEY=کلید_خودت_اینجا
   ```

بدون این کلید، بقیه اپ عادی کار می‌کند؛ فقط صفحه «دستیار هوشمند» و تحلیل AI در داشبورد غیرفعال می‌ماند.

### ۳. Frontend

```bash
cd frontend
npm install
```

---

## اجرای روزمره

دو ترمینال جدا باز کن:

```bash
# ترمینال ۱ — بک‌اند
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

```bash
# ترمینال ۲ — فرانت‌اند
cd frontend
npm run dev
```

اپ در آدرس زیر باز می‌شود:
**http://localhost:5173**

مستندات API: **http://localhost:8000/docs**

---

## نکات مهم

- اول Backend را روشن کن، بعد Frontend
- داده‌های نمونه با دستور `python seed_demo_data.py` وارد می‌شوند
- داشبورد قدیمی Streamlit (پوشه `dashboard/`) همچنان کار می‌کند ولی دیگر رابط اصلی نیست

---

## مسیر بعدی: تبدیل به اپ اندروید

چون فرانت‌اند حالا کاملاً از بک‌اند جداست (یک REST API مستقل)، این وب‌اپ را می‌توان با یکی از این روش‌ها به اپ اندروید تبدیل کرد:

- **Capacitor:** همین کد React را بدون تغییر زیاد به یک اپ بومی اندروید/iOS پکیج می‌کند
- **PWA:** با چند خط تنظیمات، همین سایت قابل نصب روی گوشی می‌شود (ساده‌ترین مسیر)
- **React Native:** بازنویسی UI با همان منطق و همان بک‌اند، برای تجربه کاملاً بومی

---

## تکنولوژی‌ها

- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: React + Vite + Tailwind CSS + recharts
- یادگیری ماشین کلاسیک: scikit-learn (Naive Bayes + Linear Regression)
- هوش مصنوعی مولد: Google Gemini API (رایگان)

---

## لایسنس

MIT
