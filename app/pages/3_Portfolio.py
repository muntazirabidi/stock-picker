"""Portfolio management page."""

import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Portfolio - Equity Research",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Portfolio Management")
st.markdown("Track holdings, allocation, and get deployment recommendations")

# Database path
DB_PATH = Path("data/portfolio.db")


def get_tracker():
    """Get HoldingsTracker instance."""
    from src.portfolio import HoldingsTracker
    return HoldingsTracker(DB_PATH)


def get_allocation():
    """Get current allocation analysis."""
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


# Sidebar
st.sidebar.header("Portfolio Actions")

action = st.sidebar.radio(
    "Action",
    ["View Status", "Add Holding", "Deploy Capital", "Alerts"],
)

if action == "View Status":
    st.markdown("## Portfolio Status")

    with st.spinner("Loading portfolio..."):
        allocation, positions, prices = get_allocation()

    if not allocation:
        st.warning("No holdings found. Add some positions to get started!")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Value", f"${allocation.total_value:,.0f}")
        with col2:
            st.metric("Total Cost", f"${allocation.total_cost:,.0f}")
        with col3:
            gain_loss = allocation.total_value - allocation.total_cost
            gain_pct = (gain_loss / allocation.total_cost * 100) if allocation.total_cost > 0 else 0
            st.metric(
                "Gain/Loss",
                f"${gain_loss:,.0f}",
                f"{gain_pct:+.1f}%",
            )
        with col4:
            st.metric("Positions", len(allocation.position_allocations))

        st.markdown("---")

        # Tier allocation chart
        st.markdown("### Tier Allocation")

        tier_data = []
        for tier, tier_alloc in allocation.tier_allocations.items():
            tier_name = tier.value.replace("tier_", "Tier ")
            tier_data.append({
                "Tier": tier_name,
                "Target %": tier_alloc.target_pct * 100,
                "Actual %": tier_alloc.actual_pct * 100,
                "Value": tier_alloc.actual_value,
            })

        tier_df = pd.DataFrame(tier_data)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                tier_df,
                values="Value",
                names="Tier",
                title="Current Allocation",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=tier_df["Tier"],
                y=tier_df["Target %"],
                name="Target",
                marker_color="lightblue",
            ))
            fig.add_trace(go.Bar(
                x=tier_df["Tier"],
                y=tier_df["Actual %"],
                name="Actual",
                marker_color="steelblue",
            ))
            fig.update_layout(
                title="Target vs Actual Allocation",
                barmode="group",
                yaxis_title="Percentage",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Holdings table
        st.markdown("### Holdings")

        holdings_data = []
        for pos in allocation.position_allocations:
            holdings_data.append({
                "Ticker": pos.ticker,
                "Tier": pos.tier.value.replace("tier_", ""),
                "Shares": f"{pos.shares:.2f}",
                "Cost": f"${pos.cost_basis:,.0f}",
                "Value": f"${pos.current_value:,.0f}",
                "Gain/Loss": f"{pos.gain_loss_pct*100:+.1f}%",
                "Weight": f"{pos.weight_pct*100:.1f}%",
            })

        holdings_df = pd.DataFrame(holdings_data)
        st.dataframe(holdings_df, use_container_width=True)

elif action == "Add Holding":
    st.markdown("## Add New Holding")

    with st.form("add_holding"):
        col1, col2 = st.columns(2)

        with col1:
            ticker = st.text_input("Ticker", max_chars=10).upper()
            shares = st.number_input("Shares", min_value=0.01, value=1.0, step=0.1)
            cost = st.number_input("Total Cost ($)", min_value=0.0, value=100.0, step=10.0)

        with col2:
            purchase_date = st.date_input("Purchase Date", value=date.today())
            tier = st.selectbox("Tier", ["1", "2", "3"])
            notes = st.text_input("Notes (optional)")

        submitted = st.form_submit_button("Add Holding", type="primary")

        if submitted:
            if not ticker:
                st.error("Please enter a ticker symbol")
            else:
                try:
                    tracker = get_tracker()
                    tracker.add_holding(
                        ticker=ticker,
                        shares=shares,
                        cost_basis=cost,
                        purchase_date=purchase_date,
                        tier=tier,
                        notes=notes or None,
                    )
                    st.success(f"Added {shares} shares of {ticker} (Tier {tier})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding holding: {e}")

    # Current holdings preview
    st.markdown("---")
    st.markdown("### Current Holdings")

    tracker = get_tracker()
    positions = tracker.get_all_positions()

    if positions:
        for pos in positions:
            tier_num = pos.tier.value.replace("tier_", "")
            st.text(f"{pos.ticker}: {pos.total_shares:.2f} shares @ ${pos.cost_per_share:.2f} (Tier {tier_num})")
    else:
        st.info("No holdings yet")

elif action == "Deploy Capital":
    st.markdown("## Deploy Capital")

    amount = st.number_input(
        "Amount to Deploy ($)",
        min_value=100.0,
        value=1000.0,
        step=100.0,
    )

    if st.button("Get Recommendations", type="primary"):
        with st.spinner("Analyzing portfolio and generating recommendations..."):
            from src.data import YahooClient
            from src.metrics import MetricsCalculator
            from src.portfolio import DeploymentAdvisor
            from src.scoring import UniverseScorer

            tracker = get_tracker()
            positions = tracker.get_all_positions()

            if not positions:
                st.warning("No existing positions. Add holdings first.")
            else:
                client = YahooClient()
                calculator = MetricsCalculator()
                scorer = UniverseScorer()
                advisor = DeploymentAdvisor()

                # Get held tickers + some candidates
                held_tickers = [p.ticker for p in positions]
                candidate_tickers = list(set(
                    held_tickers +
                    ["AAPL", "MSFT", "GOOGL", "AMZN", "V", "MA", "COST", "HUBS"]
                ))

                prices = {}
                metrics_list = []

                progress = st.progress(0)
                for i, ticker in enumerate(candidate_tickers):
                    progress.progress((i + 1) / len(candidate_tickers))
                    try:
                        financials = client.get_company_financials(ticker, years=5)
                        if financials:
                            if financials.quote:
                                prices[ticker] = financials.quote.price
                            metrics = calculator.calculate(financials)
                            metrics_list.append(metrics)
                    except Exception:
                        pass

                progress.empty()

                scores = scorer.score_universe(metrics_list)

                plan = advisor.recommend(
                    capital=amount,
                    tracker=tracker,
                    prices=prices,
                    scores=scores,
                )

                # Display plan
                st.markdown("---")
                st.markdown(f"### Deployment Plan for ${amount:,.0f}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("To Deploy", f"${plan.total_deployed:,.0f}")
                with col2:
                    st.metric("Remaining", f"${plan.remaining_cash:,.0f}")
                with col3:
                    st.metric("# of Buys", plan.num_buys)

                if plan.reasoning:
                    st.markdown("**Reasoning:**")
                    for reason in plan.reasoning:
                        st.markdown(f"- {reason}")

                if plan.recommendations:
                    st.markdown("### Recommendations")

                    for rec in plan.recommendations:
                        tier_num = rec.tier.value.replace("tier_", "")
                        score_str = f"{rec.score:.0f}" if rec.score else "N/A"

                        with st.container():
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                            with col1:
                                st.markdown(f"**{rec.ticker}** (Tier {tier_num})")
                            with col2:
                                st.metric("Amount", f"${rec.amount:,.0f}")
                            with col3:
                                st.metric("Score", score_str)
                            with col4:
                                st.caption(rec.reason)
                        st.markdown("---")
                else:
                    st.info("No recommendations generated. All positions may be at target allocation.")

elif action == "Alerts":
    st.markdown("## Portfolio Alerts")

    with st.spinner("Checking for alerts..."):
        allocation, positions, prices = get_allocation()

        if not allocation:
            st.warning("No holdings found. Add some positions to get started!")
        else:
            from src.data import YahooClient
            from src.metrics import MetricsCalculator
            from src.portfolio import AlertGenerator
            from src.scoring import UniverseScorer

            client = YahooClient()
            calculator = MetricsCalculator()
            scorer = UniverseScorer()
            alert_gen = AlertGenerator()

            # Score held positions
            metrics_list = []
            for pos in positions:
                try:
                    financials = client.get_company_financials(pos.ticker, years=5)
                    if financials:
                        metrics_list.append(calculator.calculate(financials))
                except Exception:
                    pass

            scores = scorer.score_universe(metrics_list)

            alerts = alert_gen.generate_all_alerts(
                allocation=allocation,
                current_scores=scores,
                previous_scores=None,
            )

            if not alerts:
                st.success("No alerts - portfolio looks healthy!")
            else:
                # Group by severity
                critical = [a for a in alerts if a.severity.value == "critical"]
                warnings = [a for a in alerts if a.severity.value == "warning"]
                info = [a for a in alerts if a.severity.value == "info"]

                if critical:
                    st.markdown("### 🚨 Critical")
                    for alert in critical:
                        st.error(f"**{alert.ticker or 'Portfolio'}**: {alert.message}")
                        if alert.details:
                            st.caption(alert.details)
                        if alert.action_suggested:
                            st.info(f"Suggested: {alert.action_suggested}")

                if warnings:
                    st.markdown("### ⚠️ Warnings")
                    for alert in warnings:
                        st.warning(f"**{alert.ticker or 'Portfolio'}**: {alert.message}")
                        if alert.details:
                            st.caption(alert.details)
                        if alert.action_suggested:
                            st.info(f"Suggested: {alert.action_suggested}")

                if info:
                    st.markdown("### ℹ️ Info")
                    for alert in info:
                        st.info(f"**{alert.ticker or 'Portfolio'}**: {alert.message}")
                        if alert.details:
                            st.caption(alert.details)
