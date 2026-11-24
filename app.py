"""MetroGraph Analytics - Main Application Entrypoint.

Configures application routing and navigation using Streamlit's modern st.navigation API,
ensuring only the 5 core pages are registered, setting 'Metro Overview' as the default landing page,
and preventing duplicate 'app' entries in the navigation list.
"""

import streamlit as st

from src.core.logging_config import configure_logging, get_logger
from src.core.settings import APP_ICON, APP_NAME
from src.ui.session_state import init_session_state
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_theme_css

# 1. Setup Logging
configure_logging()
logger = get_logger("metrograph.app")
logger.info("Initializing MetroGraph Analytics Application.")

# 2. Configure Streamlit Navigation (Only 5 core pages, Metro Overview as default landing)
pages = [
    st.Page(
        "pages/1_Metro_Overview.py",
        title="Metro Overview",
        icon="🗺️",
        default=True,
    ),
    st.Page(
        "pages/2_Route_Planner.py",
        title="Route Planner",
        icon="🧭",
    ),
    st.Page(
        "pages/3_Station_Importance.py",
        title="Station Importance",
        icon="⭐",
    ),
    st.Page(
        "pages/4_Closure_Simulator.py",
        title="Closure Simulator",
        icon="🚧",
    ),
    st.Page(
        "pages/5_Algorithm_Lab.py",
        title="Algorithm Lab",
        icon="⚡",
    ),
]

# 3. Setup Navigation Controller
nav = st.navigation(pages, position="sidebar")

# 4. Global App Configuration & Theming
st.set_page_config(
    page_title=f"{APP_NAME} - Delhi Metro Network",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(apply_theme_css(), unsafe_allow_html=True)

# 5. Initialize Session State & Render Sidebar Status
init_session_state()
render_sidebar()

# 6. Run Active Page Content
nav.run()
