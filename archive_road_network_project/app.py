"""Streamlit entry point for the seven dashboard pages."""

import streamlit as st

from config import APP_NAME
from pages._shared import PAGES


def main() -> None:
    """Register dashboard pages using Streamlit's sidebar navigation."""
    st.set_page_config(page_title=APP_NAME, layout="wide")
    navigation = st.navigation(
        [st.Page(f"pages/{filename}", title=title) for filename, title, _ in PAGES]
    )
    navigation.run()


if __name__ == "__main__":
    main()
