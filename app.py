import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="TaskLens🔎", layout="centered")

# -------------------- STYLES --------------------
page_bg = """
<style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #E6E6FA, #D8BFD8);
        background-attachment: fixed;
        position: relative;
    }
    [data-testid="stAppViewContainer"]::after {
        content: "";
        opacity: 0.05;
        top: 0; left: 0; bottom: 0; right: 0;
        position: absolute;
        pointer-events: none;
    }

    /* Header & Sidebar */
    [data-testid="stHeader"] { background: rgba(255,255,255,0); }
    [data-testid="stSidebar"] { background-color: #f7f7f7; }

    /* DataFrame / Table / Expander */
    [data-testid="stExpander"], [data-testid="stDataFrame"], [data-testid="stTable"] {
        background-color: #FFE4EC !important;
        border-radius: 12px;
        border: 1px solid #d3d3d3;
        box-shadow: 2px 3px 10px rgba(180, 130, 180, 0.4);
        padding: 10px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stExpander"]:hover,
    [data-testid="stDataFrame"]:hover,
    [data-testid="stTable"]:hover {
        transform: translateY(-3px);
        box-shadow: 4px 6px 15px rgba(160, 100, 160, 0.5);
    }

    /* Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(145deg, #FFB6C1, #FFC0CB);
        border-radius: 10px;
        border: 1px solid #d3d3d3;
        color: #2e2e2e;
        font-weight: bold;
        box-shadow: 2px 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        background: linear-gradient(145deg, #FFC0CB, #FFB6C1);
        transform: translateY(-2px);
        box-shadow: 4px 6px 8px rgba(0,0,0,0.3);
        color: #000000;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background-color: #f0f0f0 !important;
        border-radius: 8px;
        border: 1px solid #c0c0c0 !important;
        color: #333333 !important;
        box-shadow: inset 1px 2px 4px rgba(0,0,0,0.1);
    }

    /* Fonts */
    .stMarkdown, .stSubheader, .stCaption, .stText {
        color: #2e2e2e !important;
        font-family: "Poppins", sans-serif;
    }
    h1, h2, h3 { color: #c77dff; text-shadow: 1px 1px 3px rgba(200, 150, 255, 0.6); }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------- APP TITLE --------------------
st.title("TaskLens🔎")
st.caption("See your productivity through a lilac-tinted lens 💜")

# -------------------- SESSION STATE --------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Task", "Category", "Date", "Status", "TimeTaken"])

df = st.session_state.df

# -------------------- ADD NEW TASK --------------------
with st.expander("📋 Add New Task"):
    task = st.text_input("Task name")
    category = st.selectbox("Category", ["Academic", "Personal", "Learning", "Work", "Other"])
    status = st.selectbox("Status", ["Pending", "Done"])
    time_taken = st.number_input("Time taken (hours)", min_value=0.0, step=0.5)
    add = st.button("📋 Add Task")

    if add and task:
        new_data = pd.DataFrame([[task, category, datetime.now().date(), status, time_taken]],
                                columns=df.columns)
        st.session_state.df = pd.concat([df, new_data], ignore_index=True)
        st.success("Task added successfully ✅")
        df = st.session_state.df

# -------------------- TASK LIST --------------------
st.subheader("🗳️ Your Task List")

if not df.empty:
    for i, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([0.05, 0.35, 0.3, 0.3])
        with col1:
            checked = st.checkbox("", value=(row["Status"]=="Done"), key=f"task_{i}")
        with col2:
            st.markdown(f"**{row['Task']}**")
        with col3:
            st.markdown(f"{row['Category']}")
        with col4:
            st.markdown(f"{row['TimeTaken']} hrs")

        # Update status in DataFrame
        if checked:
            df.at[i, "Status"] = "Done"
        else:
            df.at[i, "Status"] = "Pending"
    st.session_state.df = df
else:
    st.info("🤔 No tasks yet — start by adding one! 🧐")

# -------------------- INSIGHTS --------------------
if not df.empty:
    total = len(df)
    completed = len(df[df["Status"] == "Done"])
    pending = total - completed
    avg_time = df[df["Status"] == "Done"]["TimeTaken"].mean() if completed else 0

    st.markdown("---")
    st.subheader("🧩 Productivity Insights")

    st.write(f"✅ **Total tasks:** {total}")
    st.write(f"🤓 **Completed tasks:** {completed}")
    st.write(f"⏳ **Pending tasks:** {pending}")
    st.write(f"⏰ **Average time per completed task:** {avg_time:.2f} hrs")

    # ---- Category Efficiency ----
    st.markdown("### 📨 Category Efficiency")
    cat_perf = df.groupby(["Category", "Status"]).size().unstack(fill_value=0)
    cat_perf["Completed %"] = (cat_perf.get("Done", 0) / cat_perf.sum(axis=1) * 100).round(1)
    st.table(cat_perf)

    # ---- Most Productive Day ----
    df["Date"] = pd.to_datetime(df["Date"])
    daily_done = df[df["Status"]=="Done"].groupby("Date").size()
    if not daily_done.empty:
        best_day = daily_done.idxmax().strftime("%d %b %Y")
        st.write(f"🤖 **Most productive day:** {best_day} ({daily_done.max()} tasks completed)")

    # ---- Productivity Score ----
    score = (completed / total * 70) + max(0, 30 - min(avg_time * 2, 30))
    st.write(f"🤩🌟 Productivity Score: **{score:.1f} / 100**")
    if score >= 80:
        st.success("🚀 You showed up today Champ! That's enough 🩷")
    elif score >= 50:
        st.info("😃 Doing well! Try to improve your daily consistency 🫵🏼")
    else:
        st.warning("🥺 Productivity low — get up again, my friend ❤️‍🩹!")







   