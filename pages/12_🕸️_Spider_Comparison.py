import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Multi-Metric Radar", layout="wide")
st.title("🕸️ Multi-Metric Vehicle Profile")
st.markdown("Compare the complete environmental footprint of an EV vs. an ICE vehicle across five critical dimensions simultaneously. **Smaller shapes indicate a lower overall environmental impact.**")

# --- 1. Load Data ---
@st.cache_data
def load_ember_data():
    try:
        df = pd.read_csv("../ember_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("ember_data.csv")
        
    co2_data = df[df['Variable'] == 'CO2 intensity'].copy()
    latest_year = co2_data['Year'].max()
    return co2_data[co2_data['Year'] == latest_year]

with st.spinner("Loading real-world grid data..."):
    grid_data = load_ember_data()

# --- 2. Sidebar UI ---
st.sidebar.header("🌍 Scenario Settings")
country_list = sorted(grid_data['Area'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Choose a Charging Grid:", country_list, index=country_list.index("World") if "World" in country_list else 0)

ci_g_kwh = grid_data[grid_data['Area'] == selected_country]['Value'].values[0]

st.sidebar.divider()
st.sidebar.header("🚗 Vehicle Assumptions")
annual_mileage = st.sidebar.number_input("Annual Mileage (km/year)", value=15000, step=1000)
lifespan = 15

# Standard Presets
e_ev_manu = 12000
e_ice_manu = 7000
ev_efficiency = 0.16
e_ice_op = 0.22

# --- 3. The Math Engine (Calculating the 5 Dimensions) ---
# Dimension 1: Manufacturing Debt (kg CO2e)
# Dimension 2: 15-Year Operational Impact (kg CO2e)
ev_op_15yr = (ci_g_kwh / 1000.0) * ev_efficiency * annual_mileage * lifespan
ice_op_15yr = e_ice_op * annual_mileage * lifespan

# Dimension 3: Total Lifecycle Volume (kg CO2e)
ev_total = e_ev_manu + ev_op_15yr
ice_total = e_ice_manu + ice_op_15yr

# Dimension 4: Grid Dependency (Scale of 0 to 100 based on grid dirtiness)
ev_grid_dependency = min((ci_g_kwh / 800) * 100, 100) # 800+ is terrible
ice_grid_dependency = 0 # ICE vehicles don't depend on the electric grid

# Dimension 5: Break-Even Delay (km)
carbon_debt = e_ev_manu - e_ice_manu
op_savings_per_km = e_ice_op - ((ci_g_kwh / 1000.0) * ev_efficiency)

if op_savings_per_km > 0:
    break_even_km = carbon_debt / op_savings_per_km
else:
    break_even_km = 300000 # Cap at 300k to represent "Never"

# ICE break-even delay is practically "0" for the sake of comparison since it starts with the advantage
ice_break_even = 0 

# --- 4. Normalization for the Radar Chart ---
# We must scale raw numbers to a 0-100 scale so the chart plots smoothly
categories = ['Manufacturing Debt', '15-Yr Operational', 'Lifecycle Volume', 'Grid Dependency', 'Break-Even Delay']

def normalize(ev_val, ice_val):
    max_val = max(ev_val, ice_val)
    if max_val == 0: return 0, 0
    return (ev_val / max_val) * 100, (ice_val / max_val) * 100

ev_mfg_norm, ice_mfg_norm = normalize(e_ev_manu, e_ice_manu)
ev_op_norm, ice_op_norm = normalize(ev_op_15yr, ice_op_15yr)
ev_tot_norm, ice_tot_norm = normalize(ev_total, ice_total)
ev_grid_norm, ice_grid_norm = ev_grid_dependency, ice_grid_dependency
ev_be_norm, ice_be_norm = normalize(break_even_km, ice_break_even)

ev_normalized = [ev_mfg_norm, ev_op_norm, ev_tot_norm, ev_grid_norm, ev_be_norm]
ice_normalized = [ice_mfg_norm, ice_op_norm, ice_tot_norm, ice_grid_norm, ice_be_norm]

# Raw values for the hover tooltips
ev_raw = [f"{e_ev_manu:,.0f} kg", f"{ev_op_15yr:,.0f} kg", f"{ev_total:,.0f} kg", f"{ci_g_kwh:,.0f} gCO2/kWh", f"{break_even_km:,.0f} km"]
ice_raw = [f"{e_ice_manu:,.0f} kg", f"{ice_op_15yr:,.0f} kg", f"{ice_total:,.0f} kg", "0 (Fossil Fuel)", "Baseline"]

# --- 5. Draw the Spider Chart ---
st.subheader(f"Environmental Profile in {selected_country}")

fig = go.Figure()

# Add ICE Polygon
fig.add_trace(go.Scatterpolar(
    r=ice_normalized,
    theta=categories,
    fill='toself',
    name='Internal Combustion (ICE)',
    line=dict(color='#e74c3c'),
    fillcolor='rgba(231, 76, 60, 0.4)',
    text=ice_raw,
    hovertemplate="%{theta}<br>Value: %{text}<extra></extra>"
))

# Add EV Polygon
fig.add_trace(go.Scatterpolar(
    r=ev_normalized,
    theta=categories,
    fill='toself',
    name='Electric Vehicle (EV)',
    line=dict(color='#2ecc71'),
    fillcolor='rgba(46, 204, 113, 0.5)',
    text=ev_raw,
    hovertemplate="%{theta}<br>Value: %{text}<extra></extra>"
))



fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=False, range=[0, 100]) # Hide the 0-100 numbers to keep it clean
    ),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# --- 6. Quick Analysis ---
st.divider()
st.markdown("### 🔍 Profile Breakdown")
st.info("The EV (Green) sharply spikes outward on **Manufacturing Debt** and **Grid Dependency**. However, look at the **15-Yr Operational** axis. If the grid is clean, the green shape will completely collapse inward on that side, giving the EV a vastly superior total lifecycle volume compared to the massive red ICE shape.")