# End-to-End User Dashboard Workflows

This document outlines the six core user workflows implemented and verified in Phase 7.

---

### Workflow A: Network Exploration & Line Filtering
1. **Entry:** Launch `app.py`. The dashboard displays summary metrics for the active dataset.
2. **Navigation:** Navigate to **1. Metro Overview** via the sidebar.
3. **Filtering:** In the "Filter by Metro Line" dropdown, select a specific line (e.g. `Yellow Line` or `Blue Line`).
4. **Inspection:** The Plotly visualization isolates stations on the chosen line. Check the "Show Interchange Hubs Only" box to isolate transfer points.
5. **Registry Review:** Switch across the "Stations Registry" and "Interchange Hubs" tabs to review raw metadata.

---

### Workflow B: Minimum-Stop and Fastest Route Planning
1. **Navigation:** Go to **2. Route Planner**.
2. **Input:** Select origin (e.g., `Rajiv Chowk`) and destination (e.g., `Hauz Khas`).
3. **Objective:** Choose `Minimum Stops (BFS)` or `Minimum Travel Time (Dijkstra)`.
4. **Execution:** Click **Find Optimal Route**.
5. **Results:** Review total stops, transit time, line segments table, and schematic route map with highlighted path.

---

### Workflow C: Line-Aware Transfer Optimization
1. **Navigation:** On **2. Route Planner**, choose origin and destination on separate lines (e.g., `Dwarka Sector 21` to `Noida Electronic City`).
2. **Objective:** Select `Minimum Transfers (0-1 BFS)` or `Fastest with Transfer Penalty (Dijkstra)`.
3. **Friction Adjustment:** Adjust the transfer wait penalty slider (e.g., 5.0 minutes).
4. **Evaluation:** Click **Compare All Algorithms**.
5. **Inspection:** Review the multi-objective comparison table contrasting stop count against transfer penalties and transit friction. Expand "Step-by-Step Passenger Directions" for walking instructions.

---

### Workflow D: Station Importance & Bottleneck Detection
1. **Navigation:** Open **3. Station Importance**.
2. **Centrality Rankings:** View top betweenness and degree centrality stations in the ranking table.
3. **Heatmap:** Switch to "Network Centrality Map" to visually inspect bridge nodes and cut-vertices.
4. **Cut-Vertex Inspection:** Open the "Articulation Points" tab to examine stations whose failure segments the network.
5. **Pairwise Comparison:** Use "Station Comparison" to compare two hubs side-by-side.

---

### Workflow E: Outage Simulation & Automated Detours
1. **Navigation:** Open **4. Closure Simulator**.
2. **Selection:** Select a critical hub (e.g. `Rajiv Chowk`) under "Select Stations to Close".
3. **Simulation:** Click **Run Simulation**.
4. **Metrics:** Observe the delta metrics (Active Stations $\Delta -1$, incident connections removed, reachable pair loss).
5. **Detour Rerouting:** In the rerouting panel, select an origin and destination that previously traversed the closed hub. Click **Check Route Availability & Detour**.
6. **Visualization:** Inspect the disruption map showing the red `X` over the closed station, dotted red severed links, and alternative detour route.

---

### Workflow F: Artifact & Data Exports
1. **Navigation:** Open **6. Results & Exports**.
2. **Base Data:** Download base CSV tables (Stations, Lines, Connections).
3. **Route Export:** Download the calculated route segment CSV and JSON itinerary.
4. **Simulation Export:** Download the closure impact metrics CSV and full simulation payload JSON.
5. **GraphML Cache:** Click "Generate & Cache GraphML File" to create serialized graph caches.
