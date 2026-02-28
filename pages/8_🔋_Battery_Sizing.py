import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Battery Sizing Impact", layout="wide")
st.title("🔋 Battery Sizing Impact Analyzer")
st.markdown("Understand how the physical size of an EV battery scales the initial manufacturing carbon debt and delays the break-even point.")

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

# Fetch baseline CI
ci_g_kwh = grid_data[grid_data['Area'] == selected_country]['Value'].values[0]

st.sidebar.divider()
st.sidebar.header("⚙️ Manufacturing Assumptions")
e_ice_manu = st.sidebar.number_input("ICE Vehicle Total Mfg (kg CO2e)", value=7000, step=500)
e_ev_glider = st.sidebar.number_input("EV 'Glider' Mfg (kg CO2e)", value=5000, step=500, help="Emissions to build the EV body/motors, excluding the battery.")
battery_emissions_factor = st.sidebar.number_input("Battery Factor (kg CO2e/kWh)", value=100, step=10, help="Standard LCA estimate for lithium-ion battery production.")

st.sidebar.divider()
st.sidebar.header("🚗 Operational Stats")
ev_efficiency = st.sidebar.number_input("EV Consumption (kWh/km)", value=0.18, step=0.01)
e_ice_op = st.sidebar.number_input("ICE Emissions (kg/km)", value=0.22, step=0.01)

# Interactive marker for the user's specific choice
target_battery = st.sidebar.slider("Target Battery Size (kWh)", min_value=20, max_value=200, value=60, step=5)

# --- 3. The Math Engine ---
# Calculate Operational Savings
e_ev_op = (ci_g_kwh / 1000.0) * ev_efficiency
op_savings = e_ice_op - e_ev_op

# Generate an array of battery sizes from 20kWh (plug-in hybrid) to 200kWh (heavy electric truck)
battery_sizes = np.arange(20, 205, 5)

# Calculate Manufacturing Debt for each battery size: 
# Total EV Mfg = Glider + (Battery Size * Factor)
ev_total_manu = e_ev_glider + (battery_sizes * battery_emissions_factor)
carbon_debts = ev_total_manu - e_ice_manu

# Calculate Parity Distance for each size
if op_savings > 0:
    parity_distances = carbon_debts / op_savings
else:
    parity_distances = np.full_like(battery_sizes, float('inf'))

# Calculate the specific target vehicle's stats
target_ev_manu = e_ev_glider + (target_battery * battery_emissions_factor)
target_debt = target_ev_manu - e_ice_manu
target_parity = target_debt / op_savings if op_savings > 0 else float('inf')

# --- 4. Dashboard Display ---
st.subheader(f"Battery Impact in {selected_country}")
col1, col2, col3 = st.columns(3)
col1.metric("EV Mfg Footprint", f"{target_ev_manu:,.0f} kg CO2e")
col2.metric("Carbon Debt vs ICE", f"{target_debt:,.0f} kg CO2e")

if op_savings > 0:
    col3.metric("Break-Even Distance", f"{target_parity:,.0f} km")
else:
    col3.metric("Break-Even Distance", "Never")
    st.error("⚠️ The grid is too dirty! Operational savings are negative, so the battery debt can never be repaid.")

st.divider()

# --- 5. Visualization ---
if op_savings > 0:
    fig = go.Figure()
    
    # Plot the line showing how parity distance scales with battery size
    fig.add_trace(go.Scatter(
        x=battery_sizes, 
        y=parity_distances, 
        mode='lines', 
        name='Break-Even Distance',
        line=dict(color='#3498db', width=4),
        hovertemplate='<b>Battery:</b> %{x} kWh<br><b>Parity:</b> %{y:,.0f} km<extra></extra>'
    ))
    
    # Add a prominent marker for the user's selected Target Battery
    fig.add_trace(go.Scatter(
        x=[target_battery], 
        y=[target_parity], 
        mode='markers+text', 
        name='Your Selection',
        marker=dict(color='#e74c3c', size=14, line=dict(color='white', width=2)),
        text=[f"{target_battery} kWh<br>{target_parity:,.0f} km"],
        textposition="top left",
        hoverinfo='skip'
    ))

    
    
    fig.update_layout(
        title="<b>The Cost of Range Anxiety: How Battery Size Delays Carbon Parity</b>",
        xaxis_title="Battery Capacity (kWh)",
        yaxis_title="Distance to Break-Even (km)",
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', zeroline=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)