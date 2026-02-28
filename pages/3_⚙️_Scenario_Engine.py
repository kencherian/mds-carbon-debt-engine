import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="CDE Scenario Engine", layout="wide")
st.title("⚙️ The CDE Scenario Engine (Integrated)")
st.markdown("This module combines **Real-World Vehicle Presets**, **Global Grid Data**, and **Future Decarbonization Modeling** to find the exact carbon break-even year.")

# --- 1. Load Data ---
@st.cache_data
def load_ember_data():
    # Attempt to load from parent directory first (since we are in the 'pages' folder)
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
st.sidebar.header("1. Region & Grid Future")
country_list = sorted(grid_data['Area'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Choose a Grid:", country_list, index=country_list.index("World") if "World" in country_list else 0)

# Fetch baseline CI (CI_0)
ci_0_g_kwh = grid_data[grid_data['Area'] == selected_country]['Value'].values[0]

r_pct = st.sidebar.slider("Grid Decarbonization Rate (%/year)", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
r = r_pct / 100.0

st.sidebar.divider()

# --- NEW: Vehicle Presets Integration ---
st.sidebar.header("2. Choose Vehicle Profile")
vehicle_db = {
    "Compact Car (e.g., Leaf vs Corolla)": {"ev_manu": 8500, "ice_manu": 5500, "ev_op": 0.14, "ice_op": 0.18},
    "Mid-Size Sedan (e.g., Model 3 vs 3 Series)": {"ev_manu": 11000, "ice_manu": 7000, "ev_op": 0.16, "ice_op": 0.22},
    "Large SUV/Truck (e.g., Lightning vs F-150)": {"ev_manu": 16000, "ice_manu": 9000, "ev_op": 0.24, "ice_op": 0.35}
}
selected_class = st.sidebar.selectbox("Vehicle Class:", list(vehicle_db.keys()))
defaults = vehicle_db[selected_class]

# Advanced users can open this to tweak the preset numbers
with st.sidebar.expander("⚙️ Fine-Tune Vehicle Specs"):
    e_ev_manu = st.number_input("EV Mfg (kg CO2e)", value=defaults["ev_manu"], step=500)
    e_ice_manu = st.number_input("ICE Mfg (kg CO2e)", value=defaults["ice_manu"], step=500)
    ev_efficiency = st.number_input("EV Cons. (kWh/km)", value=defaults["ev_op"], step=0.01)
    e_ice_op = st.number_input("ICE Emiss. (kg/km)", value=defaults["ice_op"], step=0.01)

st.sidebar.divider()
st.sidebar.header("3. Vehicle Usage")
annual_mileage = st.sidebar.number_input("Annual Mileage (km/year)", value=15000, step=1000)
vehicle_lifespan = st.sidebar.slider("Vehicle Lifespan (Years)", min_value=5, max_value=25, value=15)

# --- 3. The Time-Series Math Engine ---
years = np.arange(1, vehicle_lifespan + 1)
cumulative_distance = years * annual_mileage

# Calculate grid intensity for each year: CI(t) = CI_0 * (1-r)^(t-1)
grid_intensity_t = ci_0_g_kwh * (1 - r)**(years - 1)

# Emissions calculations
ev_emissions_per_km_t = (grid_intensity_t / 1000.0) * ev_efficiency
ev_annual_emissions = ev_emissions_per_km_t * annual_mileage
ice_annual_emissions = np.full(vehicle_lifespan, e_ice_op * annual_mileage)

ev_cumulative = e_ev_manu + np.cumsum(ev_annual_emissions)
ice_cumulative = e_ice_manu + np.cumsum(ice_annual_emissions)

parity_mask = ev_cumulative < ice_cumulative

# --- 4. Dashboard Display ---
st.header(f"Simulation: {selected_class} in {selected_country}")
col1, col2, col3 = st.columns(3)
col1.metric("Starting Grid", f"{ci_0_g_kwh:,.0f} gCO2/kWh")
col2.metric(f"Grid in Year {vehicle_lifespan}", f"{grid_intensity_t[-1]:,.0f} gCO2/kWh")

if not any(parity_mask):
    col3.metric("Break-Even Point", "Never")
    st.error("⚠️ Under this scenario, the EV never pays off its carbon debt within its expected lifespan.")
else:
    parity_year = np.argmax(parity_mask) + 1 
    parity_distance = parity_year * annual_mileage
    col3.metric("Break-Even Point", f"Year {parity_year}")
    st.success(f"✅ The EV achieves carbon parity in **Year {parity_year}** ({parity_distance:,.0f} km)! The grid's {r_pct}% annual improvement visibly bends the EV emissions curve.")

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
    title=f"Dynamic Carbon Parity: {selected_class} in {selected_country}",
    color_discrete_map={'EV Total Emissions': '#2ecc71', 'ICE Total Emissions': '#95a5a6'},
    markers=True
)

if any(parity_mask):
    fig.add_vline(x=parity_year, line_dash="dash", line_color="#e74c3c", annotation_text=f"Parity: Year {parity_year}")

st.plotly_chart(fig, use_container_width=True)