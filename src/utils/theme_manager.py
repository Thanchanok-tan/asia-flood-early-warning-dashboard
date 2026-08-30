import os
import streamlit as st

def init_state_and_theme():
    """Synchronize theme and localization language with URL query params and session state."""
    # Query parameters read
    query_params = st.query_params

    # Default settings
    if "lang" not in st.session_state:
        st.session_state["lang"] = query_params.get("lang", "en")
    
    if "theme" not in st.session_state:
        st.session_state["theme"] = query_params.get("theme", "light")

def update_query_params(theme_choice: str, lang_choice: str):
    """Synchronize URL query params with updated user settings."""
    st.session_state["theme"] = theme_choice
    st.session_state["lang"] = lang_choice
    st.query_params["theme"] = theme_choice
    st.query_params["lang"] = lang_choice

def inject_custom_css():
    """Inject custom responsive CSS and theme variables."""
    current_theme = st.session_state.get("theme", "light")

    if current_theme == "dark":
        theme_vars = """
        :root {
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --card-border: #1f2937;
            --text-primary: #f9fafb;
            --text-secondary: #9ca3af;
            --accent-blue: #3b82f6;
            --shadow-color: rgba(0, 0, 0, 0.4);
            --header-gradient: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        }
        .stApp {
            background-color: #0b0f19 !important;
            color: #f9fafb !important;
        }
        """
    else: # light mode default
        theme_vars = """
        :root {
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --card-border: #e2e8f0;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --accent-blue: #2563eb;
            --shadow-color: rgba(0, 0, 0, 0.05);
            --header-gradient: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        }
        .stApp {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        """

    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static", "css", "custom.css")
    custom_css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            custom_css_content = f.read()

    full_css = f"""
    <style>
    {theme_vars}
    {custom_css_content}
    </style>
    """
    st.markdown(full_css, unsafe_allow_html=True)
