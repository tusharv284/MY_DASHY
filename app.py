import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import silhouette_score

# ── Page Config ──────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="ReactDash Analytics", page_icon="🔵")

# ── CSS for ReactDash Style ───────────────────────────────────────
st.markdown("""
<style>
.stApp { 
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
.stMetric > label { color: #94a3b8 !important; font-size: 12px; }
.stMetric > div > div:last-child { color: #f1f5f9 !important; }
section[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
}
.stPlotlyChart { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────────────
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        "Firm_ID": [f"F{i:03d}" for i in range(1, n+1)],
        "Sys_Integration_Issue": np.random.choice([0,1,2,3,4,5], n, p=[0.05,0.1,0.2,0.3,0.2,0.15]),
        "Manual_Errors": np.random.choice([0,1,2,3], n, p=[0.3,0.3,0.25,0.15]),
        "RealTime_Insights": np.random.choice([0,1], n, p=[0.6,0.4]),
        "Annual_Revenue_K": np.random.lognormal(6, 1.2, n).clip(50, 1000),
        "Scalability_Score": np.random.normal(50, 15, n).clip(10, 100),
        "Employee_Count": np.random.choice([10,25,50,100,250,500], n, p=[0.3,0.25,0.2,0.15,0.07,0.03]),
        "Region": np.random.choice(["Dubai","Abu Dhabi","Sharjah","Ajman","RAK"], n),
        "Cluster": np.random.choice(["Strugglers","Satisfied","Scalers"], n, p=[0.35,0.25,0.4])
    })
    # Target variable
    df["Adoption_Interest"] = (
        (df["Sys_Integration_Issue"] > 2) * 0.4 +
        (df["Manual_Errors"] > 1) * 0.3 +
        (df["Annual_Revenue_K"] > 200) * 0.2 +
        np.random.normal(0, 0.1, n)
    ).clip(0,1).round()
    return df

df = load_data()

# ── Train Models ─────────────────────────────────────────────────
@st.cache_resource
def train_models(df):
    le = LabelEncoder()
    df_ml = df.copy()
    df_ml["Region_Enc"] = le.fit_transform(df_ml["Region"])
    df_ml["Cluster_Enc"] = le.fit_transform(df_ml["Cluster"])
    
    # RF Classification
    features = ["Sys_Integration_Issue","Manual_Errors","Annual_Revenue_K",
                "Scalability_Score","Employee_Count","Region_Enc"]
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(df_ml[features], df_ml["Adoption_Interest"])
    
    # KMeans Clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    cluster_features = ["Sys_Integration_Issue","Annual_Revenue_K","Scalability_Score"]
    kmeans.fit(df_ml[cluster_features])
    
    return rf, kmeans

rf_model, kmeans_model = train_models(df)

# ── HEADER ───────────────────────────────────────────────────────
st.markdown("""
<div style='background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%); 
            padding: 15px; border-radius: 12px; margin-bottom: 20px;'>
    <h1 style='color: white; margin: 0; font-size: 28px;'>🔵 UAE E-Commerce Analytics Dashboard</h1>
    <p style='color: #bfdbfe; margin: 5px 0 0 0;'>Classification | Clustering | Association Rules | Regression</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px; text-align: center;'>
        <div style='width: 60px; height
