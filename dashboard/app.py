"""
داشبورد مدیریت هزینه — ظاهر تیره مدرن + تقویم شمسی
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date as greg_date
import html as html_module
import jdatetime

st.set_page_config(
    page_title="مدیریت هزینه",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# استایل
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #000000;
    --bg-card: #16181c;
    --border: #2f3336;
    --border-hover: #3e444a;
    --text: #e7e9ea;
    --text-muted: #71767b;
    --accent: #1d9bf0;
    --accent-hover: #1a8cd8;
    --green: #00ba7c;
    --red: #f4212e;
    --yellow: #ffd400;
}

html, body, [class*="css"], .stApp {
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; height: 0; }
div[data-testid="stToolbar"], .stDeployButton { display: none; }

section[data-testid="stSidebar"] {
    background-color: var(--bg) !important;
    border-left: 1px solid var(--border) !important;
}
.block-container {
    padding-top: 1.5rem !important;
    max-width: 1100px !important;
}

h1, h2, h3, h4 {
    color: var(--text) !important;
    font-weight: 700 !important;
}
p, span, label, .stMarkdown { color: var(--text) !important; }

div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
}
div[data-testid="stMetric"] label { color: var(--text-muted) !important; font-size: 0.85rem !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--text) !important; font-size: 1.45rem !important; font-weight: 700 !important;
}

.stButton > button {
    border-radius: 9999px !important;
    font-weight: 700 !important;
    border: 1px solid var(--border) !important;
    background: transparent !important;
    color: var(--text) !important;
}
.stButton > button:hover { background: rgba(239,243,244,0.1) !important; }
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}

div[role="radiogroup"] label {
    border-radius: 9999px !important;
    padding: 10px 16px !important;
    font-weight: 600 !important;
}
div[role="radiogroup"] label:hover { background: rgba(231,233,234,0.1) !important; }

.stSuccess, .stError, .stInfo, .stWarning {
    direction: rtl; text-align: right; border-radius: 12px !important;
}
.stDataFrame { direction: rtl; border-radius: 16px !important; }

.x-header {
    padding-bottom: 12px; margin-bottom: 18px;
    border-bottom: 1px solid var(--border);
}
.x-title { font-size: 1.35rem; font-weight: 800; color: var(--text); }
.x-subtitle { color: var(--text-muted); font-size: 0.9rem; margin-top: 2px; }
.x-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 16px 18px; margin-bottom: 12px;
}
.x-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(29,155,240,0.12); color: var(--accent);
    border-radius: 9999px; padding: 4px 12px; font-size: 0.8rem; font-weight: 600;
}
.x-muted { color: var(--text-muted); font-size: 0.88rem; }
.x-logo { font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem; }
.x-logo span { color: var(--accent); }
.insight-row {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 14px 16px; margin-bottom: 10px;
}
.cat-tile {
    border: 1px solid var(--border); border-radius: 16px;
    padding: 14px 16px; margin-bottom: 10px; background: var(--bg-card);
}
.info-box {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 16px; margin-bottom: 16px; line-height: 1.8;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# تقویم شمسی
# ─────────────────────────────────────────────
PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]


def jalali_date_picker(label: str, key: str, default: jdatetime.date | None = None) -> greg_date:
    """انتخاب تاریخ شمسی → برگرداندن تاریخ میلادی برای API"""
    today_j = jdatetime.date.today()
    default = default or today_j

    st.markdown(f"**{label}**")
    c1, c2, c3 = st.columns(3)
    with c1:
        year = st.selectbox(
            "سال",
            options=list(range(today_j.year - 5, today_j.year + 2)),
            index=list(range(today_j.year - 5, today_j.year + 2)).index(default.year)
            if default.year in range(today_j.year - 5, today_j.year + 2)
            else 5,
            key=f"{key}_y",
            label_visibility="collapsed",
        )
    with c2:
        month = st.selectbox(
            "ماه",
            options=list(range(1, 13)),
            format_func=lambda m: PERSIAN_MONTHS[m - 1],
            index=default.month - 1,
            key=f"{key}_m",
            label_visibility="collapsed",
        )
    with c3:
        # تعداد روز ماه شمسی
        try:
            max_day = jdatetime.date(year, month, 1).j_month_days(year, month) if hasattr(jdatetime.date, "j_month_days") else 31
        except Exception:
            max_day = 31
        # jdatetime: month days
        if month <= 6:
            max_day = 31
        elif month <= 11:
            max_day = 30
        else:
            # اسفند
            max_day = 30 if jdatetime.date(year, 1, 1).isleap() else 29

        day_default = min(default.day, max_day)
        day = st.selectbox(
            "روز",
            options=list(range(1, max_day + 1)),
            index=day_default - 1,
            key=f"{key}_d",
            label_visibility="collapsed",
        )

    j = jdatetime.date(year, month, day)
    return j.togregorian()


def to_jalali_str(g_date_str: str) -> str:
    """رشته تاریخ میلادی YYYY-MM-DD → نمایش شمسی"""
    try:
        y, m, d = map(int, str(g_date_str)[:10].split("-"))
        j = jdatetime.date.fromgregorian(date=greg_date(y, m, d))
        return f"{j.year}/{j.month:02d}/{j.day:02d}"
    except Exception:
        return str(g_date_str)


# ─────────────────────────────────────────────
# ارتباط با API
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="x-logo">◈ <span>هزینه</span></div>', unsafe_allow_html=True)

API_URL = st.sidebar.text_input(
    "آدرس سرور",
    value="http://127.0.0.1:8000/api",
    help="اگر سرور روی پورت دیگری است تغییر دهید",
)


def api_get(path: str, params=None):
    try:
        r = requests.get(f"{API_URL}{path}", params=params, timeout=6)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"__error__": "connection"}
    except Exception as e:
        return {"__error__": str(e)}


def api_post(path: str, json_data: dict = None):
    try:
        r = requests.post(f"{API_URL}{path}", json=json_data or {}, timeout=6)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"__error__": "connection"}
    except Exception as e:
        return {"__error__": str(e)}


def show_api_error(result):
    if result is None:
        return True
    if isinstance(result, dict) and result.get("__error__") == "connection":
        st.error(
            "سرور خاموش است. ابتدا فایل start-backend.bat را اجرا کنید "
            "یا دستور زیر را بزنید:\n"
            "uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
        )
        return True
    if isinstance(result, dict) and result.get("__error__"):
        st.error(f"خطا: {result['__error__']}")
        return True
    return False


def x_header(title: str, subtitle: str = ""):
    sub = f'<div class="x-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="x-header"><div><div class="x-title">{title}</div>{sub}</div></div>',
        unsafe_allow_html=True,
    )


def plotly_layout(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Vazirmatn, Tahoma", color="#e7e9ea", size=12),
        title_font=dict(size=15, color="#e7e9ea"),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor="#2f3336", color="#71767b"),
        yaxis=dict(gridcolor="#2f3336", color="#71767b"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        coloraxis_showscale=False,
    )
    return fig


# ─────────────────────────────────────────────
# منو
# ─────────────────────────────────────────────
page = st.sidebar.radio(
    "منو",
    ["خانه", "ثبت تراکنش", "عادت‌ها", "تحلیل", "دسته‌ها"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    '<p class="x-muted" style="padding:0 8px">نسخه ۱.۶</p>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# خانه
# ─────────────────────────────────────────────
if page == "خانه":
    x_header("خانه", "نمای کلی هزینه‌ها")

    overview = api_get("/analytics/overview")
    if show_api_error(overview):
        st.stop()

    if overview:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("مجموع هزینه", f"{overview.get('total_spent', 0):,.0f}")
        c2.metric("این ماه", f"{overview.get('this_month', 0):,.0f}")
        c3.metric("میانگین روزانه", f"{overview.get('avg_daily', 0):,.0f}")
        c4.metric("تعداد تراکنش", overview.get("transaction_count", 0))

        if overview.get("top_category"):
            st.markdown(
                f'<div style="margin:14px 0"><span class="x-chip">🏆 {html_module.escape(str(overview["top_category"]))}</span>'
                f'<span class="x-muted" style="margin-right:10px">پرهزینه‌ترین دسته</span></div>',
                unsafe_allow_html=True,
            )

    summary = api_get("/analytics/summary", params={"months": 12})
    if summary and not show_api_error(summary) and isinstance(summary, list) and summary:
        df_month = pd.DataFrame(summary)
        if not df_month.empty:
            left, right = st.columns([1.4, 1])
            with left:
                fig = px.bar(
                    df_month, x="month", y="total",
                    labels={"month": "", "total": ""},
                    color_discrete_sequence=["#1d9bf0"],
                )
                plotly_layout(fig)
                fig.update_layout(title="روند ماهانه")
                st.plotly_chart(fig, use_container_width=True)
            with right:
                last = summary[-1]
                if last.get("by_category"):
                    cat_df = pd.DataFrame(list(last["by_category"].items()), columns=["دسته", "مبلغ"])
                    fig2 = px.pie(
                        cat_df, values="مبلغ", names="دسته", hole=0.62,
                        color_discrete_sequence=["#1d9bf0", "#00ba7c", "#ffd400", "#f4212e", "#7856ff", "#ff7a00"],
                    )
                    plotly_layout(fig2)
                    fig2.update_layout(title="تقسیم دسته‌ها")
                    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="x-title" style="font-size:1.1rem;margin:18px 0 10px">آخرین تراکنش‌ها</div>', unsafe_allow_html=True)
    expenses = api_get("/expenses/", params={"limit": 15})
    if expenses and not show_api_error(expenses) and isinstance(expenses, list):
        if expenses:
            rows = []
            for e in expenses:
                rows.append({
                    "تاریخ": to_jalali_str(e.get("date", "")),
                    "توضیح": e.get("description", ""),
                    "مبلغ": e.get("amount", 0),
                    "دسته": e["category"]["name"] if isinstance(e.get("category"), dict) else "",
                    "نوع": "درآمد" if e.get("tx_type") == "income" else "هزینه",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<p class="x-muted">هنوز تراکنشی ثبت نشده.</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ثبت تراکنش
# ─────────────────────────────────────────────
elif page == "ثبت تراکنش":
    x_header("ثبت تراکنش", "هزینه یا درآمد جدید")

    cats = api_get("/categories/")
    if show_api_error(cats):
        st.stop()
    cats = cats or []
    cat_options = {f"{c.get('icon', '')} {c['name']}": c["id"] for c in cats}
    if not cat_options:
        st.warning("هنوز دسته‌ای نیست. به صفحه «دسته‌ها» بروید.")
        st.stop()

    description = st.text_input("توضیح", placeholder="مثلاً: ناهار رستوران")
    if description and len(description) > 2:
        suggestion = api_get("/expenses/suggest-category", params={"description": description})
        if suggestion and not suggestion.get("__error__") and suggestion.get("suggested_category"):
            st.markdown(
                f'<span class="x-chip">پیشنهاد دسته: {html_module.escape(str(suggestion["suggested_category"]))}</span>',
                unsafe_allow_html=True,
            )

    c1, c2 = st.columns(2)
    with c1:
        amount = st.number_input("مبلغ (تومان)", min_value=1.0, step=10000.0, format="%.0f")
    with c2:
        g_date = jalali_date_picker("تاریخ (شمسی)", key="exp_date")

    c3, c4 = st.columns(2)
    with c3:
        category = st.selectbox("دسته", options=list(cat_options.keys()))
    with c4:
        tx_type = st.selectbox(
            "نوع",
            options=["expense", "income"],
            format_func=lambda x: "هزینه" if x == "expense" else "درآمد",
        )

    notes = st.text_area("یادداشت (اختیاری)", height=70)

    if st.button("ثبت", type="primary", use_container_width=True):
        if not description or not description.strip():
            st.error("توضیح را وارد کنید.")
        else:
            result = api_post("/expenses/", {
                "amount": amount,
                "description": description.strip(),
                "date": g_date.isoformat(),
                "category_id": cat_options[category],
                "notes": notes or None,
                "tx_type": tx_type,
            })
            if isinstance(result, dict) and result.get("__error__"):
                show_api_error(result)
            elif result:
                st.success("با موفقیت ثبت شد.")
            else:
                st.error("خطا در ذخیره.")

# ─────────────────────────────────────────────
# عادت‌ها
# ─────────────────────────────────────────────
elif page == "عادت‌ها":
    x_header("عادت‌ها", "پیگیری کارهای روزانه")

    st.markdown(
        """
<div class="info-box">
<strong>عادت چیست؟</strong><br>
عادت یک کار روزانه (یا هفتگی) است که می‌خواهید مرتب انجامش دهید؛ مثلاً ورزش، مطالعه یا بدون فست‌فود بودن.<br><br>
هر روز فقط <strong>یک‌بار</strong> می‌توانید تیک «انجام شد» بزنید. با هر تیک، شمارندهٔ پشت‌سرهم (استریک) افزایش می‌یابد.
اگر یک روز را از دست بدهید، استریک فعلی صفر می‌شود ولی رکورد طولانی‌ترین استریک حفظ می‌شود.
</div>
""",
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["لیست عادت‌ها", "ساخت عادت جدید"])

    with tab1:
        habits = api_get("/habits/")
        if show_api_error(habits):
            st.stop()
        habits = habits or []
        if not habits:
            st.markdown('<p class="x-muted">عادتی ندارید. از تب کناری یکی بسازید.</p>', unsafe_allow_html=True)

        for h in habits:
            icon = html_module.escape(str(h.get("icon", "✅")))
            name = html_module.escape(str(h.get("name", "")))
            desc = html_module.escape(str(h.get("description") or ""))
            st.markdown(
                f'<div class="x-card"><div style="font-weight:700;font-size:1.05rem">{icon} {name}</div>'
                f'<div class="x-muted">{desc}</div></div>',
                unsafe_allow_html=True,
            )
            streak = api_get(f"/habits/{h['id']}/streak")
            if streak and not streak.get("__error__"):
                a, b, c = st.columns(3)
                a.metric("استریک فعلی", f"{streak.get('current_streak', 0)}")
                b.metric("طولانی‌ترین", streak.get("longest_streak", 0))
                c.metric("کل انجام‌شده", streak.get("total_completed", 0))

            col_btn, col_msg = st.columns([1, 2])
            with col_btn:
                if st.button("انجام شد · امروز", key=f"done_{h['id']}", type="primary"):
                    result = api_post(
                        "/habits/log",
                        {
                            "habit_id": h["id"],
                            "date": greg_date.today().isoformat(),
                            "completed": True,
                        },
                    )
                    if result and not result.get("__error__"):
                        st.session_state[f"habit_ok_{h['id']}"] = True
                        st.rerun()
                    elif show_api_error(result):
                        pass
            if st.session_state.get(f"habit_ok_{h['id']}"):
                st.success("برای امروز ثبت شد. آمار بالا به‌روز است.")
                # پاک کردن فلگ تا پیام یک‌بار دیده شود
                del st.session_state[f"habit_ok_{h['id']}"]

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    with tab2:
        name = st.text_input("نام عادت", placeholder="مثلاً مطالعه ۲۰ صفحه")
        icon = st.text_input("آیکون", value="📚")
        desc = st.text_area("توضیح (اختیاری)", height=70)
        freq = st.selectbox(
            "تکرار",
            ["daily", "weekly"],
            format_func=lambda x: "روزانه" if x == "daily" else "هفتگی",
        )
        if st.button("ساخت عادت", type="primary", use_container_width=True):
            if not name.strip():
                st.error("نام عادت لازم است.")
            else:
                result = api_post(
                    "/habits/",
                    {
                        "name": name.strip(),
                        "icon": icon,
                        "description": desc,
                        "target_frequency": freq,
                    },
                )
                if result and not result.get("__error__"):
                    st.success("عادت ساخته شد.")
                    st.rerun()
                elif isinstance(result, dict) and result.get("__error__"):
                    show_api_error(result)
                else:
                    st.error("ساخت عادت ناموفق بود.")

# ─────────────────────────────────────────────
# تحلیل
# ─────────────────────────────────────────────
elif page == "تحلیل":
    x_header("تحلیل", "پیش‌بینی و الگوها")

    pred = api_get("/analytics/predict")
    if show_api_error(pred):
        st.stop()

    if pred and not pred.get("__error__"):
        c1, c2, c3 = st.columns(3)
        c1.metric("تخمین ماه بعد", f"{pred.get('next_month_estimate', 0):,.0f}")
        conf_map = {"high": "بالا", "medium": "متوسط", "low": "کم"}
        conf = str(pred.get("confidence", "")).lower()
        c2.metric("میزان اطمینان", conf_map.get(conf, conf))
        method_map = {
            "linear_regression": "رگرسیون خطی",
            "simple_average": "میانگین ساده",
            "insufficient_data": "داده ناکافی",
        }
        method = str(pred.get("method", ""))
        c3.metric("روش", method_map.get(method, method))

        details = pred.get("details") or {}
        interval = details.get("prediction_interval_95")
        if interval:
            st.markdown(
                f'<p class="x-muted">بازه تقریبی ۹۵٪: {interval[0]:,.0f} تا {interval[1]:,.0f}</p>',
                unsafe_allow_html=True,
            )
        with st.expander("جزئیات مدل"):
            st.json(details)

    st.markdown('<div class="x-title" style="font-size:1.1rem;margin:20px 0 12px">الگوهای شناسایی‌شده</div>', unsafe_allow_html=True)
    insights = api_get("/analytics/insights")
    if insights and not show_api_error(insights) and isinstance(insights, list):
        if not insights:
            st.markdown('<p class="x-muted">هنوز الگویی پیدا نشده.</p>', unsafe_allow_html=True)
        for ins in insights:
            sev = ins.get("severity", "info")
            dot = {"warning": "#ffd400", "success": "#00ba7c", "info": "#1d9bf0"}.get(sev, "#71767b")
            title = html_module.escape(str(ins.get("title", "")))
            desc = html_module.escape(str(ins.get("description", "")))
            st.markdown(
                f'<div class="insight-row">'
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
                f'<span style="width:8px;height:8px;border-radius:50%;background:{dot};display:inline-block"></span>'
                f'<strong>{title}</strong></div>'
                f'<div class="x-muted">{desc}</div></div>',
                unsafe_allow_html=True,
            )

# ─────────────────────────────────────────────
# دسته‌ها
# ─────────────────────────────────────────────
elif page == "دسته‌ها":
    x_header("دسته‌ها", "دسته‌های پیش‌فرض و دسته‌های خودتان")

    st.markdown(
        """
<div class="info-box">
هنگام نصب، چند دستهٔ فارسی به‌صورت خودکار ساخته می‌شود.
می‌توانید دستهٔ جدید هم اضافه کنید (مثلاً «اجاره» یا «قسط»).
</div>
""",
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["لیست دسته‌ها", "افزودن دسته جدید"])

    with tab1:
        if st.button("بارگذاری مجدد دسته‌های پیش‌فرض"):
            result = api_post("/categories/seed", {})
            if result is not None and not (isinstance(result, dict) and result.get("__error__")):
                st.success(f"{len(result) if isinstance(result, list) else 0} دسته اضافه/بررسی شد.")
                st.rerun()
            elif show_api_error(result):
                pass

        cats = api_get("/categories/")
        if show_api_error(cats):
            st.stop()
        cats = cats or []
        if not cats:
            st.markdown('<p class="x-muted">دسته‌ای وجود ندارد.</p>', unsafe_allow_html=True)
        else:
            cols = st.columns(3)
            for i, c in enumerate(cats):
                with cols[i % 3]:
                    color = c.get("color", "#1d9bf0")
                    safe_name = html_module.escape(str(c.get("name", "")))
                    safe_icon = html_module.escape(str(c.get("icon", "")))
                    st.markdown(
                        f'<div class="cat-tile" style="border-right:3px solid {color}">'
                        f'<div style="font-size:1.3rem;margin-bottom:4px">{safe_icon}</div>'
                        f'<div style="font-weight:600">{safe_name}</div></div>',
                        unsafe_allow_html=True,
                    )

    with tab2:
        st.markdown("**دسته جدید بسازید**")
        new_name = st.text_input("نام دسته", placeholder="مثلاً اجاره خانه")
        new_icon = st.text_input("آیکون", value="📌")
        new_color = st.color_picker("رنگ", value="#1d9bf0")
        if st.button("افزودن دسته", type="primary", use_container_width=True):
            if not new_name.strip():
                st.error("نام دسته لازم است.")
            else:
                result = api_post(
                    "/categories/",
                    {
                        "name": new_name.strip(),
                        "icon": new_icon or "📌",
                        "color": new_color,
                    },
                )
                if result and not result.get("__error__"):
                    st.success(f"دسته «{new_name.strip()}» اضافه شد.")
                    st.rerun()
                elif isinstance(result, dict) and result.get("__error__"):
                    # ممکن است پیام ۴۰۰ باشد
                    err = result["__error__"]
                    if "400" in str(err) or "exists" in str(err).lower() or "وجود" in str(err):
                        st.error("این دسته از قبل وجود دارد.")
                    else:
                        show_api_error(result)
                else:
                    st.error("افزودن دسته ناموفق بود. شاید نام تکراری باشد.")
