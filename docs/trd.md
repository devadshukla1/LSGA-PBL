# MetroGraph Analytics: Technical Requirements Document (TRD)

## 1. System Architecture Overview
MetroGraph Analytics is structured as a layered, modular Python application using Streamlit for user interface presentation, NetworkX for graph topological computations, pandas for schema ingestion, and Plotly for hardware-accelerated offline data visualization.

```
+-------------------------------------------------------------+
|                Streamlit Presentation Layer                 |
|   app.py (Dashboard) | pages/ 1-6 (Modular Domain Pages)    |
|   src/ui/ (theme.py, components.py, sidebar.py)             |
+-------------------------------------------------------------+
                              |
+-------------------------------------------------------------+
|              Domain Logic & Engine Services                 |
|   src/data/         : loader.py, schemas.py                 |
|   src/graph/        : metro_builder.py, validator.py        |
|   src/algorithms/   : [Phase 3-4 Routing Engines]           |
|   src/analytics/    : [Phase 5 Centrality Engines]          |
|   src/simulation/   : [Phase 6 Disruption Engines]          |
|   src/visualization/: metro_plot.py (Offline Plotly)        |
+-------------------------------------------------------------+
                              |
+-------------------------------------------------------------+
|              Core Foundations & Infrastructure              |
|   config.py, src/core/settings.py                           |
|   src/core/logging_config.py, src/core/exceptions.py        |
+-------------------------------------------------------------+
                              |
+-------------------------------------------------------------+
|                    Persistence & Data                       |
|   data/sample/ (stations.csv, lines.csv, connections.csv)   |
|   data/processed/, results/benchmarks/, results/exports/    |
+-------------------------------------------------------------+
```

## 2. Graph Data Model Specification
- **Representation**: `networkx.MultiGraph` (Undirected Multigraph).
- **Rationale**:
  1. Undirected edges reflect bidirectional passenger transit operations in the simplified model.
  2. MultiGraph capability preserves parallel edges between the same station pair when served by distinct metro lines (e.g. Red Line and Yellow Line running parallel tracks between major junctions).
- **Node Invariants**:
  - `name`: string
  - `lat`, `lon`: float (synthetic schematic coordinates)
  - `lines`: set of line IDs
  - `is_interchange`: boolean (True if `len(lines) >= 2`)
- **Edge Invariants**:
  - `line_id`: string
  - `line_name`: string
  - `line_color`: string (hex format)
  - `distance_km`: float (> 0.0)
  - `estimated_time_min`: float (> 0.0)

## 3. Technology Stack & Constraints
- **Language**: Python 3.11.x (tested on CPython 3.11.16).
- **Core Dependencies**:
  - `streamlit>=1.30.0,<2.0.0`
  - `networkx>=3.2.1,<4.0.0`
  - `pandas>=2.1.0,<3.0.0`
  - `numpy>=1.26.0,<3.0.0`
  - `plotly>=5.18.0,<6.0.0`
  - `folium>=0.15.0,<1.0.0` (optional future)
  - `streamlit-folium>=0.16.0,<1.0.0`
- **Development & Verification**:
  - `pytest>=7.4.0,<9.0.0`
  - `ruff>=0.2.0,<1.0.0`

## 4. Verification & Testing Strategy
- **Configuration & Invariants**: Tests confirm deterministic resolution of absolute paths and default settings.
- **Data Integrity**: Tests assert referential integrity across CSV files, positive weights, and rejection of corrupt datasets.
- **Graph Topology**: Tests assert MultiGraph type, parallel edge preservation, node/edge counts, and connectivity.
- **Headless UI Testing**: Automated compilation and Streamlit `AppTest` simulation across all 7 pages.
- **Linting**: Ruff code quality and formatting checks.
