import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
import altair as alt

# ================== CONFIG ==================
st.set_page_config(
    page_title="Mini SIEM Dashboard",
    layout="wide"
)

LOG_FILE = Path("data/logs.jsonl")  # مسار ملف اللوقات
# ============================================


def parse_time(x):
    """تحويل أي صيغة وقت إلى datetime آمن"""
    if x is None:
        return None

    # Epoch timestamp
    if isinstance(x, (int, float)):
        try:
            return datetime.fromtimestamp(x)
        except:
            return None

    # ISO string
    if isinstance(x, str):
        try:
            return datetime.fromisoformat(x.replace("Z", ""))
        except:
            return None

    return None


def load_events(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except:
                continue

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # محاولة إيجاد حقل الوقت
    time_field = None
    for col in ["timestamp", "@timestamp", "@server_time", "time_created"]:
        if col in df.columns:
            time_field = col
            break

    if time_field:
        df["time_parsed"] = df[time_field].apply(parse_time)
    else:
        df["time_parsed"] = None

    return df


# ================== UI ==================
st.title("🛡️ Mini SIEM Dashboard (Windows Events)")

df = load_events(LOG_FILE)

# ================== SIDEBAR FILTERS ==================
st.sidebar.header("Filters")

event_id_filter = st.sidebar.text_input("Event ID", "4625")
user_filter = st.sidebar.text_input("Username contains")
ip_filter = st.sidebar.text_input("IP contains")
max_rows = st.sidebar.slider("Max rows", 50, 2000, 300)

filtered = df.copy()

if not filtered.empty:
    if event_id_filter and "event_id" in filtered.columns:
        filtered = filtered[
            filtered["event_id"].astype(str) == event_id_filter
        ]

    if user_filter:
        for col in ["username", "user", "TargetUserName", "account_name"]:
            if col in filtered.columns:
                filtered = filtered[
                    filtered[col].astype(str)
                    .str.contains(user_filter, case=False, na=False)
                ]
                break

    if ip_filter:
        for col in ["ip", "IpAddress", "source_ip", "src_ip"]:
            if col in filtered.columns:
                filtered = filtered[
                    filtered[col].astype(str)
                    .str.contains(ip_filter, case=False, na=False)
                ]
                break

# ================== METRICS ==================
c1, c2, c3, c4 = st.columns(4)

total_events = 0 if df.empty else len(df)

failed_logins = 0
if not df.empty and "event_id" in df.columns:
    failed_logins = (df["event_id"].astype(str) == "4625").sum()

last_time = None
last_time = None
last_time_str = "N/A"

if not df.empty and "time_parsed" in df.columns:
    lt = df["time_parsed"].dropna().max()

    if isinstance(lt, (int, float)):
        try:
            lt = datetime.fromtimestamp(lt)
        except:
            lt = None

    if isinstance(lt, datetime):
        last_time_str = lt.strftime("%Y-%m-%d %H:%M:%S")

c1.metric("Total Events", total_events)
c2.metric("Failed Logins (4625)", int(failed_logins))
c3.metric("Filtered Events", 0 if filtered.empty else len(filtered))

c4.metric("Last Event Time", last_time_str)

st.divider()

# ================== TABLE ==================
left, right = st.columns([1.3, 1])

with left:
    st.subheader("📄 Latest Events")
    if filtered.empty:
        st.info("No data available.")
    else:
        show_df = filtered.sort_values(
            by="time_parsed",
            ascending=False
        )
        st.dataframe(
            show_df.head(max_rows),
            use_container_width=True
        )

# ================== CHART ==================
with right:
    st.subheader("📈 Failed Login Trend")

    if (
        df.empty
        or "event_id" not in df.columns
        or "time_parsed" not in df.columns
    ):
        st.warning("Insufficient data to draw chart.")
    else:
        dff = df[
            (df["event_id"].astype(str) == "4625")
            & (df["time_parsed"].notna())
        ].copy()

        if dff.empty:
            st.info("No failed login events.")
        else:
            dff["minute"] = dff["time_parsed"].dt.floor("min")
            grp = dff.groupby("minute").size().reset_index(name="count")

            chart = (
                alt.Chart(grp)
                .mark_line(point=True)
                .encode(
                    x="minute:T",
                    y="count:Q",
                    tooltip=["minute:T", "count:Q"],
                )
                .interactive()
            )

            st.altair_chart(chart, use_container_width=True)

st.caption("Mini SIEM – FYP | Windows Event 4625 Monitoring")
