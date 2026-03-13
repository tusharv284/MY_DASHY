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
zone_filter = st.sidebar.multiselect("Zone Type", zone_options, default=zone_o
