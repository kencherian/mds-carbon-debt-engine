import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mini-CDE Dashboard", layout="wide")
st.title("🔋 The 'Mini-CDE' Integrated Dashboard")
st.markdown("This vertical slice integrates real-world Ember grid data with your Carbon Parity mathematical model.")

# --- 1. Load the Ember Data ---
@st.cache_data
def load_ember_data():
    df = pd.read_csv("ember_data.csv")
    co2_data = df[df['Variable'] == 'CO2 intensity'].copy()
    # Let's automatically grab the most recent year in the dataset
    latest_year = co2_data['Year'].max()
    return co2_data[co2_data['Year'] == latest_year], latest_year

with st.spinner("Loading real-world grid data..."):
    grid_data, data_year = load_ember_data()

# --- 2. Sidebar Inputs ---
st.sidebar.header("🌍 1. Select Region")
# Get a clean list of all countries/regions
country_list = grid_data['Area'].dropna().unique().tolist()
country_list.sort()
selected_country = st.sidebar.selectbox("Choose a Grid:", country_list, index=country_list.index("World") if "World" in country_list else 0)

# Fetch the actual Carbon Intensity for the chosen region!
country_ci_g_kwh = grid_data[grid_data['Area'] == selected_country]['Value'].values[0]

st.sidebar.divider()
st.sidebar.header("🚗 2. Vehicle Assumptions")
e_ev_manu = st.sidebar.number_input("EV Manufacturing (kg CO2e)", value=10000, step=500)
e_ice_manu = st.sidebar.number_input("ICE Manufacturing (kg CO2e)", value=6000, step=500)

st.sidebar.markdown("**Operational Efficiency**")
ev_efficiency = st.sidebar.number_input("EV Consumption (kWh/km)", value=0.15, step=0.01, help="Typical EV uses ~0.15 to 0.20 kWh per km.")
e_ice_op = st.sidebar.number_input("ICE Emissions (kg CO2e/km)", value=0.20, step=0.01, help="Typical gas car emits ~0.20 kg per km.")

# --- 3. The Core CDE Math ---
# Convert grid intensity from gCO2/kWh to kgCO2/kWh, then multiply by EV efficiency
grid_intensity_kg = country_ci_g_kwh / 1000.0
e_ev_op = grid_intensity_kg * ev_efficiency

st.header(f"Grid Profile: {selected_country} ({data_year})")
col1, col2 = st.columns(2)
col1.metric("Grid Carbon Intensity", f"{country_ci_g_kwh:,.1f} gCO2/kWh")
col2.metric("Calculated EV Emissions", f"{e_ev_op:.3f} kg CO2e/km")

st.divider()

# --- 4. Parity Logic & Visualization ---
carbon_debt = e_ev_manu - e_ice_manu
op_savings_per_km = e_ice_op - e_ev_op

if carbon_debt <= 0:
    st.success("🎉 No Carbon Debt! The EV is greener from the factory door.")
elif op_savings_per_km <= 0:
    st.error(f"⚠️ In **{selected_country}**, the grid is too carbon-intensive! The EV emits {e_ev_op:.3f} kg/km, which is worse than the ICE ({e_ice_op:.3f} kg/km). The carbon debt will NEVER be paid off!")
else:
    parity_distance = carbon_debt / op_savings_per_km
    st.success(f"✅ In **{selected_country}**, an EV pays off its carbon debt after **{parity_distance:,.0f} km**.")
    
    # Generate the Chart Data
    distances = list(range(0, 300000, 2000))
    ev_total = [e_ev_manu + (e_ev_op * d) for d in distances]
    ice_total = [e_ice_manu + (e_ice_op * d) for d in distances]
    
    chart_data = pd.DataFrame({'Distance (km)': distances, 'EV Emissions': ev_total, 'ICE Emissions': ice_total})
    chart_data_melted = chart_data.melt(id_vars=['Distance (km)'], value_vars=['EV Emissions', 'ICE Emissions'], var_name='Vehicle Type', value_name='Total Emissions (kg CO2e)')
    
    # Plotly Chart
    fig = px.line(
        chart_data_melted, x='Distance (km)', y='Total Emissions (kg CO2e)', 
        color='Vehicle Type', title=f"Carbon Debt Equilibirum in {selected_country}", 
        color_discrete_map={'EV Emissions': '#2ecc71', 'ICE Emissions': '#95a5a6'}
    )
    fig.add_vline(x=parity_distance, line_dash="dash", line_color="#e74c3c", annotation_text=f"Break-even: {parity_distance:,.0f} km", annotation_position="bottom right")
    
    st.plotly_chart(fig, use_container_width=True)