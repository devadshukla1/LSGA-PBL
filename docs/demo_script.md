# Live Project Demonstration Script

**Estimated Duration:** 5–7 Minutes  
**Audience:** Project Evaluators, Faculty Examiners, and Peers  

---

### Phase 1: Application Launch & Architectural Scope (1 Minute)
1. **Start Application:**
   ```powershell
   streamlit run app.py
   ```
2. **Landing Page Overview (`app.py`):**
   - Point out the active dataset: **Delhi Metro Network (260 stations, 13 lines, 25 interchanges)**.
   - Show the summary topology cards (Vertices $|V|=260$, Connections $|E|=289$).
   - Highlight the offline schematic network diagram rendered via Plotly. Mention the zero-OSM / zero-external-tile guarantee.

---

### Phase 2: Metro Overview & Line Filtering (1 Minute)
1. **Navigate to `1_Metro_Overview.py` via the sidebar:**
   - Demonstrate the "Filter by Metro Line" dropdown. Select `Yellow Line`.
   - Point out how the Plotly view isolates the Yellow Line stations from Samaypur Badli to Millennium City Centre Gurugram.
   - Check "Show Interchange Hubs Only" to highlight major connection hubs like Rajiv Chowk, Kashmere Gate, and Central Secretariat.
   - Show the data registries tab (Stations, Lines, Connections, Interchanges).

---

### Phase 3: Smart Route Planning & Transfer Optimization (1.5 Minutes)
1. **Navigate to `2_Route_Planner.py`:**
   - **Scenario 1:** Select Origin: `Dwarka Sector 21` (`STN053`) and Destination: `Noida City Centre` (`STN176`).
   - Run **Minimum Stops (BFS)**: Show stops, travel time, and path trace.
   - Run **Minimum Transfers (0-1 BFS)**: Show how 0-1 BFS eliminates unnecessary line changes.
   - Click **Compare All Algorithms**: Review the multi-objective comparison table contrasting BFS, Dijkstra (time), Dijkstra (dist), 0-1 BFS, Lexicographic, and Transfer-Aware Dijkstra.
   - Open the **Step-by-Step Passenger Directions** expander to show turn-by-turn walking instructions.

---

### Phase 4: Station Importance & Bottleneck Detection (1 Minute)
1. **Navigate to `3_Station_Importance.py`:**
   - Show the **Centrality Rankings** table sorted by Betweenness Centrality.
   - Explain why high-betweenness stations (e.g. `Hauz Khas`, `Rajiv Chowk`) serve as critical bridge nodes.
   - Switch to the **Articulation Points** tab: Explain that cut-vertices are stations whose single removal disconnects sections of the network.
   - Switch to **Station Comparison**: Select `Rajiv Chowk` and `Kashmere Gate` side-by-side.

---

### Phase 5: Closure Simulation & Detour Rerouting (1.5 Minutes)
1. **Navigate to `4_Closure_Simulator.py`:**
   - Under "Select Stations to Close", pick `Rajiv Chowk` (`STN199`).
   - Click **Run Simulation**.
   - Review the Before-and-After Metrics table: Active stations decrease from 260 to 259, incident tracks decrease from 289 to 281, and reachable station pairs decrease.
   - In Section 3, test a journey traversing Rajiv Chowk (e.g. `Dwarka Sector 21` to `Noida City Centre`).
   - Click **Check Route Availability & Detour**: Show the rerouting outcome status (`REROUTED`), stops delta, and travel time penalty.
   - Inspect Section 4: Point out the red `✕` cross over Rajiv Chowk and the red dotted severed track links on the disruption map.

---

### Phase 6: Algorithm Lab & Results Export (1 Minute)
1. **Navigate to `5_Algorithm_Lab.py`:**
   - Review the theoretical complexity table.
   - Click "Profile Centrality Algorithms" and "Profile Single-Station Closure" to show live microsecond timing measurements.
2. **Navigate to `6_Results.py`:**
   - Demonstrate the export center: Download Route Segments CSV, Route Itinerary JSON, and Closure Impact CSV.
   - Conclude by summarizing the reproducibility and architectural rigor of the system.
