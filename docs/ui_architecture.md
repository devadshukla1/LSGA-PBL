# UI Architecture & Component Hierarchy

## 1. Design System & Tokens
The application enforces a dark UI theme specified in `.streamlit/config.toml` and programmatic design tokens in `src/ui/theme.py`:
- `background`: `#0B1120`
- `sidebar`: `#111827`
- `card_bg`: `#1E293B`
- `card_border`: `#334155`
- `primary`: `#38BDF8`
- `secondary`: `#818CF8`
- `success`: `#22C55E`
- `warning`: `#F59E0B`
- `error`: `#EF4444`

## 2. Component Structure (`src/ui/`)
```
src/ui/
├── __init__.py           # Re-exports clean component and session state API
├── theme.py              # Design tokens and custom CSS injection
├── components.py         # Reusable cards, headers, empty states, and status badges
├── session_state.py      # Session state defaults, dataset fingerprinting & caching
└── sidebar.py            # Multipage persistent sidebar and dataset selector
```

## 3. Caching & Graph Immutability Strategy
1. **Dataset Loading (`@st.cache_data`):** Datasets are loaded and schema-validated once per path and cached in memory.
2. **Graph Construction (`@st.cache_resource`):** NetworkX `MultiGraph` instances are keyed by dataset fingerprint.
3. **State Invalidation (`src/ui/session_state.py`):** When the user toggles datasets, `invalidate_stale_results()` automatically purges route results, closure simulations, and pairwise comparisons to guarantee data integrity across pages.
4. **Isolated Simulation:** Station closure simulations execute strictly on `graph.copy()`, leaving the cached resource untouched.
