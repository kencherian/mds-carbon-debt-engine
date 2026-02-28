import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Grid Mix Deconstructor", layout="wide")
st.title("🔋 The Grid Mix Deconstructor")
st.markdown("Understand *why* a region's carbon intensity is high or low by looking at its actual power generation mix.")

# --- 1. Load and Clean the Data ---
@st.cache_data
def load_generation_data():
    # Attempt to load from parent directory first
    try:
        df = pd.read_csv("../ember_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("ember_data.csv")
        
    # We only want the breakdown of Electricity generation in percentages
    gen_data = df[(df['Category'] == 'Electricity generation') & (df['Unit'] == '%')].copy()
    
    # Ember includes aggregated groups (like "Fossil" or "Clean"). 
    # We must filter these out so our pie chart doesn't double-count the data!
    aggregates = ['Clean', 'Fossil', 'Gas and Other Fossil', 'Hydro, Bioenergy and Other Renewables', 'Renewables', 'Wind and Solar', 'Total Generation']
    
    # Keep only the specific fuel sources
    specific_sources = gen_data[~gen_data['Variable'].isin(aggregates)]
    
    # Grab the most recent year available
    latest_year = specific_sources['Year'].max()
    return specific_sources[specific_sources['Year'] == latest_year], latest_year

with st.spinner("Loading generation mix data..."):
    grid_mix_data, data_year = load_generation_data()

# --- 2. Sidebar UI ---
st.sidebar.header("🌍 Select Region")
country_list = sorted(grid_mix_data['Area'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Choose a Country/Region:", country_list, index=country_list.index("World") if "World" in country_list else 0)

# Filter for the chosen country
country_data = grid_mix_data[grid_mix_data['Area'] == selected_country]

st.divider()
st.subheader(f"Electricity Generation Mix: {selected_country} ({data_year})")

# --- 3. Visualization ---
col1, col2 = st.columns([2, 1]) # Make the chart column wider than the data table column

with col1:
    # Create a Plotly Donut Chart
    fig = px.pie(
        country_data, 
        values='Value', 
        names='Variable', 
        hole=0.4, # This hole parameter turns a pie chart into a donut chart
        # Map specific colors to fuel types so Coal is always dark, Solar is yellow, etc.
        color='Variable',
        color_discrete_map={
            'Coal': '#111111',         # Black
            'Gas': '#A0522D',          # Brown
            'Other Fossil': '#696969', # Gray
            'Nuclear': '#8A2BE2',      # Purple
            'Hydro': '#4169E1',        # Blue
            'Wind': '#87CEEB',         # Light Blue
            'Solar': '#FFD700',        # Yellow
            'Bioenergy': '#228B22',    # Green
            'Other Renewables': '#32CD32' # Lime
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Raw Data")
    # Clean up the dataframe for display
    display_df = country_data[['Variable', 'Value']].rename(columns={'Variable': 'Source', 'Value': '% of Total'})
    display_df = display_df.sort_values(by='% of Total', ascending=False)
    
    # Display without the pandas index numbers
    st.dataframe(display_df, hide_index=True)