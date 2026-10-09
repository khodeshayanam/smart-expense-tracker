"""
Smart Expense & Habit Tracker — داشبورد فارسی
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import html as html_module

# ─────────────────────────────────────────────
# تنظیمات صفحه (باید اولین دستور باشه)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="مدیریت هزینه هوشمند",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# استایل تاریک + راست‌چین فارسی
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* راست‌چین کل صفحه */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: Tahoma, "Segoe UI", Arial, sans-serif !important;
    }

    /* پس‌زمینه تاریک */
    .stApp {
        background-color: #0f1117;
        color: #e2e8f0;
    }

    /* سایدبار */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-left: 1px solid #30363d;
    }

    /* کارت متریک */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 1.6rem !important;
    }

    /* دکمه‌ها */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* عنوان‌ها */
    h1, h2, h3 {
        color: #f8fafc !important;
    }

    /* پیام موفقیت و خطا */
    .stSuccess, .stError, .stInfo, .stWarning {
        direction: rtl;
        text-align: right;
    }

    /* جداول */
    .stDataFrame {
        direction: rtl;
    }

    /* مخفی کردن منوی استریملت */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# آدرس API
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ تنظیمات")
    API_URL = st.text_input(
        "آدرس API",
        value="http://127.0.0.1:8000/api",
        help="اگر سرور روی پورت دیگه‌ای اجرا شده، اینجا تغییر بده"
    )
    st.markdown("---")

# ─────────────────────────────────────────────
# توابع ارتباط با API
# ─────────────────────────────────────────────
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
    """اگر API خطا داد، پیام واضح نشون بده"""
    if result is None:
        return True
    if isinstance(result, dict) and result.get("__error__") == "connection":
        st.error("""
        🔴 **سرور روشن نیست!**
        
        اول Backend رو اجرا کن:
        1. برو به پوشه `backend`
        2. فایل `start-backend.bat` رو دوبار کلیک کن
        یا این دستور رو بزن:
        ```
        uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
        ```
        """)
        return True
    if isinstance(result, dict) and result.get("__error__"):
        st.error(f"خطا در ارتباط با سرور: {result['__error__']}")
        return True
    return False


# ─────────────────────────────────────────────
# منوی سایدبار
# ─────────────────────────────────────────────
st.sidebar.markdown("## 💰 مدیریت هزینه")
page = st.sidebar.radio(
    "منو",
    [
        "📊 داشبورد",
        "➕ ثبت هزینه",
        "✅ عادت‌ها",
        "🔮 تحلیل و پیش‌بینی",
        "🏷️ دسته‌بندی‌ها",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption("نسخه ۱.۱ · FastAPI + Streamlit")

# ─────────────────────────────────────────────
# صفحه داشبورد
# ─────────────────────────────────────────────
if page == "📊 داشبورد":
    st.title("📊 داشبورد کلی")
    st.caption("خلاصه وضعیت مالی و عادت‌های شما")

    overview = api_get("/analytics/overview")
    if show_api_error(overview):
        st.stop()

    if overview:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("مجموع هزینه‌ها", f"{overview.get('total_spent', 0):,.0f}")
        c2.metric("این ماه", f"{overview.get('this_month', 0):,.0f}")
        c3.metric("میانگین روزانه", f"{overview.get('avg_daily', 0):,.0f}")
        c4.metric("تعداد تراکنش", overview.get("transaction_count", 0))

        if overview.get("top_category"):
            st.info(f"🏆 پرهزینه‌ترین دسته: **{overview['top_category']}**")

    # نمودار ماهانه
    summary = api_get("/analytics/summary", params={"months": 12})
    if summary and not show_api_error(summary) and isinstance(summary, list) and summary:
        df_month = pd.DataFrame(summary)
        if not df_month.empty and "month" in df_month.columns:
            fig = px.bar(
                df_month,
                x="month",
                y="total",
                title="روند هزینه ماهانه",
                color="total",
                color_continuous_scale="Teal",
                labels={"month": "ماه", "total": "مبلغ"},
            )
            fig.update_layout(
                height=380,
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Tahoma"),
            )
            st.plotly_chart(fig, use_container_width=True)

            # نمودار دایره‌ای آخرین ماه
            last = summary[-1] if summary else None
            if last and last.get("by_category"):
                cat_df = pd.DataFrame(
                    list(last["by_category"].items()),
                    columns=["دسته", "مبلغ"]
                )
                fig2 = px.pie(
                    cat_df,
                    values="مبلغ",
                    names="دسته",
                    title=f"تقسیم‌بندی دسته‌ها — {last.get('month', '')}",
                    hole=0.45,
                )
                fig2.update_layout(
                    height=380,
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Tahoma"),
                )
                st.plotly_chart(fig2, use_container_width=True)

    # جدول آخرین هزینه‌ها
    st.subheader("آخرین هزینه‌ها")
    expenses = api_get("/expenses/", params={"limit": 15})
    if expenses and not show_api_error(expenses) and isinstance(expenses, list):
        df = pd.DataFrame(expenses)
        if not df.empty:
            df["دسته"] = df["category"].apply(
                lambda x: x.get("name", "") if isinstance(x, dict) else ""
            )
            display_df = df[["date", "description", "amount", "دسته"]].rename(
                columns={
                    "date": "تاریخ",
                    "description": "توضیح",
                    "amount": "مبلغ",
                }
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("هنوز هزینه‌ای ثبت نشده.")
    elif not show_api_error(expenses):
        st.info("هنوز هزینه‌ای ثبت نشده.")

# ─────────────────────────────────────────────
# ثبت هزینه جدید
# ─────────────────────────────────────────────
elif page == "➕ ثبت هزینه":
    st.title("➕ ثبت هزینه جدید")

    cats = api_get("/categories/")
    if show_api_error(cats):
        st.stop()

    cats = cats or []
    cat_options = {f"{c.get('icon', '')} {c['name']}": c["id"] for c in cats}

    if not cat_options:
        st.warning("هنوز دسته‌بندی وجود ندارد. اول به صفحه «دسته‌بندی‌ها» برو و دکمه‌ی ساخت دسته‌های پیش‌فرض را بزن.")
        st.stop()

    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("مبلغ (تومان)", min_value=1.0, step=1000.0, format="%.0f")
        with col2:
            exp_date = st.date_input("تاریخ", value=date.today())

        description = st.text_input("توضیح", placeholder="مثال: ناهار رستوران")
        category = st.selectbox("دسته‌بندی", options=list(cat_options.keys()))
        notes = st.text_area("یادداشت (اختیاری)", height=80)

        # پیشنهاد هوشمند
        if description and len(description) > 2:
            suggestion = api_get("/expenses/suggest-category", params={"description": description})
            if suggestion and not suggestion.get("__error__") and suggestion.get("suggested_category"):
                st.caption(f"🤖 پیشنهاد هوشمند: **{suggestion['suggested_category']}**")

        submitted = st.form_submit_button("💾 ذخیره هزینه", type="primary", use_container_width=True)

        if submitted:
            payload = {
                "amount": amount,
                "description": description,
                "date": exp_date.isoformat(),
                "category_id": cat_options[category],
                "notes": notes or None,
            }
            result = api_post("/expenses/", payload)
            if show_api_error(result):
                pass
            elif result:
                st.success("✅ هزینه با موفقیت ذخیره شد!")
                st.balloons()

# ─────────────────────────────────────────────
# عادت‌ها
# ─────────────────────────────────────────────
elif page == "✅ عادت‌ها":
    st.title("✅ پیگیری عادت‌ها")

    tab1, tab2 = st.tabs(["عادت‌های من", "ساخت عادت جدید"])

    with tab1:
        habits = api_get("/habits/")
        if show_api_error(habits):
            st.stop()

        habits = habits or []
        if not habits:
            st.info("هنوز عادتی نساختی. از تب کنار، یک عادت جدید بساز.")
        else:
            for h in habits:
                with st.container():
                    st.markdown(f"### {h.get('icon', '✅')} {h['name']}")
                    if h.get("description"):
                        st.caption(h["description"])

                    streak = api_get(f"/habits/{h['id']}/streak")
                    if streak and not streak.get("__error__"):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("streak فعلی", f"{streak.get('current_streak', 0)} 🔥")
                        c2.metric("طولانی‌ترین", streak.get("longest_streak", 0))
                        c3.metric("کل انجام‌شده", streak.get("total_completed", 0))

                    if st.button("✓ امروز انجام شد", key=f"done_{h['id']}", type="primary"):
                        result = api_post(
                            "/habits/log",
                            {
                                "habit_id": h["id"],
                                "date": date.today().isoformat(),
                                "completed": True,
                            },
                        )
                        if result and not result.get("__error__"):
                            st.success("ثبت شد! 🎉")
                            st.rerun()
                    st.markdown("---")

    with tab2:
        with st.form("habit_form"):
            name = st.text_input("نام عادت", placeholder="مثال: مطالعه ۲۰ صفحه")
            icon = st.text_input("آیکون (ایموجی)", value="📚")
            desc = st.text_area("توضیح (اختیاری)")
            freq = st.selectbox("تکرار", ["daily", "weekly"], format_func=lambda x: "روزانه" if x == "daily" else "هفتگی")

            if st.form_submit_button("ساخت عادت", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("نام عادت را وارد کن.")
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
                        st.success("عادت ساخته شد!")
                        st.rerun()

# ─────────────────────────────────────────────
# تحلیل و پیش‌بینی
# ─────────────────────────────────────────────
elif page == "🔮 تحلیل و پیش‌بینی":
    st.title("🔮 تحلیل هوشمند و پیش‌بینی")

    pred = api_get("/analytics/predict")
    if show_api_error(pred):
        st.stop()

    if pred and not pred.get("__error__"):
        st.subheader("📈 پیش‌بینی ماه بعد")
        col1, col2, col3 = st.columns(3)
        col1.metric("تخمین هزینه", f"{pred.get('next_month_estimate', 0):,.0f}")
        col2.metric("میزان اطمینان", str(pred.get("confidence", "")).upper())
        col3.metric("روش", str(pred.get("method", "")).replace("_", " ").title())

        if pred.get("details"):
            with st.expander("جزئیات مدل"):
                st.json(pred["details"])

    st.subheader("💡 الگوهای شناسایی‌شده")
    insights = api_get("/analytics/insights")
    if insights and not show_api_error(insights) and isinstance(insights, list):
        if not insights:
            st.info("هنوز الگوی خاصی شناسایی نشده. چند هزینه بیشتر ثبت کن.")
        for ins in insights:
            icon = {"warning": "🟠", "success": "🟢", "info": "🔵"}.get(ins.get("severity", ""), "⚪")
            st.markdown(f"{icon} **{ins.get('title', '')}**  \n{ins.get('description', '')}")
            st.markdown("")

# ─────────────────────────────────────────────
# دسته‌بندی‌ها
# ─────────────────────────────────────────────
elif page == "🏷️ دسته‌بندی‌ها":
    st.title("🏷️ دسته‌بندی‌ها")

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("🌱 ساخت دسته‌های پیش‌فرض", type="primary", use_container_width=True):
            result = api_post("/categories/seed", {})
            if result and not result.get("__error__"):
                st.success(f"{len(result)} دسته ساخته شد!")
                st.rerun()
            elif show_api_error(result):
                pass

    st.markdown("")
    cats = api_get("/categories/")
    if show_api_error(cats):
        st.stop()

    cats = cats or []
    if cats:
        cols = st.columns(3)
        for i, c in enumerate(cats):
            with cols[i % 3]:
                color = c.get("color", "#6366f1")
                safe_name = html_module.escape(str(c.get("name", "")))
                safe_icon = html_module.escape(str(c.get("icon", "")))
                # color already validated as #RRGGBB by API
                st.markdown(
                    f"""
                    <div style="
                        background: {color}18;
                        border-right: 4px solid {color};
                        padding: 14px 16px;
                        border-radius: 10px;
                        margin-bottom: 12px;
                        direction: rtl;
                    ">
                        <span style="font-size: 1.5rem;">{safe_icon}</span>
                        <b style="margin-right: 8px; color: #e2e8f0;">{safe_name}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("هنوز دسته‌ای وجود ندارد. دکمه بالا را بزن تا دسته‌های پیش‌فرض ساخته شوند.")
