import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="3PL Financial Intelligence", layout="wide")

# --- 2. ADVANCED STYLING ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .main-header { font-size: 2.2em; font-weight: 800; color: #1e3799; border-bottom: 3px solid #1e3799; }
    .section-head { font-size: 1.2em; font-weight: 700; color: #4b6584; margin-top: 20px; }
    [data-testid="stMetricValue"] { font-size: 1.8em !important; color: #1e3799; }
    .stDataFrame { border: 1px solid #d1d8e0; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA INITIALIZATION (PER BEST PRACTICE DOC) ---
def initialize_3pl_engine():
    if 'ledger' not in st.session_state:
        months = pd.date_range(start="2025-01-01", periods=12, freq='MS').strftime('%b %Y')
        # Detailed line items based on your provided screenshot
        st.session_state.ledger = pd.DataFrame({
            'Month': months,
            'Handling Rev': [115000.0] * 12,
            'Storage Rev': [105000.0] * 12,
            'VAS Rev': [45000.0] * 12,
            'Mgmt Fees': [15000.0] * 12,
            'Pass-Through Rev': [20000.0] * 12,
            'Labor (Direct)': [126000.0] * 12,
            'Facility (Fixed)': [58800.0] * 12,
            'Consumables': [11200.0] * 12,
            'IT/Admin': [14000.0] * 12,
            'Corp Mgmt': [16800.0] * 12,
            'Depreciation': [14000.0] * 12
        })

initialize_3pl_engine()

# --- 4. SIDEBAR: OPERATIONAL DRIVERS ---
with st.sidebar:
    st.header("⚙️ Facility Drivers")
    vol = st.number_input("Throughput (Pallets)", value=5000, min_value=1)
    sqft = st.number_input("Facility SQFT", value=100000)
    actual_rent = st.number_input("Base Rent Expense", value=45000)
    
    st.divider()
    st.header("🎯 Best Practice Targets")
    target_gp = st.number_input("Target GP %", value=30.0) / 100
    target_ebitda = st.number_input("Target EBITDA %", value=19.0) / 100

# --- 5. CALCULATION LOGIC ---
df = st.session_state.ledger.copy()

# Revenue Logic
df['Gross Revenue'] = df['Handling Rev'] + df['Storage Rev'] + df['VAS Rev'] + df['Mgmt Fees'] + df['Pass-Through Rev']
df['Net Revenue'] = df['Gross Revenue'] - df['Pass-Through Rev']

# Cost Logic
df['Total Direct Costs'] = df['Labor (Direct)'] + df['Facility (Fixed)'] + df['Consumables']
df['Gross Profit'] = df['Net Revenue'] - df['Total Direct Costs']
df['EBITDA'] = df['Gross Profit'] - (df['IT/Admin'] + df['Corp Mgmt'])
df['EBIT'] = df['EBITDA'] - df['Depreciation']

# Single Month Analysis (Selected via UI)
st.markdown('<div class="main-header">🛡️ 3PL Playbook: Professional Diagnostic</div>', unsafe_allow_html=True)
sel_month = st.selectbox("Analyze Reporting Period:", df['Month'])
m = df[df['Month'] == sel_month].iloc[0]

# --- 6. HIGH-DENSITY KPI GRID ---
st.markdown('<p class="section-head">💰 Financial Performance (vs. Net Revenue)</p>', unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

# Margin Calcs
gp_m = m['Gross Profit'] / m['Net Revenue']
eb_m = m['EBITDA'] / m['Net Revenue']

kpi1.metric("Net Revenue", f"${m['Net Revenue']:,.0f}")
kpi2.metric("Gross Profit", f"${m['Gross Profit']:,.0f}", f"{gp_m:.1%}")
kpi3.metric("EBITDA", f"${m['EBITDA']:,.0f}", f"{eb_m:.1%}")
kpi4.metric("EBIT", f"${m['EBIT']:,.0f}", f"{(m['EBIT']/m['Net Revenue']):.1%}")

st.markdown('<p class="section-head">📊 Operational Benchmarks</p>', unsafe_allow_html=True)
op1, op2, op3, op4 = st.columns(4)

# Rent Recovery: Storage Revenue / Actual Base Rent
rent_rec = m['Storage Rev'] / actual_rent
# Labor % of Net Revenue
labor_eff = m['Labor (Direct)'] / m['Net Revenue']

op1.metric("Rent Recovery", f"{rent_rec:.1%}", delta="Goal: 125-140%", delta_color="normal" if rent_rec >= 1.25 else "inverse")
op2.metric("Labor Efficiency", f"{labor_eff:.1%}", delta="Goal: 45%", delta_color="inverse")
op3.metric("GP / Pallet", f"${m['Gross Profit']/vol:,.2f}")
op4.metric("Rev / SQFT", f"${m['Net Revenue']/sqft:,.2f}")

# --- 7. INTERACTIVE LEDGER & BRIDGE ---
st.divider()
c_led, c_bridge = st.columns([2, 1])

with c_led:
    st.subheader("📝 Monthly Operating Ledger")
    # Data editor updates the session state
    st.session_state.ledger = st.data_editor(st.session_state.ledger, hide_index=True, use_container_width=True)

with c_bridge:
    st.subheader("🧪 Profit Bridge")
    fig = go.Figure(go.Waterfall(
        orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Net Rev", "Labor", "Facility", "Consumables", "SG&A", "EBITDA"],
        y = [m['Net Revenue'], -m['Labor (Direct)'], -m['Facility (Fixed)'], -m['Consumables'], -(m['IT/Admin'] + m['Corp Mgmt']), 0],
        connector = {"line":{"color":"#1e3799"}},
    ))
    fig.update_layout(height=400, margin=dict(t=20, b=20, l=10, r=10), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# --- 8. STRATEGIC CONTROLS ---
st.divider()
if st.button("📂 Export Finalized Strategic Pack"):
    st.balloons()
    st.success(f"Final Audit for {sel_month} Complete.")
    
