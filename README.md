# Drawly - Multi-Domain Logical Analytics & Predictor Suite

**Drawly** is an analytical suite combining mathematical probability models for **UK National Lottery (Lotto 6/59)**, **Horse Racing Value Ratings**, **High-Growth Stock Explosion Radar**, and **Football Match Predictor (Poisson xG Engine)**. Optimized for hosting on **Enhance Host** or any standard web server.

---

## 🌟 Modules & Features

### 🎰 1. UK National Lotto (6/59 Matrix)
- **Theoretical vs. Empirical Odds Engine**: Baseline odds (\(10.169\%\)) vs empirical frequency rates.
- **Hot & Overdue Recency Gaps**: Tracks draw gaps relative to Poisson expected return intervals (\(\approx 9.83\) draws).
- **Chi-Square Goodness-of-Fit Test**: Evaluates statistical uniform random noise vs empirical trend deviations.
- **Pair Co-occurrence Matrix**: 59x59 affinity matrix for pair co-occurrences.
- **Logical Ticket Generator**: Generates 6-number lines with sum bounds, odd/even balance checks, and line harmony score breakdowns.

### 🐎 2. Horse Racing Predictor & Value Engine
- **Composite Rating Engine**: Combines Recent Form, Official Rating (OR), Course & Distance (C&D) compatibility, and Jockey/Trainer strike rates.
- **Fair Odds & Value Overlays**: Calculates true fair odds (\(1 / P_{\text{win}}\)) and flags **High Value Overlays**.
- **Forecast & Trifecta Generator**: Produces Straight Forecast (1st & 2nd) and Combination Trifecta suggestions.

### 📈 3. Stock Explosion Radar
- **Explosion Potential Index (0-100)**: Evaluates Volume Surge Ratios, YoY Revenue Growth %, Short Squeeze Float %, RSI(14) Momentum, and Upcoming Catalysts.
- **Breakout Scanner**: Highlights high-conviction momentum stocks and projected target upside %.

### ⚽ 4. Football Match Predictor (Soccer Betting Engine)
- **Poisson Expected Goals (xG)**: Models Home & Away attack vs defense ratings.
- **1X2 Probabilities & Fair Odds**: Calculates Home Win, Draw, and Away Win probabilities vs bookmaker odds.
- **Over/Under 2.5 & BTTS**: Computes match goal expectations and top 4 correct score probabilities.

---

## 🚀 Quick Deployment to Enhance Host

### Option A: Direct Static Hosting (Recommended)
1. Log into your **Enhance Control Panel**.
2. Go to **File Manager** -> `public_html`.
3. Upload `public_html/index.html` and `public_html/lotto_data.json`.
4. Open your domain URL in any browser!

### Option B: Python WSGI / Flask App
1. In Enhance Panel, create a **Python Application**.
2. Upload the repository files.
3. Set entry point to `app:app`.

---

## 📄 License
MIT License
