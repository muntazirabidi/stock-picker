"""Main Streamlit application for Equity Research System."""

import streamlit as st

st.set_page_config(
    page_title="Equity Research",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for minimalist design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Clean typography */
    .main-header {
        font-size: 2.5rem;
        font-weight: 300;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    .sub-header {
        font-size: 1rem;
        color: #666;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    .card {
        background: #fafafa;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #eee;
        transition: all 0.2s ease;
    }

    .card:hover {
        border-color: #ddd;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 500;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }

    .card-text {
        font-size: 0.9rem;
        color: #666;
        line-height: 1.6;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Streamlit overrides */
    .stMetric label {
        color: #888 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""

    # Header
    st.markdown('<p class="main-header">Equity Research</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Find quality compounders before they become mega-caps</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Navigation cards
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Universe</div>
            <div class="card-text">
                Score and rank stocks from S&P 500, Nasdaq 100, or custom lists.
                Filter by stage, sort by composite score.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Universe", use_container_width=True):
            st.switch_page("pages/1_Universe.py")

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">Company</div>
            <div class="card-text">
                Deep analysis of individual stocks. Quality metrics,
                growth trends, valuation, and stage classification.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Analyze Company", use_container_width=True):
            st.switch_page("pages/2_Company.py")

    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-title">Portfolio</div>
            <div class="card-text">
                Track your holdings, monitor allocation by tier,
                and get deployment recommendations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Manage Portfolio", use_container_width=True):
            st.switch_page("pages/3_Portfolio.py")

    st.markdown("---")

    # Quick stats
    try:
        from src.data import YahooClient
        client = YahooClient()
        stats = client.cache_stats()

        st.markdown("##### System Status")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cached", stats["valid"])
        with col2:
            st.metric("Size", f"{stats['total_size_mb']:.1f} MB")
        with col3:
            st.metric("TTL", f"{stats['ttl_hours']}h")
        with col4:
            st.metric("Expired", stats["expired"])

    except Exception:
        pass


if __name__ == "__main__":
    main()
