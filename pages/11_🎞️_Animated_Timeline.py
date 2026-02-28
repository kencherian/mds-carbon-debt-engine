import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Animated Timeline", layout="wide")
st.title("🎞️ The Global Decarbonization Timeline")
st.markdown("Watch the evolution of the global power grid. Click **Play** to see how countries have expanded their energy generation while fighting to lower their carbon intensity.")

# --- 1. Load and Transform Data ---
@st.cache_data
def load_animated_data():
    try:
        df = pd.read_csv("../ember_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("ember_data.csv")
        
    # Filter out aggregated regions so we only plot actual countries
    regions_to_exclude = ['World', 'Asia', 'Europe', 'European Union (27)', 'North America', 'Latin America and Caribbean', 'Africa', 'Oceania', 'G20', 'G7', 'ASEAN']
    country_df = df[~df['Area'].isin(regions_to_exclude)]
    
    # 1. Extract Carbon Intensity (Y-Axis)
    intensity = country_df[country_df['Variable'] == 'CO2 intensity'][['Area', 'Year', 'Value']]
    intensity = intensity.rename(columns={'Value': 'Intensity (gCO2/kWh)'})
    
    # 2. Extract Total Generation (X-Axis and Bubble Size)
    generation = country_df[country_df['Variable'] == 'Total Generation'][['Area', 'Year', 'Value']]
    generation = generation.rename(columns={'Value': 'Total Generation (TWh)'})
    
    # Merge them together on Country and Year
    merged_data = pd.merge(intensity, generation, on=['Area', 'Year']).dropna()
    
    # Sort by year so the animation plays chronologically
    merged_data = merged_data.sort_values('Year')
    
    return merged_data

with st.spinner("Processing historical animation frames..."):
    animated_df = load_animated_data()

# --- 2. Build the Animated Bubble Chart ---
st.subheader("Grid Intensity vs. Total Power Generation")

# Create the Plotly Express Animated Scatter Plot
fig = px.scatter(
    animated_df,
    x="Total Generation (TWh)", 
    y="Intensity (gCO2/kWh)", 
    animation_frame="Year",      # This creates the play button and timeline slider!
    animation_group="Area",      # This tells Plotly to track the same country bubble across years
    size="Total Generation (TWh)", # Bigger bubbles = More electricity generated
    color="Area",                # Each country gets its own color
    hover_name="Area",
    log_x=True,                  # Log scale so massive countries (China/USA) don't squash small countries
    size_max=60,                 # Make the biggest bubbles nice and large
    range_x=[1, max(animated_df['Total Generation (TWh)']) * 1.5], 
    range_y=[0, max(animated_df['Intensity (gCO2/kWh)']) + 100],
    title="Global Energy Transition (2000 - Present)"
)

# Polish the layout
fig.update_layout(
    height=700,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', title_font=dict(size=14)),
    yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)', title_font=dict(size=14)),
    showlegend=False # Hide legend because there are too many countries; hover provides names
)

# Slow down the animation slightly so it's easier to present
fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800

st.plotly_chart(fig, use_container_width=True)

# --- 3. Presenter Notes ---
st.divider()
st.markdown("### 🎤 Presentation Guide")
st.info("""
**When presenting this to your MDS panel, tell them to watch these specific movements:**
1. **The Massive Bubbles (China & USA):** Notice how they sit far to the right (massive energy generation). Watch them slowly drift downwards as their carbon intensity improves over the decades.
2. **The "Green" European Drop:** Keep an eye on the bubbles starting in the middle-left. You will see countries like the UK plummet straight down the Y-axis as they aggressively phase out coal in the 2010s.
3. **The X-Axis Expansion:** Notice how almost all developing nations drift steadily to the right as they industrialize and demand more total electricity (TWh).
""")