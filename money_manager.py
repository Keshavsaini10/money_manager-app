import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WealthTrack",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: #0d1117;
    color: #e6edf3;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px 20px;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem !important;
    color: #e6edf3;
}

[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #8b949e;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

[data-testid="metric-container"] [data-testid="stMetricDelta"] svg {
    display: none;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stSelectbox"] select,
div[data-baseweb="select"] {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* Delete button */
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
}

/* Tabs */
[data-testid="stTabs"] [role="tab"] {
    font-weight: 600;
    color: #8b949e;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #58a6ff;
    border-bottom: 2px solid #58a6ff;
}

/* Dividers */
hr { border-color: #30363d; }

/* Page title */
h1 {
    font-family: 'DM Serif Display', serif !important;
    color: #e6edf3 !important;
}
h2, h3 {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: #c9d1d9 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #30363d;
    border-radius: 10px;
    overflow: hidden;
}

/* Success / Error messages */
[data-testid="stAlert"] {
    border-radius: 8px;
}

/* Badge-like category pills */
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Data persistence ──────────────────────────────────────────────────────────
DATA_FILE = "wealthtrack_data.json"

CATEGORY_COLORS = {
    "Food & Dining": "#f97316",
    "Housing": "#8b5cf6",
    "Transport": "#3b82f6",
    "Healthcare": "#ec4899",
    "Entertainment": "#eab308",
    "Shopping": "#06b6d4",
    "Utilities": "#6366f1",
    "Education": "#10b981",
    "Travel": "#f43f5e",
    "Savings": "#22c55e",
    "Investment": "#84cc16",
    "Salary": "#34d399",
    "Freelance": "#a78bfa",
    "Other": "#94a3b8",
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"transactions": [], "budget": {}, "savings_goal": 0.0}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_df(transactions):
    if not transactions:
        return pd.DataFrame(columns=["id", "date", "type", "category", "description", "amount"])
    df = pd.DataFrame(transactions)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df.sort_values("date", ascending=False).reset_index(drop=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 WealthTrack")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "➕ Add Transaction", "📋 Transactions", "🎯 Budget & Goals", "📈 Analytics"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    df_all = get_df(data["transactions"])
    if not df_all.empty:
        income_total = df_all[df_all["type"] == "Income"]["amount"].sum()
        expense_total = df_all[df_all["type"] == "Expense"]["amount"].sum()
        net = income_total - expense_total
        color = "#22c55e" if net >= 0 else "#f87171"
        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #30363d;border-radius:10px;padding:14px 18px;">
            <div style="color:#8b949e;font-size:0.75rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Net Balance</div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:{color}">
                ₹{net:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
EXPENSE_CATEGORIES = [
    "Food & Dining", "Housing", "Transport", "Healthcare",
    "Entertainment", "Shopping", "Utilities", "Education", "Travel", "Other"
]
INCOME_CATEGORIES = ["Salary", "Freelance", "Investment", "Other"]


def add_transaction(t_type, category, description, amount, t_date):
    import uuid
    tx = {
        "id": str(uuid.uuid4()),
        "date": str(t_date),
        "type": t_type,
        "category": category,
        "description": description,
        "amount": float(amount),
    }
    data["transactions"].append(tx)
    save_data(data)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.markdown("# Dashboard")
    st.markdown("Your complete financial picture at a glance.")

    df = get_df(data["transactions"])

    if df.empty:
        st.info("No transactions yet. Add one from the **➕ Add Transaction** page.")
    else:
        # KPIs
        income = df[df["type"] == "Income"]["amount"].sum()
        expense = df[df["type"] == "Expense"]["amount"].sum()
        net = income - expense
        savings_rate = (net / income * 100) if income > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Income", f"₹{income:,.0f}", delta="")
        c2.metric("Total Expenses", f"₹{expense:,.0f}", delta="")
        c3.metric("Net Balance", f"₹{net:,.0f}", delta="")
        c4.metric("Savings Rate", f"{savings_rate:.1f}%", delta="")

        st.markdown("---")

        col_l, col_r = st.columns([3, 2])

        with col_l:
            st.markdown("### Monthly Cash Flow")
            df["month"] = df["date"].dt.to_period("M").astype(str)
            monthly = df.groupby(["month", "type"])["amount"].sum().reset_index()
            fig = px.bar(
                monthly, x="month", y="amount", color="type",
                barmode="group",
                color_discrete_map={"Income": "#34d399", "Expense": "#f87171"},
                template="plotly_dark",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend_title="", xaxis_title="", yaxis_title="Amount (₹)",
                font=dict(family="DM Sans"),
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_r:
            st.markdown("### Expense Breakdown")
            exp_df = df[df["type"] == "Expense"]
            if not exp_df.empty:
                cat_totals = exp_df.groupby("category")["amount"].sum().reset_index()
                colors = [CATEGORY_COLORS.get(c, "#94a3b8") for c in cat_totals["category"]]
                fig2 = go.Figure(go.Pie(
                    labels=cat_totals["category"],
                    values=cat_totals["amount"],
                    hole=0.55,
                    marker_colors=colors,
                    textinfo="percent",
                    textfont_size=11,
                ))
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans", color="#c9d1d9"),
                    legend=dict(font=dict(size=11)),
                    margin=dict(l=0, r=0, t=10, b=0),
                    showlegend=True,
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Recent transactions
        st.markdown("### Recent Transactions")
        recent = df.head(8).copy()
        recent["date"] = recent["date"].dt.strftime("%d %b %Y")
        recent["amount"] = recent.apply(
            lambda r: f"{'+'if r['type']=='Income' else '-'}₹{r['amount']:,.2f}", axis=1
        )
        st.dataframe(
            recent[["date", "type", "category", "description", "amount"]],
            use_container_width=True, hide_index=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ADD TRANSACTION
# ─────────────────────────────────────────────────────────────────────────────
elif page == "➕ Add Transaction":
    st.markdown("# Add Transaction")

    t_type = st.radio("Transaction Type", ["Expense", "Income"], horizontal=True)
    cats = EXPENSE_CATEGORIES if t_type == "Expense" else INCOME_CATEGORIES

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", cats)
        amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
    with col2:
        description = st.text_input("Description", placeholder="e.g. Grocery shopping")
        t_date = st.date_input("Date", value=date.today())

    if st.button("Add Transaction", use_container_width=True):
        if amount > 0 and description.strip():
            add_transaction(t_type, category, description.strip(), amount, t_date)
            st.session_state.data = load_data()
            st.success(f"✅ {t_type} of ₹{amount:,.2f} added successfully!")
            st.rerun()
        else:
            st.error("Please fill in all fields with valid values.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: TRANSACTIONS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📋 Transactions":
    st.markdown("# All Transactions")

    df = get_df(data["transactions"])
    if df.empty:
        st.info("No transactions found.")
    else:
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_type = st.selectbox("Filter by Type", ["All", "Income", "Expense"])
        with fc2:
            all_cats = ["All"] + sorted(df["category"].unique().tolist())
            f_cat = st.selectbox("Filter by Category", all_cats)
        with fc3:
            search = st.text_input("Search description", placeholder="Type to search…")

        filtered = df.copy()
        if f_type != "All":
            filtered = filtered[filtered["type"] == f_type]
        if f_cat != "All":
            filtered = filtered[filtered["category"] == f_cat]
        if search:
            filtered = filtered[filtered["description"].str.contains(search, case=False, na=False)]

        st.markdown(f"**{len(filtered)} transactions** found")

        display = filtered.copy()
        display["date"] = display["date"].dt.strftime("%d %b %Y")
        display["amount_display"] = display.apply(
            lambda r: f"{'+'if r['type']=='Income' else '-'}₹{r['amount']:,.2f}", axis=1
        )

        st.dataframe(
            display[["date", "type", "category", "description", "amount_display"]].rename(
                columns={"amount_display": "amount"}
            ),
            use_container_width=True, hide_index=True,
        )

        st.markdown("---")
        st.markdown("### Delete a Transaction")
        del_id = st.selectbox(
            "Select transaction to delete",
            options=filtered["id"].tolist(),
            format_func=lambda i: next(
                (f"{t['date']} | {t['category']} | ₹{t['amount']}" for t in data["transactions"] if t["id"] == i), i
            ),
        )
        if st.button("🗑️ Delete Selected", type="secondary"):
            data["transactions"] = [t for t in data["transactions"] if t["id"] != del_id]
            save_data(data)
            st.session_state.data = load_data()
            st.success("Transaction deleted.")
            st.rerun()

        # Export
        csv = filtered.to_csv(index=False).encode()
        st.download_button("⬇️ Export as CSV", csv, "transactions.csv", "text/csv")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: BUDGET & GOALS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🎯 Budget & Goals":
    st.markdown("# Budget & Goals")

    col_b, col_g = st.columns([3, 2])

    # ── Monthly Budget ────────────────────────────────────────────────────────
    with col_b:
        st.markdown("### Monthly Category Budgets")
        budget = data.get("budget", {})
        updated = False

        for cat in EXPENSE_CATEGORIES:
            current = budget.get(cat, 0.0)
            val = st.number_input(
                f"{cat}", min_value=0.0, value=float(current),
                step=100.0, format="%.0f", key=f"budget_{cat}"
            )
            if val != current:
                budget[cat] = val
                updated = True

        if st.button("Save Budgets", use_container_width=True):
            data["budget"] = budget
            save_data(data)
            st.session_state.data = load_data()
            st.success("Budgets saved!")

        # Budget vs actual this month
        df = get_df(data["transactions"])
        if not df.empty and budget:
            st.markdown("### This Month: Budget vs Actual")
            now = datetime.now()
            this_month = df[
                (df["type"] == "Expense") &
                (df["date"].dt.month == now.month) &
                (df["date"].dt.year == now.year)
            ]
            cat_spent = this_month.groupby("category")["amount"].sum().to_dict()

            rows = []
            for cat, budgeted in budget.items():
                if budgeted > 0:
                    spent = cat_spent.get(cat, 0)
                    pct = min(spent / budgeted * 100, 100)
                    rows.append({"category": cat, "budgeted": budgeted, "spent": spent, "pct": pct})

            if rows:
                fig = go.Figure()
                for r in rows:
                    color = "#f87171" if r["pct"] >= 90 else "#34d399" if r["pct"] < 70 else "#fbbf24"
                    fig.add_trace(go.Bar(
                        x=[r["pct"]], y=[r["category"]], orientation="h",
                        marker_color=color, showlegend=False,
                        hovertemplate=f"<b>{r['category']}</b><br>Spent: ₹{r['spent']:,.0f}<br>Budget: ₹{r['budgeted']:,.0f}<extra></extra>",
                    ))
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(range=[0, 100], title="% Used", ticksuffix="%"),
                    yaxis_title="", margin=dict(l=0, r=0, t=10, b=0),
                    font=dict(family="DM Sans"),
                    barmode="overlay", height=max(250, len(rows) * 38),
                )
                st.plotly_chart(fig, use_container_width=True)

    # ── Savings Goal ──────────────────────────────────────────────────────────
    with col_g:
        st.markdown("### Savings Goal")
        goal = st.number_input(
            "Set savings goal (₹)", min_value=0.0,
            value=float(data.get("savings_goal", 0)),
            step=1000.0, format="%.0f"
        )
        if st.button("Save Goal"):
            data["savings_goal"] = goal
            save_data(data)
            st.session_state.data = load_data()
            st.success("Goal saved!")

        df = get_df(data["transactions"])
        if not df.empty and goal > 0:
            income = df[df["type"] == "Income"]["amount"].sum()
            expense = df[df["type"] == "Expense"]["amount"].sum()
            net = income - expense
            pct = min(net / goal * 100, 100)
            color = "#22c55e" if pct >= 80 else "#fbbf24" if pct >= 40 else "#f87171"
            st.markdown(f"""
            <div style="margin-top:20px;background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px">
                <div style="color:#8b949e;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em">Progress</div>
                <div style="font-family:'DM Serif Display',serif;font-size:2.2rem;color:{color};margin:8px 0">
                    ₹{max(net,0):,.0f}
                </div>
                <div style="color:#8b949e;font-size:.85rem">of ₹{goal:,.0f} goal</div>
                <div style="background:#0d1117;border-radius:999px;height:10px;margin:16px 0 4px">
                    <div style="background:{color};border-radius:999px;height:10px;width:{pct:.1f}%;transition:width .5s"></div>
                </div>
                <div style="color:#8b949e;font-size:.8rem;text-align:right">{pct:.1f}% achieved</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈 Analytics":
    st.markdown("# Analytics")

    df = get_df(data["transactions"])
    if df.empty:
        st.info("Add some transactions to see analytics.")
    else:
        tab1, tab2, tab3 = st.tabs(["📅 Trends", "🏷️ Categories", "📊 Income vs Expense"])

        with tab1:
            st.markdown("### Daily Spending Trend")
            daily = df[df["type"] == "Expense"].groupby(df["date"].dt.date)["amount"].sum().reset_index()
            daily.columns = ["date", "amount"]
            fig = px.area(
                daily, x="date", y="amount",
                template="plotly_dark", color_discrete_sequence=["#58a6ff"],
            )
            fig.update_traces(fill="tozeroy", fillcolor="rgba(88,166,255,0.15)")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="", yaxis_title="Spending (₹)",
                font=dict(family="DM Sans"), margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Cumulative Net Worth Over Time")
            df_sorted = df.sort_values("date")
            df_sorted["signed"] = df_sorted.apply(lambda r: r["amount"] if r["type"] == "Income" else -r["amount"], axis=1)
            df_sorted["cumulative"] = df_sorted["signed"].cumsum()
            fig2 = px.line(
                df_sorted, x="date", y="cumulative",
                template="plotly_dark", color_discrete_sequence=["#34d399"],
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="", yaxis_title="Cumulative (₹)",
                font=dict(family="DM Sans"), margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            st.markdown("### Top Expense Categories (All Time)")
            exp_df = df[df["type"] == "Expense"]
            if not exp_df.empty:
                cat_df = exp_df.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=True)
                colors = [CATEGORY_COLORS.get(c, "#94a3b8") for c in cat_df["category"]]
                fig3 = go.Figure(go.Bar(
                    x=cat_df["amount"], y=cat_df["category"],
                    orientation="h", marker_color=colors,
                    text=cat_df["amount"].apply(lambda x: f"₹{x:,.0f}"),
                    textposition="outside",
                ))
                fig3.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="Total Spent (₹)", yaxis_title="",
                    font=dict(family="DM Sans"), margin=dict(l=0, r=80, t=10, b=0),
                    height=max(300, len(cat_df) * 40),
                )
                st.plotly_chart(fig3, use_container_width=True)

        with tab3:
            st.markdown("### Monthly Income vs Expense")
            df["month"] = df["date"].dt.to_period("M").astype(str)
            monthly = df.groupby(["month", "type"])["amount"].sum().reset_index()
            fig4 = px.bar(
                monthly, x="month", y="amount", color="type",
                barmode="group",
                color_discrete_map={"Income": "#34d399", "Expense": "#f87171"},
                template="plotly_dark",
                text_auto=True,
            )
            fig4.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend_title="", xaxis_title="", yaxis_title="Amount (₹)",
                font=dict(family="DM Sans"), margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig4, use_container_width=True)

            # Summary table
            pivot = monthly.pivot(index="month", columns="type", values="amount").fillna(0)
            pivot.columns.name = None
            if "Income" in pivot.columns and "Expense" in pivot.columns:
                pivot["Net"] = pivot["Income"] - pivot["Expense"]
            pivot = pivot.reset_index().rename(columns={"month": "Month"})
            st.dataframe(pivot.style.format({c: "₹{:,.0f}" for c in pivot.columns if c != "Month"}),
                         use_container_width=True, hide_index=True)