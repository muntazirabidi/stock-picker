"""Educational content and metric definitions."""

import streamlit as st

st.set_page_config(
    page_title="Learn | Equity Research",
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

    .metric-def {
        background: #fafafa;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-left: 3px solid #1565c0;
    }

    .metric-name {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }

    .metric-formula {
        font-family: monospace;
        font-size: 0.85rem;
        background: #1565c0;
        color: #ffffff;
        padding: 0.35rem 0.75rem;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 0.5rem;
    }

    .metric-desc {
        font-size: 0.9rem;
        color: #333333;
        line-height: 1.6;
    }

    .interpretation {
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid #eee;
    }

    .good { color: #2e7d32; }
    .caution { color: #ef6c00; }
    .bad { color: #c62828; }

    .stage-card {
        background: #fafafa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .stage-card p {
        color: #333333;
        margin-bottom: 0.5rem;
    }

    .stage-card strong {
        color: #1a1a1a;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown('<p class="page-title">Learn</p>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Understand the metrics and how to interpret your results</p>', unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("### Topics")
    topic = st.radio(
        "Select topic",
        ["Scoring System", "Quality Metrics", "Growth Metrics", "Strength Metrics", "Valuation Metrics", "Company Stages"],
        label_visibility="collapsed",
    )

if topic == "Scoring System":
    st.markdown("## How Scoring Works")

    st.markdown("""
    The composite score (0-100) ranks each stock relative to others in the universe.
    It's **not** an absolute measure—a score of 70 means the stock ranks better than
    ~70% of peers on the metrics we track.
    """)

    st.markdown("### Score Interpretation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-def" style="border-left-color: #2e7d32;">
            <div class="metric-name good">60+ : Strong</div>
            <div class="metric-desc">
                Top third of universe. High quality with solid fundamentals.
                Consider for core positions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-def" style="border-left-color: #ef6c00;">
            <div class="metric-name caution">40-60 : Average</div>
            <div class="metric-desc">
                Middle of the pack. May have strengths in some areas
                but weaknesses in others. Dig deeper.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-def" style="border-left-color: #c62828;">
            <div class="metric-name bad">Below 40 : Weak</div>
            <div class="metric-desc">
                Below average on most metrics. May be turnaround
                situation or value trap. Proceed with caution.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Category Weights")

    st.markdown("""
    The composite score combines four categories. Weights vary by company stage:

    | Category | Mature | Compounder | Growth |
    |----------|--------|------------|--------|
    | **Quality** | 35% | 25% | 30%* |
    | **Growth** | 15% | 30% | 25%* |
    | **Strength** | 25% | 15% | 20%* |
    | **Valuation** | 25% | 30% | 25%* |

    *Growth companies use different metrics (Rule of 40, SBC, etc.)
    """)

    st.info("""
    **Key insight**: A high-growth company shouldn't be penalized for low FCF margins
    if it's efficiently reinvesting. That's why we score by stage.
    """)

elif topic == "Quality Metrics":
    st.markdown("## Quality Metrics")
    st.markdown("*Measures how efficiently a company generates profits*")

    st.markdown("---")

    # ROIC
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">ROIC — Return on Invested Capital</div>
        <div class="metric-formula">NOPAT / (Equity + Debt - Cash)</div>
        <div class="metric-desc">
            The most important quality metric. Shows how much profit a company generates
            for every dollar invested in the business. Measures true economic profitability
            regardless of capital structure.
        </div>
        <div class="interpretation">
            <span class="good">● >15% = Excellent</span> — Strong competitive advantage<br>
            <span class="caution">● 8-15% = Good</span> — Solid business, covers cost of capital<br>
            <span class="bad">● <8% = Poor</span> — May not earn cost of capital
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ROE
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">ROE — Return on Equity</div>
        <div class="metric-formula">Net Income / Shareholders' Equity</div>
        <div class="metric-desc">
            Profit generated per dollar of shareholder equity. High ROE can come from
            genuine profitability OR from high leverage—always check debt levels too.
        </div>
        <div class="interpretation">
            <span class="good">● >20% = Excellent</span> — If with low debt<br>
            <span class="caution">● 10-20% = Good</span> — Typical for quality companies<br>
            <span class="bad">● <10% = Below average</span> — Unless very low debt
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Gross Margin
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">Gross Margin</div>
        <div class="metric-formula">(Revenue - COGS) / Revenue</div>
        <div class="metric-desc">
            How much of each revenue dollar is left after direct costs. High gross margins
            indicate pricing power, differentiation, or low-cost production. Very stable
            over time for quality businesses.
        </div>
        <div class="interpretation">
            <span class="good">● >60% = Excellent</span> — Software, luxury, pharma<br>
            <span class="caution">● 30-60% = Good</span> — Most quality businesses<br>
            <span class="bad">● <30% = Low</span> — Commodity business, intense competition
        </div>
    </div>
    """, unsafe_allow_html=True)

    # FCF Margin
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">FCF Margin — Free Cash Flow Margin</div>
        <div class="metric-formula">Free Cash Flow / Revenue</div>
        <div class="metric-desc">
            Cash profit per dollar of revenue. Unlike earnings, FCF is hard to manipulate.
            This is real cash the company can use for dividends, buybacks, acquisitions,
            or debt paydown.
        </div>
        <div class="interpretation">
            <span class="good">● >20% = Excellent</span> — Cash machine<br>
            <span class="caution">● 10-20% = Good</span> — Healthy cash generation<br>
            <span class="bad">● <10% = Low</span> — May need lots of reinvestment
        </div>
    </div>
    """, unsafe_allow_html=True)

elif topic == "Growth Metrics":
    st.markdown("## Growth Metrics")
    st.markdown("*Measures how fast the company is expanding*")

    st.markdown("---")

    # Revenue CAGR
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">Revenue CAGR — Compound Annual Growth Rate</div>
        <div class="metric-formula">((End Value / Start Value)^(1/years)) - 1</div>
        <div class="metric-desc">
            Smoothed annual growth rate. More reliable than year-over-year because it
            accounts for volatility. We track 1Y, 3Y, and 5Y CAGRs.
        </div>
        <div class="interpretation">
            <span class="good">● >15% = High growth</span> — Growing faster than economy<br>
            <span class="caution">● 5-15% = Moderate</span> — Solid, sustainable growth<br>
            <span class="bad">● <5% = Slow</span> — Mature or struggling
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Rule of 40
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">Rule of 40 (Growth Companies)</div>
        <div class="metric-formula">Revenue Growth % + FCF Margin %</div>
        <div class="metric-desc">
            SaaS/tech metric balancing growth vs profitability. A company growing 50% with
            -10% margins (score: 40) is as healthy as one growing 20% with 20% margins
            (score: 40). Higher is better.
        </div>
        <div class="interpretation">
            <span class="good">● >40 = Excellent</span> — Best-in-class SaaS<br>
            <span class="caution">● 20-40 = Good</span> — Healthy balance<br>
            <span class="bad">● <20 = Concerning</span> — Neither growing fast nor profitable
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Earnings Growth
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">Earnings Growth</div>
        <div class="metric-formula">Change in EPS over time</div>
        <div class="metric-desc">
            Should roughly track revenue growth for quality companies. If earnings grow
            faster than revenue, margins are expanding (good). If slower, margins are
            compressing (investigate why).
        </div>
        <div class="interpretation">
            <span class="good">● > Revenue growth</span> — Margin expansion<br>
            <span class="caution">● = Revenue growth</span> — Stable margins<br>
            <span class="bad">● < Revenue growth</span> — Margin pressure
        </div>
    </div>
    """, unsafe_allow_html=True)

elif topic == "Strength Metrics":
    st.markdown("## Financial Strength")
    st.markdown("*Measures balance sheet health and risk*")

    st.markdown("---")

    # Debt/Equity
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">Debt-to-Equity Ratio</div>
        <div class="metric-formula">Total Debt / Shareholders' Equity</div>
        <div class="metric-desc">
            How much the company relies on debt vs equity financing. Low debt = more
            flexibility, survives downturns. High debt = amplified returns but also
            amplified risk.
        </div>
        <div class="interpretation">
            <span class="good">● <0.5 = Conservative</span> — Strong balance sheet<br>
            <span class="caution">● 0.5-1.5 = Moderate</span> — Acceptable for stable businesses<br>
            <span class="bad">● >1.5 = High leverage</span> — Risky in downturns
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Current Ratio
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">Current Ratio</div>
        <div class="metric-formula">Current Assets / Current Liabilities</div>
        <div class="metric-desc">
            Can the company pay its bills due within a year? Measures short-term
            liquidity. Too low = cash crunch risk. Too high = inefficient use of cash.
        </div>
        <div class="interpretation">
            <span class="good">● 1.5-3.0 = Healthy</span> — Comfortable liquidity<br>
            <span class="caution">● 1.0-1.5 = Adequate</span> — Watch closely<br>
            <span class="bad">● <1.0 = Danger</span> — May struggle to pay bills
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interest Coverage
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">Interest Coverage</div>
        <div class="metric-formula">EBIT / Interest Expense</div>
        <div class="metric-desc">
            How many times over can the company pay its interest? Critical for
            companies with debt. Low coverage means a small earnings decline could
            cause a debt crisis.
        </div>
        <div class="interpretation">
            <span class="good">● >8x = Very safe</span> — Interest is trivial<br>
            <span class="caution">● 3-8x = Adequate</span> — Can handle normal volatility<br>
            <span class="bad">● <3x = Risky</span> — Debt burden is heavy
        </div>
    </div>
    """, unsafe_allow_html=True)

elif topic == "Valuation Metrics":
    st.markdown("## Valuation Metrics")
    st.markdown("*Measures what you're paying for the business*")

    st.markdown("---")

    # P/E
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">P/E — Price to Earnings</div>
        <div class="metric-formula">Stock Price / Earnings Per Share</div>
        <div class="metric-desc">
            Years of current earnings to "pay back" your investment. Most common
            valuation metric but easily manipulated via accounting. Compare within
            same industry only.
        </div>
        <div class="interpretation">
            <span class="good">● 10-20x = Reasonable</span> — For stable earners<br>
            <span class="caution">● 20-40x = Growth premium</span> — Better be growing fast<br>
            <span class="bad">● >40x or negative</span> — Speculative or unprofitable
        </div>
    </div>
    """, unsafe_allow_html=True)

    # FCF Yield
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">FCF Yield — Free Cash Flow Yield</div>
        <div class="metric-formula">Free Cash Flow / Market Cap</div>
        <div class="metric-desc">
            The "earnings yield" but with real cash. If FCF yield is 5%, you're getting
            $5 of cash generation for every $100 invested. Higher = cheaper stock.
            Think of it like a bond yield.
        </div>
        <div class="interpretation">
            <span class="good">● >5% = Attractive</span> — Good cash return on price<br>
            <span class="caution">● 2-5% = Fair</span> — Typical for quality companies<br>
            <span class="bad">● <2% = Expensive</span> — Priced for perfection
        </div>
    </div>
    """, unsafe_allow_html=True)

    # EV/EBITDA
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">EV/EBITDA</div>
        <div class="metric-formula">Enterprise Value / EBITDA</div>
        <div class="metric-desc">
            Enterprise value accounts for debt, so it's better for comparing companies
            with different capital structures. Lower = cheaper. Commonly used in M&A
            to value businesses.
        </div>
        <div class="interpretation">
            <span class="good">● <10x = Cheap</span> — May be undervalued<br>
            <span class="caution">● 10-15x = Fair</span> — Typical for quality<br>
            <span class="bad">● >15x = Premium</span> — High expectations baked in
        </div>
    </div>
    """, unsafe_allow_html=True)

    # PEG
    st.markdown("""
    <div class="metric-def">
        <div class="metric-name">PEG — Price/Earnings to Growth</div>
        <div class="metric-formula">P/E Ratio / Earnings Growth Rate</div>
        <div class="metric-desc">
            Adjusts P/E for growth rate. A P/E of 30 with 30% growth (PEG=1) is "fair."
            P/E of 30 with 15% growth (PEG=2) is expensive. Useful for comparing
            companies with different growth rates.
        </div>
        <div class="interpretation">
            <span class="good">● <1 = Undervalued</span> — Growth not fully priced<br>
            <span class="caution">● 1-2 = Fair</span> — Reasonable for growers<br>
            <span class="bad">● >2 = Expensive</span> — Better have a moat
        </div>
    </div>
    """, unsafe_allow_html=True)

elif topic == "Company Stages":
    st.markdown("## Company Lifecycle Stages")
    st.markdown("*Why we score different companies differently*")

    st.markdown("---")

    st.markdown("""
    <div class="stage-card" style="border-left: 4px solid #2e7d32;">
        <h4 style="color: #2e7d32; margin-bottom: 0.5rem;">Mature</h4>
        <p><strong>Characteristics:</strong> Positive FCF, <10% revenue growth, established market position</p>
        <p><strong>Examples:</strong> Johnson & Johnson, Coca-Cola, Procter & Gamble</p>
        <p><strong>What matters:</strong> Dividend safety, capital returns, margin stability, balance sheet</p>
        <p><strong>Scoring focus:</strong> Heavy weight on quality (35%) and strength (25%).
        Growth matters less—we want consistency and cash returns.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stage-card" style="border-left: 4px solid #1565c0;">
        <h4 style="color: #1565c0; margin-bottom: 0.5rem;">Compounder</h4>
        <p><strong>Characteristics:</strong> Positive FCF AND 10%+ growth. The holy grail.</p>
        <p><strong>Examples:</strong> Microsoft, Visa, Costco, ASML</p>
        <p><strong>What matters:</strong> Can they sustain both growth AND profitability? Moat durability.</p>
        <p><strong>Scoring focus:</strong> Balanced weights. Growth (30%) and valuation (30%) are key
        because we're paying a premium for growth that needs to materialize.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stage-card" style="border-left: 4px solid #ef6c00;">
        <h4 style="color: #ef6c00; margin-bottom: 0.5rem;">Growth</h4>
        <p><strong>Characteristics:</strong> High growth (>20%), negative or low FCF, reinvesting aggressively</p>
        <p><strong>Examples:</strong> Snowflake, CrowdStrike (early), Datadog</p>
        <p><strong>What matters:</strong> Rule of 40, gross margins, net revenue retention, path to profitability</p>
        <p><strong>Scoring focus:</strong> Traditional metrics don't work. We use Rule of 40, unit economics,
        and SBC dilution. High gross margins (>70%) are crucial—shows eventual profitability potential.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stage-card" style="border-left: 4px solid #c62828;">
        <h4 style="color: #c62828; margin-bottom: 0.5rem;">Speculative</h4>
        <p><strong>Characteristics:</strong> Doesn't fit other categories. Turnarounds, cyclicals, unproven models.</p>
        <p><strong>Examples:</strong> Early biotech, SPACs, distressed situations</p>
        <p><strong>What matters:</strong> Case-by-case analysis. Score is less meaningful.</p>
        <p><strong>Scoring focus:</strong> Equal weights across all categories. Treat scores as rough
        guidance only—these need deep individual research.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.info("""
    **Portfolio tip**: A healthy portfolio has mostly Compounders (Tier 1-2) with some
    Mature for stability and a small allocation to Growth for upside. Avoid heavy
    concentration in Speculative unless you've done deep research.
    """)
