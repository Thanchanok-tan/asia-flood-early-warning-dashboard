import datetime
import pandas as pd
import streamlit as st

# Initialize page layout configuration
st.set_page_config(
    page_title="Asia 25-Year Flood Risk Atlas & Early Warning System",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.config import BASINS
from src.i18n import get_text
from src.data_loader import load_dataset, filter_dataset, compute_kpis
from src.utils.theme_manager import init_state_and_theme, update_query_params, inject_custom_css
from src.components.kpi_cards import render_kpi_cards
from src.components.map_view import render_map_view
from src.components.time_series_charts import (
    render_dual_axis_chart,
    render_basin_boxplot,
    render_correlation_heatmap,
    render_seasonal_lag_chart
)
from src.components.simulator import render_simulator
from src.components.alert_feed import render_alert_feed_and_export

def main():
    # Initialize URL query parameters and state
    init_state_and_theme()

    # Load 25-year dataset
    df = load_dataset()

    # Sidebar Controls
    with st.sidebar:
        st.markdown(f"### ⚙️ {get_text(st.session_state['lang'], 'sidebar_header')}")
        
        # Language Switcher
        lang_option = st.radio(
            get_text(st.session_state['lang'], "language_label"),
            options=["English", "ภาษาไทย"],
            index=0 if st.session_state["lang"] == "en" else 1,
            horizontal=True
        )
        new_lang = "en" if lang_option == "English" else "th"

        # Theme Switcher
        theme_option = st.radio(
            get_text(new_lang, "theme_label"),
            options=[get_text(new_lang, "theme_light"), get_text(new_lang, "theme_dark")],
            index=0 if st.session_state["theme"] == "light" else 1,
            horizontal=True
        )
        new_theme = "light" if get_text(new_lang, "theme_light") in theme_option else "dark"

        # Sync changes with query parameters if modified
        if new_lang != st.session_state["lang"] or new_theme != st.session_state["theme"]:
            update_query_params(new_theme, new_lang)
            st.rerun()

        st.markdown("---")
        st.markdown(f"#### 🔍 {get_text(new_lang, 'filters_header')}")

        if not df.empty:
            # Basin Filter
            basin_list = [get_text(new_lang, "all_option")] + sorted(df["basin"].unique().tolist())
            selected_basin = st.selectbox(get_text(new_lang, "basin_filter"), options=basin_list)

            # Country Filter
            filtered_by_basin = df if selected_basin == get_text(new_lang, "all_option") else df[df["basin"] == selected_basin]
            country_list = [get_text(new_lang, "all_option")] + sorted(filtered_by_basin["country"].unique().tolist())
            selected_country = st.selectbox(get_text(new_lang, "country_filter"), options=country_list)

            # Station Filter
            filtered_by_country = filtered_by_basin if selected_country == get_text(new_lang, "all_option") else filtered_by_basin[filtered_by_basin["country"] == selected_country]
            station_list = [get_text(new_lang, "all_stations_option")] + sorted(filtered_by_country["station_name"].unique().tolist())
            selected_station = st.selectbox(get_text(new_lang, "station_filter"), options=station_list)

            # Date Range Filter
            min_d = df["date"].min().date()
            max_d = df["date"].max().date()
            date_range = st.date_input(
                get_text(new_lang, "date_range_filter"),
                value=(min_d, max_d),
                min_value=min_d,
                max_value=max_d
            )

            start_d = date_range[0] if isinstance(date_range, (tuple, list)) and len(date_range) > 0 else min_d
            end_d = date_range[1] if isinstance(date_range, (tuple, list)) and len(date_range) > 1 else max_d
        else:
            selected_basin = get_text(new_lang, "all_option")
            selected_country = get_text(new_lang, "all_option")
            selected_station = get_text(new_lang, "all_stations_option")
            start_d, end_d = None, None

    # Inject Custom CSS according to selected theme
    inject_custom_css()

    current_lang = st.session_state["lang"]

    # Filter dataset according to sidebar selections
    filtered_df = filter_dataset(
        df,
        basin=selected_basin,
        country=selected_country,
        station=selected_station,
        start_date=start_d,
        end_date=end_d
    )

    # Compute executive KPI summary
    kpi_metrics = compute_kpis(filtered_df)

    # App Header Banner
    st.markdown(
        f"""
        <div class="header-card">
            <div class="header-title">🌊 {get_text(current_lang, 'app_title')}</div>
            <div class="header-subtitle">{get_text(current_lang, 'app_subtitle')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Executive KPI Cards
    render_kpi_cards(kpi_metrics, current_lang)
    st.markdown("<br>", unsafe_allow_html=True)

    # Main Tabbed Layout
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🗺️ {get_text(current_lang, 'tab_overview')}",
        f"📈 {get_text(current_lang, 'tab_analytics')}",
        f"⚡ {get_text(current_lang, 'tab_simulator')}",
        f"🔔 {get_text(current_lang, 'tab_alerts_data')}"
    ])

    with tab1:
        render_map_view(filtered_df, current_lang)

    with tab2:
        col_left, col_right = st.columns(2)
        with col_left:
            render_dual_axis_chart(filtered_df, current_lang)
            render_correlation_heatmap(filtered_df, current_lang)
        with col_right:
            render_basin_boxplot(filtered_df, current_lang)
            render_seasonal_lag_chart(filtered_df, current_lang)

    with tab3:
        render_simulator(current_lang)

    with tab4:
        render_alert_feed_and_export(filtered_df, current_lang)

    # Footer
    st.markdown(
        f"""
        <div class="footer-container">
            {get_text(current_lang, 'footer_text')} • Version 1.0.0 (Production Grade)
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
