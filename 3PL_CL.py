import streamlit as st
import pandas as pd
import numpy as np

# Use a try-except block to handle missing modules gracefully
try:
    import plotly.graph_objects as go
    import plotly.express as px
except ModuleNotFoundError:
    st.error("Missing Plotly library. Please add 'plotly' to your requirements.txt file.")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="3PL Playbook", layout="wide")

# --- INITIALIZE STATE ---
if 'financial_engine' not in st.session_state:
    months = pd.date_range(start="2025-01-01", periods=12, freq='MS').strftime('%b %Y')
    # Explicitly set data types to float64 for stability
    st.session_state.financial_engine = pd.DataFrame({
        'Month': months,
        'Revenue': np.array([150000.0] * 12, dtype=float),
        'Handling Costs': np.array([65000.0] * 12, dtype=float),
        'Storage Overhead': np.array([35000.0] * 12, dtype=float),
        'Equipment Lease': np.array([12000.0] * 12, dtype=float),
        'Fixed OpEx': np.array([18000.0] * 12, dtype=float),
        'Taxes': np.array([4500.0] * 12, dtype=float),
        'Depreciation': np.array([2500.0] * 12, dtype=float)
    })
    if 'pallet_throughput' not in st.session_state:
        st.session_state.pallet_throughput = 5000

initialize_state()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🕹️ Facility Drivers")
    vol = st.number_input("Monthly Pallet Throughput", min_value=1, value=st.session_state.pallet_throughput)
    fte = st.number_input("Warehouse FTE", min_value=1, value=45)
    locs = st.number_input("Occupied Locations", min_value=1, value=8500)
    
    st.divider()
    st.subheader("🎯 Performance Targets")
    tar_gp = st.slider("Target GP/Pallet ($)", 5.0, 30.0, 12.5)
    
# --- 5. DATA PROCESSING ---
# Apply the calculation engine to the current state
processed_df = calculate_metrics(st.session_state.financial_engine, vol)

# --- 6. MAIN UI ---
st.markdown('<div class="main-header">🛡️ Warehouse Diagnostic Dashboard</div>', unsafe_allow_html=True)

# Month Selector for Dynamic View
selected_month_name = st.selectbox("Focus Month Analysis", processed_df['Month'])
m_data = processed_df[processed_df['Month'] == selected_month_name].iloc[0]

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Revenue", f"${m_data['Revenue']:,.0f}")
with col2:
    gp_pct = (m_data['GP'] / m_data['Revenue']) * 100
    st.metric("Gross Profit", f"${m_data['GP']:,.0f}", f"{gp_pct:.1f}% Margin")
with col3:
    st.metric("EBITDA", f"${m_data['EBITDA']:,.0f}")
with col4:
    gp_pallet = m_data['GP_Per_Pallet']
    st.metric("GP / Pallet", f"${gp_pallet:,.2f}", delta=f"{gp_pallet - tar_gp:,.2f} vs Target")

st.divider()

# Charts & Editor Row
c_left, c_right = st.columns([1.2, 1])

with c_left:
    st.subheader("📝 Live Financial Ledger")
    # Using the editor to update session state directly
    edited_df = st.data_editor(
        st.session_state.financial_engine,
        use_container_width=True,
        hide_index=True,
        key="editor"
    )
    # Check if data changed and update state to trigger rerun
    if not edited_df.equals(st.session_state.financial_engine):
        st.session_state.financial_engine = edited_df
        st.rerun()

with c_right:
    st.subheader("📊 Profitability Bridge")
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "total"],
        x=["Revenue", "Handling", "Storage", "Leases", "Admin", "EBITDA"],
        y=[m_data['Revenue'], -m_data['Handling Costs'], -m_data['Storage Overhead'], 
           -m_data['Equipment Lease'], -m_data['Fixed OpEx'], 0],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- 7. FOOTER ---
st.divider()
if st.button("🚀 Export Monthly Report"):
    st.toast("Report generated successfully!", icon="✅")
