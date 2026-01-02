"""Company deep-dive analysis page."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Company Analysis - Equity Research",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Company Analysis")
st.markdown("Deep dive into individual stock metrics and fundamentals")


@st.cache_data(ttl=3600)
def analyze_company(ticker: str):
    """Fetch and analyze company data."""
    from src.data import YahooClient
    from src.metrics import MetricsCalculator
    from src.scoring import UniverseScorer

    client = YahooClient()
    calculator = MetricsCalculator()
    scorer = UniverseScorer()

    financials = client.get_company_financials(ticker, years=5)
    if not financials:
        return None, None, None

    metrics = calculator.calculate(financials)
    scores = scorer.score_universe([metrics])

    return financials, metrics, scores[0] if scores else None


# Sidebar
st.sidebar.header("Company Selection")

ticker = st.sidebar.text_input(
    "Enter Ticker",
    value="MSFT",
    max_chars=10,
).upper()

quick_picks = st.sidebar.radio(
    "Quick Picks",
    ["Custom", "MSFT", "AAPL", "V", "COST", "HUBS", "CRWD"],
)

if quick_picks != "Custom":
    ticker = quick_picks

if st.sidebar.button("🔍 Analyze", type="primary") or ticker:
    if not ticker:
        st.warning("Please enter a ticker symbol")
    else:
        with st.spinner(f"Analyzing {ticker}..."):
            financials, metrics, score = analyze_company(ticker)

        if not financials:
            st.error(f"Could not fetch data for {ticker}")
        else:
            # Header with company info
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                name = financials.profile.name if financials.profile else ticker
                st.markdown(f"## {name}")
                if financials.profile:
                    st.caption(f"{financials.profile.sector} | {financials.profile.industry}")

            with col2:
                if financials.quote:
                    st.metric(
                        "Price",
                        f"${financials.quote.price:.2f}",
                        f"{financials.quote.change_percent:.1f}%" if financials.quote.change_percent else None,
                    )

            with col3:
                if financials.quote:
                    mkt_cap = financials.quote.market_cap
                    if mkt_cap:
                        if mkt_cap >= 1e12:
                            cap_str = f"${mkt_cap/1e12:.2f}T"
                        elif mkt_cap >= 1e9:
                            cap_str = f"${mkt_cap/1e9:.1f}B"
                        else:
                            cap_str = f"${mkt_cap/1e6:.0f}M"
                        st.metric("Market Cap", cap_str)

            with col4:
                if score:
                    score_val = score.composite_score or 0
                    color = "normal" if score_val >= 50 else "inverse"
                    st.metric("Score", f"{score_val:.1f}", delta_color=color)

            st.markdown("---")

            # Stage classification
            if metrics and metrics.stage:
                stage = metrics.stage
                st.markdown(f"### Stage: **{stage.stage.value.upper()}**")
                st.progress(stage.confidence)
                st.caption(f"Confidence: {stage.confidence:.0%}")

                if stage.reasons:
                    st.markdown("**Classification Reasons:**")
                    for reason in stage.reasons[:5]:
                        st.markdown(f"- {reason}")

            st.markdown("---")

            # Score breakdown
            if score and score.category_scores:
                st.markdown("### Score Breakdown")

                score_cols = st.columns(4)
                categories = ["quality", "growth", "strength", "valuation"]
                icons = ["⭐", "📈", "💪", "💰"]

                for i, (cat, icon) in enumerate(zip(categories, icons)):
                    val = score.category_scores.get(cat)
                    with score_cols[i]:
                        st.metric(
                            f"{icon} {cat.title()}",
                            f"{val:.1f}" if val else "N/A",
                        )

            st.markdown("---")

            # Tabs for detailed metrics
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Quality Metrics",
                "📈 Growth Metrics",
                "💪 Strength Metrics",
                "💰 Valuation Metrics",
            ])

            with tab1:
                if metrics and metrics.traditional and metrics.traditional.quality:
                    q = metrics.traditional.quality
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("ROIC", f"{q.roic:.1%}" if q.roic else "N/A")
                    with cols[1]:
                        st.metric("ROE", f"{q.roe:.1%}" if q.roe else "N/A")
                    with cols[2]:
                        st.metric("ROA", f"{q.roa:.1%}" if q.roa else "N/A")

                    cols2 = st.columns(3)
                    with cols2[0]:
                        st.metric("Gross Margin", f"{q.gross_margin:.1%}" if q.gross_margin else "N/A")
                    with cols2[1]:
                        st.metric("Operating Margin", f"{q.operating_margin:.1%}" if q.operating_margin else "N/A")
                    with cols2[2]:
                        st.metric("FCF Margin", f"{q.fcf_margin:.1%}" if q.fcf_margin else "N/A")

            with tab2:
                if metrics and metrics.traditional and metrics.traditional.growth:
                    g = metrics.traditional.growth
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Revenue CAGR (3Y)", f"{g.revenue_cagr_3y:.1%}" if g.revenue_cagr_3y else "N/A")
                    with cols[1]:
                        st.metric("EPS CAGR (3Y)", f"{g.eps_cagr_3y:.1%}" if g.eps_cagr_3y else "N/A")
                    with cols[2]:
                        st.metric("FCF CAGR (3Y)", f"{g.fcf_cagr_3y:.1%}" if g.fcf_cagr_3y else "N/A")

                    if metrics.growth_stage:
                        st.markdown("**Growth Stage Metrics:**")
                        if metrics.growth_stage.efficiency:
                            eff = metrics.growth_stage.efficiency
                            cols3 = st.columns(2)
                            with cols3[0]:
                                st.metric("Rule of 40", f"{eff.rule_of_40:.1f}" if eff.rule_of_40 else "N/A")
                            with cols3[1]:
                                st.metric("Magic Number", f"{eff.magic_number:.2f}" if eff.magic_number else "N/A")

            with tab3:
                if metrics and metrics.traditional and metrics.traditional.strength:
                    s = metrics.traditional.strength
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Debt/Equity", f"{s.debt_to_equity:.2f}" if s.debt_to_equity else "N/A")
                    with cols[1]:
                        st.metric("Current Ratio", f"{s.current_ratio:.2f}" if s.current_ratio else "N/A")
                    with cols[2]:
                        st.metric("Interest Coverage", f"{s.interest_coverage:.1f}x" if s.interest_coverage else "N/A")

            with tab4:
                if metrics and metrics.traditional and metrics.traditional.valuation:
                    v = metrics.traditional.valuation
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("P/E", f"{v.pe_ratio:.1f}" if v.pe_ratio else "N/A")
                    with cols[1]:
                        st.metric("P/FCF", f"{v.price_to_fcf:.1f}" if v.price_to_fcf else "N/A")
                    with cols[2]:
                        st.metric("EV/EBITDA", f"{v.ev_to_ebitda:.1f}" if v.ev_to_ebitda else "N/A")

                    cols2 = st.columns(3)
                    with cols2[0]:
                        st.metric("FCF Yield", f"{v.fcf_yield:.1%}" if v.fcf_yield else "N/A")
                    with cols2[1]:
                        st.metric("Earnings Yield", f"{v.earnings_yield:.1%}" if v.earnings_yield else "N/A")
                    with cols2[2]:
                        st.metric("PEG Ratio", f"{v.peg_ratio:.2f}" if v.peg_ratio else "N/A")

            st.markdown("---")

            # Historical financials chart
            if financials.income_statements:
                st.markdown("### Historical Financials")

                years = []
                revenues = []
                net_incomes = []

                for stmt in sorted(financials.income_statements, key=lambda x: x.fiscal_year):
                    years.append(stmt.fiscal_year)
                    revenues.append(stmt.total_revenue / 1e9 if stmt.total_revenue else 0)
                    net_incomes.append(stmt.net_income / 1e9 if stmt.net_income else 0)

                fig = make_subplots(specs=[[{"secondary_y": True}]])

                fig.add_trace(
                    go.Bar(x=years, y=revenues, name="Revenue ($B)", marker_color="steelblue"),
                    secondary_y=False,
                )

                fig.add_trace(
                    go.Scatter(x=years, y=net_incomes, name="Net Income ($B)",
                               mode="lines+markers", marker_color="green"),
                    secondary_y=True,
                )

                fig.update_layout(
                    title="Revenue and Net Income Trend",
                    xaxis_title="Year",
                    height=400,
                )
                fig.update_yaxes(title_text="Revenue ($B)", secondary_y=False)
                fig.update_yaxes(title_text="Net Income ($B)", secondary_y=True)

                st.plotly_chart(fig, use_container_width=True)

            # Company description
            if financials.profile and financials.profile.description:
                with st.expander("Company Description"):
                    st.write(financials.profile.description)

else:
    st.info("Enter a ticker symbol and click 'Analyze' to begin")

    # Popular picks
    st.markdown("### Popular Picks")
    popular = ["MSFT", "AAPL", "V", "MA", "COST", "GOOGL", "HUBS", "CRWD", "SNOW"]

    cols = st.columns(3)
    for i, tick in enumerate(popular):
        with cols[i % 3]:
            if st.button(tick):
                st.session_state["ticker"] = tick
                st.rerun()
