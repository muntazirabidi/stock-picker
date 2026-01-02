"""Universe browsing and scoring page."""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Universe - Equity Research",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Universe Browser")
st.markdown("Score and rank stocks from your investment universe")


@st.cache_data(ttl=3600)
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
    else:
        return []


@st.cache_data(ttl=3600)
def score_tickers(tickers: tuple) -> pd.DataFrame:
    """Score a list of tickers and return as DataFrame."""
    from src.data import YahooClient
    from src.metrics import MetricsCalculator
    from src.scoring import UniverseScorer

    client = YahooClient()
    calculator = MetricsCalculator()
    scorer = UniverseScorer()

    metrics_list = []

    progress = st.progress(0)
    status = st.empty()

    for i, ticker in enumerate(tickers):
        status.text(f"Scoring {ticker}... ({i+1}/{len(tickers)})")
        progress.progress((i + 1) / len(tickers))

        try:
            financials = client.get_company_financials(ticker, years=5)
            if financials:
                metrics = calculator.calculate(financials)
                metrics_list.append(metrics)
        except Exception:
            pass

    status.empty()
    progress.empty()

    if not metrics_list:
        return pd.DataFrame()

    scores = scorer.score_universe(metrics_list)

    # Build results DataFrame
    data = []
    for score in scores:
        data.append({
            "Ticker": score.ticker,
            "Name": score.name or "",
            "Stage": score.stage.value,
            "Score": score.composite_score,
            "Quality": score.quality_score,
            "Growth": score.growth_score,
            "Strength": score.strength_score,
            "Valuation": score.valuation_score,
        })

    df = pd.DataFrame(data)
    df = df.sort_values("Score", ascending=False).reset_index(drop=True)
    df.index = df.index + 1  # 1-indexed rank
    df.index.name = "Rank"

    return df


# Sidebar controls
st.sidebar.header("Universe Selection")

universe_type = st.sidebar.selectbox(
    "Select Universe",
    ["S&P 500", "Nasdaq 100", "Combined", "Custom"],
)

if universe_type == "Custom":
    custom_tickers = st.sidebar.text_area(
        "Enter tickers (one per line)",
        value="MSFT\nAAPL\nV\nMA\nCOST",
        height=150,
    )
    tickers = [t.strip().upper() for t in custom_tickers.split("\n") if t.strip()]
else:
    with st.spinner(f"Loading {universe_type}..."):
        all_tickers = load_universe(universe_type)

    st.sidebar.info(f"Found {len(all_tickers)} stocks")

    # Limit selection for performance
    max_tickers = st.sidebar.slider(
        "Max stocks to score",
        min_value=10,
        max_value=min(100, len(all_tickers)),
        value=min(30, len(all_tickers)),
    )

    # Filter by first letter
    first_letters = sorted(set(t[0] for t in all_tickers if t))
    selected_letters = st.sidebar.multiselect(
        "Filter by first letter",
        first_letters,
        default=None,
    )

    if selected_letters:
        tickers = [t for t in all_tickers if t[0] in selected_letters][:max_tickers]
    else:
        tickers = all_tickers[:max_tickers]

st.sidebar.markdown(f"**Selected: {len(tickers)} tickers**")

# Main content
if st.button("📊 Score Universe", type="primary"):
    if not tickers:
        st.warning("No tickers selected")
    else:
        with st.spinner(f"Scoring {len(tickers)} stocks..."):
            df = score_tickers(tuple(tickers))

        if df.empty:
            st.error("No data returned. Check your internet connection.")
        else:
            st.success(f"Scored {len(df)} stocks")

            # Filters
            col1, col2 = st.columns(2)
            with col1:
                stages = df["Stage"].unique().tolist()
                selected_stages = st.multiselect(
                    "Filter by Stage",
                    stages,
                    default=stages,
                )

            with col2:
                min_score = st.slider(
                    "Minimum Score",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                )

            # Apply filters
            filtered_df = df[
                (df["Stage"].isin(selected_stages)) &
                (df["Score"].fillna(0) >= min_score)
            ]

            st.markdown(f"### Results ({len(filtered_df)} stocks)")

            # Display table
            st.dataframe(
                filtered_df.style.format({
                    "Score": "{:.1f}",
                    "Quality": "{:.1f}",
                    "Growth": "{:.1f}",
                    "Strength": "{:.1f}",
                    "Valuation": "{:.1f}",
                }).background_gradient(
                    subset=["Score"],
                    cmap="RdYlGn",
                    vmin=0,
                    vmax=100,
                ),
                use_container_width=True,
                height=500,
            )

            # Stage distribution
            st.markdown("### Stage Distribution")
            stage_counts = filtered_df["Stage"].value_counts()
            st.bar_chart(stage_counts)

            # Top picks
            st.markdown("### Top 10 Picks")
            top_10 = filtered_df.head(10)
            for _, row in top_10.iterrows():
                score_color = "green" if (row["Score"] or 0) >= 60 else "orange" if (row["Score"] or 0) >= 40 else "red"
                st.markdown(
                    f"**{row['Ticker']}** - {row['Name'][:40]} | "
                    f"Stage: {row['Stage']} | "
                    f"Score: :{score_color}[{row['Score']:.1f}]"
                )

else:
    st.info("Click 'Score Universe' to analyze stocks")

    # Show sample
    st.markdown("### Sample Tickers")
    st.code("\n".join(tickers[:20]))
