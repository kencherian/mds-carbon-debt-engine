import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Behavior Heatmap", layout="wide")
st.title("🗺️ Driving Behavior & Grid Heatmap")
st.markdown("This contour map visualizes a two-way sensitivity analysis, calculating the carbon break-even year across thousands of combinations of Grid Intensities and Annual Mileages simultaneously.")

# --- 1. Sidebar UI (Vehicle Base Stats) ---
st.sidebar.header("🚗 Vehicle Assumptions")
e_ev_manu = st.sidebar.number_input("EV Manufacturing (kg CO2e)", value=10000, step=500)
e_ice_manu = st.sidebar.number_input("ICE Manufacturing (kg CO2e)", value=6000, step=500)
ev_efficiency = st.sidebar.number_input("EV Consumption (kWh/km)", value=0.15, step=0.01)
e_ice_op = st.sidebar.number_input("ICE Emissions (kg CO2e/km)", value=0.20, step=0.01)

st.sidebar.divider()
st.sidebar.markdown("**How to read this chart:**")
st.sidebar.markdown("- **X-Axis:** How dirty the grid is.")
st.sidebar.markdown("- **Y-Axis:** How much you drive.")
st.sidebar.markdown("- **Color:** How many years until the EV pays off its carbon debt. Darker is better!")

# --- 2. Matrix Generation (The Math Engine) ---
carbon_debt = e_ev_manu - e_ice_manu

# Define the ranges for our X and Y axes
grid_intensities = np.linspace(0, 1000, 100) # From 0 to 1000 gCO2/kWh
annual_mileages = np.linspace(5000, 40000, 100) # From 5k to 40k km per year

# Create a 2D grid (matrix) of these values
X_grid, Y_mileage = np.meshgrid(grid_intensities, annual_mileages)

# Calculate EV operational emissions per km for every point on the grid
EV_op_emissions = (X_grid / 1000.0) * ev_efficiency

# Calculate operational savings per km
op_savings = e_ice_op - EV_op_emissions

# --- Handle negative savings (where grid is too dirty) ---
# We use np.where to prevent dividing by zero or negative numbers.
# If savings <= 0, we set the parity year to a high cap (e.g., 30 years) to represent "Never"
parity_km = np.where(op_savings > 0, carbon_debt / op_savings, float('inf'))

# Calculate Parity Year (Z-axis)
Z_years = parity_km / Y_mileage

# Cap the maximum years displayed on the chart to 25 (typical max vehicle lifespan)
Z_years = np.clip(Z_years, 0, 25)

# --- 3. Visualization ---
st.subheader("Carbon Parity Contour Map")

# Create a Plotly Contour Map
fig = go.Figure(data=go.Contour(
    z=Z_years,
    x=grid_intensities,
    y=annual_mileages,
    colorscale="RdYlGn_r", # Red (Bad/Long) to Yellow to Green (Good/Fast). Reversed with _r
    contours=dict(
        start=0,
        end=25,
        size=2, # Draw a contour line every 2 years
        showlabels=True, # Show the year numbers on the lines
        labelfont=dict(size=12, color='white')
    ),
    colorbar=dict(
        title="Years to Parity",
        tickvals=[0, 5, 10, 15, 20, 25],
        ticktext=['0', '5', '10', '15', '20', '25+ (Never)']
    ),
    hovertemplate="<b>Grid:</b> %{x:,.0f} gCO2/kWh<br><b>Mileage:</b> %{y:,.0f} km/yr<br><b>Parity:</b> %{z:.1f} Years<extra></extra>"
))



fig.update_layout(
    xaxis_title="Grid Carbon Intensity (gCO2/kWh)",
    yaxis_title="Annual Driving Mileage (km/year)",
    height=600,
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', zeroline=False)
)

st.plotly_chart(fig, use_container_width=True)

# --- 4. Contextualizing the Data ---
st.info("💡 **Insights:** Notice the extreme top-left (Clean Grid + High Mileage). Parity is reached in under 2 years! However, look at the bottom-right (Dirty Grid + Low Mileage). A car driven very little on a coal-heavy grid may take over 20 years to offset its manufacturing emissions, completely negating its environmental benefit.")