"""Portfolio management page."""

import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
import plotly.graph_objects as go

st.set_page_config(
    page_title="Portfolio | Equity Research",
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

    .metric-card {
        background: #fafafa;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }

    .big-number {
        font-size: 2rem;
        font-weight: 600;
        color: #1a1a1a;
    }

    .big-number.positive { color: #2e7d32; }
    .big-number.negative { color: #c62828; }

    .small-label {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    .tier-badge {
        display: inline-block;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        text-align: center;
        line-height: 24px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .tier-1 { background: #e8f5e9; color: #2e7d32; }
    .tier-2 { background: #e3f2fd; color: #1565c0; }
    .tier-3 { background: #fff3e0; color: #ef6c00; }

    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    .recommendation-card {
        background: #fafafa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #1565c0;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = Path("data/portfolio.db")


def get_tracker():
    from src.portfolio import HoldingsTracker
    return HoldingsTracker(DB_PATH)


def get_allocation():
    from src.data import YahooClient
    from src.portfolio import AllocationAnalyzer

    tracker = get_tracker()
    positions = tracker.get_all_positions()

    if not positions:
        return None, None, {}

    client = YahooClient()
    prices = {}

    for pos in positions:
        quote = client.get_quote(pos.ticker)
        if quote:
            prices[pos.ticker] = quote.price

    analyzer = AllocationAnalyzer()
    allocation = analyzer.analyze(tracker, prices)

    return allocation, positions, prices


# Page header
st.markdown('<p class="page-title">Portfolio</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Actions")

    action = st.radio(
        "Select action",
        ["Overview", "Add Position", "Deploy Capital"],
        label_visibility="collapsed",
    )

# Main content
if action == "Overview":
    with st.spinner("Loading portfolio..."):
        allocation, positions, prices = get_allocation()

    if not allocation:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; color: #888;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">💼</div>
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">No positions yet</div>
            <div style="font-size: 0.9rem;">Add your first holding to get started</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Portfolio summary
        total_value = allocation.total_value
        total_cost = allocation.total_cost
        gain_loss = total_value - total_cost
        gain_loss_pct = (gain_loss / total_cost * 100) if total_cost > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="big-number">${total_value:,.0f}</div>
                <div class="small-label">Total Value</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            color_class = "positive" if gain_loss >= 0 else "negative"
            sign = "+" if gain_loss >= 0 else ""
            st.markdown(f"""
            <div class="metric-card">
                <div class="big-number {color_class}">{sign}${gain_loss:,.0f}</div>
                <div class="small-label">Gain/Loss ({sign}{gain_loss_pct:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="big-number">{len(allocation.position_allocations)}</div>
                <div class="small-label">Positions</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="big-number">${total_cost:,.0f}</div>
                <div class="small-label">Cost Basis</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Tier allocation
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("##### Tier Allocation")

            tier_data = []
            for tier, tier_alloc in allocation.tier_allocations.items():
                tier_num = tier.value.replace("tier_", "")
                tier_data.append({
                    "Tier": f"Tier {tier_num}",
                    "Target": tier_alloc.target_pct,
                    "Actual": tier_alloc.actual_pct,
                    "Value": tier_alloc.actual_value,
                })

            colors = ["#2e7d32", "#1565c0", "#ef6c00"]
            values = [t["Value"] for t in tier_data]
            labels = [t["Tier"] for t in tier_data]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker_colors=colors,
                textinfo="percent",
                textposition="outside",
                showlegend=False,
            )])

            fig.update_layout(
                height=200,
                margin=dict(l=20, r=20, t=20, b=20),
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("##### Allocation vs Target")

            for tier_info in tier_data:
                tier_name = tier_info["Tier"]
                target = tier_info["Target"] * 100
                actual = tier_info["Actual"] * 100
                diff = actual - target

                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.markdown(f"**{tier_name}**")
                with col_b:
                    st.markdown(f"Target: {target:.0f}%")
                with col_c:
                    color = "#2e7d32" if abs(diff) < 5 else "#ef6c00" if abs(diff) < 10 else "#c62828"
                    sign = "+" if diff > 0 else ""
                    st.markdown(f"<span style='color: {color};'>Actual: {actual:.0f}% ({sign}{diff:.0f}%)</span>", unsafe_allow_html=True)

        st.markdown("---")

        # Holdings table
        st.markdown("##### Holdings")

        holdings_data = []
        for pos in allocation.position_allocations:
            tier_num = pos.tier.value.replace("tier_", "")
            holdings_data.append({
                "Ticker": pos.ticker,
                "Tier": tier_num,
                "Shares": pos.shares,
                "Cost": pos.cost_basis,
                "Value": pos.current_value,
                "Gain/Loss": f"{pos.gain_loss_pct*100:+.1f}%",
                "Weight": f"{pos.weight_pct*100:.1f}%",
            })

        df = pd.DataFrame(holdings_data)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Cost": st.column_config.NumberColumn("Cost", format="$%.0f"),
                "Value": st.column_config.NumberColumn("Value", format="$%.0f"),
                "Shares": st.column_config.NumberColumn("Shares", format="%.2f"),
            },
            hide_index=True,
        )

elif action == "Add Position":
    st.markdown("##### Add New Position")

    col1, col2 = st.columns(2)

    with col1:
        ticker = st.text_input("Ticker", placeholder="MSFT").upper()
        shares = st.number_input("Shares", min_value=0.01, value=1.0, step=0.1)
        cost = st.number_input("Total Cost ($)", min_value=0.0, value=100.0, step=10.0)

    with col2:
        purchase_date = st.date_input("Purchase Date", value=date.today())
        tier = st.selectbox("Tier", ["1", "2", "3"])
        notes = st.text_input("Notes (optional)")

    st.markdown("---")

    if st.button("Add Position", type="primary"):
        if not ticker:
            st.error("Please enter a ticker")
        else:
            tracker = get_tracker()
            tracker.add_holding(
                ticker=ticker,
                shares=shares,
                cost_basis=cost,
                purchase_date=purchase_date,
                tier=tier,
                notes=notes or None,
            )
            st.success(f"Added {shares} shares of {ticker}")
            st.rerun()

    # Show current holdings preview
    st.markdown("---")
    st.markdown("##### Current Holdings")

    tracker = get_tracker()
    positions = tracker.get_all_positions()

    if positions:
        for pos in positions:
            tier_num = pos.tier.value.replace("tier_", "")
            st.text(f"{pos.ticker}: {pos.total_shares:.2f} shares @ ${pos.cost_per_share:.2f} (Tier {tier_num})")
    else:
        st.caption("No holdings yet")

elif action == "Deploy Capital":
    st.markdown("##### Deploy Capital")
    st.markdown('<p class="page-subtitle">Get recommendations for deploying new capital</p>', unsafe_allow_html=True)

    amount = st.number_input(
        "Amount to deploy ($)",
        min_value=100.0,
        value=1000.0,
        step=100.0,
        label_visibility="collapsed",
    )

    if st.button("Get Recommendations", type="primary"):
        tracker = get_tracker()
        positions = tracker.get_all_positions()

        if not positions:
            st.warning("Add some holdings first to get deployment recommendations")
        else:
            with st.spinner("Analyzing portfolio..."):
                from src.data import YahooClient
                from src.metrics import MetricsCalculator
                from src.portfolio import DeploymentAdvisor
                from src.scoring import UniverseScorer

                client = YahooClient()
                calculator = MetricsCalculator()
                scorer = UniverseScorer()
                advisor = DeploymentAdvisor()

                held_tickers = [p.ticker for p in positions]
                candidate_tickers = list(set(
                    held_tickers + ["AAPL", "MSFT", "GOOGL", "V", "MA", "COST"]
                ))

                prices = {}
                metrics_list = []

                for ticker in candidate_tickers:
                    try:
                        financials = client.get_company_financials(ticker, years=5)
                        if financials:
                            if financials.quote:
                                prices[ticker] = financials.quote.price
                            metrics = calculator.calculate(financials)
                            metrics_list.append(metrics)
                    except Exception:
                        pass

                scores = scorer.score_universe(metrics_list)

                plan = advisor.recommend(
                    capital=amount,
                    tracker=tracker,
                    prices=prices,
                    scores=scores,
                )

            # Display results
            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("To Deploy", f"${plan.total_deployed:,.0f}")
            with col2:
                st.metric("Remaining", f"${plan.remaining_cash:,.0f}")
            with col3:
                st.metric("Recommendations", plan.num_buys)

            if plan.reasoning:
                st.markdown("##### Analysis")
                for reason in plan.reasoning:
                    st.caption(f"• {reason}")

            if plan.recommendations:
                st.markdown("---")
                st.markdown("##### Buy Recommendations")

                for rec in plan.recommendations:
                    tier_num = rec.tier.value.replace("tier_", "")
                    score_str = f"{rec.score:.0f}" if rec.score else "N/A"

                    st.markdown(f"""
                    <div class="recommendation-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 1.1rem; font-weight: 600;">{rec.ticker}</span>
                                <span class="tier-badge tier-{tier_num}" style="margin-left: 0.5rem;">{tier_num}</span>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.25rem; font-weight: 600;">${rec.amount:,.0f}</div>
                                <div style="font-size: 0.8rem; color: #888;">~{rec.shares_estimate:.1f} shares</div>
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;">
                            Score: {score_str} · {rec.reason}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recommendations at this time")
