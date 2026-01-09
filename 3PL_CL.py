import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="3PL IE Dashboard", layout="wide")

# --- 2. STYLING ---
st.markdown("""
    <style>
    .main-header { font-size: 2.2em; font-weight: 800; color: #1e3799; border-bottom: 2px solid #1e3799; }
    .metric-box { background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #d1d8e0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE INITIALIZATION ---
def initialize_ie_engine():
    if 'ledger' not in st.session_state:
        months = pd.date_range(start="2025-01-01", periods=12, freq='MS').strftime('%b %Y')
        st.session_state.ledger = pd.DataFrame({
            'Month': months,
            'Handling Rev': [115000.0] * 12,
            'Storage Rev': [105000.0] * 12,
            'VAS Rev': [45000.0] * 12,
            'Pass-Through': [20000.0] * 12,
            'Direct Labor': [110000.0] * 12,
            'Indirect Labor': [10000.0] * 12,  # Supervisors/Leads
            'OT Expense': [6000.0] * 12,
            'MHE Lease': [8000.0] * 12,
            'MHE Maint/Fuel': [2500.0] * 12,
            'Facility Cost': [58800.0] * 12,
            'IT/Admin': [14000.0] * 12,
            'Corp Mgmt': [16800.0] * 12,
            'Depreciation': [14000.0] * 12
        })

initialize_ie_engine()

# --- 4. SIDEBAR: OPERATIONAL DRIVERS ---
with st.sidebar:
    st.header("🏭 Facility & Assets")
    sqft = st.number_input("Total Facility SQFT", value=120000)
    actual_rent = st.number_input("Base Rent Expense", value=45000)
    mhe_units = st.number_input("Total MHE Fleet Count", value=15)
    
    st.divider()
    st.header("👷 Labor & Throughput")
    total_hc = st.number_input("Total Headcount", value=55)
    pallet_vol = st.number_input("Pallet Throughput", value=5500)
    
    st.divider()
    st.header("🎯 Best Practice Targets")
    target_ot = st.slider("Target OT %", 0.0, 10.0, 3.0) / 100
    target_ratio = st.slider("Target Direct:Indirect Ratio", 5, 15, 10)

# --- 5. LOGIC & CALCULATIONS ---
df = st.session_state.ledger.copy()
df['Net Revenue'] = (df['Handling Rev'] + df['Storage Rev'] + df['VAS Rev'] + 15000) # Including Mgmt Fees
df['Total MHE Cost'] = df['MHE Lease'] + df['MHE Maint/Fuel']
df['Total Labor'] = df['Direct Labor'] + df['Indirect Labor'] + df['OT Expense']
df['Direct Costs'] = df['Total Labor'] + df['Facility Cost'] + df['Total MHE Cost']
df['EBITDA'] = df['Net Revenue'] - df['Direct Costs'] - df['IT/Admin'] - df['Corp Mgmt']

# Focus Month Analysis
st.markdown('<div class="main-header">🛡️ 3PL Playbook: IE & Asset Intelligence</div>', unsafe_allow_html=True)
sel_month = st.selectbox("Select Analysis Period", df['Month'])
m = df[df['Month'] == sel_month].iloc[0]

# --- 6. ADVANCED KPI GRID ---
st.subheader("🚀 Labor & MHE Efficiency")
k1, k2, k3, k4 = st.columns(4)

# KPI 1: Direct to Indirect Ratio
ratio_val = m['Direct Labor'] / (m['Indirect Labor'] if m['Indirect Labor'] > 0 else 1)
k1.metric("Dir:Ind Ratio", f"{ratio_val:.1f}:1", delta=f"Goal: {target_ratio}:1")

# KPI 2: OT % of Total Labor
ot_pct = m['OT Expense'] / m['Total Labor']
k2.metric("Overtime %", f"{ot_pct:.1%}", delta=f"Target: {target_ot:.1%}", delta_color="inverse")

# KPI 3: MHE Cost per Unit
mhe_per_unit = m['Total MHE Cost'] / mhe_units
k3.metric("MHE Cost / Unit", f"${mhe_per_unit:,.0f}", help="Lease + Maintenance + Fuel per fork")

# KPI 4: Rent Recovery
rent_rec = m['Storage Rev'] / actual_rent
k4.metric("Rent Recovery", f"{rent_rec:.1%}", delta="Goal: 125%+")

# --- 7. DETAILED P&L & ASSET WATERFALL ---
st.divider()
c_led, c_chart = st.columns([1.5, 1])

with c_led:
    st.subheader("📝 Activity-Based Operating Ledger")
    st.session_state.ledger = st.data_editor(st.session_state.ledger, hide_index=True, use_container_width=True)

with c_chart:
    st.subheader("📉 Asset & Expense Leakage")
    # Mapping the journey from Net Revenue to EBITDA with MHE visibility
    fig = go.Figure(go.Waterfall(
        x = ["Net Rev", "Direct Labor", "Indirect/OT", "MHE Costs", "Facility", "SG&A", "EBITDA"],
        y = [m['Net Revenue'], -m['Direct Labor'], -(m['Indirect Labor'] + m['OT Expense']), -m['Total MHE Cost'], -m['Facility Cost'], -(m['IT/Admin'] + m['Corp Mgmt']), 0],
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "total"],
        connector = {"line":{"color":"#1e3799"}},
    ))
    fig.update_layout(height=450, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# --- 8. IE COMMENTARY ---
st.divider()
st.subheader("🔍 IE Tactical Observations")
o1, o2 = st.columns(2)
with o1:
    eff_val = pallet_vol / total_hc
    st.write(f"**Throughput Efficiency:** {eff_val:.1f} Pallets per Head")
    st.write(f"**Facility Density:** {pallet_vol / (sqft/1000):.2f} Pallets per 1k SQFT")
with o2:
    mhe_util = pallet_vol / mhe_units
    st.write(f"**MHE Utilization:** {mhe_util:.1f} Touches per Machine")
    st.progress(min(ot_pct * 10, 1.0), text=f"OT Burn Rate: {ot_pct:.1%}")
