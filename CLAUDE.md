# Equity Research System

## Project Overview
Multi-universe stock screening and portfolio management system for finding high-quality growth companies ("compounders") before they become mega-caps.

## Owner Profile
- Technical investor (PhD physics, AI/ML professional)
- Long time horizon: 5-10 years
- Monthly deployment: £1000-2000
- Edge: Can build sophisticated systems, understand statistics

## Architecture

### Universe Tiers
1. **Tier 1 - Established Compounders (60%)**: S&P 500 + S&P 400 MidCap, >$10B market cap
2. **Tier 2 - High Growth (30%)**: Russell 1000 Growth, Nasdaq 100 non-mega-caps, $2B-$50B
3. **Tier 3 - Opportunistic (10%)**: International ADRs, spinoffs, manual watchlist

### Stage-Aware Scoring
Companies are classified by lifecycle stage and scored with appropriate metrics:
- **Mature**: Traditional metrics (ROIC, FCF margins, stability)
- **Compounder**: Blend of quality and growth metrics
- **Growth**: Unit economics, Rule of 40, runway, dilution
- **Speculative**: Flagged for manual review

### Tech Stack
- Python 3.11+
- Data: pandas, SQLite, parquet
- API: requests, aiohttp (parallel fetching)
- UI: Streamlit
- Caching: file-based with TTL
- Validation: pydantic
- Testing: pytest

### Primary Data Source
Financial Modeling Prep (FMP) API - requires API key in environment variable `FMP_API_KEY`

## Directory Structure
```
equity-research/
├── src/
│   ├── data/           # FMP client, universe loaders, caching
│   ├── metrics/        # Traditional + growth-stage metrics
│   ├── scoring/        # Percentile ranking, composite scores
│   ├── portfolio/      # Holdings, allocation, deployment
│   └── cli.py
├── app/                # Streamlit UI
├── data/
│   ├── cache/          # API response cache
│   ├── processed/      # Parquet files
│   └── portfolio.db    # SQLite for holdings
├── tests/
├── watchlist.csv       # Manual stock additions
└── holdings.csv        # Current portfolio
```

## Key Commands
```bash
# Full pipeline refresh
python -m src.cli refresh --universe all

# Score specific tickers
python -m src.cli score HUBS FICO COST

# Monthly deployment recommendation
python -m src.cli deploy --amount 1000

# Portfolio status with alerts
python -m src.cli portfolio --alerts

# Run Streamlit UI
streamlit run app/streamlit_app.py
```

## Development Guidelines
- Cache all API responses aggressively (FMP has rate limits)
- Use batch endpoints where available
- All metrics calculations must have test coverage
- Parquet for processed data, SQLite for portfolio state
- Type hints required, pydantic models for data validation

## Build Phases
1. **Phase 1**: Data foundation - FMP client, universe loaders, caching
2. **Phase 2**: Metrics engine - traditional + growth metrics, stage classification
3. **Phase 3**: Scoring - percentile ranking, composite scores
4. **Phase 4**: Portfolio logic - holdings, allocation, deployment recommendations
5. **Phase 5**: CLI interface
6. **Phase 6**: Streamlit UI
