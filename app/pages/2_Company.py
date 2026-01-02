"""Company deep-dive analysis page."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta

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

    .news-card {
        background: #fafafa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid #1565c0;
    }

    .news-title {
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }

    .news-meta {
        font-size: 0.75rem;
        color: #888;
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


@st.cache_data(ttl=300, show_spinner=False)
def get_price_data(ticker: str, days: int = 365):
    """Fetch price data from Polygon."""
    try:
        from src.data import PolygonClient
        client = PolygonClient()
        end = date.today()
        start = end - timedelta(days=days)
        return client.get_daily_bars(ticker, start, end, limit=days)
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def get_technical_indicators(ticker: str):
    """Fetch technical indicators from Polygon."""
    try:
        from src.data import PolygonClient
        client = PolygonClient()
        sma_50 = client.get_sma(ticker, window=50, limit=100)
        sma_200 = client.get_sma(ticker, window=200, limit=100)
        rsi = client.get_rsi(ticker, window=14, limit=100)
        return sma_50, sma_200, rsi
    except Exception:
        return [], [], []


@st.cache_data(ttl=600, show_spinner=False)
def get_news(ticker: str, limit: int = 10):
    """Fetch news from Polygon."""
    try:
        from src.data import PolygonClient
        client = PolygonClient()
        return client.get_news(ticker, limit=limit)
    except Exception:
        return []


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

        # Main tabs
        tab_chart, tab_quality, tab_growth, tab_strength, tab_valuation, tab_news = st.tabs(
            ["Price Chart", "Quality", "Growth", "Strength", "Valuation", "News"]
        )

        # Price Chart Tab
        with tab_chart:
            with st.spinner("Loading price data..."):
                bars = get_price_data(ticker, days=365)
                sma_50, sma_200, rsi = get_technical_indicators(ticker)

            if bars:
                # Create subplot with price and RSI
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.05,
                    row_heights=[0.7, 0.3],
                    subplot_titles=(f"{ticker} Price", "RSI (14)")
                )

                # Price line
                dates = [b.date for b in bars]
                closes = [b.close for b in bars]

                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=closes,
                        name="Price",
                        line=dict(color="#1565c0", width=2),
                    ),
                    row=1, col=1
                )

                # SMA 50
                if sma_50:
                    sma_dates = [s.date for s in sma_50]
                    sma_vals = [s.value for s in sma_50]
                    fig.add_trace(
                        go.Scatter(
                            x=sma_dates,
                            y=sma_vals,
                            name="SMA 50",
                            line=dict(color="#ef6c00", width=1, dash="dot"),
                        ),
                        row=1, col=1
                    )

                # SMA 200
                if sma_200:
                    sma_dates = [s.date for s in sma_200]
                    sma_vals = [s.value for s in sma_200]
                    fig.add_trace(
                        go.Scatter(
                            x=sma_dates,
                            y=sma_vals,
                            name="SMA 200",
                            line=dict(color="#2e7d32", width=1, dash="dot"),
                        ),
                        row=1, col=1
                    )

                # RSI
                if rsi:
                    rsi_dates = [r.date for r in rsi]
                    rsi_vals = [r.value for r in rsi]
                    fig.add_trace(
                        go.Scatter(
                            x=rsi_dates,
                            y=rsi_vals,
                            name="RSI",
                            line=dict(color="#9c27b0", width=2),
                        ),
                        row=2, col=1
                    )

                    # RSI overbought/oversold lines
                    fig.add_hline(y=70, line_dash="dash", line_color="#c62828", opacity=0.5, row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="#2e7d32", opacity=0.5, row=2, col=1)

                fig.update_layout(
                    height=500,
                    margin=dict(l=0, r=0, t=40, b=0),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    hovermode="x unified",
                )

                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")

                st.plotly_chart(fig, use_container_width=True)

                # Price stats
                if len(closes) > 1:
                    col1, col2, col3, col4 = st.columns(4)
                    current = closes[-1]
                    high_52w = max(closes)
                    low_52w = min(closes)
                    change_ytd = ((current - closes[0]) / closes[0]) * 100

                    with col1:
                        st.metric("Current", f"${current:.2f}")
                    with col2:
                        st.metric("52W High", f"${high_52w:.2f}", f"{((current/high_52w)-1)*100:.1f}%")
                    with col3:
                        st.metric("52W Low", f"${low_52w:.2f}", f"{((current/low_52w)-1)*100:+.1f}%")
                    with col4:
                        st.metric("YTD Change", f"{change_ytd:+.1f}%")

                # RSI interpretation
                if rsi:
                    latest_rsi = rsi[-1].value
                    if latest_rsi >= 70:
                        st.warning(f"RSI at {latest_rsi:.0f} - Overbought territory (>70)")
                    elif latest_rsi <= 30:
                        st.success(f"RSI at {latest_rsi:.0f} - Oversold territory (<30)")
                    else:
                        st.info(f"RSI at {latest_rsi:.0f} - Neutral range (30-70)")
            else:
                st.info("Price data not available. Check if Polygon API key is configured.")

        # Quality Tab
        with tab_quality:
            if metrics and metrics.traditional and metrics.traditional.quality:
                q = metrics.traditional.quality

                def quality_indicator(val, good, mid):
                    if val is None:
                        return ""
                    if val >= good:
                        return "🟢"
                    if val >= mid:
                        return "🟡"
                    return "🔴"

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    ind = quality_indicator(q.roic, 0.15, 0.08)
                    st.metric(f"ROIC {ind}", format_pct(q.roic), help="Return on Invested Capital. >15% excellent, 8-15% good")
                with col2:
                    ind = quality_indicator(q.roe, 0.20, 0.10)
                    st.metric(f"ROE {ind}", format_pct(q.roe), help="Return on Equity. >20% excellent (check debt), 10-20% good")
                with col3:
                    ind = quality_indicator(q.gross_margin, 0.60, 0.30)
                    st.metric(f"Gross Margin {ind}", format_pct(q.gross_margin), help="Pricing power indicator. >60% excellent, 30-60% good")
                with col4:
                    ind = quality_indicator(q.operating_margin, 0.20, 0.10)
                    st.metric(f"Op. Margin {ind}", format_pct(q.operating_margin), help="Operating efficiency. >20% excellent")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    ind = quality_indicator(q.net_margin, 0.15, 0.05)
                    st.metric(f"Net Margin {ind}", format_pct(q.net_margin), help="Bottom line profitability")
                with col2:
                    ind = quality_indicator(q.fcf_margin, 0.20, 0.10)
                    st.metric(f"FCF Margin {ind}", format_pct(q.fcf_margin), help="Cash profit per dollar revenue. >20% = cash machine")
                with col3:
                    st.metric("ROA", format_pct(q.roa), help="Return on Assets")
                with col4:
                    st.metric("Asset Turn", format_ratio(q.asset_turnover), help="Revenue efficiency per dollar of assets")

                st.caption("🟢 Excellent  🟡 Good  🔴 Below average")

        # Growth Tab
        with tab_growth:
            if metrics and metrics.traditional and metrics.traditional.growth:
                g = metrics.traditional.growth

                def growth_indicator(val):
                    if val is None:
                        return ""
                    if val >= 0.15:
                        return "🟢"
                    if val >= 0.05:
                        return "🟡"
                    return "🔴"

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    ind = growth_indicator(g.revenue_growth_1y)
                    st.metric(f"Rev Growth 1Y {ind}", format_pct(g.revenue_growth_1y), help="Year-over-year revenue change")
                with col2:
                    ind = growth_indicator(g.revenue_growth_3y_cagr)
                    st.metric(f"Rev CAGR 3Y {ind}", format_pct(g.revenue_growth_3y_cagr), help="3-year compound annual growth rate")
                with col3:
                    ind = growth_indicator(g.revenue_growth_5y_cagr)
                    st.metric(f"Rev CAGR 5Y {ind}", format_pct(g.revenue_growth_5y_cagr), help="5-year compound annual growth rate")
                with col4:
                    ind = growth_indicator(g.earnings_growth_1y)
                    st.metric(f"Earnings 1Y {ind}", format_pct(g.earnings_growth_1y), help="Year-over-year earnings change")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    ind = growth_indicator(g.earnings_growth_3y_cagr)
                    st.metric(f"Earn CAGR 3Y {ind}", format_pct(g.earnings_growth_3y_cagr), help="Should track or exceed revenue growth")
                with col2:
                    ind = growth_indicator(g.fcf_growth_1y)
                    st.metric(f"FCF Growth 1Y {ind}", format_pct(g.fcf_growth_1y), help="Cash flow growth")
                with col3:
                    ind = growth_indicator(g.fcf_growth_3y_cagr)
                    st.metric(f"FCF CAGR 3Y {ind}", format_pct(g.fcf_growth_3y_cagr), help="3-year cash flow growth")

                st.caption("🟢 >15% High growth  🟡 5-15% Moderate  🔴 <5% Slow")

        # Strength Tab
        with tab_strength:
            if metrics and metrics.traditional and metrics.traditional.strength:
                s = metrics.traditional.strength

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    de = s.debt_to_equity
                    ind = "🟢" if de and de < 0.5 else "🟡" if de and de < 1.5 else "🔴" if de else ""
                    st.metric(f"Debt/Equity {ind}", format_ratio(de), help="<0.5 conservative, 0.5-1.5 moderate, >1.5 high leverage")
                with col2:
                    cr = s.current_ratio
                    ind = "🟢" if cr and 1.5 <= cr <= 3 else "🟡" if cr and cr >= 1 else "🔴" if cr else ""
                    st.metric(f"Current Ratio {ind}", format_ratio(cr), help="1.5-3.0 healthy, <1.0 liquidity risk")
                with col3:
                    ic = s.interest_coverage
                    ind = "🟢" if ic and ic > 8 else "🟡" if ic and ic > 3 else "🔴" if ic else ""
                    st.metric(f"Int. Coverage {ind}", f"{ic:.1f}x" if ic else "—", help=">8x very safe, 3-8x adequate, <3x risky")

                st.caption("🟢 Strong  🟡 Adequate  🔴 Watch closely")

        # Valuation Tab
        with tab_valuation:
            if metrics and metrics.traditional and metrics.traditional.valuation:
                v = metrics.traditional.valuation

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    pe = v.pe_ratio
                    ind = "🟢" if pe and 10 <= pe <= 20 else "🟡" if pe and pe <= 40 else "🔴" if pe else ""
                    st.metric(f"P/E {ind}", format_ratio(pe), help="10-20x reasonable, 20-40x growth premium, >40x speculative")
                with col2:
                    st.metric("P/S", format_ratio(v.ps_ratio), help="Price to Sales ratio")
                with col3:
                    st.metric("P/B", format_ratio(v.pb_ratio), help="Price to Book ratio")
                with col4:
                    ev = v.ev_to_ebitda
                    ind = "🟢" if ev and ev < 10 else "🟡" if ev and ev < 15 else "🔴" if ev else ""
                    st.metric(f"EV/EBITDA {ind}", format_ratio(ev), help="<10x cheap, 10-15x fair, >15x premium")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("EV/Sales", format_ratio(v.ev_to_sales), help="Enterprise Value to Sales")
                with col2:
                    fy = v.fcf_yield
                    ind = "🟢" if fy and fy > 0.05 else "🟡" if fy and fy > 0.02 else "🔴" if fy else ""
                    st.metric(f"FCF Yield {ind}", format_pct(fy), help=">5% attractive, 2-5% fair, <2% expensive")
                with col3:
                    ey = v.earnings_yield
                    ind = "🟢" if ey and ey > 0.05 else "🟡" if ey and ey > 0.03 else "🔴" if ey else ""
                    st.metric(f"Earn Yield {ind}", format_pct(ey), help="Inverse of P/E. Higher = cheaper")
                with col4:
                    peg = v.peg_ratio
                    ind = "🟢" if peg and peg < 1 else "🟡" if peg and peg < 2 else "🔴" if peg else ""
                    st.metric(f"PEG {ind}", format_ratio(peg), help="<1 undervalued, 1-2 fair, >2 expensive for growth")

                st.caption("🟢 Attractive  🟡 Fair  🔴 Expensive")

        # News Tab
        with tab_news:
            with st.spinner("Loading news..."):
                news = get_news(ticker, limit=10)

            if news:
                for article in news:
                    time_ago = ""
                    if article.published:
                        delta = date.today() - article.published.date()
                        if delta.days == 0:
                            time_ago = "Today"
                        elif delta.days == 1:
                            time_ago = "Yesterday"
                        else:
                            time_ago = f"{delta.days}d ago"

                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-title">{article.title}</div>
                        <div class="news-meta">{article.publisher_name or 'Unknown'} · {time_ago}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if article.article_url:
                        st.markdown(f"[Read more]({article.article_url})")
                    st.markdown("")
            else:
                st.info("No recent news available.")

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
