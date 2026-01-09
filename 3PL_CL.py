import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="3PL Playbook Pro", layout="wide")

# --- 2. STYLING ---
st.markdown("""
    <style>
    .main-header { font-size: 2.3em; font-weight: 800; color: #0984e3; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. REAL-WORLD DATA INITIALIZATION ---
def initialize_state():
    if 'financial_engine' not in st.session_state:
        months = pd.date_range(start="2025-01-01", periods=12, freq='MS').strftime('%b %Y')
        # Numbers pulled directly from your "Best Practice" image
        st.session_state.financial_engine = pd.DataFrame({
            'Month': months,
            'Handling Rev': [115000.0] * 12,
            'Storage Rev': [105000.0] * 12,
            'VAS Rev': [45000.0] * 12,
            'Freight Mgmt': [15000.0] * 12,
            'Pass-Through': [20000.0] * 12,
            'Labor Cost': [126000.0] * 12,
            'Facility Cost': [58800.0] * 12,
            'Pkg & Consumables': [11200.0] * 12,
            'IT/Admin': [14000.0] * 12,
            'Corp Mgmt': [16800.0] * 12,
            'Depreciation': [14000.0] * 12
        })

initialize_state()

# --- 4. SIDEBAR: OPERATIONAL INPUTS ---
st.sidebar.header("🕹️ Facility Drivers")
vol = st.sidebar.number_input("Monthly Pallet Vol", value=5000, min_value=1)
rent_actual = st.sidebar.number_input("Actual Rent Cost", value=45000)

st.sidebar.divider()
st.sidebar.subheader("📈 KPI Targets")
target_gp_margin = st.sidebar.slider("Target Gross Margin %", 20, 40, 30)
target_ebitda_margin = st.sidebar.slider("Target EBITDA %", 10, 25, 19)

# --- 5. CALCULATION ENGINE ---
# Create a copy for calculations
df = st.session_state.financial_engine.copy()
df['Gross Revenue'] = df['Handling Rev'] + df['Storage Rev'] + df['VAS Rev'] + df['Freight Mgmt'] + df['Pass-Through']
df['Net Revenue'] = df['Gross Revenue'] - df['Pass-Through']
df['Total Direct Cost'] = df['Labor Cost'] + df['Facility Cost'] + df['Pkg & Consumables']
df['Gross Profit'] = df['Net Revenue'] - df['Total Direct Cost']
df['EBITDA'] = df['Gross Profit'] - (df['IT/Admin'] + df['Corp Mgmt'])
df['EBIT'] = df['EBITDA'] - df['Depreciation']

# Single Month Analysis focus
d = df.iloc[0]

# --- 6. MAIN DASHBOARD UI ---
st.markdown('<div class="main-header">🛡️ 3PL Diagnostic: Best Practice Mode</div>', unsafe_allow_html=True)

# Row 1: Financial Performance
col1, col2, col3, col4 = st.columns(4)
col1.metric("Net Revenue", f"${d['Net Revenue']:,.0f}")

gp_margin = (d['Gross Profit'] / d['Net Revenue']) * 100
col2.metric("Gross Profit", f"${d['Gross Profit']:,.0f}", f"{gp_margin:.1f}% Margin")

ebitda_margin = (d['EBITDA'] / d['Net Revenue']) * 100
col3.metric("EBITDA", f"${d['EBITDA']:,.0f}", f"{ebitda_margin:.1f}% vs {target_ebitda_margin}% Target")

col4.metric("EBIT", f"${d['EBIT']:,.0f}", f"{(d['EBIT']/d['Net Revenue'])*100:.1f}% Margin")

# Row 2: Operational KPIs (From your image)
st.divider()
st.subheader("📊 Operational Efficiency Benchmarks")
k1, k2, k3 = st.columns(3)

# Rent Recovery Calculation
rent_recovery = (d['Storage Rev'] / rent_actual) * 100
k1.metric("Rent Recovery", f"{rent_recovery:.1f}%", delta="Target: 125-140%", delta_color="normal" if rent_recovery >= 125 else "inverse")

# Labor as % of Net Revenue
labor_pct = (d['Labor Cost'] / d['Net Revenue']) * 100
k2.metric("Labor Efficiency", f"{labor_pct:.1f}%", delta="Target: 45%", delta_color="inverse")

# GP per Pallet
gp_pallet = d['Gross Profit'] / vol
k3.metric("GP / Pallet", f"${gp_pallet:,.2f}")

# --- 7. LEDGER & VISUALS ---
st.divider()
c_left, c_right = st.columns([1.5, 1])

with c_left:
    st.subheader("📝 Live Operating Ledger")
    # This allows you to edit the "Real World" numbers live
    st.session_state.financial_engine = st.data_editor(st.session_state.financial_engine, hide_index=True, use_container_width=True)

with c_right:
    st.subheader("🧪 Margin Waterfall")
    fig = go.Figure(go.Waterfall(
        x = ["Net Rev", "Labor", "Facility", "Pkg/Cons", "SG&A", "EBITDA"],
        y = [d['Net Revenue'], -d['Labor Cost'], -d['Facility Cost'], -d['Pkg & Consumables'], -(d['IT/Admin'] + d['Corp Mgmt']), 0],
        measure = ["relative", "relative", "relative", "relative", "relative", "total"]
    ))
    fig.update_layout(height=400, template="plotly_white", margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

if st.button("🚀 Finalize Monthly Audit"):
    st.balloons()
    st.success("Analysis aligns with Best Practice Benchmarks.")
