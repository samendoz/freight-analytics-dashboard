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
    # Asegúrate de usar el nombre correcto del archivo generado
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

# Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
            
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3065/3065440.png", width=80)
st.sidebar.title("Control de Operaciones")
st.sidebar.markdown("Filtros de Auditoría")

# Origin and Sentiment Filters
origin_list = st.sidebar.multiselect(
    "Origen de la Carga", 
    options=df["load_origin"].unique(), 
    default=df["load_origin"].unique()
)

df["carrier_sentiment"] = df["carrier_sentiment"].str.capitalize()
sentiment_list = st.sidebar.multiselect(
    "Sentimiento del Carrier", 
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
st.markdown("Análisis avanzado de rendimiento, conversión y rendimiento financiero de embudos inbound.")
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

# Render KPIs as cards. Make all cards match the highest height for a uniform look
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(f'<div class="metric-box"><h4>📈 Conversion Rate</h4><h2>{conversion_rate:.1f}%</h2></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="metric-box"><h4>📦 Closed Contracts</h4><h2>{total_booked}</h2></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="metric-box"><h4>💵 Expected Revenue</h4><h2>${expected_revenue:,.2f} USD</h2></div>', unsafe_allow_html=True)
with kpi4:
    # Mostramos el delta financiero total de la operación
    st.markdown(f'<div class="metric-box"><h4>💰 Financial Delta</h4><h2>${total_variance:,.2f} USD</h2></div>', unsafe_allow_html=True)
with kpi5:
    st.markdown(f'<div class="metric-box"><h4>🔄 Avg. Negotiation Rounds</h4><h2>{avg_rounds:.1f} prom.</h2></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 6. Visualizaciones Gráficas con Plotly
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🎯 Number of calls per Class")
    
    #Commented because test data does not reflect an actual funnel
    outcome_counts = df_filtered["call_outcome_class"].value_counts().reset_index()
    outcome_counts.columns = ["Outcome Class", "Count"]
    
    # fig_funnel = go.Figure(go.Funnel(
    #     y=outcome_counts["Outcome Class"],
    #     x=outcome_counts["Count"],
    #     textinfo="value",
    #     marker={"color": ["#2ebd59", "#3498db", "#e74c3c", "#95a5a6"]}
    # ))
    # fig_funnel.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
    # st.plotly_chart(fig_funnel, use_container_width=True)

    #make a bar chart for the different outcome classes
    total = outcome_counts["Count"].sum()
    outcome_counts["Percentage"] = (outcome_counts["Count"] / total * 100).round(1).astype(str) + "%"

    fig_bar = px.bar(
        outcome_counts,
        x="Count",
        y="Outcome Class",
        orientation="h",
        text="Percentage",
        labels={"Count": "Number of Calls", "Outcome Class": "Call Outcome"}
    )
    fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🎭 Correlation: Sentiment vs Number of Negotiation Rounds")

    fig_scatter = px.box(
        df_filtered, 
        x="carrier_sentiment", 
        y="negotiation_rounds",
        color="carrier_sentiment",
        labels={"carrier_sentiment": "Carrier Sentiment", "negotiation_rounds": "Negotiation Rounds"},
        color_discrete_map={"Positive": "#2ebd59", "Neutral": "#f1c40f", "Frustrated": "#e74c3c"}
    )
    fig_scatter.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=300)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

#  Call hisotry Table
st.subheader("📝 Call History Records")

# Formatting the DataFrame for better readability in the table
formatted_df = df_filtered.copy()
formatted_df["listed_price"] = formatted_df["listed_price"].map("${:,.2f}".format)
formatted_df["agreed_price"] = formatted_df["agreed_price"].map("${:,.2f}".format)
formatted_df["created_at"] = formatted_df["created_at"].dt.strftime('%Y-%m-%d %H:%M')
formatted_df["call_duration"] = formatted_df["call_duration"].map("{:,} seg".format)

# Column order mapping
columns_to_show = [
    "id", "created_at", "mc_number", "carrier_name", 
    "load_origin", "load_destination", "listed_price", 
    "agreed_price", "negotiation_rounds", "call_outcome_class", 
    "carrier_sentiment", "call_duration"
]

st.dataframe(
    formatted_df[columns_to_show],
    use_container_width=True,
    hide_index=True
)