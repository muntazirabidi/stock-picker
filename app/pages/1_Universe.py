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

    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        margin-bottom: 1rem;
    }

    .score-value {
        font-size: 2.5rem;
        font-weight: 600;
    }

    .score-label {
        font-size: 0.8rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stage-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .stage-mature { background: #e8f5e9; color: #2e7d32; }
    .stage-compounder { background: #e3f2fd; color: #1565c0; }
    .stage-growth { background: #fff3e0; color: #ef6c00; }
    .stage-speculative { background: #fce4ec; color: #c2185b; }

    .stock-row {
        padding: 1rem 0;
        border-bottom: 1px solid #f0f0f0;
    }

    .stock-ticker {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
    }

    .stock-name {
        font-size: 0.85rem;
        color: #666;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #eee;
        border-radius: 8px;
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
            "Name": (score.name or "")[:35],
            "Stage": score.stage.value.title(),
            "Score": round(score.composite_score, 1) if score.composite_score else None,
            "Quality": round(score.quality_score, 1) if score.quality_score else None,
            "Growth": round(score.growth_score, 1) if score.growth_score else None,
            "Strength": round(score.strength_score, 1) if score.strength_score else None,
            "Value": round(score.valuation_score, 1) if score.valuation_score else None,
        })

    df = pd.DataFrame(data)
    df = df.sort_values("Score", ascending=False, na_position="last").reset_index(drop=True)
    df.index = df.index + 1
    return df


# Page header
st.markdown('<p class="page-title">Universe</p>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Score and rank stocks by quality, growth, strength, and valuation</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Settings")

    universe_type = st.selectbox(
        "Universe",
        ["S&P 500", "Nasdaq 100", "Combined", "Custom"],
        label_visibility="collapsed",
    )

    if universe_type == "Custom":
        custom_tickers = st.text_area(
            "Tickers (one per line)",
            value="MSFT\nAAPL\nV\nMA\nCOST\nHUBS",
            height=120,
            label_visibility="collapsed",
        )
        tickers = [t.strip().upper() for t in custom_tickers.split("\n") if t.strip()]
    else:
        with st.spinner("Loading..."):
            all_tickers = load_universe(universe_type)

        st.caption(f"{len(all_tickers)} stocks available")

        max_tickers = st.slider(
            "Stocks to score",
            10, min(100, len(all_tickers)), 25,
            label_visibility="collapsed",
        )
        tickers = all_tickers[:max_tickers]

    st.markdown("---")
    run_button = st.button("Score Universe", type="primary", use_container_width=True)

# Main content
if run_button and tickers:
    with st.spinner(f"Scoring {len(tickers)} stocks..."):
        progress_bar = st.progress(0)
        df = score_tickers(tuple(tickers))
        progress_bar.empty()

    if df.empty:
        st.error("No data returned")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        valid_scores = df["Score"].dropna()
        with col1:
            st.metric("Stocks Scored", len(df))
        with col2:
            st.metric("Avg Score", f"{valid_scores.mean():.1f}" if len(valid_scores) > 0 else "N/A")
        with col3:
            st.metric("Top Score", f"{valid_scores.max():.1f}" if len(valid_scores) > 0 else "N/A")
        with col4:
            compounders = len(df[df["Stage"] == "Compounder"])
            st.metric("Compounders", compounders)

        st.markdown("---")

        # Filters
        col1, col2 = st.columns([1, 3])

        with col1:
            stages = ["All"] + df["Stage"].unique().tolist()
            selected_stage = st.selectbox("Filter by stage", stages, label_visibility="collapsed")

        with col2:
            min_score = st.slider("Minimum score", 0, 100, 0, label_visibility="collapsed")

        # Apply filters
        filtered_df = df.copy()
        if selected_stage != "All":
            filtered_df = filtered_df[filtered_df["Stage"] == selected_stage]
        filtered_df = filtered_df[filtered_df["Score"].fillna(0) >= min_score]

        # Results count
        st.caption(f"Showing {len(filtered_df)} of {len(df)} stocks")

        # Data table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=450,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score",
                    min_value=0,
                    max_value=100,
                    format="%.1f",
                ),
                "Quality": st.column_config.NumberColumn("Quality", format="%.1f"),
                "Growth": st.column_config.NumberColumn("Growth", format="%.1f"),
                "Strength": st.column_config.NumberColumn("Strength", format="%.1f"),
                "Value": st.column_config.NumberColumn("Value", format="%.1f"),
            },
        )

        # Top picks summary
        st.markdown("---")
        st.markdown("##### Top Picks")

        top_5 = filtered_df.head(5)
        cols = st.columns(5)

        for i, (_, row) in enumerate(top_5.iterrows()):
            with cols[i]:
                score_val = row["Score"] if pd.notna(row["Score"]) else 0

                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: #fafafa; border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: #888;">#{i+1}</div>
                    <div style="font-size: 1.25rem; font-weight: 600;">{row['Ticker']}</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: {'#2e7d32' if score_val >= 60 else '#ef6c00' if score_val >= 40 else '#666'};">{score_val:.0f}</div>
                    <div style="font-size: 0.7rem; color: #888; text-transform: uppercase;">{row['Stage']}</div>
                </div>
                """, unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #888;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
        <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">Ready to score</div>
        <div style="font-size: 0.9rem;">Select a universe and click "Score Universe" to begin</div>
    </div>
    """, unsafe_allow_html=True)
