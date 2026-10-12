"""
Smart Expense Tracker — UI inspired by X (dark, minimal, modern)
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import html as html_module

st.set_page_config(
    page_title="Expense",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# X-inspired design system
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #000000;
    --bg-elevated: #0a0a0a;
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
    direction: rtl;
    text-align: right;
    font-family: 'Inter', Tahoma, "Segoe UI", sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; height: 0; }
div[data-testid="stToolbar"] { display: none; }
.stDeployButton { display: none; }

/* Sidebar — X left rail feel */
section[data-testid="stSidebar"] {
    background-color: var(--bg) !important;
    border-left: 1px solid var(--border) !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] > div {
    background-color: var(--bg) !important;
    padding-top: 1.5rem !important;
}

/* Main content width like X */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

/* Typography */
h1, h2, h3, h4 {
    color: var(--text) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}
h1 { font-size: 1.75rem !important; margin-bottom: 0.25rem !important; }
h2 { font-size: 1.35rem !important; }
h3 { font-size: 1.15rem !important; }

p, span, label, .stMarkdown {
    color: var(--text) !important;
}

/* Metric cards — X card style */
div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    transition: border-color 0.15s ease;
}
div[data-testid="stMetric"]:hover {
    border-color: var(--border-hover) !important;
}
div[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
}

/* Buttons — X pill / primary */
.stButton > button {
    border-radius: 9999px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.4rem !important;
    border: 1px solid var(--border) !important;
    background: transparent !important;
    color: var(--text) !important;
    transition: background 0.15s ease, border-color 0.15s ease !important;
}
.stButton > button:hover {
    background: rgba(239, 243, 244, 0.1) !important;
    border-color: var(--border-hover) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background-color: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}

/* Radio / nav */
div[role="radiogroup"] label {
    background: transparent !important;
    border-radius: 9999px !important;
    padding: 10px 16px !important;
    margin-bottom: 4px !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    transition: background 0.12s ease !important;
}
div[role="radiogroup"] label:hover {
    background: rgba(231, 233, 234, 0.1) !important;
}

/* Alerts */
.stSuccess, .stError, .stInfo, .stWarning {
    direction: rtl;
    text-align: right;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}

/* Dataframe */
.stDataFrame {
    direction: rtl;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    overflow: hidden;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--text) !important;
    border-bottom-color: var(--accent) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}

/* Custom utility classes */
.x-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
}
.x-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.03em;
}
.x-subtitle {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-top: 2px;
}
.x-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px 18px;
    margin-bottom: 12px;
    transition: border-color 0.15s ease;
}
.x-card:hover {
    border-color: var(--border-hover);
}
.x-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(29, 155, 240, 0.12);
    color: var(--accent);
    border-radius: 9999px;
    padding: 4px 12px;
    font-size: 0.8rem;
    font-weight: 600;
}
.x-muted { color: var(--text-muted); font-size: 0.88rem; }
.x-logo {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.04em;
    margin-bottom: 1.2rem;
}
.x-logo span { color: var(--accent); }
.insight-row {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.insight-row strong { color: var(--text); }
.cat-tile {
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 10px;
    background: var(--bg-card);
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# API helpers
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="x-logo">◈ <span>Expense</span></div>', unsafe_allow_html=True)

API_URL = st.sidebar.text_input(
    "API",
    value="http://127.0.0.1:8000/api",
    label_visibility="collapsed",
    help="آدرس Backend",
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
            "سرور خاموش است. ابتدا `start-backend.bat` را اجرا کنید "
            "یا:\n`uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`"
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


def plotly_x_layout(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Tahoma", color="#e7e9ea", size=12),
        title_font=dict(size=15, color="#e7e9ea"),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor="#2f3336", zerolinecolor="#2f3336", color="#71767b"),
        yaxis=dict(gridcolor="#2f3336", zerolinecolor="#2f3336", color="#71767b"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e7e9ea")),
        coloraxis_showscale=False,
    )
    return fig


# ─────────────────────────────────────────────
# Navigation
# ─────────────────────────────────────────────
page = st.sidebar.radio(
    "nav",
    ["خانه", "ثبت تراکنش", "عادت‌ها", "تحلیل", "دسته‌ها"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<p class="x-muted" style="padding: 0 8px;">v1.5 · FastAPI + Streamlit</p>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────
if page == "خانه":
    x_header("خانه", "نمای کلی هزینه‌ها و فعالیت‌ها")

    overview = api_get("/analytics/overview")
    if show_api_error(overview):
        st.stop()

    if overview:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("مجموع هزینه", f"{overview.get('total_spent', 0):,.0f}")
        c2.metric("این ماه", f"{overview.get('this_month', 0):,.0f}")
        c3.metric("میانگین روزانه", f"{overview.get('avg_daily', 0):,.0f}")
        c4.metric("تراکنش‌ها", overview.get("transaction_count", 0))

        if overview.get("top_category"):
            st.markdown(
                f'<div style="margin:14px 0"><span class="x-chip">🏆 {html_module.escape(str(overview["top_category"]))}</span>'
                f'<span class="x-muted" style="margin-right:10px">پرهزینه‌ترین دسته</span></div>',
                unsafe_allow_html=True,
            )

    summary = api_get("/analytics/summary", params={"months": 12})
    if summary and not show_api_error(summary) and isinstance(summary, list) and summary:
        df_month = pd.DataFrame(summary)
        if not df_month.empty and "month" in df_month.columns:
            left, right = st.columns([1.4, 1])

            with left:
                fig = px.bar(
                    df_month,
                    x="month",
                    y="total",
                    labels={"month": "", "total": ""},
                    color_discrete_sequence=["#1d9bf0"],
                )
                fig.update_traces(marker_line_width=0, opacity=0.95)
                plotly_x_layout(fig, 340)
                fig.update_layout(title="روند ماهانه")
                st.plotly_chart(fig, use_container_width=True)

            with right:
                last = summary[-1]
                if last.get("by_category"):
                    cat_df = pd.DataFrame(
                        list(last["by_category"].items()), columns=["دسته", "مبلغ"]
                    )
                    fig2 = px.pie(
                        cat_df,
                        values="مبلغ",
                        names="دسته",
                        hole=0.62,
                        color_discrete_sequence=[
                            "#1d9bf0",
                            "#00ba7c",
                            "#ffd400",
                            "#f4212e",
                            "#7856ff",
                            "#ff7a00",
                            "#e7e9ea",
                            "#71767b",
                        ],
                    )
                    plotly_x_layout(fig2, 340)
                    fig2.update_layout(title=f"دسته‌ها · {last.get('month', '')}")
                    fig2.update_traces(textposition="outside", textinfo="percent")
                    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="x-title" style="font-size:1.1rem;margin:18px 0 10px">آخرین تراکنش‌ها</div>', unsafe_allow_html=True)
    expenses = api_get("/expenses/", params={"limit": 12})
    if expenses and not show_api_error(expenses) and isinstance(expenses, list):
        if expenses:
            df = pd.DataFrame(expenses)
            df["دسته"] = df["category"].apply(
                lambda x: x.get("name", "") if isinstance(x, dict) else ""
            )
            df["نوع"] = df.get("tx_type", "expense").apply(
                lambda t: "درآمد" if t == "income" else "هزینه"
            )
            show = df[["date", "description", "amount", "دسته", "نوع"]].rename(
                columns={"date": "تاریخ", "description": "توضیح", "amount": "مبلغ"}
            )
            st.dataframe(show, use_container_width=True, hide_index=True)
        else:
            st.markdown('<p class="x-muted">هنوز تراکنشی ثبت نشده.</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ADD TRANSACTION
# ─────────────────────────────────────────────
elif page == "ثبت تراکنش":
    x_header("ثبت تراکنش", "هزینه یا درآمد جدید")

    cats = api_get("/categories/")
    if show_api_error(cats):
        st.stop()
    cats = cats or []
    cat_options = {f"{c.get('icon', '')} {c['name']}": c["id"] for c in cats}

    if not cat_options:
        st.warning("اول از صفحه «دسته‌ها» دسته‌های پیش‌فرض را بساز.")
        st.stop()

    description = st.text_input("توضیح", placeholder="مثلاً: ناهار رستوران", key="exp_desc")
    if description and len(description) > 2:
        suggestion = api_get("/expenses/suggest-category", params={"description": description})
        if suggestion and not suggestion.get("__error__") and suggestion.get("suggested_category"):
            st.markdown(
                f'<span class="x-chip">🤖 {html_module.escape(str(suggestion["suggested_category"]))}</span>',
                unsafe_allow_html=True,
            )

    c1, c2 = st.columns(2)
    with c1:
        amount = st.number_input("مبلغ", min_value=1.0, step=1000.0, format="%.0f", key="exp_amount")
    with c2:
        exp_date = st.date_input("تاریخ", value=date.today(), key="exp_date")

    c3, c4 = st.columns(2)
    with c3:
        category = st.selectbox("دسته", options=list(cat_options.keys()), key="exp_cat")
    with c4:
        tx_type = st.selectbox(
            "نوع",
            options=["expense", "income"],
            format_func=lambda x: "هزینه" if x == "expense" else "درآمد",
            key="exp_type",
        )

    notes = st.text_area("یادداشت", height=70, key="exp_notes", placeholder="اختیاری")

    if st.button("ثبت", type="primary", use_container_width=True):
        if not description or not description.strip():
            st.error("توضیح را وارد کنید.")
        else:
            payload = {
                "amount": amount,
                "description": description.strip(),
                "date": exp_date.isoformat(),
                "category_id": cat_options[category],
                "notes": notes or None,
                "tx_type": tx_type,
            }
            result = api_post("/expenses/", payload)
            if isinstance(result, dict) and result.get("__error__"):
                show_api_error(result)
            elif result:
                st.success("ثبت شد.")
            else:
                st.error("خطا در ذخیره.")

# ─────────────────────────────────────────────
# HABITS
# ─────────────────────────────────────────────
elif page == "عادت‌ها":
    x_header("عادت‌ها", "پیگیری روزانه و streak")

    tab1, tab2 = st.tabs(["لیست عادت‌ها", "عادت جدید"])

    with tab1:
        habits = api_get("/habits/")
        if show_api_error(habits):
            st.stop()
        habits = habits or []
        if not habits:
            st.markdown('<p class="x-muted">عادتی ندارید. از تب کناری بسازید.</p>', unsafe_allow_html=True)
        for h in habits:
            icon = html_module.escape(str(h.get("icon", "✅")))
            name = html_module.escape(str(h.get("name", "")))
            st.markdown(
                f'<div class="x-card"><div style="font-weight:700;font-size:1.05rem">{icon} {name}</div>'
                f'<div class="x-muted">{html_module.escape(str(h.get("description") or ""))}</div></div>',
                unsafe_allow_html=True,
            )
            streak = api_get(f"/habits/{h['id']}/streak")
            if streak and not streak.get("__error__"):
                a, b, c = st.columns(3)
                a.metric("streak", f"{streak.get('current_streak', 0)}")
                b.metric("بیشینه", streak.get("longest_streak", 0))
                c.metric("کل", streak.get("total_completed", 0))
            if st.button("انجام شد · امروز", key=f"done_{h['id']}", type="primary"):
                result = api_post(
                    "/habits/log",
                    {
                        "habit_id": h["id"],
                        "date": date.today().isoformat(),
                        "completed": True,
                    },
                )
                if result and not result.get("__error__"):
                    st.success("ثبت شد")
                    st.rerun()
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with tab2:
        name = st.text_input("نام", placeholder="مثلاً مطالعه ۲۰ صفحه")
        icon = st.text_input("آیکون", value="📚")
        desc = st.text_area("توضیح", height=70)
        freq = st.selectbox(
            "تکرار",
            ["daily", "weekly"],
            format_func=lambda x: "روزانه" if x == "daily" else "هفتگی",
        )
        if st.button("ساخت عادت", type="primary", use_container_width=True):
            if not name.strip():
                st.error("نام لازم است.")
            else:
                result = api_post(
                    "/habits/",
                    {
                        "name": name,
                        "icon": icon,
                        "description": desc,
                        "target_frequency": freq,
                    },
                )
                if result and not result.get("__error__"):
                    st.success("ساخته شد.")
                    st.rerun()
                elif show_api_error(result):
                    pass

# ─────────────────────────────────────────────
# ANALYTICS
# ─────────────────────────────────────────────
elif page == "تحلیل":
    x_header("تحلیل", "پیش‌بینی و الگوها")

    pred = api_get("/analytics/predict")
    if show_api_error(pred):
        st.stop()

    if pred and not pred.get("__error__"):
        c1, c2, c3 = st.columns(3)
        c1.metric("تخمین ماه بعد", f"{pred.get('next_month_estimate', 0):,.0f}")
        c2.metric("اطمینان", str(pred.get("confidence", "")).upper())
        c3.metric("روش", str(pred.get("method", "")).replace("_", " "))

        details = pred.get("details") or {}
        interval = details.get("prediction_interval_95")
        if interval:
            st.markdown(
                f'<p class="x-muted">بازه تقریبی ۹۵٪: {interval[0]:,.0f} — {interval[1]:,.0f}</p>',
                unsafe_allow_html=True,
            )
        with st.expander("جزئیات مدل"):
            st.json(details)

    st.markdown('<div class="x-title" style="font-size:1.1rem;margin:20px 0 12px">الگوها</div>', unsafe_allow_html=True)
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
# CATEGORIES
# ─────────────────────────────────────────────
elif page == "دسته‌ها":
    x_header("دسته‌ها", "مدیریت برچسب‌های هزینه")

    if st.button("ساخت دسته‌های پیش‌فرض", type="primary"):
        result = api_post("/categories/seed", {})
        if result and not result.get("__error__"):
            st.success(f"{len(result)} دسته ساخته شد")
            st.rerun()
        elif show_api_error(result):
            pass

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

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
