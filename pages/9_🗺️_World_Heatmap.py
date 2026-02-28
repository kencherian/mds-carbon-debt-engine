import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Grid Heatmap", layout="wide")
st.title("🗺️ Global Carbon Intensity Heatmap")
st.markdown("Explore the geographic distribution of grid carbon intensity. Use the slider to see how global grids have evolved over time.")

# --- 1. Load Data ---
@st.cache_data
def load_historical_ember_data():
    try:
        df = pd.read_csv("../ember_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("ember_data.csv")
        
    # Get all CO2 intensity data (not just the latest year!)
    co2_data = df[df['Variable'] == 'CO2 intensity'].copy()
    
    # Filter out aggregated regions (like "World", "Asia", "EU") so they don't mess up the country map
    regions_to_exclude = ['World', 'Asia', 'Europe', 'European Union (27)', 'North America', 'Latin America and Caribbean', 'Africa', 'Oceania', 'G20', 'G7', 'ASEAN']
    country_only_data = co2_data[~co2_data['Area'].isin(regions_to_exclude)]
    
    return country_only_data

with st.spinner("Loading global historical data..."):
    map_data = load_historical_ember_data()

# --- 2. Interactive UI ---
# Find the min and max years in the dataset
min_year = int(map_data['Year'].min())
max_year = int(map_data['Year'].max())

col1, col2 = st.columns([3, 1])

with col1:
    # Year Slider
    selected_year = st.slider("Select Year to Visualize:", min_value=min_year, max_value=max_year, value=max_year, step=1)

with col2:
    # Map Projection Style
    projection_style = st.selectbox(
        "Map Style", 
        ["natural earth", "orthographic", "equirectangular", "mercator"]
    )

# Filter data for the selected year
year_data = map_data[map_data['Year'] == selected_year]

# --- 3. Generate the Choropleth Map ---
fig = px.choropleth(
    year_data,
    locations="Area",             # The column with country names
    locationmode="country names", # Tell Plotly these are names, not ISO codes
    color="Value",                # The column to base the color on (Carbon Intensity)
    hover_name="Area",            # What shows up in bold when you hover
    color_continuous_scale="RdYlGn_r", # Red (Dirty) to Yellow to Green (Clean). The '_r' reverses it!
    range_color=[0, 800],         # Lock the color scale so the colors don't jump around when you change years
    labels={'Value': 'Carbon Intensity (gCO2/kWh)'},
    title=f"Global Grid Carbon Intensity in {selected_year}"
)



fig.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type=projection_style,
        bgcolor='rgba(0,0,0,0)' # Transparent background
    ),
    margin={"r":0,"t":40,"l":0,"b":0},
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)

# --- 4. Data Insights Table ---
st.divider()
st.subheader(f"Top & Bottom Performers in {selected_year}")

# Sort the data to find the cleanest and dirtiest grids
sorted_data = year_data.sort_values(by='Value')
cleanest = sorted_data.head(5)[['Area', 'Value']].rename(columns={'Area': 'Country', 'Value': 'Intensity (gCO2/kWh)'})
dirtiest = sorted_data.tail(5)[['Area', 'Value']].rename(columns={'Area': 'Country', 'Value': 'Intensity (gCO2/kWh)'}).sort_values(by='Intensity (gCO2/kWh)', ascending=False)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**🌍 Top 5 Cleanest Grids**")
    st.dataframe(cleanest, hide_index=True, use_container_width=True)

with col_b:
    st.markdown("**🏭 Top 5 Most Carbon-Intensive Grids**")
    st.dataframe(dirtiest, hide_index=True, use_container_width=True)