import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Lenskart Site Intelligence",
    page_icon="👓"
)

# ── Dark Theme CSS ────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0f0f0f; }
section[data-testid="stSidebar"] { background-color: #1a1a1a; }
div[data-testid="stMetric"] {
    background: #1a1a1a;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #2a2a2a;
}
h1, h2, h3, h4, p, label { color: #f0f0f0 !important; }
div[data-testid="stDataFrame"] { background: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

# ── Load Data from GitHub ─────────────────────────────────────────
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/tusharv284/my_dashy/main/lenskart_synthetic_data.csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"❌ Could not load data. Check your GitHub URL. Error: {e}")
        st.stop()

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Lenskart_Logo.svg/320px-Lenskart_Logo.svg.png", width=160)
st.sidebar.markdown("---")
st.sidebar.title("⚙️ Score Weights")

w_foot = st.sidebar.slider("Footfall Weight",       0.0, 1.0, 0.30, 0.05)
w_demo = st.sidebar.slider("Demographics Weight",   0.0, 1.0, 0.25, 0.05)
w_comp = st.sidebar.slider("Competitor Gap Weight", 0.0, 1.0, 0.20, 0.05)
w_rent = st.sidebar.slider("Rent Penalty",          0.0, 1.0, 0.15, 0.05)
w_poi  = st.sidebar.slider("POI Score Weight",      0.0, 1.0, 0.10, 0.05)

st.sidebar.markdown("---")
st.sidebar.title("🔍 Filters")

zone_options = df["Zone_Type"].unique().tolist()
zone_filter = st.sidebar.multiselect("Zone Type", zone_options, default=zone_options)

parking_filter = st.sidebar.checkbox("Parking Available Only", value=False)
metro_max = st.sidebar.slider("Max Metro Distance (km)", 0.5, 4.5, 4.5, 0.5)

# ── Apply Filters ─────────────────────────────────────────────────
df_f = df[df["Zone_Type"].isin(zone_filter)].copy()
if parking_filter:
    df_f = df_f[df_f["Parking_Available"] == True]
df_f = df_f[df_f["Metro_Proximity_Km"] <= metro_max]

# ── Recompute Composite Score ─────────────────────────────────────
df_f["Composite"] = (
    df_f["Footfall_Score"] * w_foot +
    df_f["Demo_Score"]     * w_demo +
    df_f["Competitor_Gap"] * w_comp -
    df_f["Rent_Index"]     * w_rent +
    df_f["POI_Score"]      * w_poi
).round(1)

# ── Aggregate by Locality ─────────────────────────────────────────
summary = (
    df_f.groupby("Locality").agg(
        Composite           = ("Composite",           "mean"),
        Monthly_Revenue_AED = ("Monthly_Revenue_AED", "mean"),
        ROI_Score           = ("ROI_Score",           "mean"),
        Footfall_Score      = ("Footfall_Score",      "mean"),
        Competitor_Gap      = ("Competitor_Gap",      "mean"),
        Demo_Score          = ("Demo_Score",          "mean"),
        Rent_Index          = ("Rent_Index",          "mean"),
        POI_Score           = ("POI_Score",           "mean"),
        Daily_Footfall      = ("Daily_Footfall",      "mean"),
        Avg_Spend_AED       = ("Avg_Spend_AED",       "mean"),
        Recommended         = ("Recommended",         "mean"),
    )
    .reset_index()
    .sort_values("Composite", ascending=False)
    .round(1)
)

top3 = summary.head(3)

# ── Header ────────────────────────────────────────────────────────
st.title("👓 Lenskart Dubai — Outlet Site Intelligence")
st.caption(f"Analysing {len(df_f)} records across {summary.shape[0]} localities · Adjust sidebar to re-rank in real time")
st.markdown("---")

# ── Row 1: KPI Cards ──────────────────────────────────────────────
st.subheader("🏆 Top 3 Recommended Localities")
c1, c2, c3 = st.columns(3)
medals = ["🥇", "🥈", "🥉"]
for col, medal, (_, row) in zip([c1, c2, c3], medals, top3.iterrows()):
    with col:
        st.metric(
            label=f"{medal} {row['Locality']}",
            value=f"Score: {row['Composite']:.1f}",
            delta=f"ROI: {row['ROI_Score']:.1f}x | AED {row['Monthly_Revenue_AED']:,.0f}/mo"
        )

st.markdown("---")

# ── Row 2: Bar Chart + Radar ──────────────────────────────────────
col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.subheader("📊 Locality Rankings — Composite Score")
    bar_data = summary.head(12).sort_values("Composite")
    colors = ["#00c9a7" if r < 3 else "#457B9D" for r in range(len(bar_data)-1, -1, -1)]
    fig_bar = go.Figure(go.Bar(
        x=bar_data["Composite"],
        y=bar_data["Locality"],
        orientation='h',
        marker_color=colors,
        text=bar_data["Composite"],
        textposition="outside"
    ))
    fig_bar.update_layout(
        paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a",
        font_color="white", height=420,
        xaxis=dict(title="Composite Score", gridcolor="#2a2a2a"),
        yaxis=dict(title=""),
        margin=dict(l=10, r=40, t=20, b=40)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🎯 Top 3 Factor Breakdown")
    cats   = ["Footfall_Score", "Demo_Score", "Competitor_Gap", "POI_Score", "Rent_Index"]
    labels = ["Footfall", "Demographics", "Comp Gap", "POI", "Rent"]
    radar_colors = ["#00c9a7", "#457B9D", "#E63946"]
    fig_r = go.Figure()
    for i, (_, row) in enumerate(top3.iterrows()):
        vals = [row[c] for c in cats] + [row[cats[0]]]
        fig_r.add_trace(go.Scatterpolar(
            r=vals, theta=labels + [labels[0]],
            fill='toself', name=row['Locality'],
            line_color=radar_colors[i]
        ))
    fig_r.update_layout(
        polar=dict(
            bgcolor="#1a1a1a",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2a2a2a"),
            angularaxis=dict(gridcolor="#2a2a2a")
        ),
        paper_bgcolor="#1a1a1a", font_color="white",
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        height=420, margin=dict(l=30, r=30, t=20, b=60)
    )
    st.plotly_chart(fig_r, use_container_width=True)

st.markdown("---")

# ── Row 3: Scatter + Revenue Bar ─────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🗺️ Opportunity Map")
    st.caption("Top-right = High footfall + Low competition (sweet spot)")
    fig_s = px.scatter(
        summary, x="Footfall_Score", y="Competitor_Gap",
        size="Composite", color="ROI_Score",
        text="Locality", hover_name="Locality",
        hover_data={"Monthly_Revenue_AED": True, "Composite": True},
        color_continuous_scale="RdYlGn", size_max=45
    )
    fig_s.update_traces(textposition="top center")
    fig_s.update_layout(
        paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a",
        font_color="white", height=400,
        xaxis=dict(title="Footfall Score", gridcolor="#2a2a2a"),
        yaxis=dict(title="Competitor Gap", gridcolor="#2a2a2a"),
        margin=dict(l=10, r=10, t=20, b=40)
    )
    st.plotly_chart(fig_s, use_container_width=True)

with col_b:
    st.subheader("💰 Monthly Revenue Potential")
    rev_data = summary.sort_values("Monthly_Revenue_AED", ascending=False).head(10)
    fig_rev = px.bar(
        rev_data, x="Locality", y="Monthly_Revenue_AED",
        color="ROI_Score", color_continuous_scale="Teal",
        text=rev_data["Monthly_Revenue_AED"].apply(lambda x: f"AED {x/1e6:.1f}M")
    )
    fig_rev.update_traces(textposition="outside")
    fig_rev.update_layout(
        paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a",
        font_color="white", height=400,
        xaxis=dict(title="", tickangle=-30, gridcolor="#2a2a2a"),
        yaxis=dict(title="Monthly Revenue (AED)", gridcolor="#2a2a2a"),
        margin=dict(l=10, r=10, t=20, b=80)
    )
    st.plotly_chart(fig_rev, use_container_width=True)

st.markdown("---")

# ── Row 4: Full Data Table ────────────────────────────────────────
st.subheader("📋 Full Locality Report")
display_cols = {
    "Locality": "Locality",
    "Composite": "Score",
    "Monthly_Revenue_AED": "Revenue/mo (AED)",
    "ROI_Score": "ROI",
    "Footfall_Score": "Footfall",
    "Demo_Score": "Demographics",
    "Competitor_Gap": "Comp Gap",
    "Rent_Index": "Rent Index",
    "Daily_Footfall": "Daily Footfall"
}
table_df = summary[list(display_cols.keys())].rename(columns=display_cols)
st.dataframe(
    table_df.style.background_gradient(cmap="Greens", subset=["Score"])
                  .background_gradient(cmap="RdYlGn", subset=["ROI"])
                  .format({"Revenue/mo (AED)": "{:,.0f}", "ROI": "{:.1f}x",
                           "Daily Footfall": "{:,.0f}"}),
    use_container_width=True,
    height=420
)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("---")
st.caption("📍 Lenskart Dubai Site Intelligence Dashboard · Built with Streamlit & Plotly · Data: Synthetic")
