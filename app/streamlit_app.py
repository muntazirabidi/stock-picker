"""Main Streamlit application for Equity Research System."""

import streamlit as st

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Equity Research System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main application entry point."""
    st.title("📊 Equity Research System")
    st.markdown("*Find quality compounders before they become mega-caps*")

    st.markdown("---")

    # Dashboard overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔍 Universe")
        st.markdown("""
        Browse and score stocks from:
        - S&P 500
        - Nasdaq 100
        - Custom watchlist

        Navigate to **Universe** page to explore.
        """)

    with col2:
        st.markdown("### 📈 Company Analysis")
        st.markdown("""
        Deep dive into individual stocks:
        - Quality metrics
        - Growth metrics
        - Stage classification
        - Historical trends

        Navigate to **Company** page to analyze.
        """)

    with col3:
        st.markdown("### 💼 Portfolio")
        st.markdown("""
        Manage your holdings:
        - Track allocation by tier
        - View performance
        - Get deployment recommendations
        - Monitor alerts

        Navigate to **Portfolio** page to manage.
        """)

    st.markdown("---")

    # Quick stats
    st.markdown("### Quick Status")

    try:
        from src.data import YahooClient

        client = YahooClient()
        stats = client.cache_stats()

        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("Cached Entries", stats["valid"])
        with stat_col2:
            st.metric("Cache Size", f"{stats['total_size_mb']:.2f} MB")
        with stat_col3:
            st.metric("Cache TTL", f"{stats['ttl_hours']}h")
        with stat_col4:
            st.metric("Expired", stats["expired"])

    except Exception as e:
        st.warning(f"Could not load cache stats: {e}")

    # Getting started
    st.markdown("---")
    st.markdown("### Getting Started")

    st.markdown("""
    1. **Score stocks**: Go to the **Universe** page to browse and score stocks
    2. **Analyze companies**: Go to the **Company** page to deep dive into specific tickers
    3. **Track portfolio**: Go to the **Portfolio** page to add holdings and get deployment recommendations

    **CLI Commands:**
    ```bash
    # Score specific tickers
    python -m src.cli score MSFT AAPL V

    # Get deployment recommendations
    python -m src.cli deploy --amount 1000

    # Check portfolio status
    python -m src.cli portfolio status --alerts
    ```
    """)


if __name__ == "__main__":
    main()
