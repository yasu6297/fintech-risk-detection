import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(
    page_title="FinTech Risk & Anomaly Radar",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. CSS for Card Lift, Neon Border Glow & Smooth Hover Micro-interactions
st.markdown("""
    <style>
    .main { background-color: #0b0f19; }
    
    /* Interactive Card hover effect */
    .kpi-card {
        background: linear-gradient(145deg, #111827, #1e293b);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-6px);
        border-color: #f87171;
        box-shadow: 0 12px 24px -6px rgba(248, 113, 113, 0.25), 0 0 15px rgba(248, 113, 113, 0.15);
    }
    
    /* Interactive Tab hover styling */
    button[data-baseweb="tab"] {
        transition: all 0.2s ease-in-out;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    button[data-baseweb="tab"]:hover {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Reusable Animated JavaScript KPI Component
def render_animated_kpis(kpis):
    """
    Renders metrics that tick up from 1 to their target values smoothly
    using browser requestAnimationFrame.
    """
    card_htmls = ""
    for kpi in kpis:
        card_htmls += f"""
        <div class="kpi-card">
            <div class="label">{kpi['label']}</div>
            <div class="value">
                <span class="prefix">{kpi.get('prefix', '')}</span>
                <span class="counter" data-target="{kpi['target']}" data-decimals="{kpi.get('decimals', 0)}">1</span>
                <span class="suffix">{kpi.get('suffix', '')}</span>
            </div>
        </div>
        """
        
    full_component = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background: transparent; padding: 6px 0; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }}
        .kpi-card {{
            background: linear-gradient(145deg, #111827, #1e293b);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px 20px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }}
        .kpi-card:hover {{
            transform: translateY(-5px);
            border-color: #f87171;
            box-shadow: 0 10px 20px -5px rgba(248, 113, 113, 0.25);
        }}
        .label {{
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .value {{
            color: #f87171;
            font-size: 1.75rem;
            font-weight: 700;
            display: flex;
            align-items: baseline;
            gap: 2px;
        }}
        .prefix, .suffix {{
            font-size: 1.2rem;
            color: #ef4444;
            font-weight: 600;
        }}
    </style>

    <div class="grid">
        {card_htmls}
    </div>

    <script>
    function animateCounters() {{
        const counters = document.querySelectorAll('.counter');
        const duration = 1200; // 1.2s tick-up duration
        
        counters.forEach(counter => {{
            const target = +counter.getAttribute('data-target');
            const decimals = +counter.getAttribute('data-decimals');
            const startTime = performance.now();
            
            function update(currentTime) {{
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Ease-out cubic formula for natural deceleration
                const easeOut = 1 - Math.pow(1 - progress, 3);
                const currentVal = 1 + (target - 1) * easeOut;
                
                if (decimals > 0) {{
                    counter.innerText = currentVal.toLocaleString('en-US', {{ minimumFractionDigits: decimals, maximumFractionDigits: decimals }});
                }} else {{
                    counter.innerText = Math.floor(currentVal).toLocaleString('en-US');
                }}
                
                if (progress < 1) {{
                    requestAnimationFrame(update);
                }} else {{
                    if (decimals > 0) {{
                        counter.innerText = target.toLocaleString('en-US', {{ minimumFractionDigits: decimals, maximumFractionDigits: decimals }});
                    }} else {{
                        counter.innerText = Math.round(target).toLocaleString('en-US');
                    }}
                }}
            }}
            requestAnimationFrame(update);
        }});
    }}
    window.addEventListener('load', animateCounters);
    animateCounters();
    </script>
    """
    components.html(full_component, height=115)

# 3. Data Ingestion
@st.cache_data
def load_data():
    df = pd.read_csv("scored_transactions.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

df = load_data()

# 4. Sidebar Controls
with st.sidebar:
    st.title("🛡️ Risk Radar Ops")
    st.caption("Unsupervised Anomaly Triage Engine")
    
    st.markdown("### Risk Calibration")
    score_threshold = st.slider(
        "Anomaly Score Threshold",
        min_value=float(df["anomaly_score"].min()),
        max_value=float(df["anomaly_score"].max()),
        value=float(df["anomaly_score"].quantile(0.985)),
        step=0.01
    )
    
    payment_filter = st.multiselect(
        "Payment Modes",
        options=df["payment_mode"].unique(),
        default=df["payment_mode"].unique()
    )

filtered_df = df[df["payment_mode"].isin(payment_filter)].copy()
filtered_df["flagged_by_threshold"] = (filtered_df["anomaly_score"] >= score_threshold).astype(int)

# Metric totals
total_txns = len(filtered_df)
flagged_txns = int(filtered_df["flagged_by_threshold"].sum())
flagged_rate = float((flagged_txns / total_txns) * 100) if total_txns > 0 else 0.0
flagged_volume_inr = float(filtered_df[filtered_df["flagged_by_threshold"] == 1]["amount"].sum())

# Header
st.markdown("## 🛡️ FinTech Risk & Behavioral Anomaly Engine")
st.caption("Real-time isolation forest scoring & baseline variance diagnostics")

# Render the dynamic tick-up counter cards
render_animated_kpis([
    {"label": "Total Scored Feeds", "target": total_txns, "decimals": 0, "suffix": " txns"},
    {"label": "Flagged For Review", "target": flagged_txns, "decimals": 0, "suffix": " alerts"},
    {"label": "Flagged Ratio", "target": flagged_rate, "decimals": 2, "suffix": "%"},
    {"label": "Flagged Exposure", "target": flagged_volume_inr, "decimals": 2, "prefix": "₹"}
])

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# 5. Interactive Tabs & Rich Hover Visualizations
tab_radar, tab_distribution, tab_queue = st.tabs([
    "🔬 Behavioral Anomaly Radar",
    "📊 Risk Feature Distributions",
    "🚨 High-Risk Investigation Queue"
])

with tab_radar:
    st.markdown("#### User Ticket Size vs. Baseline Z-Score (Hover points to inspect live telemetry)")
    
    sample_df = filtered_df.sample(n=min(6000, len(filtered_df)), random_state=42).copy()
    sample_df["Status"] = sample_df["flagged_by_threshold"].map({1: "🚨 Anomaly / Flagged", 0: "✅ Normal"})
    
    fig_scatter = px.scatter(
        sample_df,
        x="amount",
        y="amount_zscore",
        color="Status",
        color_discrete_map={"✅ Normal": "#3b82f6", "🚨 Anomaly / Flagged": "#ef4444"},
        hover_name="transaction_id",
        title="Transaction Amount vs. User Baseline Z-Score (With Axis Crosshairs)",
        labels={"amount": "Transaction Value (₹)", "amount_zscore": "Z-Score (Standard Deviations Away)"}
    )
    
    # Glowing hover card and tracking crosshairs
    fig_scatter.update_traces(
        marker=dict(size=7, opacity=0.75, line=dict(width=1, color="#ffffff")),
        hovertemplate=(
            "<b>🆔 %{hovertext}</b><br><br>"
            "💵 <b>Amount:</b> ₹%{x:,.2f}<br>"
            "📈 <b>Z-Score:</b> %{y:.2f} σ<br>"
            "<extra></extra>"
        )
    )
    
    fig_scatter.update_xaxes(showspikes=True, spikecolor="#ef4444", spikethickness=1, spikedash="dot", spikemode="across")
    fig_scatter.update_yaxes(showspikes=True, spikecolor="#ef4444", spikethickness=1, spikedash="dot", spikemode="across")
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af"),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#ef4444",
            font_size=13,
            font_family="Inter, sans-serif",
            font_color="#f8fafc"
        )
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab_distribution:
    col_a, col_b = st.columns(2)
    with col_a:
        fig_score = px.histogram(
            filtered_df,
            x="anomaly_score",
            color="flagged_by_threshold",
            color_discrete_map={0: "#3b82f6", 1: "#ef4444"},
            nbins=50,
            title="Anomaly Score Cutoff Histogram"
        )
        fig_score.update_traces(
            hovertemplate="<b>Risk Score Range:</b> %{x:.3f}<br><b>Count:</b> %{y:,d}<extra></extra>"
        )
        fig_score.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af"),
            hoverlabel=dict(bgcolor="#0f172a", bordercolor="#3b82f6", font_color="#ffffff")
        )
        st.plotly_chart(fig_score, use_container_width=True)
    
    with col_b:
        fig_mode = px.pie(
            filtered_df[filtered_df["flagged_by_threshold"] == 1],
            names="payment_mode",
            title="Flagged Anomalies by Payment Mode",
            hole=0.55,
            color_discrete_sequence=["#ef4444", "#f97316", "#eab308", "#8b5cf6"]
        )
        fig_mode.update_traces(
            hovertemplate="<b>%{label}</b><br>Volume: %{value:,d} txns<br>Share: %{percent:.1%}<extra></extra>",
            marker=dict(line=dict(color="#0f172a", width=2))
        )
        fig_mode.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af"),
            hoverlabel=dict(bgcolor="#0f172a", bordercolor="#ef4444", font_color="#ffffff")
        )
        st.plotly_chart(fig_mode, use_container_width=True)

with tab_queue:
    st.markdown("#### High-Priority Incident Review Table (Top 50 Most Anomalous)")
    queue_df = (
        filtered_df[filtered_df["flagged_by_threshold"] == 1]
        .sort_values(by="anomaly_score", ascending=False)
        .head(50)[["transaction_id", "user_id", "timestamp", "payment_mode", "amount", "amount_zscore", "seconds_since_prev_txn", "anomaly_score"]]
        .rename(columns={
            "transaction_id": "Txn ID",
            "user_id": "User",
            "timestamp": "Timestamp",
            "payment_mode": "Method",
            "amount": "Amount (₹)",
            "amount_zscore": "Z-Score",
            "seconds_since_prev_txn": "Delta T (sec)",
            "anomaly_score": "Risk Score"
        })
    )
    st.dataframe(queue_df, use_container_width=True)
    
    csv_queue = queue_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Triage Queue to CSV",
        data=csv_queue,
        file_name="high_risk_transactions_queue.csv",
        mime="text/csv"
    )