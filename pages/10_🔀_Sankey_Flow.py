import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="LCA Sankey Flow", layout="wide")
st.title("🔀 Life Cycle Assessment (LCA) Sankey Flow")
st.markdown("Trace the complete physical flow of carbon emissions from raw materials and energy generation to the final 15-year lifecycle footprint.")

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
st.sidebar.header("🚗 Vehicle & Usage")
annual_mileage = st.sidebar.number_input("Annual Mileage (km/year)", value=15000, step=1000)
lifespan = st.sidebar.slider("Vehicle Lifespan (Years)", min_value=5, max_value=25, value=15)

st.sidebar.divider()
st.sidebar.header("⚙️ Base Assumptions")
e_ice_manu = 7000
e_ev_glider = 5000
battery_mfg = 6000 # Assuming a 60kWh battery at 100kg/kWh
ev_efficiency = 0.16
e_ice_op = 0.22

# --- 3. The Math Engine ---
# Calculate Operational Totals over the Lifespan
e_ev_op_annual = (ci_g_kwh / 1000.0) * ev_efficiency * annual_mileage
ev_op_total = e_ev_op_annual * lifespan

ice_op_total = e_ice_op * annual_mileage * lifespan

e_ev_manu_total = e_ev_glider + battery_mfg

ev_grand_total = e_ev_manu_total + ev_op_total
ice_grand_total = e_ice_manu + ice_op_total

# --- 4. Sankey Diagram Configuration ---
# Define the Nodes (The blocks)
nodes = [
    "Raw Battery Minerals",       # 0
    "Standard Auto Materials",    # 1
    f"{selected_country} Grid",   # 2
    "Fossil Fuels (Oil)",         # 3
    "EV Manufacturing",           # 4
    "ICE Manufacturing",          # 5
    "EV Operational (15 yrs)",    # 6
    "ICE Operational (15 yrs)",   # 7
    "Total EV Footprint",         # 8
    "Total ICE Footprint"         # 9
]

# Define the Links (The flowing pipes: Source Node -> Target Node, Value)
source = [0, 1, 1, 2, 3, 4, 6, 5, 7]
target = [4, 4, 5, 6, 7, 8, 8, 9, 9]
values = [
    battery_mfg,       # 0->4: Battery Minerals to EV Mfg
    e_ev_glider,       # 1->4: Standard Materials to EV Mfg
    e_ice_manu,        # 1->5: Standard Materials to ICE Mfg
    ev_op_total,       # 2->6: Grid to EV Ops
    ice_op_total,      # 3->7: Oil to ICE Ops
    e_ev_manu_total,   # 4->8: EV Mfg to EV Total
    ev_op_total,       # 6->8: EV Ops to EV Total
    e_ice_manu,        # 5->9: ICE Mfg to ICE Total
    ice_op_total       # 7->9: ICE Ops to ICE Total
]

# Set beautiful colors for the nodes and flows
node_colors = [
    "#8e44ad", "#7f8c8d", "#2980b9", "#c0392b", 
    "#2ecc71", "#95a5a6", "#3498db", "#e74c3c", 
    "#27ae60", "#c0392b"
]

# Flow colors with transparency
link_colors = [
    "rgba(142, 68, 173, 0.4)",  # Battery
    "rgba(127, 140, 141, 0.4)", # EV Glider
    "rgba(127, 140, 141, 0.4)", # ICE Materials
    "rgba(41, 128, 185, 0.4)",  # Grid
    "rgba(192, 57, 43, 0.4)",   # Oil
    "rgba(46, 204, 113, 0.5)",  # EV Mfg -> Total
    "rgba(52, 152, 219, 0.5)",  # EV Ops -> Total
    "rgba(149, 165, 166, 0.5)", # ICE Mfg -> Total
    "rgba(231, 76, 60, 0.5)"    # ICE Ops -> Total
]

# --- 5. Draw the Chart ---
st.subheader(f"Lifecycle Carbon Flow: EV vs ICE in {selected_country}")

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=25,
        thickness=30,
        line=dict(color="black", width=0.5),
        label=nodes,
        color=node_colors,
        hovertemplate='%{label}<br>Volume: %{value:,.0f} kg CO2e<extra></extra>'
    ),
    link=dict(
        source=source,
        target=target,
        value=values,
        color=link_colors,
        hovertemplate='Source: %{source.label}<br>Target: %{target.label}<br>Flow: %{value:,.0f} kg CO2e<extra></extra>'
    )
)])



fig.update_layout(
    height=650,
    font=dict(size=14, color="white"),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)

# --- 6. Executive Summary ---
st.divider()
st.markdown("### 📊 Flow Analysis")
if ev_grand_total < ice_grand_total:
    st.success(f"In **{selected_country}**, the massive flow of fossil fuels required to power the ICE vehicle ({ice_op_total:,.0f} kg) heavily outweighs the initial EV battery penalty ({battery_mfg:,.0f} kg).")
else:
    st.error(f"In **{selected_country}**, the carbon intensity of the regional grid creates a massive flow of operational emissions ({ev_op_total:,.0f} kg), resulting in a larger total footprint than the ICE vehicle.")