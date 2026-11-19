"""User-friendly error and warning handling for Streamlit dashboard interfaces."""

import logging

import streamlit as st

_LOGGER = logging.getLogger("smartroute.ui")


def handle_ui_exception(
    error: Exception,
    context: str = "Operation failed",
    show_details: bool = True,
) -> None:
    """Safely log error and display clean user-friendly alert in Streamlit."""
    _LOGGER.error("UI error in %s: %s", context, error, exc_info=True)
    msg = f"{context}: {error}" if context else str(error)
    st.error(msg)
    if show_details and hasattr(error, "__cause__") and error.__cause__:
        st.caption(f"Underlying cause: {error.__cause__}")


def display_error(
    message: str,
    suggestion: str | None = None,
) -> None:
    """Display a formatted error card with an optional suggested remedy."""
    st.error(message)
    if suggestion:
        st.info(f"Suggestion: {suggestion}")
