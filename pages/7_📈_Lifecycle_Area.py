import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Lifecycle Area", layout="wide")
st.title("📈 Total Lifecycle Area Under the Curve")
st.markdown("Visualizing the total physical volume of carbon emitted over a 15-year vehicle lifespan. The area of the colored regions represents the total kg of CO2e released into the atmosphere.")

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
ci_0_g_kwh = grid_data[grid_data['Area'] == selected_country]['Value'].values[0]

r_pct = st.sidebar.slider("Grid Decarbonization Rate (%/year)", min_value=0.0, max_value=10.0, value=2.0, step=0.5)
r = r_pct / 100.0

st.sidebar.divider()
st.sidebar.header("🚗 Vehicle & Usage")
annual_mileage = st.sidebar.number_input("Annual Mileage (km/year)", value=15000, step=1000)
lifespan = st.sidebar.slider("Vehicle Lifespan (Years)", min_value=5, max_value=20, value=15)

# Vehicle presets from earlier prototypes
e_ev_manu = 11000  # Mid-size EV
e_ice_manu = 7000  # Mid-size ICE
ev_efficiency = 0.16
e_ice_op = 0.22

# --- 3. Math Engine (Year-by-Year Cumulative Arrays) ---
years = np.arange(0, lifespan + 1)

# ICE Math (Constant operational emissions)
ice_manu_array = np.full(lifespan + 1, e_ice_manu)
ice_op_annual = np.full(lifespan + 1, e_ice_op * annual_mileage)
ice_op_annual[0] = 0 # No driving in Year 0
ice_op_cum = np.cumsum(ice_op_annual)
ice_total_volume = ice_manu_array[-1] + ice_op_cum[-1]

# EV Math (Decarbonizing operational emissions)
ev_manu_array = np.full(lifespan + 1, e_ev_manu)
grid_intensity_t = ci_0_g_kwh * (1 - r)**years
ev_op_annual = (grid_intensity_t / 1000.0) * ev_efficiency * annual_mileage
ev_op_annual[0] = 0 # No driving in Year 0
ev_op_cum = np.cumsum(ev_op_annual)
ev_total_volume = ev_manu_array[-1] + ev_op_cum[-1]

# --- 4. Visualization (Side-by-Side Area Charts) ---
st.subheader(f"Total Lifecycle Volume in {selected_country}")
st.markdown(f"Comparing a **Mid-Size EV** to a **Mid-Size ICE** driven **{annual_mileage:,} km/year** over **{lifespan} years**.")

col1, col2 = st.columns(2)

# Chart 1: ICE Vehicle
with col1:
    fig_ice = go.Figure()
    # Bottom Layer: Manufacturing
    fig_ice.add_trace(go.Scatter(
        x=years, y=ice_manu_array, mode='none',
        fill='tozeroy', fillcolor='rgba(149, 165, 166, 0.5)', # Gray
        name='ICE Manufacturing', stackgroup='one'
    ))
    # Top Layer: Cumulative Operational
    fig_ice.add_trace(go.Scatter(
        x=years, y=ice_op_cum, mode='none',
        fill='tonexty', fillcolor='rgba(231, 76, 60, 0.7)', # Red
        name='ICE Operational (Fuel)', stackgroup='one'
    ))
    fig_ice.update_layout(
        title=f"ICE Vehicle: {ice_total_volume:,.0f} kg CO2e Total",
        xaxis_title="Years Driven", yaxis_title="Cumulative Emissions (kg CO2e)",
        yaxis=dict(range=[0, max(ice_total_volume, ev_total_volume) * 1.1]), # Lock axes to be equal
        plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified"
    )
    st.plotly_chart(fig_ice, use_container_width=True)

# Chart 2: Electric Vehicle
with col2:
    fig_ev = go.Figure()
    # Bottom Layer: Manufacturing (Notice it's a thicker band than ICE)
    fig_ev.add_trace(go.Scatter(
        x=years, y=ev_manu_array, mode='none',
        fill='tozeroy', fillcolor='rgba(46, 204, 113, 0.5)', # Green
        name='EV Manufacturing (Battery)', stackgroup='one'
    ))
    # Top Layer: Cumulative Operational (Notice the wedge grows slower)
    fig_ev.add_trace(go.Scatter(
        x=years, y=ev_op_cum, mode='none',
        fill='tonexty', fillcolor='rgba(52, 152, 219, 0.7)', # Blue
        name='EV Operational (Grid)', stackgroup='one'
    ))
    fig_ev.update_layout(
        title=f"Electric Vehicle: {ev_total_volume:,.0f} kg CO2e Total",
        xaxis_title="Years Driven", yaxis_title="Cumulative Emissions (kg CO2e)",
        yaxis=dict(range=[0, max(ice_total_volume, ev_total_volume) * 1.1]), # Lock axes to be equal
        plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified"
    )
    
    st.plotly_chart(fig_ev, use_container_width=True)

# --- 5. Final Insights ---
st.divider()
savings = ice_total_volume - ev_total_volume
if savings > 0:
    st.success(f"**Conclusion:** Over a {lifespan}-year lifespan, the EV prevents **{savings:,.0f} kg of CO2e** from entering the atmosphere in {selected_country}.")
else:
    st.error(f"**Conclusion:** Over a {lifespan}-year lifespan, the EV actually generates **{abs(savings):,.0f} kg MORE CO2e** than the ICE vehicle due to the carbon-intensive grid in {selected_country}.")