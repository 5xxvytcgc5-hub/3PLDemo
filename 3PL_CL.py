import streamlit as st
import pandas as pd
import numpy as np

# 1. Safe Imports
try:
    import plotly.graph_objects as go
except ImportError:
    st.error("Please create a requirements.txt file with 'plotly' included.")
    st.stop()

# 2. Page Setup
st.set_page_config(page_title="3PL Playbook Pro", layout="wide")

# 3. State Management
def init_data():
    if 'df' not in st.session_state:
        months = pd.date_range(start="2025-01-01", periods=12, freq='MS').strftime('%b %Y')
        st.session_state.df = pd.DataFrame({
            'Month': months,
            'Revenue': [150000.0] * 12,
            'Handling': [65000.0] * 12,
            'Storage': [35000.0] * 12,
            'Admin': [18000.0] * 12,
            'Depreciation': [2500.0] * 12
        })

init_data()

# 4. Sidebar Controls
with st.sidebar:
    st.header("Facility Drivers")
    vol = st.number_input("Monthly Pallet Vol", value=5000, min_value=1)
    target_gp = st.slider("Target GP/Pallet", 5.0, 25.0, 12.5)

# 5. Dashboard Calculations
df = st.session_state.df
# We focus on the first month for the dashboard metrics
d = df.iloc[0] 
gp = d['Revenue'] - d['Handling'] - d['Storage']
ebitda = gp - d['Admin']

# 6. UI Layout
st.title("🛡️ 3PL Diagnostic & Strategy")

col1, col2, col3 = st.columns(3)
col1.metric("Gross Profit", f"${gp:,.0f}")
col2.metric("EBITDA", f"${ebitda:,.0f}")
col3.metric("GP / Pallet", f"${gp/vol:,.2f}", delta=f"{ (gp/vol) - target_gp:,.2f} vs Target")

st.divider()

# 7. Data Editor & Visualization
c_left, c_right = st.columns([1, 1])

with c_left:
    st.subheader("Financial Ledger")
    st.session_state.df = st.data_editor(st.session_state.df, hide_index=True)

with c_right:
    st.subheader("Profit Bridge")
    fig = go.Figure(go.Waterfall(
        x = ["Rev", "Handl", "Stor", "Admin", "EBITDA"],
        y = [d['Revenue'], -d['Handling'], -d['Storage'], -d['Admin'], 0],
        measure = ["relative", "relative", "relative", "relative", "total"]
    ))
    fig.update_layout(height=400, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
