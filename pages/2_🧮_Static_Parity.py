import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Carbon Parity Calculator", layout="centered")
st.title("🧮 Static Carbon Parity Calculator")
st.markdown("This prototype calculates the break-even distance where an EV pays off its manufacturing carbon debt compared to an ICE vehicle.")

# --- NEW: Real-World Vehicle Database ---
st.header("1. Choose Vehicle Profiles")

vehicle_db = {
    "Compact Car (e.g., Nissan Leaf vs Toyota Corolla)": {
        "ev_manu": 8500, "ice_manu": 5500, "ev_op": 0.14, "ice_op": 0.18
    },
    "Mid-Size Sedan (e.g., Tesla Model 3 vs BMW 3 Series)": {
        "ev_manu": 11000, "ice_manu": 7000, "ev_op": 0.16, "ice_op": 0.22
    },
    "Large SUV/Truck (e.g., Ford F-150 Lightning vs F-150 Gas)": {
        "ev_manu": 16000, "ice_manu": 9000, "ev_op": 0.24, "ice_op": 0.35
    },
    "Custom / Manual Entry": {
        "ev_manu": 10000, "ice_manu": 6000, "ev_op": 0.05, "ice_op": 0.20
    }
}

# Dropdown for the user to select a preset
selected_class = st.selectbox("Select a Vehicle Class to Compare:", list(vehicle_db.keys()))

# Fetch the default values for the selected class
defaults = vehicle_db[selected_class]

st.markdown("### Fine-Tune Parameters")
st.markdown("*(These values are auto-filled based on your selection above, but you can adjust them!)*")

# Create two columns for a clean layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Manufacturing Emissions (kg CO2e)")
    e_ev_manu = st.number_input("EV Manufacturing Emissions", value=defaults["ev_manu"], step=500)
    e_ice_manu = st.number_input("ICE Manufacturing Emissions", value=defaults["ice_manu"], step=500)

with col2:
    st.subheader("Operational Emissions (kg CO2e / km)")
    # EV operational emissions
    e_ev_op = st.number_input("EV Operational Emissions per km", value=defaults["ev_op"], step=0.01, format="%.3f")
    # ICE operational emissions
    e_ice_op = st.number_input("ICE Operational Emissions per km", value=defaults["ice_op"], step=0.01, format="%.3f")

st.divider()

st.header("2. Carbon Parity Results")

# Calculate the manufacturing debt
carbon_debt = e_ev_manu - e_ice_manu

# Calculate the operational savings per km
op_savings_per_km = e_ice_op - e_ev_op

# --- Handle Edge Cases & Calculate ---
if carbon_debt <= 0:
    st.success("🎉 No Carbon Debt! The EV is greener from kilometer 0.")
    st.metric(label="Break-Even Distance", value="0 km")

elif op_savings_per_km <= 0:
    st.error("⚠️ The EV operational emissions are higher than or equal to the ICE. The carbon debt will NEVER be paid off on this grid!")
    st.metric(label="Break-Even Distance", value="Infinite")

else:
    # The actual Carbon Parity Distance formula
    parity_distance = carbon_debt / op_savings_per_km
    
    st.info(f"The EV starts with a manufacturing carbon debt of **{carbon_debt:,.0f} kg CO2e**.")
    st.info(f"The EV saves **{op_savings_per_km:.3f} kg CO2e** every kilometer driven.")
    
    # Display the final result
    st.metric(
        label="🚗 Break-Even Distance (Carbon Parity)", 
        value=f"{parity_distance:,.0f} km"
    )

st.divider()
st.header("3. Cumulative Emissions Visualizer")

# Only draw the chart if it's a valid scenario (EV operational is lower than ICE)
if op_savings_per_km > 0:
    
    # 1. Create an array of distances from 0 to 300,000 km (in steps of 1000)
    distances = list(range(0, 300000, 1000))
    
    # 2. Calculate cumulative emissions for each distance
    ev_total_emissions = [e_ev_manu + (e_ev_op * d) for d in distances]
    ice_total_emissions = [e_ice_manu + (e_ice_op * d) for d in distances]
    
    # 3. Create a Pandas DataFrame for Plotly
    chart_data = pd.DataFrame({
        'Distance (km)': distances,
        'EV Emissions': ev_total_emissions,
        'ICE Emissions': ice_total_emissions
    })
    
    # 4. Melt the DataFrame to make it easier for Plotly to draw multiple lines
    chart_data_melted = chart_data.melt(
        id_vars=['Distance (km)'], 
        value_vars=['EV Emissions', 'ICE Emissions'],
        var_name='Vehicle Type', 
        value_name='Total Emissions (kg CO2e)'
    )
    
    # 5. Create the Plotly Line Chart
    fig = px.line(
        chart_data_melted, 
        x='Distance (km)', 
        y='Total Emissions (kg CO2e)', 
        color='Vehicle Type',
        title="EV vs ICE: Cumulative Carbon Emissions Over Time",
        color_discrete_map={'EV Emissions': 'green', 'ICE Emissions': 'gray'}
    )
    
    # 6. Add a vertical line to explicitly highlight the Parity Distance
    fig.add_vline(
        x=parity_distance, 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"Parity @ {parity_distance:,.0f} km", 
        annotation_position="top left"
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Cannot generate a comparison chart because the EV does not reach carbon parity in this scenario.")