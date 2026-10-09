"""
Smart Expense & Habit Tracker — Professional Streamlit Dashboard
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = st.sidebar.text_input("API Base URL", value="http://127.0.0.1:8000/api")

# Custom CSS
st.markdown(
    """
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .stMetric {
        background-color: #1e1e2f;
        padding: 12px;
        border-radius: 10px;
    }
    h1, h2, h3 { color: #e2e8f0; }
</style>
""",
    unsafe_allow_html=True,
)


def api_get(path: str, params=None):
    try:
        r = requests.get(f"{API_URL}{path}", params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(path: str, json_data: dict):
    try:
        r = requests.post(f"{API_URL}{path}", json=json_data, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ─────────────────────────────────────────────
# Sidebar Navigation
# ─────────────────────────────────────────────
st.sidebar.title("💰 Smart Tracker")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Expense", "Habits", "Insights & Forecast", "Categories"],
    label_visibility="collapsed",
)

# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
if page == "Dashboard":
    st.title("📊 Overview Dashboard")

    overview = api_get("/analytics/overview")
    if overview:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Spent", f"{overview['total_spent']:,.0f}")
        c2.metric("This Month", f"{overview['this_month']:,.0f}")
        c3.metric("Avg Daily", f"{overview['avg_daily']:,.0f}")
        c4.metric("Transactions", overview["transaction_count"])

        if overview.get("top_category"):
            st.info(f"🏆 Top category: **{overview['top_category']}**")

    # Monthly chart
    summary = api_get("/analytics/summary", params={"months": 12})
    if summary:
        df_month = pd.DataFrame(summary)
        if not df_month.empty:
            fig = px.bar(
                df_month,
                x="month",
                y="total",
                title="Monthly Spending Trend",
                color="total",
                color_continuous_scale="Viridis",
            )
            fig.update_layout(height=400, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            # Category breakdown of last month
            last = summary[-1] if summary else None
            if last and last.get("by_category"):
                cat_df = pd.DataFrame(
                    list(last["by_category"].items()), columns=["Category", "Amount"]
                )
                fig2 = px.pie(
                    cat_df,
                    values="Amount",
                    names="Category",
                    title=f"Category Split — {last['month']}",
                    hole=0.4,
                )
                fig2.update_layout(height=400, template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

    # Recent expenses table
    st.subheader("Recent Expenses")
    expenses = api_get("/expenses/", params={"limit": 20})
    if expenses:
        df = pd.DataFrame(expenses)
        if not df.empty:
            df["category_name"] = df["category"].apply(
                lambda x: x["name"] if isinstance(x, dict) else ""
            )
            st.dataframe(
                df[["date", "description", "amount", "category_name"]].rename(
                    columns={
                        "date": "Date",
                        "description": "Description",
                        "amount": "Amount",
                        "category_name": "Category",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

# ─────────────────────────────────────────────
# ADD EXPENSE
# ─────────────────────────────────────────────
elif page == "Add Expense":
    st.title("➕ Add New Expense")

    cats = api_get("/categories/") or []
    cat_options = {f"{c['icon']} {c['name']}": c["id"] for c in cats}

    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        amount = col1.number_input("Amount", min_value=0.01, step=1000.0, format="%.0f")
        exp_date = col2.date_input("Date", value=date.today())
        description = st.text_input("Description", placeholder="e.g. Lunch at cafe")
        category = st.selectbox("Category", options=list(cat_options.keys()) if cat_options else ["No categories"])
        notes = st.text_area("Notes (optional)")

        # Auto-suggest
        if description and len(description) > 3:
            suggestion = api_get("/expenses/suggest-category/", params={"description": description})
            if suggestion and suggestion.get("suggested_category"):
                st.caption(f"🤖 AI suggests: **{suggestion['suggested_category']}**")

        submitted = st.form_submit_button("Save Expense", type="primary")
        if submitted:
            if not cat_options:
                st.error("Please seed categories first (go to Categories page)")
            else:
                payload = {
                    "amount": amount,
                    "description": description,
                    "date": exp_date.isoformat(),
                    "category_id": cat_options[category],
                    "notes": notes or None,
                }
                result = api_post("/expenses/", payload)
                if result:
                    st.success("✅ Expense saved successfully!")

# ─────────────────────────────────────────────
# HABITS
# ─────────────────────────────────────────────
elif page == "Habits":
    st.title("✅ Habit Tracker")

    tab1, tab2 = st.tabs(["My Habits", "Add Habit"])

    with tab1:
        habits = api_get("/habits/") or []
        if not habits:
            st.info("No habits yet. Create one in the next tab!")
        for h in habits:
            with st.expander(f"{h['icon']} {h['name']}", expanded=True):
                st.write(h.get("description") or "_No description_")
                streak = api_get(f"/habits/{h['id']}/streak")
                if streak:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Current Streak", f"{streak['current_streak']} 🔥")
                    c2.metric("Longest", streak["longest_streak"])
                    c3.metric("Total Done", streak["total_completed"])

                if st.button(f"Mark Done Today", key=f"done_{h['id']}"):
                    result = api_post(
                        "/habits/log",
                        {"habit_id": h["id"], "date": date.today().isoformat(), "completed": True},
                    )
                    if result:
                        st.success("Logged! 🎉")
                        st.rerun()

    with tab2:
        with st.form("habit_form"):
            name = st.text_input("Habit name", placeholder="e.g. Read 20 pages")
            icon = st.text_input("Icon (emoji)", value="✅")
            desc = st.text_area("Description")
            freq = st.selectbox("Frequency", ["daily", "weekly"])
            if st.form_submit_button("Create Habit"):
                result = api_post(
                    "/habits/",
                    {"name": name, "icon": icon, "description": desc, "target_frequency": freq},
                )
                if result:
                    st.success("Habit created!")
                    st.rerun()

# ─────────────────────────────────────────────
# INSIGHTS & FORECAST
# ─────────────────────────────────────────────
elif page == "Insights & Forecast":
    st.title("🔮 Smart Insights & Forecast")

    pred = api_get("/analytics/predict")
    if pred:
        st.subheader("📈 Next Month Prediction")
        col1, col2, col3 = st.columns(3)
        col1.metric("Estimated Spend", f"{pred['next_month_estimate']:,.0f}")
        col2.metric("Confidence", pred["confidence"].upper())
        col3.metric("Method", pred["method"].replace("_", " ").title())

        if pred.get("details"):
            with st.expander("Model details"):
                st.json(pred["details"])

    st.subheader("💡 Detected Patterns")
    insights = api_get("/analytics/insights") or []
    for ins in insights:
        color = {"warning": "🟠", "success": "🟢", "info": "🔵"}.get(ins["severity"], "⚪")
        st.markdown(f"{color} **{ins['title']}**  \n{ins['description']}")

# ─────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────
elif page == "Categories":
    st.title("🏷️ Categories")

    if st.button("🌱 Seed Default Categories", type="primary"):
        result = api_post("/categories/seed", {})
        if result is not None:
            st.success(f"Seeded {len(result)} categories!")
            st.rerun()

    cats = api_get("/categories/") or []
    if cats:
        cols = st.columns(3)
        for i, c in enumerate(cats):
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="background:{c['color']}22; border-left:4px solid {c['color']};
                    padding:12px; border-radius:8px; margin-bottom:10px;">
                    <span style="font-size:1.4rem">{c['icon']}</span>
                    <b>{c['name']}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No categories yet. Click the seed button above.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ · FastAPI + Streamlit + scikit-learn")