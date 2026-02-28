import streamlit as st
import pandas as pd
import plotly.express as px
# 1. Set up the page configuration
st.set_page_config(page_title="Grid Explorer Prototype", layout="wide")
st.title("⚡ Regional Grid Intensity Explorer")

# 2. Define a function to load the data with caching
@st.cache_data
def load_data():
    df = pd.read_csv("ember_data.csv")
    
    # The Ember dataset is "long" format. 
    # We only want to keep rows where the Variable is 'CO2 intensity'
    co2_data = df[df['Variable'] == 'CO2 intensity'].copy()
    return co2_data

# 3. Load the data into a Pandas DataFrame
with st.spinner("Loading Ember dataset..."):
    grid_data = load_data()

# 4. Display the raw data and column names to see what we're working with
st.subheader("Filtered Data Preview (CO2 Intensity Only)")
st.write(f"Total rows: {grid_data.shape[0]}")
st.dataframe(grid_data[['Area', 'Year', 'Variable', 'Value', 'Unit']].head(10))

st.divider() # Adds a nice horizontal line for visual separation
st.header("Interactive Grid Data")

# --- Step 3: Interactive Filters ---

# 1. Create a slider in the sidebar for the Year
min_year = int(grid_data['Year'].min())
max_year = int(grid_data['Year'].max())

st.sidebar.header("Controls")
selected_year = st.sidebar.slider("Select a Year", min_year, max_year, max_year)

# 2. Filter the Pandas DataFrame based on the selected year
filtered_data = grid_data[grid_data['Year'] == selected_year]

# 3. Clean up the data for visualization
# We only want rows that have an actual Area and a Value
clean_data = filtered_data.dropna(subset=['Area', 'Value'])

# Rename the 'Value' column to something more descriptive for the user
display_data = clean_data.rename(columns={'Value': 'CO2 Intensity (gCO2/kWh)'})

st.write(f"Showing CO2 intensity data for the year: **{selected_year}**")
st.dataframe(display_data[['Area', 'Year', 'CO2 Intensity (gCO2/kWh)']].head(15))

st.divider()
st.header("🌍 Global Carbon Intensity Map")

# 1. Prepare data for the map
# We only want to map actual countries, not grouped regions like "World" or "EU"
# Countries usually have a 3-letter ISO code, while groups often leave this blank
map_data = display_data.dropna(subset=['ISO 3 code'])

# 2. Create the Plotly Choropleth map
fig = px.choropleth(
    map_data,
    locations="ISO 3 code",          # Matches the standard 3-letter country codes
    color="CO2 Intensity (gCO2/kWh)", # The column we are using for the color scale
    hover_name="Area",               # Shows the country name when you hover
    color_continuous_scale="YlOrRd", # Yellow to Orange to Red color scale
    title=f"Grid Carbon Intensity in {selected_year} (gCO2/kWh)",
    labels={'CO2 Intensity (gCO2/kWh)': 'gCO2/kWh'}
)

# 3. Tweak the layout to make it look nicer
fig.update_layout(
    margin={"r":0,"t":40,"l":0,"b":0},
    geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular')
)

# 4. Display the chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# 5. Add a Top 10 Bar Chart just for fun!
st.subheader(f"Top 10 Most Carbon-Intensive Grids ({selected_year})")
top_10 = map_data.nlargest(10, 'CO2 Intensity (gCO2/kWh)')
fig_bar = px.bar(
    top_10, 
    x='CO2 Intensity (gCO2/kWh)', 
    y='Area', 
    orientation='h',
    color='CO2 Intensity (gCO2/kWh)',
    color_continuous_scale="Reds"
)
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}) # Sorts the longest bar to the top
st.plotly_chart(fig_bar, use_container_width=True)