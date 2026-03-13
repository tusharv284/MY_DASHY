import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Lenskart Site Intelligence", page_icon="👓")

st.markdown("""
<style>
.stApp { background-color: #0f0f0f; }
div[data-testid="stMetric"] { background: #1a1a1a; border-radius: 12px; padding: 16px; }
h1, h2, h3 { color: #f0f0f0; }
</style>
""", unsafe_allow_html=True)

# ── GITHUB DATA SOURCE ──────────────────────────────────────────
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/<your_username>/<your_repo>/main/<your_file>.csv"
    return pd.read_csv(url)

df = load_data()
# ───────────────────────────────────────────────────────────────

# ── Sidebar Filters ──
st.sidebar.title("⚙️ Score Weights")
w_foot = st.sidebar.slider("Footfall",       0.0, 1.0, 0.30)
w_demo = st.sidebar.slider("Demographics",   0.0, 1.0, 0.25)
w_comp = st.sidebar.slider("Competitor Gap", 0.0, 1.0, 0.20)
w_rent = st.sidebar.slider("Rent Penalty",   0.0, 1.0, 0.15)
w_poi  = st.sidebar.slider("POI Score",      0.0, 1.0, 0.10)

zone_filter = st.sidebar.multiselect(
    "Filter by Zone Type",
    options=df["Zone_Type"].unique(),
    default=df["Zone_Type"].unique()
)

# ── Recompute Score Dynamically ──
df_filtered = df[df["Zone_Type"].isin(zone_filter)].copy()
df_filtered["Composite"] = (
    df_filtered["Footfall_Score"] * w_foot +
    df_filtered["Demo_Score"]     * w_demo +
    df_filtered["Competitor_Gap"] * w_comp -
    df_filtered["Rent_Index"]     * w_rent +
    df_filtered["POI_Score"]      * w_poi
).round(1)

# Aggregate by locality
locality_summary = (
    df_filtered.groupby("Locality")
    .agg(
        Composite        = ("Composite", "mean"),
        Avg_Revenue      = ("Monthly_Revenue_AED", "mean"),
        Avg_ROI          = ("ROI_Score", "mean"),
        Footfall_Score   = ("Footfall_Score", "mean"),
        Competitor_Gap   = ("Competitor_Gap", "mean"),
        Rent_Index       = ("Rent_Index", "mean"),
        Demo_Score       = ("Demo_Score", "mean"),
        POI_Score        = ("POI_Score", "mean"),
    )
    .reset_index()
    .sort_values("Composite", ascending=False)
)

# ── Header ──
st.title("👓 Lenskart Dubai — Outlet Site Intelligence")
st.caption("Data sourced from GitHub · Adjust sidebar weights to re-rank localities in real time")

# ── Row 1: KPI Cards ──
top3 = locality_summary.head(3)
c1, c2, c3 = st.columns(3)
for col, (_, row) in zip([c1, c2, c3], top3.iterrows()):
    with col:
        st.metric(
            label=f"🏆 {row['Locality']}",
            value=f"Score: {row['Composite']:.1f}",
            delta=f"ROI: {row['Avg_ROI']:.2f}x | Rev: AED {row['Avg_Revenue']:,.0f}/mo"
        )

st.markdown("---")

# ── Row 2: Bar Chart + Radar ──
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📊 Locality Rankings")
    fig_bar = px.bar(
        locality_summary.head(10).sort_values("Composite"),
        x="Composite", y="Locality", orientation='h',
        color="Composite", color_continuous_scale="Teal"
    )
    fig_bar.update_layout(paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a",
                          font_color="white", height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🎯 Factor Breakdown — Top 3")
    cats   = ["Footfall_Score", "Demo_Score", "Competitor_Gap", "POI_Score"]
    labels = ["Footfall", "Demographics", "Comp Gap", "POI"]
    fig_r  = go.Figure()
    for _, row in top3.iterrows():
        vals = [row[c] for c in cats] + [row[cats[0]]]
        fig_r.add_trace(go.Scatterpolar(r=vals, theta=labels + [labels[0]],
                                         fill='toself', name=row['Locality']))
    fig_r.update_layout(paper_bgcolor="#1a1a1a", font_color="white",
                         polar=dict(bgcolor="#1a1a1a"), height=400)
    st.plotly_chart(fig_r, use_container_width=True)

# ── Row 3: Scatter + Table ──
col_a, col_b = st.columns([1.2, 1])

with col_a:
    st.subheader("🗺️ Opportunity Map")
    fig_s = px.scatter(
        locality_summary, x="Footfall_Score", y="Competitor_Gap",
        size="Composite", color="Avg_ROI", text="Locality",
        color_continuous_scale="RdYlGn", size_max=40
    )
    fig_s.update_traces(textposition="top center")
    fig_s.update_layout(paper_bgcolor="#1a1a1a", plot_bgcolor="#1a1a1a",
                         font_color="white", height=400)
    st.plotly_chart(fig_s, use_container_width=True)

with col_b:
    st.subheader("📋 Full Report")
    st.dataframe(
        locality_summary[["Locality", "Composite", "Avg_Revenue", "Avg_ROI", "Rent_Index"]]
        .rename(columns={"Avg_Revenue": "Revenue/mo (AED)", "Avg_ROI": "ROI"})
        .style.background_gradient(cmap="Greens", subset=["Composite"]),
        height=400
    )
