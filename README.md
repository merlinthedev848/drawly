# Drawly - UK National Lotto & Horse Racing Logical Analyzer

**Drawly** is a mathematical probability analyzer and logical line generator for the **UK National Lottery (Lotto 6/59)** and **Horse Racing Value Predictor**, optimized for hosting on **Enhance Host** or any standard web server.

---

## 🌟 Key Features

### 🎰 UK National Lotto (6/59 Matrix)
- **Theoretical vs. Empirical Odds Engine**: Theoretical baseline (\(P(X) = \frac{6}{59} \approx 10.169\%\)) compared against empirical frequency rates.
- **Hot & Overdue Recency Gaps**: Tracks draw gap counts relative to expected Poisson return intervals (\(\approx 9.83\) draws).
- **Chi-Square Goodness-of-Fit Test**: Assesses statistical uniform random noise vs empirical trends.
- **Pair Co-occurrence Matrix**: 59x59 affinity matrix identifying numbers drawn together most frequently.
- **Logical Ticket Generator**: Generates 6-number lines with sum filtering, odd/even balance checks, and line harmony score breakdowns.

### 🐎 Horse Racing Predictor & Value Engine
- **Composite Rating Engine**: Combines Recent Form, Official Rating (OR), Course & Distance (C&D) compatibility, and Jockey/Trainer strike rates.
- **Fair Odds & Value Overlays**: Calculates true fair odds (\(1 / P_{\text{win}}\)) and flags **High Value Overlays** where bookmaker odds exceed fair odds.
- **Forecast & Trifecta Generator**: Produces Straight Forecast (1st & 2nd) and Combination Trifecta suggestions.

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

## 💻 Local Setup & Running

```bash
# Clone repository
git clone https://github.com/merlinthedev848/drawly.git
cd drawly

# Run Flask backend app locally
python app.py
```
Open `http://localhost:5000` in your web browser.

---

## 📄 License
MIT License
