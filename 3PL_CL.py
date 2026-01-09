import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="3PL Playbook: IE & Finance", layout="wide")

# --- 2. STYLING ---
st.markdown("""
    <style>
    .main-header { font-size: 2.2em; font-weight: 800; color: #1e3799; border-bottom: 2px solid #1e3799; }
    .stMetric { background-color: #ffffff; border: 1px solid #e6e9ef; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE INITIALIZATION ---
def initialize_engine():
    if 'ledger' not in st.session_state:
        months = pd.date_range(start="2025-01-01", periods=12, freq='MS').strftime('%b %Y')
        st.session_state.ledger = pd.DataFrame({
            'Month': months,
            'Handling Rev': [115000.0] * 12,
            'Storage Rev': [105000.0] * 12,
            'VAS Rev': [45000.0] * 12,
            'Pass-Through': [20000.0] * 12,
            'Direct Labor': [110000.0] * 12,
            'Indirect Labor': [10000.0] * 12,
            'OT Expense': [6000.0] * 12,
            'Facility Fixed': [58800.0] * 12,
            'MHE Lease/Maint': [10500.0] * 12,
            'Pkg & Consumables': [11200.0] * 12,
            'IT/Admin': [14000.0] * 12,
            'Corp Mgmt Fee': [16800.0] * 12,
            'Depreciation': [14000.0] * 12
        })

initialize_engine()

# --- 4. SIDEBAR: OPERATIONAL DRIVERS ---
with st.sidebar:
    st.header("⚙️ Facility & IE Drivers")
    total_sqft = st.number_input("Total Facility SQFT", value=120000)
    actual_rent = st.number_input("Actual Rent (Base)", value=45000)
    mhe_fleet = st.number_input("MHE Fleet Count", value=18)
    
    st.divider()
    st.header("📦 Throughput & Headcount")
    vol = st.number_input("Pallet Throughput", value=5500)
    headcount = st.number_input("Total Warehouse HC", value=60)
    
    st.divider()
    st.header("🎯 Best Practice Targets")
    target_gp_pct = st.slider("Target GP %", 20, 40, 30) / 100
    target_ratio = st.slider("Dir:Ind Ratio Target", 5, 15, 10)
    target_ot = st.slider("Target OT %", 0, 10, 3) / 100

# --- 5. CALCULATION ENGINE ---
df = st.session_state.ledger.copy()
df['Net Revenue'] = df['Handling Rev'] + df['Storage Rev'] + df['VAS Rev'] + 15000 
df['Total Labor'] = df['Direct Labor'] + df['Indirect Labor'] + df['OT Expense']
df['Direct Costs'] = df['Total Labor'] + df['Facility Fixed'] + df['MHE Lease/Maint'] + df['Pkg & Consumables']
df['Gross Profit'] = df['Net Revenue'] - df['Direct Costs']
df['EBITDA'] = df['Gross Profit'] - (df['IT/Admin'] + df['Corp Mgmt Fee'])

# Selected Month
st.markdown('<div class="main-header">🛡️ 3PL Diagnostic: Finance & IE Intelligence</div>', unsafe_allow_html=True)
sel_month = st.selectbox("Reporting Period", df['Month'])
m = df[df['Month'] == sel_month].iloc[0]

# --- 6. KPI DASHBOARD WITH CALCULATED DELTAS ---
st.subheader("💰 Financial Performance")
f1, f2, f3, f4 = st.columns(4)

# GP Metric with Delta vs Target
current_gp_pct = m['Gross Profit'] / m['Net Revenue']
gp_delta = current_gp_pct - target_gp_pct

f1.metric("Net Revenue", f"${m['Net Revenue']:,.0f}")
f2.metric("Gross Profit", f"${m['Gross Profit']:,.0f}", f"{gp_delta:+.1%} vs Target")
f3.metric("EBITDA", f"${m['EBITDA']:,.0f}", f"{(m['EBITDA']/m['Net Revenue']):.1%}")
f4.metric("GP / Pallet", f"${m['Gross Profit']/vol:,.2f}")

st.subheader("🚀 Operational & IE Benchmarks")
ie1, ie2, ie3, ie4 = st.columns(4)

# KPI 1: Dir:Ind Ratio (Higher is better)
dir_ind_ratio = m['Direct Labor'] / (m['Indirect Labor'] if m['Indirect Labor'] > 0 else 1)
ratio_diff = dir_ind_ratio - target_ratio
ie1.metric("Dir:Ind Ratio", f"{dir_ind_ratio:.1f}:1", f"{ratio_diff:+.1f} vs Target")

# KPI 2: Rent Recovery (Higher is better)
rent_rec = m['Storage Rev'] / actual_rent
ie2.metric("Rent Recovery", f"{rent_rec:.1%}", f"{(rent_rec - 1.25):+.1%} vs Min (125%)")

# KPI 3: Overtime % (Lower is better - using 'inverse' delta color)
ot_pct = m['OT Expense'] / m['Total Labor']
ot_variance = ot_pct - target_ot
ie3.metric("Overtime %", f"{ot_pct:.1%}", f"{ot_variance:+.1%} vs Target", delta_color="inverse")

# KPI 4: MHE Utilization
ie4.metric("MHE Efficiency", f"{vol/mhe_fleet:.0f} Pallets/Unit", f"Fleet: {mhe_fleet}")

# --- 7. DATA EDITOR & VISUALS ---
st.divider()
c_left, c_right = st.columns([1.8, 1])

with c_left:
    st.subheader("📝 Activity-Based Operating Ledger")
    st.session_state.ledger = st.data_editor(st.session_state.ledger, hide_index=True, use_container_width=True)

with c_right:
    
    st.subheader("🧪 Financial Leakage")
    fig = go.Figure(go.Waterfall(
        orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Net Rev", "Direct Lab", "Indirect/OT", "Facility", "MHE", "SG&A", "EBITDA"],
        y = [m['Net Revenue'], -m['Direct Labor'], -(m['Indirect Labor']+m['OT Expense']), -m['Facility Fixed'], -m['MHE Lease/Maint'], -(m['IT/Admin']+m['Corp Mgmt Fee']), 0],
        connector = {"line":{"color":"#1e3799"}},
    ))
    fig.update_layout(height=450, margin=dict(t=20, b=20, l=10, r=10), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
