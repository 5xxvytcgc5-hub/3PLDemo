import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="3PL Playbook Pro", layout="wide")

# --- 2. STYLING ---
st.markdown("""
    <style>
    .main-header { font-size: 2.2em; font-weight: 800; color: #1e3799; border-bottom: 2px solid #1e3799; }
    .kpi-card { background-color: #f1f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #1e3799; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE INITIALIZATION (REAL-WORLD 3PL PARAMETERS) ---
def initialize_engine():
    if '3pl_ledger' not in st.session_state:
        months = pd.date_range(start="2025-01-01", periods=12, freq='MS').strftime('%b %Y')
        st.session_state['3pl_ledger'] = pd.DataFrame({
            'Month': months,
            'Handling Rev': [115000.0] * 12,
            'Storage Rev': [105000.0] * 12,
            'VAS Rev': [45000.0] * 12,
            'Mgmt Fees': [15000.0] * 12,
            'Pass-Through': [20000.0] * 12,
            'Direct Labor': [110000.0] * 12,
            'Indirect Labor': [16000.0] * 12,
            'Facility Cost': [58800.0] * 12,
            'Consumables': [11200.0] * 12,
            'IT & Admin': [14000.0] * 12,
            'Corp Allocations': [16800.0] * 12,
            'Depreciation': [14000.0] * 12
        })

initialize_engine()

# --- 4. SIDEBAR: OPERATIONAL DRIVERS ---
with st.sidebar:
    st.header("⚙️ Facility Specs")
    total_sqft = st.number_input("Total Facility SQFT", value=120000)
    actual_rent = st.number_input("Base Rent Expense", value=45000)
    
    st.divider()
    st.header("📦 Activity Drivers")
    throughput = st.number_input("Total Pallet Thruput", value=5500)
    occupied_locs = st.number_input("Avg Occupied Locs", value=8200)

# --- 5. LOGIC & CALCULATIONS ---
df = st.session_state['3pl_ledger'].copy()

# Revenue Logic
df['Gross Rev'] = df[['Handling Rev', 'Storage Rev', 'VAS Rev', 'Mgmt Fees', 'Pass-Through']].sum(axis=1)
df['Net Rev'] = df['Gross Rev'] - df['Pass-Through']

# Cost Logic
df['Total Labor'] = df['Direct Labor'] + df['Indirect Labor']
df['Direct Costs'] = df['Direct Labor'] + df['Facility Cost'] + df['Consumables']
df['Gross Profit'] = df['Net Rev'] - df['Direct Costs']
df['EBITDA'] = df['Gross Profit'] - (df['Indirect Labor'] + df['IT & Admin'] + df['Corp Allocations'])
df['EBIT'] = df['EBITDA'] - df['Depreciation']

# Single Month Analysis focus
st.markdown('<div class="main-header">🛡️ 3PL Diagnostic Intelligence</div>', unsafe_allow_html=True)
selected_month = st.selectbox("Select Reporting Period", df['Month'])
m = df[df['Month'] == selected_month].iloc[0]

# --- 6. KPI DASHBOARD ---
st.subheader("💰 Financial Health")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Net Revenue", f"${m['Net Rev']:,.0f}")
c2.metric("Gross Margin", f"{(m['Gross Profit']/m['Net Rev']):.1%}", f"${m['Gross Profit']:,.0f}")
c3.metric("EBITDA Margin", f"{(m['EBITDA']/m['Net Rev']):.1%}", f"${m['EBITDA']:,.0f}")
c4.metric("EBIT Margin", f"{(m['EBIT']/m['Net Rev']):.1%}")

st.divider()

st.subheader("📊 Operational Benchmarks")
o1, o2, o3, o4 = st.columns(4)

# Rent Recovery: (Storage Revenue / Base Rent Expense)
# Goal: > 125% per Best Practice
rent_rec = (m['Storage Rev'] / actual_rent)
o1.metric("Rent Recovery", f"{rent_rec:.1%}", delta="Goal: 125-140%")

# Labor Efficiency: Labor / Net Revenue
labor_pct = (m['Total Labor'] / m['Net Rev'])
o2.metric("Labor Efficiency", f"{labor_pct:.1%}", delta="Goal: 45%", delta_color="inverse")

o3.metric("GP / Pallet", f"${m['Gross Profit']/throughput:,.2f}")
o4.metric("Rev / SQFT", f"${m['Net Rev']/total_sqft:,.2f}")

# --- 7. LEDGER & VISUALIZATION ---
st.divider()
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("📝 Operating Ledger")
    st.session_state['3pl_ledger'] = st.data_editor(
        st.session_state['3pl_ledger'], 
        hide_index=True, 
        use_container_width=True
    )

with col_right:
    st.subheader("🧪 Margin Waterfall")
    fig = go.Figure(go.Waterfall(
        x = ["Net Rev", "Direct Labor", "Facility", "Consumables", "Admin/Indirect", "EBITDA"],
        y = [m['Net Rev'], -m['Direct Labor'], -m['Facility Cost'], -m['Consumables'], -(m['Indirect Labor'] + m['IT & Admin']), 0],
        measure = ["relative", "relative", "relative", "relative", "relative", "total"]
    ))
    fig.update_layout(height=450, template="plotly_white", margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

if st.button("🚀 Lock & Export Strategic Audit"):
    st.balloons()
    st.success(f"Audit Prepared for {selected_month}")
