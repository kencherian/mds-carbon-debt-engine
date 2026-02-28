import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="CDE Scenario Engine", layout="wide")
st.title("⚙️ The CDE Scenario Engine")
st.markdown("This prototype simulates how **grid decarbonization over time** accelerates the carbon parity break-even point.")

# --- 1. Load Data ---
@st.cache_data
def load_ember_data():
    df = pd.read_csv("ember_data.csv")
    co2_data = df[df['Variable'] == 'CO2 intensity'].copy()
    latest_year = co2_data['Year'].max()
    return co2_data[co2_data['Year'] == latest_year]

with st.spinner("Loading real-world grid data..."):
    grid_data = load_ember_data()

# --- 2. UI Inputs ---
st.sidebar.header("1. Region & Grid Future")
country_list = sorted(grid_data['Area'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Choose a Grid:", country_list, index=country_list.index("World") if "World" in country_list else 0)

# Fetch baseline CI (CI_0)
ci_0_g_kwh = grid_data[grid_data['Area'] == selected_country]['Value'].values[0]

# The New Scenario Input!
r_pct = st.sidebar.slider("Grid Decarbonization Rate (%/year)", min_value=0.0, max_value=10.0, value=3.0, step=0.5, help="How fast is the grid improving?")
r = r_pct / 100.0

st.sidebar.divider()
st.sidebar.header("2. Vehicle Usage")
annual_mileage = st.sidebar.number_input("Annual Mileage (km/year)", value=15000, step=1000)
vehicle_lifespan = st.sidebar.slider("Vehicle Lifespan (Years)", min_value=10, max_value=25, value=15)

st.sidebar.divider()
st.sidebar.header("3. Vehicle Assumptions")
e_ev_manu = st.sidebar.number_input("EV Manufacturing (kg CO2e)", value=10000, step=500)
e_ice_manu = st.sidebar.number_input("ICE Manufacturing (kg CO2e)", value=6000, step=500)
ev_efficiency = st.sidebar.number_input("EV Consumption (kWh/km)", value=0.15, step=0.01)
e_ice_op = st.sidebar.number_input("ICE Emissions (kg CO2e/km)", value=0.20, step=0.01)

# --- 3. The Time-Series Math Engine ---
# Create an array of years
years = np.arange(1, vehicle_lifespan + 1)
cumulative_distance = years * annual_mileage

# Calculate grid intensity for each year: CI(t) = CI_0 * (1-r)^(t-1)
# We use t-1 so Year 1 uses the current grid, Year 2 uses the improved grid, etc.
grid_intensity_t = ci_0_g_kwh * (1 - r)**(years - 1)

# EV emissions per year (converting gCO2 to kgCO2)
ev_emissions_per_km_t = (grid_intensity_t / 1000.0) * ev_efficiency
ev_annual_emissions = ev_emissions_per_km_t * annual_mileage

# ICE annual emissions are constant
ice_annual_emissions = np.full(vehicle_lifespan, e_ice_op * annual_mileage)

# Calculate CUMULATIVE emissions (manufacturing + sum of operational years)
ev_cumulative = e_ev_manu + np.cumsum(ev_annual_emissions)
ice_cumulative = e_ice_manu + np.cumsum(ice_annual_emissions)

# --- 4. Find the Break-Even Point ---
# Check where EV becomes less than ICE
parity_mask = ev_cumulative < ice_cumulative

st.header(f"Scenario Analysis: {selected_country}")
col1, col2, col3 = st.columns(3)
col1.metric("Current Grid Intensity", f"{ci_0_g_kwh:,.0f} gCO2/kWh")
col2.metric(f"Grid Intensity in Year {vehicle_lifespan}", f"{grid_intensity_t[-1]:,.0f} gCO2/kWh")

if not any(parity_mask):
    st.error("⚠️ Under this scenario, the EV never pays off its carbon debt within its lifespan.")
else:
    # Find the exact year it crosses over
    parity_year = np.argmax(parity_mask) + 1 
    parity_distance = parity_year * annual_mileage
    
    col3.metric("Break-Even Point", f"Year {parity_year} ({parity_distance:,.0f} km)")
    st.success(f"✅ The EV achieves carbon parity in **Year {parity_year}**! Thanks to the {r_pct}% decarbonization rate, its operational footprint shrinks every year.")

st.divider()

# --- 5. Visualization ---
chart_data = pd.DataFrame({
    'Year': years,
    'Cumulative Distance (km)': cumulative_distance,
    'EV Total Emissions': ev_cumulative,
    'ICE Total Emissions': ice_cumulative
})

chart_data_melted = chart_data.melt(
    id_vars=['Year', 'Cumulative Distance (km)'], 
    value_vars=['EV Total Emissions', 'ICE Total Emissions'], 
    var_name='Vehicle Type', 
    value_name='Total Emissions (kg CO2e)'
)

fig = px.line(
    chart_data_melted, 
    x='Year', 
    y='Total Emissions (kg CO2e)', 
    color='Vehicle Type', 
    hover_data=['Cumulative Distance (km)'],
    title="Dynamic Carbon Parity (Factoring in Grid Improvements)",
    color_discrete_map={'EV Total Emissions': '#2ecc71', 'ICE Total Emissions': '#95a5a6'},
    markers=True
)

if any(parity_mask):
    fig.add_vline(x=parity_year, line_dash="dash", line_color="#e74c3c", annotation_text=f"Parity: Year {parity_year}")

st.plotly_chart(fig, use_container_width=True)