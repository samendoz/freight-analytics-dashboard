# 📊 Enterprise Freight Analytics Platform

An enterprise-grade Business Intelligence (BI) and operational analytics dashboard designed for modern freight brokerage environments. This application processes transaction logs, compliance status records, and multi-round rate negotiation telemetry to deliver real-time actionable insights into inbound carrier operations.

Built with **Python**, **Streamlit**, and **Plotly**, this decoupled analytical engine turns post-interaction metrics into an optimized decision-making system for freight brokers and logistics executives.

---

## 🚀 Key Performance Indicators (KPIs)

The interface natively extracts, aggregates, and visualizes 5 vital dimensions of logistics operations:

1. **Conversion Rate:** The percentage of processed carrier inquiries that successfully transition from initial call to an `accepted` shipping contract status.
2. **Closed Contracts:** A high-level volume counter tracking completed and secured capacity transactions.
3. **Expected Revenue:** Aggregate transactional volume calculating gross booked financial value directly from successful carrier contract closures (`agreed_price`).
4. **Financial Delta:** Real-time yield tracking displaying the precise variance between baseline target rates (`listed_price`) and final locked booking rates (`agreed_price`).
5. **Avg. Negotiation Rounds:** Granular friction monitoring tracking iterative counteroffer cycles (ranging from 0 to 3 rounds) to establish algorithmic thresholds.

---

## 🎨 Operational Visualizations

- **Horizontal Yield Dissemination:** Automatically replaces traditional static metrics with a relative percentage-weighted horizontal distribution chart (`px.bar`), pinpointing interaction drivers by their discrete outcome classes.
- **Negotiation Friction Boxplots:** Correlates carrier sentiments (Positive, Neutral, Frustrated) directly with the volume of negotiation cycles to identify customer experience benchmarks.
- **Granular Filter Controls:** Dynamic multi-select querying on the sidebar allows real-time segmentation of metrics based on geographic cargo origins (`load_origin`) and behavioral sentiment categories (`carrier_sentiment`).

---

## 🛠️ Data Pipeline & Architecture

The application is engineered as a highly lightweight consumer layer optimized for reading heavy analytical tables. It utilizes an automatic in-memory caching mechanism (`@st.cache_data`) to prevent redundant system execution cycles.