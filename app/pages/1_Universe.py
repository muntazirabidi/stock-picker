"""Universe browsing and scoring page."""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Universe | Equity Research",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimalist CSS
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

    .top-stock {
        background: #fafafa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #1565c0;
    }

    .rank-badge {
        display: inline-block;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #1565c0;
        color: white;
        text-align: center;
        line-height: 28px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-right: 0.75rem;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    .interpretation-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 3px solid #1565c0;
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

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    valid_scores = df["Score"].dropna()
    with col1:
        st.metric("Scored", len(df), help="Number of stocks successfully scored")
    with col2:
        st.metric("Avg Score", f"{valid_scores.mean():.1f}" if len(valid_scores) > 0 else "N/A")
    with col3:
        st.metric("Top Score", f"{valid_scores.max():.1f}" if len(valid_scores) > 0 else "N/A")
    with col4:
        compounders = len(df[df["Stage"] == "Compounder"])
        st.metric("Compounders", compounders, help="Companies with FCF+ and >10% growth")

    # Interpretation guide
    with st.expander("How to interpret scores", expanded=False):
        st.markdown("""
        **Composite Score (0-100)** ranks each stock vs peers in the universe:
        - **60+** = Top third. Strong fundamentals, consider for core positions
        - **40-60** = Average. May have strengths and weaknesses. Dig deeper
        - **<40** = Below average. Proceed with caution

        **Category Scores:**
        - **Quality**: Profitability (ROIC, margins). Higher = more efficient
        - **Growth**: Revenue & earnings growth rates. Higher = faster growing
        - **Strength**: Balance sheet health (debt, liquidity). Higher = safer
        - **Value**: Valuation metrics (P/E, FCF yield). Higher = cheaper

        **Stages:**
        - **Mature**: Stable, FCF positive, <10% growth. Focus on yield & stability
        - **Compounder**: The sweet spot. FCF positive AND >10% growth
        - **Growth**: High growth but may not be profitable yet
        - **Speculative**: Doesn't fit categories. Needs individual research
        """)

    st.markdown("---")

    # Filters and sorting
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        stages = ["All"] + sorted(df["Stage"].dropna().unique().tolist())
        selected_stage = st.selectbox("Stage", stages, help="Filter by company lifecycle stage")

    with col2:
        sort_options = {
            "Score (High to Low)": ("Score", False),
            "Score (Low to High)": ("Score", True),
            "Quality (High to Low)": ("Quality", False),
            "Growth (High to Low)": ("Growth", False),
            "Strength (High to Low)": ("Strength", False),
            "Value (High to Low)": ("Value", False),
            "Name (A-Z)": ("Name", True),
        }
        sort_by = st.selectbox("Sort by", list(sort_options.keys()))

    with col3:
        min_score = st.slider("Minimum score", 0, 100, 0, help="Filter out stocks below this score")

    # Apply filters
    filtered_df = df.copy()
    if selected_stage != "All":
        filtered_df = filtered_df[filtered_df["Stage"] == selected_stage]
    filtered_df = filtered_df[filtered_df["Score"].fillna(0) >= min_score]

    # Apply sorting
    sort_col, ascending = sort_options[sort_by]
    filtered_df = filtered_df.sort_values(sort_col, ascending=ascending, na_position="last")
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1

    st.caption(f"Showing {len(filtered_df)} of {len(df)} stocks")

    # Two column layout: Table + Top 10
    col_table, col_top = st.columns([2, 1])

    with col_table:
        st.markdown("##### All Stocks")

        # Interactive data table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=500,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score",
                    min_value=0,
                    max_value=100,
                    format="%.1f",
                ),
                "Quality": st.column_config.NumberColumn("Quality", format="%.1f", help="Profitability metrics"),
                "Growth": st.column_config.NumberColumn("Growth", format="%.1f", help="Revenue & earnings growth"),
                "Strength": st.column_config.NumberColumn("Strength", format="%.1f", help="Balance sheet health"),
                "Value": st.column_config.NumberColumn("Value", format="%.1f", help="Valuation attractiveness"),
            },
        )

        # Download button
        csv = filtered_df.to_csv(index=True)
        st.download_button(
            "Download CSV",
            csv,
            "universe_scores.csv",
            "text/csv",
            use_container_width=True,
        )

    with col_top:
        st.markdown("##### Top 10 Picks")

        top_10 = df.sort_values("Score", ascending=False, na_position="last").head(10)

        for i, (_, row) in enumerate(top_10.iterrows(), 1):
            score_val = row["Score"] if pd.notna(row["Score"]) else 0
            color = "#2e7d32" if score_val >= 60 else "#ef6c00" if score_val >= 40 else "#666"

            stage_colors = {
                "Mature": "#e8f5e9",
                "Compounder": "#e3f2fd",
                "Growth": "#fff3e0",
                "Speculative": "#fce4ec",
            }
            stage_bg = stage_colors.get(row["Stage"], "#f5f5f5")

            st.markdown(f"""
            <div class="top-stock">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center;">
                        <span class="rank-badge">{i}</span>
                        <div>
                            <div style="font-weight: 600;">{row['Ticker']}</div>
                            <div style="font-size: 0.8rem; color: #666;">{row['Name'][:20]}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: {color};">{score_val:.0f}</div>
                        <div style="font-size: 0.7rem; background: {stage_bg}; padding: 2px 8px; border-radius: 10px;">{row['Stage']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Quick interpretation
        st.markdown("---")
        st.markdown("##### Quick Analysis")

        avg_score = valid_scores.mean()
        top_score = valid_scores.max()

        if top_score >= 70:
            st.success(f"Strong picks available. Top score: {top_score:.0f}")
        elif top_score >= 55:
            st.info(f"Decent options. Top score: {top_score:.0f}")
        else:
            st.warning(f"Limited quality. Top score: {top_score:.0f}")

        # Stage breakdown
        st.markdown("**By Stage:**")
        stage_counts = df["Stage"].value_counts()
        for stage, count in stage_counts.items():
            pct = count / len(df) * 100
            st.caption(f"{stage}: {count} ({pct:.0f}%)")

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #888;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
        <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">Ready to score</div>
        <div style="font-size: 0.9rem;">Select a universe from the sidebar and click "Score Universe"</div>
    </div>
    """, unsafe_allow_html=True)

    # What you'll get
    st.markdown("---")
    st.markdown("##### What you'll get")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **Composite Score**
        Overall ranking (0-100) combining all metrics. Higher = better quality.
        """)
    with col2:
        st.markdown("""
        **Stage Classification**
        Mature, Compounder, Growth, or Speculative based on fundamentals.
        """)
    with col3:
        st.markdown("""
        **Category Breakdown**
        Quality, Growth, Strength, and Valuation scores for deeper analysis.
        """)
