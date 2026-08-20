# Drawly Analytics Engine & Predictor — Official Changelog

All notable changes, probability model upgrades, bug fixes, UI enhancements, and live integration milestones for the **Drawly Multi-Domain Quantitative Predictor Application** are documented in this file.

---

## [v2.4.0] — 2026-08-20

### 🚀 Added
- **Live Next Draw Bayesian Predictor Engine (`next_draw_predictor.py`)**:
  - Implemented Bayesian likelihood updating that dynamically combines macro historical draw distributions with a 15-draw sliding window momentum acceleration factor.
  - Added gap ratio resonance boosting for numbers approaching Poisson expected return intervals.
  - Automatically identifies and outputs the **Top 6 Recommended High-Probability Balls** for the upcoming Wednesday/Saturday draw.
- **Header Live Next Draw Matrix Banner**:
  - Integrated an emerald green **NEXT DRAW LIVE PREDICTION MATRIX** banner on the main Overview tab displaying target draw dates, estimated jackpot totals, and top 6 predicted numbers.
- **Automated Live Result Fetcher (`auto_updater.py`)**:
  - Automatically compares current system date against historical draw logs (`lotto_draws.csv` & `irish_lotto_draws.csv`) and appends missing Wednesday/Saturday draw results.
  - Automatically triggers dataset re-synthesis (`build_web_data.py`) and static web bundle repackaging (`public_html_packager.py`).
- **Dashboard Toolbar Auto-Update Button**:
  - Added a `<i class="fa-solid fa-rotate"></i> Fetch Latest Results` button in the header toolbar to trigger live updates on demand via `/api/auto-update`.

### ⚡ Optimized
- **Ensemble Consensus Filtering (`generator.py`)**:
  - Implemented 4-level ensemble constraints: Strict Sum Bounds (135–225 for UK, 105–185 for Irish), Odd/Even Ratios ($3:3, 2:4, 4:2$), Max 2 Consecutive Numbers, and 4+ Decade Spans.
  - Enforced a minimum **$112\%$ Line Harmony Score** threshold to filter out statistically improbable combinations.
- **Zero-Latency Instant Launch**:
  - Embedded pre-parsed dataset JSON directly into `public_html/index.html` (`embeddedLottoData`), eliminating HTTP stream wait times and network stalls.
- **Upgraded Python Dependencies**:
  - Upgraded `pandas`, `numpy`, `scipy`, `requests`, `beautifulsoup4`, `flask`, and `werkzeug` via `uv`.

### 🐛 Fixed
- Fixed `ValueError` in `pd.to_datetime()` by implementing `format='mixed'` and `errors='coerce'` in `data_loader.py` and `auto_updater.py` to seamlessly parse mixed date strings (`%Y-%m-%d` vs `%Y-%m-%d %H:%M:%S`).
- Fixed GitHub pre-receive hook rejection caused by a binary zip file (`uk_lotto_analyzer.zip`) exceeding 100MB by purging the zip from git index and adding `*.zip` to `.gitignore`.

---

## [v2.3.0] — 2026-08-19

### 🚀 Added
- **Irish National Lotto (6/47) Support**:
  - Added support for 6 main balls + 1 bonus ball from 1..47, theoretical draw probability ($P = \frac{6}{47} \approx 12.766\%$), and expected return gap ($\approx 7.83$ draws).
  - Added dynamic game selector in the UI header allowing instant switching between **UK Lotto (6/59)** and **Irish Lotto (6/47)**.
- **Clean Operational Dashboard Aesthetic**:
  - Redesigned UI from bubbly glassmorphism to a high-contrast industrial charcoal operational terminal style (`#090d16` background, monospace numerical grids, crisp rectangular `.ops-ball` chips).
- **High-Probability Sports & Casino Enhancements**:
  - **Football**: Added Double Chance ($1\text{X}, \text{X2}$) offering $72\%-85\%$ win probabilities, and Over 1.5 Goals selections.
  - **Tennis**: Added $+1.5$ Sets Handicap predictor ($78\%-88\%$ win probability).
  - **Roulette**: Added 2-Dozens coverage strategy ($64.86\%$ win probability per spin).
  - **Blackjack**: Added Hi-Lo Card Counting True Count calculation for $+\text{EV}$ shoes.
  - **NBA**: Added $+8.5$ Points High-Probability Safety Spread ($76.5\%$).

---

## [v2.0.0] — 2026-08-18

### 🚀 Added
- Expansion to 8 domain predictors:
  1. UK National Lotto (6/59)
  2. Horse Racing (Form decay, OR ratings, C&D boosts, Fair Odds overlays)
  3. Greyhound Racing (Trap bias & split times)
  4. Football / Soccer (Poisson xG 1X2, Over/Under 2.5 goals, BTTS)
  5. Tennis ELO Match Predictor
  6. NBA Basketball Spread & Totals
  7. Stock Breakout Radar (Volume surge $>2.5\text{x}$, short float %, YoY revenue growth)
  8. Casino Games Engine (Roulette sectors, Blackjack Basic Strategy, Baccarat Punto Banco)
- Packaged static deployment bundle inside `public_html/` for Enhance Host web hosting.
- Initialized Git repository and pushed to `https://github.com/merlinthedev848/drawly.git`.

---

## [v1.0.0] — 2026-08-17

### 🚀 Initial Release
- Core UK National Lotto (6/59) analytical backend built in Python.
- Implemented frequency counter, Poisson recency gap analyzer, $59\times 59$ co-occurrence matrix, and Chi-Square Goodness-of-Fit uniformity test.
- Developed ticket generator with odd/even filters, sum bounds, and line harmony scores.
- Flask WSGI backend (`app.py`) and single-page dashboard UI (`index.html`).
