"""Company deep-dive analysis page."""

import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Company | Equity Research",
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

    .company-header {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }

    .company-meta {
        font-size: 0.9rem;
        color: #888;
    }

    .score-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 auto;
    }

    .metric-card {
        background: #fafafa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .stage-pill {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner=False)
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


def format_large_number(num):
    """Format large numbers with K, M, B, T suffixes."""
    if num is None:
        return "N/A"
    if abs(num) >= 1e12:
        return f"${num/1e12:.1f}T"
    if abs(num) >= 1e9:
        return f"${num/1e9:.1f}B"
    if abs(num) >= 1e6:
        return f"${num/1e6:.0f}M"
    return f"${num:,.0f}"


def format_pct(num):
    """Format percentage."""
    if num is None:
        return "—"
    return f"{num:.1%}"


def format_ratio(num):
    """Format ratio."""
    if num is None:
        return "—"
    return f"{num:.1f}"


# Page header
st.markdown('<p class="page-title">Company Analysis</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Search")

    ticker = st.text_input(
        "Ticker symbol",
        value="",
        placeholder="MSFT",
        label_visibility="collapsed",
    ).upper()

    st.markdown("##### Quick picks")
    quick_picks = ["MSFT", "AAPL", "V", "COST", "HUBS", "CRWD"]
    cols = st.columns(3)
    for i, pick in enumerate(quick_picks):
        with cols[i % 3]:
            if st.button(pick, use_container_width=True, key=f"pick_{pick}"):
                ticker = pick

    if ticker:
        st.markdown("---")
        analyze_btn = st.button("Analyze", type="primary", use_container_width=True)
    else:
        analyze_btn = False

# Main content
if ticker and analyze_btn:
    with st.spinner(f"Analyzing {ticker}..."):
        financials, metrics, score = analyze_company(ticker)

    if not financials:
        st.error(f"Could not fetch data for {ticker}")
    else:
        # Company header
        col1, col2 = st.columns([3, 1])

        with col1:
            name = financials.profile.company_name if financials.profile else ticker
            st.markdown(f'<p class="company-header">{name}</p>', unsafe_allow_html=True)

            meta_parts = []
            if financials.profile:
                if financials.profile.sector:
                    meta_parts.append(financials.profile.sector)
                if financials.profile.industry:
                    meta_parts.append(financials.profile.industry)
            if meta_parts:
                st.markdown(f'<p class="company-meta">{" · ".join(meta_parts)}</p>', unsafe_allow_html=True)

        with col2:
            if score and score.composite_score:
                score_val = score.composite_score
                color = "#2e7d32" if score_val >= 60 else "#ef6c00" if score_val >= 40 else "#666"
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: 700; color: {color};">{score_val:.0f}</div>
                    <div style="font-size: 0.8rem; color: #888; text-transform: uppercase;">Composite Score</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Key metrics row
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            price = financials.quote.price if financials.quote else None
            change = financials.quote.change_percent if financials.quote else None
            st.metric("Price", f"${price:.2f}" if price else "N/A",
                      f"{change:+.1f}%" if change else None)

        with col2:
            mkt_cap = financials.quote.market_cap if financials.quote else None
            st.metric("Market Cap", format_large_number(mkt_cap))

        with col3:
            if metrics and metrics.stage:
                stage_colors = {
                    "mature": "#e8f5e9",
                    "compounder": "#e3f2fd",
                    "growth": "#fff3e0",
                    "speculative": "#fce4ec",
                }
                stage_text_colors = {
                    "mature": "#2e7d32",
                    "compounder": "#1565c0",
                    "growth": "#ef6c00",
                    "speculative": "#c2185b",
                }
                stage_name = metrics.stage.stage.value
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Stage</div>
                    <div style="margin-top: 0.5rem;">
                        <span class="stage-pill" style="background: {stage_colors.get(stage_name, '#f5f5f5')}; color: {stage_text_colors.get(stage_name, '#666')};">
                            {stage_name.title()}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col4:
            pe = metrics.traditional.valuation.pe_ratio if metrics and metrics.traditional and metrics.traditional.valuation else None
            st.metric("P/E", format_ratio(pe))

        with col5:
            fcf_yield = metrics.traditional.valuation.fcf_yield if metrics and metrics.traditional and metrics.traditional.valuation else None
            st.metric("FCF Yield", format_pct(fcf_yield))

        st.markdown("---")

        # Score breakdown
        if score:
            st.markdown("##### Score Breakdown")

            cols = st.columns(4)
            score_data = [
                ("Quality", score.quality_score),
                ("Growth", score.growth_score),
                ("Strength", score.strength_score),
                ("Valuation", score.valuation_score),
            ]

            for i, (label, val) in enumerate(score_data):
                with cols[i]:
                    if val:
                        color = "#2e7d32" if val >= 60 else "#ef6c00" if val >= 40 else "#888"
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value" style="color: {color};">{val:.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value" style="color: #ccc;">—</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("---")

        # Detailed metrics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Quality", "Growth", "Strength", "Valuation"])

        with tab1:
            if metrics and metrics.traditional and metrics.traditional.quality:
                q = metrics.traditional.quality
                cols = st.columns(4)

                metrics_data = [
                    ("ROIC", q.roic, True),
                    ("ROE", q.roe, True),
                    ("Gross Margin", q.gross_margin, True),
                    ("Operating Margin", q.operating_margin, True),
                    ("Net Margin", q.net_margin, True),
                    ("FCF Margin", q.fcf_margin, True),
                    ("ROA", q.roa, True),
                    ("Asset Turnover", q.asset_turnover, False),
                ]

                for i, (label, val, is_pct) in enumerate(metrics_data):
                    with cols[i % 4]:
                        display_val = format_pct(val) if is_pct else format_ratio(val)
                        st.metric(label, display_val)

        with tab2:
            if metrics and metrics.traditional and metrics.traditional.growth:
                g = metrics.traditional.growth
                cols = st.columns(4)

                metrics_data = [
                    ("Revenue Growth 1Y", g.revenue_growth_1y),
                    ("Revenue CAGR 3Y", g.revenue_growth_3y_cagr),
                    ("Revenue CAGR 5Y", g.revenue_growth_5y_cagr),
                    ("Earnings Growth 1Y", g.earnings_growth_1y),
                    ("Earnings CAGR 3Y", g.earnings_growth_3y_cagr),
                    ("FCF Growth 1Y", g.fcf_growth_1y),
                    ("FCF CAGR 3Y", g.fcf_growth_3y_cagr),
                ]

                for i, (label, val) in enumerate(metrics_data):
                    with cols[i % 4]:
                        st.metric(label, format_pct(val))

        with tab3:
            if metrics and metrics.traditional and metrics.traditional.strength:
                s = metrics.traditional.strength
                cols = st.columns(4)

                st.metric("Debt/Equity", format_ratio(s.debt_to_equity))
                st.metric("Current Ratio", format_ratio(s.current_ratio))
                st.metric("Interest Coverage", f"{s.interest_coverage:.1f}x" if s.interest_coverage else "—")

        with tab4:
            if metrics and metrics.traditional and metrics.traditional.valuation:
                v = metrics.traditional.valuation
                cols = st.columns(4)

                metrics_data = [
                    ("P/E", v.pe_ratio, False),
                    ("P/S", v.ps_ratio, False),
                    ("P/B", v.pb_ratio, False),
                    ("EV/EBITDA", v.ev_to_ebitda, False),
                    ("EV/Sales", v.ev_to_sales, False),
                    ("FCF Yield", v.fcf_yield, True),
                    ("Earnings Yield", v.earnings_yield, True),
                    ("PEG", v.peg_ratio, False),
                ]

                for i, (label, val, is_pct) in enumerate(metrics_data):
                    with cols[i % 4]:
                        display_val = format_pct(val) if is_pct else format_ratio(val)
                        st.metric(label, display_val)

        # Financials chart
        if financials.income_statements:
            st.markdown("---")
            st.markdown("##### Financial Trend")

            years = []
            revenues = []
            net_incomes = []

            for stmt in sorted(financials.income_statements, key=lambda x: x.date):
                years.append(stmt.date.year)
                revenues.append(stmt.revenue / 1e9 if stmt.revenue else 0)
                net_incomes.append(stmt.net_income / 1e9 if stmt.net_income else 0)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=years,
                y=revenues,
                name="Revenue",
                marker_color="#e3f2fd",
                marker_line_color="#1565c0",
                marker_line_width=1,
            ))

            fig.add_trace(go.Scatter(
                x=years,
                y=net_incomes,
                name="Net Income",
                mode="lines+markers",
                line=dict(color="#2e7d32", width=2),
                marker=dict(size=8),
            ))

            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis_title="$ Billions",
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
            )

            st.plotly_chart(fig, use_container_width=True)

        # Stage classification reasoning
        if metrics and metrics.stage and metrics.stage.reasons:
            with st.expander("Stage Classification Reasoning"):
                for reason in metrics.stage.reasons:
                    st.markdown(f"• {reason}")

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #888;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
        <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">Enter a ticker to analyze</div>
        <div style="font-size: 0.9rem;">Type a symbol in the sidebar or select from quick picks</div>
    </div>
    """, unsafe_allow_html=True)
