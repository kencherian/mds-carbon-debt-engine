import streamlit as st

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="MDS Project: Carbon Debt Equilibrium",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Hero Section ---
st.title("⚡ Carbon Debt Equilibrium (CDE) Engine")
st.subheader("A Dynamic Lifecycle Assessment Tool for Electric Vehicles")
st.markdown("""
**Master of Data Science (MDS) Final Year Project** This application mathematically models and visualizes the exact carbon payback timeline of Electric Vehicles (EVs) versus Internal Combustion Engine (ICE) vehicles. By integrating real-world geographic grid data and predictive decarbonization rates, this tool solves the "static variable" problem found in traditional Life Cycle Assessments.
""")

st.divider()

# --- 3. Executive Abstract ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📖 Project Abstract")
    st.markdown("""
    While Electric Vehicles produce zero tailpipe emissions, their manufacturing process—specifically the lithium-ion battery—creates a massive upfront "Carbon Debt." The environmental viability of an EV depends entirely on how quickly it can pay off this debt through operational savings.
    
    This project proves that the break-even point is highly sensitive to **Geographic Location** (Grid Carbon Intensity), **Driving Behavior** (Annual Mileage), and **Vehicle Architecture** (Battery Size). 
    
    Using the open-source Ember electricity dataset, this interactive engine allows researchers, policymakers, and consumers to run thousands of two-way sensitivity analyses in real-time.
    """)

with col2:
    st.info("""
    **Key Methodologies Used:**
    * Time-Series Decarbonization Math
    * Multi-variable Sensitivity Matrices
    * Geographic Data Normalization
    * Interactive Data Storytelling
    """)

st.divider()

# --- 4. Module Directory ---
st.markdown("### 🗂️ Application Directory")
st.markdown("👈 **Please use the sidebar to navigate through the 12 interactive modules.** They are organized into three core phases:")

# Use expanders to keep the homepage clean but informative
with st.expander("📊 Phase 1: Core Data Ingestion & Baselines", expanded=True):
    st.markdown("""
    * **Global Grid Explorer:** Inspects the raw carbon intensity of world energy grids.
    * **Vehicle Presets:** Establishes the standard LCA metrics for manufacturing and operations.
    * **Grid Mix Deconstructor:** Breaks down the specific power sources (Coal, Solar, Nuclear) for any country.
    """)

with st.expander("⚙️ Phase 2: Dynamic Scenario Engines", expanded=True):
    st.markdown("""
    * **The Scenario Engine:** The core calculator for carbon parity.
    * **Multi-Region Race Simulator:** Plots the payback lines of multiple countries simultaneously.
    * **Battery Sizing Impact:** Proves how oversized EV batteries delay the break-even timeline.
    """)

with st.expander("📈 Phase 3: Advanced Academic Visualizations", expanded=True):
    st.markdown("""
    * **Behavior Heatmap:** A 3D contour map simulating thousands of grid/mileage combinations.
    * **Lifecycle Area:** Stacked area charts showing the total physical volume of carbon emitted.
    * **Global Heatmap:** An interactive choropleth world map of grid intensities.
    * **LCA Sankey Flow:** Traces the exact physical flow of carbon from raw materials to total footprint.
    * **Animated Timeline:** A Rosling-style animation of the global energy transition since 2000.
    * **Spider Comparison:** A multi-metric radar chart for executive summary comparisons.
    """)

st.divider()

# --- 5. Footer ---
st.caption("Built with Python, Streamlit, Pandas, and Plotly. Data sourced from Ember Climate.")