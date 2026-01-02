"""Universe browsing and scoring page."""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Universe | Equity Research",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .page-title {
        font-size: 1.75rem;
        font-weight: 400;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }

    .page-subtitle {
        font-size: 0.9rem;
        color: #888;
        margin-bottom: 1.5rem;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner=False)
def load_universe(universe_type: str) -> list[str]:
    """Load ticker list for given universe."""
    from src.data import YahooClient
    client = YahooClient()

    if universe_type == "S&P 500":
        return client.get_sp500_tickers()
    elif universe_type == "Nasdaq 100":
        return client.get_nasdaq100_tickers()
    elif universe_type == "Combined":
        sp500 = client.get_sp500_tickers()
        nasdaq = client.get_nasdaq100_tickers()
        return list(set(sp500 + nasdaq))
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def score_tickers(tickers: tuple) -> pd.DataFrame:
    """Score a list of tickers and return as DataFrame."""
    from src.data import YahooClient
    from src.metrics import MetricsCalculator
    from src.scoring import UniverseScorer

    client = YahooClient()
    calculator = MetricsCalculator()
    scorer = UniverseScorer()
    metrics_list = []

    for ticker in tickers:
        try:
            financials = client.get_company_financials(ticker, years=5)
            if financials:
                metrics = calculator.calculate(financials)
                metrics_list.append(metrics)
        except Exception:
            pass

    if not metrics_list:
        return pd.DataFrame()

    scores = scorer.score_universe(metrics_list)

    data = []
    for score in scores:
        data.append({
            "Ticker": score.ticker,
            "Name": (score.name or "")[:30],
            "Stage": score.stage.value.title(),
            "Score": round(score.composite_score, 1) if score.composite_score else None,
            "Quality": round(score.quality_score, 1) if score.quality_score else None,
            "Growth": round(score.growth_score, 1) if score.growth_score else None,
            "Strength": round(score.strength_score, 1) if score.strength_score else None,
            "Value": round(score.valuation_score, 1) if score.valuation_score else None,
        })

    return pd.DataFrame(data)


# Page header
st.markdown('<p class="page-title">Universe</p>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Score and rank stocks by quality, growth, strength, and valuation</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Universe")

    universe_type = st.selectbox(
        "Select universe",
        ["S&P 500", "Nasdaq 100", "Combined", "Custom"],
        label_visibility="collapsed",
    )

    if universe_type == "Custom":
        custom_tickers = st.text_area(
            "Tickers (one per line)",
            value="MSFT\nAAPL\nV\nMA\nCOST\nHUBS\nGOOGL\nAMZN\nNVDA\nCRM",
            height=150,
            label_visibility="collapsed",
        )
        tickers = [t.strip().upper() for t in custom_tickers.split("\n") if t.strip()]
    else:
        with st.spinner("Loading..."):
            all_tickers = load_universe(universe_type)

        st.caption(f"{len(all_tickers)} stocks available")

        max_tickers = st.slider(
            "Stocks to score",
            10, min(100, len(all_tickers)), 30,
            label_visibility="collapsed",
            help="More stocks = longer wait but broader analysis"
        )
        tickers = all_tickers[:max_tickers]

    st.markdown("---")
    run_button = st.button("Score Universe", type="primary", use_container_width=True)

# Main content
if "scored_df" not in st.session_state:
    st.session_state.scored_df = None

if run_button and tickers:
    with st.spinner(f"Scoring {len(tickers)} stocks... This may take a minute."):
        df = score_tickers(tuple(tickers))
        st.session_state.scored_df = df

if st.session_state.scored_df is not None and not st.session_state.scored_df.empty:
    df = st.session_state.scored_df

    # Summary metrics row
    col1, col2, col3, col4 = st.columns(4)

    valid_scores = df["Score"].dropna()
    with col1:
        st.metric("Scored", len(df))
    with col2:
        st.metric("Avg Score", f"{valid_scores.mean():.1f}" if len(valid_scores) > 0 else "N/A")
    with col3:
        st.metric("Top Score", f"{valid_scores.max():.1f}" if len(valid_scores) > 0 else "N/A")
    with col4:
        compounders = len(df[df["Stage"] == "Compounder"])
        st.metric("Compounders", compounders)

    st.markdown("---")

    # Filters row - all on one line
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        stages = ["All"] + sorted(df["Stage"].dropna().unique().tolist())
        selected_stage = st.selectbox("Stage", stages)

    with col2:
        sort_options = {
            "Score ↓": ("Score", False),
            "Score ↑": ("Score", True),
            "Quality ↓": ("Quality", False),
            "Growth ↓": ("Growth", False),
            "Strength ↓": ("Strength", False),
            "Value ↓": ("Value", False),
            "Ticker A-Z": ("Ticker", True),
        }
        sort_by = st.selectbox("Sort by", list(sort_options.keys()))

    with col3:
        min_score = st.number_input("Min Score", 0, 100, 0, step=10)

    with col4:
        show_top_n = st.selectbox("Show", ["All", "Top 10", "Top 20", "Top 50"])

    # Apply filters
    filtered_df = df.copy()
    if selected_stage != "All":
        filtered_df = filtered_df[filtered_df["Stage"] == selected_stage]
    filtered_df = filtered_df[filtered_df["Score"].fillna(0) >= min_score]

    # Apply sorting
    sort_col, ascending = sort_options[sort_by]
    filtered_df = filtered_df.sort_values(sort_col, ascending=ascending, na_position="last")

    # Apply top N filter
    if show_top_n != "All":
        n = int(show_top_n.split()[1])
        filtered_df = filtered_df.head(n)

    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1  # 1-based ranking

    st.caption(f"Showing {len(filtered_df)} of {len(df)} stocks")

    # Single clean table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=600,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
            "Quality": st.column_config.ProgressColumn(
                "Quality",
                min_value=0,
                max_value=100,
                format="%.1f",
                help="Profitability: ROIC, margins, returns"
            ),
            "Growth": st.column_config.ProgressColumn(
                "Growth",
                min_value=0,
                max_value=100,
                format="%.1f",
                help="Revenue & earnings growth rates"
            ),
            "Strength": st.column_config.ProgressColumn(
                "Strength",
                min_value=0,
                max_value=100,
                format="%.1f",
                help="Balance sheet health, debt levels"
            ),
            "Value": st.column_config.ProgressColumn(
                "Value",
                min_value=0,
                max_value=100,
                format="%.1f",
                help="Valuation attractiveness vs peers"
            ),
        },
    )

    # Download button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        csv = filtered_df.to_csv(index=True)
        st.download_button(
            "Download CSV",
            csv,
            "universe_scores.csv",
            "text/csv",
        )

    # Interpretation guide at bottom
    with st.expander("Score Interpretation Guide"):
        st.markdown("""
        | Score | Rating | Meaning |
        |-------|--------|---------|
        | 70+ | Excellent | Top tier fundamentals, strong candidate |
        | 55-70 | Good | Above average, worth researching |
        | 40-55 | Average | Mixed signals, dig deeper |
        | <40 | Below Avg | Weak fundamentals, proceed with caution |

        **Stages:** Compounder (FCF+ & >10% growth) → Mature (FCF+ & <10% growth) → Growth (high growth, not yet profitable) → Speculative (unclear)
        """)

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #888;">
        <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">Select a universe and click "Score Universe"</div>
    </div>
    """, unsafe_allow_html=True)
