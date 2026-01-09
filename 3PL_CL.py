import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="3PL Playbook Light", layout="wide")

# --- 2. THEME & STYLING ---
st.markdown("""
    <style>
    .main-header { font-size: 2.5em; font-weight: 800; color: #0984e3; margin-bottom: 0.2em; }
    .company-brand { font-size: 1.8em; font-weight: 800; color: #0984e3; margin-bottom: 10px; border-bottom: 2px solid #0984e3; }
    .stMetric { background-color: #1e1e2e; padding: 15px; border-radius: 10px; border-left: 5px solid #0984e3; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MASTER INITIALIZATION (3PL SPECIFIC) ---
def initialize_state():
    if 'financial_engine' not in st.session_state:
        months = pd.date_range(start="2025-01-01", periods=12, freq='MS').strftime('%b %Y')
        st.session_state.financial_engine = pd.DataFrame({
            'Month': months,
            'Revenue': [150000.0] * 12,           # Monthly Contract Revenue
            'Handling Costs': [65000.0] * 12,     # Variable Warehouse Labor
            'Storage Overhead': [35000.0] * 12,   # Facility utility/rent
            'Equipment Lease': [12000.0] * 12,    # Forklifts/MHE
            'Fixed OpEx': [18000.0] * 12,         # Site Management/Admin
            'Taxes': [4500.0] * 12,
            'Depreciation': [2500.0] * 12
        })

    defaults = {
        'pallet_throughput': 5000, 'staff_count': 45, 'locations': 8500,
        'target_gp_pallet': 12.50, 'target_ebit_pallet': 5.0
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

initialize_state()

# --- 4. SIDEBAR LEVERS ---
st.sidebar.markdown('<div class="company-brand">3PL Playbook</div>', unsafe_allow_html=True)
st.sidebar.subheader("🕹️ Facility Drivers")
vol = st.sidebar.number_input("Monthly Pallet Throughput", value=st.session_state.pallet_throughput, step=100)
fte = st.sidebar.number_input("Warehouse FTE", value=st.session_state.staff_count)
locs = st.sidebar.number_input("Occupied Locations", value=st.session_state.locations)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Target Economics")
tar_gp = st.sidebar.slider("Target GP/Pallet", 5.0, 25.0, value=12.5)
tar_ebit = st.sidebar.slider("Target EBIT/Pallet", 1.0, 15.0, value=5.0)

# --- 5. MAIN DASHBOARD ---
st.markdown('<div class="main-header">🛡️ Warehouse Diagnostic & Strategy</div>', unsafe_allow_html=True)

# Pull Data
d = st.session_state.financial_engine.iloc[0]
gp = d['Revenue'] - d['Handling Costs'] - d['Storage Overhead']
ebitda = gp - d['Equipment Lease'] - d['Fixed OpEx']
ebit = ebitda - d['Depreciation']

# Row 1: The 3PL KPI Grid
st.subheader("💰 Financial & Operational performance")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"${d['Revenue']:,.0f}")
c2.metric("Gross Profit", f"${gp:,.0f}", f"{(gp/d['Revenue']):.1%}")
c3.metric("EBITDA", f"${ebitda:,.0f}", f"{(ebitda/d['Revenue']):.1%}")
c4.metric("EBIT", f"${ebit:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)
c5, c6, c7, c8 = st.columns(4)
c5.metric("GP / Pallet", f"${gp/vol:,.2f}", delta=f"Target: ${tar_gp}")
c6.metric("Throughput / FTE", f"{vol/fte:,.1f} units")
c7.metric("Handling Cost / Pallet", f"${d['Handling Costs']/vol:,.2f}")
c8.metric("Rev / Location", f"${d['Revenue']/locs:,.2f}")

# Row 2: Visualizations
st.markdown("---")
col_wf, col_ledger = st.columns([1, 1])

with col_wf:
    st.subheader("📊 Profitability Bridge")
    fig_wf = go.Figure(go.Waterfall(
        x=["Revenue", "Handling", "Storage", "Leases", "Admin", "EBITDA"],
        y=[d['Revenue'], -d['Handling Costs'], -d['Storage Overhead'], -d['Equipment Lease'], -d['Fixed OpEx'], 0],
        connector={"line":{"color":"#0984e3"}}
    ))
    fig_wf.update_layout(template="plotly_dark", height=400, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_wf, use_container_width=True)

with col_ledger:
    st.subheader("📝 Live Operating Ledger")
    # Allows for on-the-fly adjustment of the base P&L
    st.session_state.financial_engine = st.data_editor(
        st.session_state.financial_engine, 
        use_container_width=True, 
        key="light_pnl_edit"
    )

# 

# Row 3: Strategic Commentary
st.markdown("---")
st.subheader("📝 Management commentary")
col_com1, col_com2 = st.columns(2)
with col_com1:
    st.text_area("Operational Risks", "Labor availability remains tight for night shifts; MHE lease renewals pending Q3.")
with col_com2:
    st.text_area("Growth Opportunities", "Potential for 15% density increase via VNA (Very Narrow Aisle) conversion in Zone B.")

if st.button("🔒 Finalize Strategic Pack"):
    st.balloons()
    st.success("Ground Transportation & 3PL Playbook Certified.")
