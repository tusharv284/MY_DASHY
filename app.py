import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

st.set_page_config(layout="wide", page_title="ReactDash Analytics", page_icon="🔵")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
.stMetric > label { color: #94a3b8 !important; font-size: 12px; }
.stMetric > div > div:last-child { color: #f1f5f9 !important; }
section[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
}
.stPlotlyChart { border-radius: 12px; }
.metric-container { background: #1e293b !important; border-radius: 12px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    np
