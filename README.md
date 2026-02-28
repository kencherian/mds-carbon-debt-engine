# ⚡ Carbon Debt Equilibrium (CDE) Engine

**Master of Data Science (MDS) Final Year Project** A dynamic, interactive Life Cycle Assessment (LCA) tool simulating the carbon payback timeline of Electric Vehicles (EVs) versus Internal Combustion Engine (ICE) vehicles.

---

## 📖 Executive Abstract
While Electric Vehicles produce zero tailpipe emissions, their manufacturing process—specifically the lithium-ion battery—creates a significant upfront "Carbon Debt." The environmental viability of an EV depends entirely on how quickly it can pay off this debt through operational savings.

This application proves mathematically that the EV break-even point is highly sensitive to **Geographic Location** (Grid Carbon Intensity), **Driving Behavior** (Annual Mileage), and **Vehicle Architecture** (Battery Size). Utilizing historical and current electricity data from Ember Climate, the CDE Engine allows researchers and policymakers to run thousands of two-way sensitivity analyses in real-time.

---

## 🗂️ Core Modules

The application features 12 interactive modules divided into three analytical phases:

### Phase 1: Core Data Ingestion & Baselines
* **Global Grid Explorer:** Inspect raw carbon intensity of world energy grids.
* **Vehicle Presets:** Establish standard LCA metrics for manufacturing and operations.
* **Grid Mix Deconstructor:** Breakdown of specific power sources (Coal, Solar, Nuclear).

### Phase 2: Dynamic Scenario Engines
* **The Scenario Engine:** The core time-series calculator for carbon parity.
* **Multi-Region Race Simulator:** Plot payback lines of multiple countries simultaneously.
* **Battery Sizing Impact:** Visualize how oversized EV batteries delay the break-even timeline.

### Phase 3: Advanced Academic Visualizations
* **Behavior Heatmap:** 3D contour mapping simulating grid/mileage combinations.
* **Lifecycle Area:** Stacked area charts highlighting total physical volume of carbon emitted.
* **Global Heatmap:** Interactive choropleth world map of grid intensities.
* **LCA Sankey Flow:** Trace the exact physical flow of carbon from raw materials to total footprint.
* **Animated Timeline:** Rosling-style animation of the global energy transition (2000-Present).
* **Spider Comparison:** Multi-metric radar chart for executive summary comparisons.

---

## 🛠️ Architecture & Team Workflow

This project was developed and orchestrated using a modern AI-assisted workflow:
* **Project Management & Planning:** Claude (Architecture & Code Generation)
* **Development & Debugging:** Cursor IDE
* **Desktop Integration:** MCP Tools
* **Production Deployment:** LAMP Stack (Linux, Apache configured as a Reverse Proxy, MySQL, PHP)
* **Application Framework:** Python, Streamlit, Pandas, Plotly

---

## 🚀 Local Installation & Setup

To run the CDE Engine on a local Windows or Linux environment:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/mds-carbon-debt-engine.git](https://github.com/yourusername/mds-carbon-debt-engine.git)
   cd mds-carbon-debt-engine
