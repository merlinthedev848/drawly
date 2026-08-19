# Drawly - Multi-Domain High Probability Analytics & Predictor Suite

**Drawly** is a comprehensive mathematical analytics and prediction suite covering all major high-probability wagering, gaming, and financial domains. Optimized for hosting on **Enhance Host** or any standard web server.

---

## 🌟 Included Predictor Engines

### 🎰 1. UK National Lotto (6/59) & EuroMillions (5+2 Stars)
- Theoretical baseline vs empirical draw rates.
- Hot trend frequency and overdue recency gap tracking (Poisson expectation).
- Chi-Square Goodness-of-Fit test & pair co-occurrence heatmap.

### 🎲 2. Roulette & Casino Probability (`casino_games_engine.py`)
- European (37 pockets) & American (38 pockets) odds breakdown.
- Sector tracking: **Voisins du Zéro**, **Tiers du Cylindre**, and **Orphelins**.
- Dozen recency bias and Red/Black statistical decay.

### 🃏 3. Blackjack & Baccarat Advisor (`casino_games_engine.py`)
- **Blackjack Basic Strategy Matrix Calculator**: Real-time optimal decision engine (Hit, Stand, Double Down, Split) based on Player hand vs Dealer upcard.
- **Baccarat (Punto Banco)**: Expected value breakdown (Banker 1.06% house edge vs Player 1.24%).

### 🐎 4. Horse & Greyhound Racing (`horse_racing_engine.py` & `sports_expanded_engine.py`)
- **Horse Racing**: Form score decay parser, Official Rating (OR) normalization, Course & Distance (C&D) win bonuses, and Fair Odds Value Overlays.
- **Greyhound Racing**: Trap bias (Inside 1-2 vs Outside) & split time analysis.

### ⚽ 5. Football & Tennis Predictor (`football_predictor_engine.py` & `sports_expanded_engine.py`)
- **Football (Poisson xG Engine)**: Expected goals, 1X2 win probabilities, fair odds value edge (+%), Over/Under 2.5 goals, BTTS %, and top 4 correct score matrix.
- **Tennis Match Predictor**: ELO rating, surface specialization (Clay, Grass, Hard), H2H records, and set betting predictions.

### 🏀 6. NBA Basketball Point Spread Engine (`sports_expanded_engine.py`)
- Possessions pace rating, expected score margins, recommended point spread picks, and Over/Under total points picks.

### 📈 7. Stock Explosion Radar (`stock_explosion_engine.py`)
- Composite **Explosion Potential Score (0-100)**: Volume Surge Ratios, YoY Revenue Growth %, Short Squeeze Float %, RSI(14) Momentum, and Upcoming Catalysts.

---

## 🚀 Deployment to Enhance Host

### Direct Static Hosting (Recommended)
1. Log into your **Enhance Control Panel**.
2. Go to **File Manager** -> `public_html`.
3. Upload `public_html/index.html` and `public_html/lotto_data.json`.
4. Open your domain URL in any browser!

---

## 📄 License
MIT License
