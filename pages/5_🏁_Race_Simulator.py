import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Multi-Region Race", layout="wide")
st.title("🏁 The Multi-Region Race Simulator")
st.markdown("Compare the carbon payback distance across multiple countries simultaneously.")

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
st.sidebar.header("🌍 Select Regions")
country_list = sorted(grid_data['Area'].dropna().unique().tolist())

default_countries = ["Norway", "United States", "India", "World"]
selected_countries = st.sidebar.multiselect(
    "Choose Grids to Compare:", 
    options=country_list, 
    default=[c for c in default_countries if c in country_list]
)

st.sidebar.divider()
st.sidebar.header("🚗 Vehicle Assumptions")
e_ev_manu = st.sidebar.number_input("EV Manufacturing (kg CO2e)", value=10000, step=500)
e_ice_manu = st.sidebar.number_input("ICE Manufacturing (kg CO2e)", value=6000, step=500)
ev_efficiency = st.sidebar.number_input("EV Consumption (kWh/km)", value=0.15, step=0.01)
e_ice_op = st.sidebar.number_input("ICE Emissions (kg CO2e/km)", value=0.20, step=0.01)

# --- 3. Math & Data Prep ---
if not selected_countries:
    st.warning("Please select at least one country from the sidebar to begin the race.")
else:
    distances = list(range(0, 300000, 2000)) # Finer steps for a smoother line
    
    # Calculate ICE line (Baseline)
    ice_emissions = [e_ice_manu + (e_ice_op * d) for d in distances]
    
    # We will use Plotly Graph Objects directly for ultimate styling control
    fig = go.Figure()

    # 1. Add the ICE Baseline (Bold, Dashed, Red)
    fig.add_trace(go.Scatter(
        x=distances, y=ice_emissions, 
        mode='lines', 
        name='ICE Baseline (Gasoline)',
        line=dict(color='#e74c3c', width=4, dash='dash'),
        hovertemplate='%{y:,.0f} kg CO2e<extra></extra>'
    ))
    
    # Calculate the manufacturing debt
    carbon_debt = e_ev_manu - e_ice_manu
    
    # Beautiful color palette for the EV lines
    colors = px.colors.qualitative.Bold
    
    leaderboard = []
    
    # 2. Add EV data for each selected country
    for idx, country in enumerate(selected_countries):
        ci_g_kwh = grid_data[grid_data['Area'] == country]['Value'].values[0]
        e_ev_op = (ci_g_kwh / 1000.0) * ev_efficiency
        
        ev_emissions = [e_ev_manu + (e_ev_op * d) for d in distances]
        line_color = colors[idx % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=distances, y=ev_emissions, 
            mode='lines', 
            name=f'EV in {country}',
            line=dict(color=line_color, width=3),
            hovertemplate='%{y:,.0f} kg CO2e<extra></extra>'
        ))
        
        # Calculate Break-Even Point for the Marker
        op_savings = e_ice_op - e_ev_op
        if op_savings > 0:
            parity_km = carbon_debt / op_savings
            
            # Only draw the dot if it happens within our 300k chart limit!
            if parity_km <= max(distances):
                parity_emissions = e_ice_manu + (e_ice_op * parity_km)
                
                # Draw the Parity Dot
                fig.add_trace(go.Scatter(
                    x=[parity_km], y=[parity_emissions],
                    mode='markers',
                    showlegend=False,
                    marker=dict(color=line_color, size=12, line=dict(color='white', width=2)),
                    hoverinfo='skip' # Keeps the hover clean
                ))
            
            status = f"{parity_km:,.0f} km"
        else:
            parity_km = float('inf')
            status = "Never (Grid too dirty)"
            
        leaderboard.append({
            "Region": country, 
            "Grid Intensity (gCO2/kWh)": round(ci_g_kwh, 1), 
            "Break-Even Distance": status, 
            "Sort Value": parity_km
        })

    # --- 4. Chart Polish ---
    st.subheader("Carbon Debt Payback: Global Comparison")
    
    fig.update_layout(
        title="<b>Cumulative Emissions: The Race to Carbon Parity</b>",
        xaxis_title="Distance Driven (km)",
        yaxis_title="Total Cumulative Emissions (kg CO2e)",
        hovermode="x unified", # Sleek unified tooltip line
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None
        ),
        xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', zeroline=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- 5. Break-Even Leaderboard ---
    st.divider()
    st.subheader("🏆 Break-Even Leaderboard")
    
    # Sort leaderboard by break-even distance
    leaderboard_df = pd.DataFrame(leaderboard).sort_values(by="Sort Value")
    
    # Display styling
    st.dataframe(leaderboard_df.drop(columns=["Sort Value"]), hide_index=True, use_container_width=True)