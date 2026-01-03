# Equity Research System

A sophisticated stock screening and portfolio management system for finding high-quality companies ("compounders") trading at reasonable valuations.

## Overview

This system helps technical investors identify undervalued quality stocks through:

- **Multi-factor Scoring**: Ranks stocks on Quality, Growth, Strength, and Valuation metrics
- **Stage-aware Analysis**: Different scoring weights for Compounders, Mature, Growth, and Speculative companies
- **Value Pick Detection**: Identifies high-quality companies trading at attractive valuations
- **Portfolio Management**: Tier-based allocation with deployment recommendations

## Features

### Universe Screening
- Score and rank S&P 500, Nasdaq 100, and custom stock lists
- 20+ fundamental metrics calculated from financial statements
- Percentile-based ranking against the full universe

### Company Analysis
- Deep-dive into individual stocks with 10-year financial history
- Quality metrics: ROIC, ROE, margins, FCF generation
- Growth metrics: Revenue/earnings CAGR, Rule of 40
- Valuation metrics: P/E, PEG, FCF Yield, EV/EBITDA

### Value Picks
- Quality vs Valuation matrix visualization
- Automatic identification of value picks (high quality + cheap)
- Smart filters to avoid value traps

### Learning Center
- Interactive explanations of all metrics
- Build intuition for stock analysis
- Framework documentation

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - REST API
- **Pandas/Polars** - Data processing
- **SQLite** - Portfolio state
- **Parquet** - Processed data storage

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Charts and visualizations
- **TanStack Query** - Data fetching

### Data Sources
- **Financial Modeling Prep (FMP)** - Primary data source
- **Yahoo Finance** - Fallback/supplementary data

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- FMP API key ([get one here](https://financialmodelingprep.com/developer))

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/muntazirabidi/stock-picker.git
cd stock-picker

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your FMP_API_KEY

# Run the API server
uvicorn api.main:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## Project Structure

```
equity-research/
├── api/                    # FastAPI backend
│   ├── main.py
│   ├── routers/
│   └── schemas.py
├── src/
│   ├── data/              # Data fetching & caching
│   │   ├── fmp_client.py
│   │   ├── universe.py
│   │   └── cache.py
│   ├── metrics/           # Metric calculations
│   │   ├── traditional.py
│   │   ├── growth_stage.py
│   │   └── calculator.py
│   ├── scoring/           # Percentile ranking
│   │   ├── percentile.py
│   │   └── composite.py
│   └── portfolio/         # Portfolio management
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── types/
│   └── package.json
├── data/
│   ├── cache/            # API response cache
│   └── processed/        # Parquet files
└── tests/
```

## Scoring System

### Metrics Categories

| Category | Metrics | Weight (Compounder) |
|----------|---------|---------------------|
| Quality | ROIC, ROE, Margins, FCF Margin | 25% |
| Growth | Revenue CAGR, Earnings Growth | 30% |
| Strength | Current Ratio, Debt/Equity | 15% |
| Valuation | P/E, FCF Yield, EV/EBITDA | 30% |

### Company Stages

- **Compounder**: FCF positive + Revenue growth ≥10%
- **Mature**: FCF positive + Revenue growth <10%
- **Growth**: FCF negative + Gross margin >40%
- **Speculative**: Requires manual review

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/universe/scores` | Get scored universe |
| `GET /api/company/{ticker}` | Full company analysis |
| `GET /api/portfolio/holdings` | Current holdings |
| `POST /api/portfolio/deploy` | Deployment recommendations |

## Configuration

Environment variables (`.env`):

```bash
FMP_API_KEY=your_api_key_here
CACHE_TTL_HOURS=24
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for personal/educational use.

## Acknowledgments

- [Financial Modeling Prep](https://financialmodelingprep.com/) for financial data
- Inspired by value investing principles from Warren Buffett and quality investing frameworks
