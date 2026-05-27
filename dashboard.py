import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

# Load Env Variables
load_dotenv()

# Fetches data from CSV file
@st.cache_data
def load_simulated_data():
    df_csv = pd.read_csv("call_history.csv")
    df_csv["created_at"] = pd.to_datetime(df_csv["created_at"])
    return df_csv

df = load_simulated_data()

# Page Config
st.set_page_config(
    page_title="Load Carrier Dashboard - Acme Logistics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling using native Streamlit CSS Variables for dynamic Light/Dark mode
st.markdown("""
    <style>
    .main { 
        background-color: var(--background-color); 
    }
    .metric-box {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3065/3065440.png", width=80)
st.sidebar.title("Dashboard Filters")

# Origin and Sentiment Filters
origin_list = st.sidebar.multiselect(
    "Load Origin", 
    options=df["load_origin"].unique(), 
    default=df["load_origin"].unique()
)

df["carrier_sentiment"] = df["carrier_sentiment"].str.capitalize()
sentiment_list = st.sidebar.multiselect(
    "Carrier Sentiment", 
    options=df["carrier_sentiment"].unique(), 
    default=df["carrier_sentiment"].unique()
)

# Filtered Dataframe
df_filtered = df[
    (df["load_origin"].isin(origin_list)) & 
    (df["carrier_sentiment"].isin(sentiment_list))
]

# Dashboard Header
st.title("📊 Load Carrier Dashboard - Acme Logistics")
st.markdown("Welcome to Acme Logistics' Load Carrier Dashboard. ")
st.markdown("---")

# Analytics
total_calls = len(df_filtered)

# Conversion Rate KPI
booked_calls = df_filtered[df_filtered["outcome"] == "accepted"]
total_booked = len(booked_calls)

conversion_rate = (total_booked / total_calls * 100) if total_calls > 0 else 0.0

# Expected Revenue KPI
expected_revenue = booked_calls["agreed_price"].sum()

# Gestión de Rendimiento Financiero (Brokerage Yield Management) KPI
brokerage_variance = booked_calls["agreed_price"] - booked_calls["listed_price"]
total_variance = brokerage_variance.sum()
avg_rounds = booked_calls["negotiation_rounds"].mean() if total_booked > 0 else 0.0

# Render KPIs as cards.
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(f'<div class="metric-box"><h4>📈 Conversion Rate</h4><h2>{conversion_rate:.1f}%</h2></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="metric-box"><h4>📦 Closed Contracts</h4><h2>{total_booked}</h2></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="metric-box"><h4>💵 Expected Revenue</h4><h2>${expected_revenue:,.2f} USD</h2></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="metric-box"><h4>💰 Financial Delta</h4><h2>${total_variance:,.2f} USD</h2></div>', unsafe_allow_html=True)
with kpi5:
    st.markdown(f'<div class="metric-box"><h4>🔄 Avg. Negotiation Rounds</h4><h2>{avg_rounds:.1f} prom.</h2></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Visualizaciones Gráficas con Plotly
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎯 Number of calls per Class")
    
    outcome_counts = df_filtered["call_outcome_class"].value_counts().reset_index()
    outcome_counts.columns = ["Outcome Class", "Count"]
    
    total = outcome_counts["Count"].sum()
    outcome_counts["Percentage"] = (outcome_counts["Count"] / total * 100).round(1).astype(str) + "%"

    fig_bar = px.bar(
        outcome_counts,
        x="Count",
        y="Outcome Class",
        orientation="h",
        text="Percentage",
        labels={"Count": "Number of Calls", "Outcome Class": "Call Outcome"},
        template="plotly_white"  # Let dynamic styling overwrite background components
    )
    
    # Update layout to make background transparent so it matches light/dark themes natively
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(128,128,128,1)"), # Neutral gray font for labels
        margin=dict(l=20, r=20, t=20, b=20), 
        height=300
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🎭 Correlation: Sentiment vs Number of Negotiation Rounds")

    fig_scatter = px.box(
        df_filtered, 
        x="carrier_sentiment", 
        y="negotiation_rounds",
        color="carrier_sentiment",
        labels={"carrier_sentiment": "Carrier Sentiment", "negotiation_rounds": "Negotiation Rounds"},
        # Adjusted colors slightly to remain highly legible on both dark and light backgrounds
        color_discrete_map={"Positive": "#2ebd59", "Neutral": "#f1c40f", "Frustrated": "#e84118"}
    )
    
    # Update layout to make background transparent
    fig_scatter.update_layout(
        showlegend=False, 
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(128,128,128,1)"),
        margin=dict(l=20, r=20, t=20, b=20), 
        height=300
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# Call history Table
st.subheader("📝 Call History Records")

# Formatting the DataFrame
formatted_df = df_filtered.copy()
formatted_df["listed_price"] = formatted_df["listed_price"].map("${:,.2f}".format)
formatted_df["agreed_price"] = formatted_df["agreed_price"].map("${:,.2f}".format)
formatted_df["created_at"] = formatted_df["created_at"].dt.strftime('%Y-%m-%d %H:%M')
formatted_df["call_duration"] = formatted_df["call_duration"].map("{:,} seg".format)

columns_to_show = [
    "id", "created_at", "mc_number", "carrier_name", 
    "load_origin", "load_destination", "listed_price", 
    "agreed_price", "negotiation_rounds", "call_outcome_class", 
    "carrier_sentiment", "call_duration"
]

# st.dataframe natively handles theme switching
st.dataframe(
    formatted_df[columns_to_show],
    use_container_width=True,
    hide_index=True
)