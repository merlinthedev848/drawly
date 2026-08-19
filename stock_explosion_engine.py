import numpy as np
import pandas as pd

def calculate_stock_explosion_score(stock):
    """
    Calculates an 'Explosion Potential Score' (0 to 100) and target upside % 
    based on technical breakout signals and fundamental catalyst metrics.
    """
    # 1. Volume Surge Score (0 - 25 pts)
    vol_ratio = stock.get('volume_surge_ratio', 1.0)
    if vol_ratio >= 3.5:
        vol_score = 25.0
    elif vol_ratio >= 2.0:
        vol_score = 18.0
    elif vol_ratio >= 1.4:
        vol_score = 12.0
    else:
        vol_score = 5.0

    # 2. Revenue & Earnings Growth Score (0 - 25 pts)
    rev_growth = stock.get('revenue_growth_yoy', 0.0)
    if rev_growth >= 80.0:
        fund_score = 25.0
    elif rev_growth >= 40.0:
        fund_score = 20.0
    elif rev_growth >= 20.0:
        fund_score = 14.0
    else:
        fund_score = 6.0

    # 3. Short Squeeze & Float Potential (0 - 20 pts)
    short_float = stock.get('short_float_pct', 5.0)
    if short_float >= 25.0:
        squeeze_score = 20.0
    elif short_float >= 15.0:
        squeeze_score = 15.0
    elif short_float >= 8.0:
        squeeze_score = 10.0
    else:
        squeeze_score = 3.0

    # 4. Technical RSI & Moving Average Momentum (0 - 20 pts)
    rsi = stock.get('rsi_14', 50.0)
    ma_cross = stock.get('golden_cross', False)
    
    if 55 <= rsi <= 72 and ma_cross:
        tech_score = 20.0
    elif rsi > 72:
        tech_score = 12.0  # Slightly overbought risk
    elif ma_cross:
        tech_score = 15.0
    else:
        tech_score = 7.0

    # 5. Catalyst Bonus (0 - 10 pts)
    has_catalyst = stock.get('catalyst_type', 'None') != 'None'
    cat_score = 10.0 if has_catalyst else 3.0

    total_score = np.round(vol_score + fund_score + squeeze_score + tech_score + cat_score, 1)
    total_score = float(np.clip(total_score, 10.0, 99.5))

    # Calculate expected target upside %
    target_upside = np.round((total_score * 1.8) + (rev_growth * 0.4), 1)

    if total_score >= 82.0:
        risk_rating = "High Explosion Conviction"
    elif total_score >= 65.0:
        risk_rating = "Moderate Breakout Potential"
    else:
        risk_rating = "Watchlist / Neutral"

    return {
        'ticker': stock.get('ticker', 'UNKNOWN'),
        'company': stock.get('company', 'Unknown Inc.'),
        'sector': stock.get('sector', 'Tech'),
        'price': stock.get('price', 10.0),
        'volume_surge_ratio': vol_ratio,
        'revenue_growth_yoy': rev_growth,
        'short_float_pct': short_float,
        'rsi_14': rsi,
        'golden_cross': ma_cross,
        'catalyst_type': stock.get('catalyst_type', 'Growth'),
        'explosion_score': total_score,
        'target_upside_pct': target_upside,
        'risk_rating': risk_rating
    }

def get_preset_explosion_stocks():
    """
    Returns preset high-growth breakout stock radar picks.
    """
    raw_stocks = [
        {
            'ticker': 'NVDA',
            'company': 'NVIDIA Corp',
            'sector': 'Semiconductors & AI',
            'price': 128.50,
            'volume_surge_ratio': 2.8,
            'revenue_growth_yoy': 122.0,
            'short_float_pct': 1.8,
            'rsi_14': 64.5,
            'golden_cross': True,
            'catalyst_type': 'Blackwell AI Chip Shipment Ramp'
        },
        {
            'ticker': 'ASTS',
            'company': 'AST SpaceMobile',
            'sector': 'Satellite Telecom',
            'price': 24.80,
            'volume_surge_ratio': 4.2,
            'revenue_growth_yoy': 150.0,
            'short_float_pct': 26.5,
            'rsi_14': 68.0,
            'golden_cross': True,
            'catalyst_type': 'Commercial Satellite Launch Squeeze'
        },
        {
            'ticker': 'PLTR',
            'company': 'Palantir Technologies',
            'sector': 'Enterprise AI & Defense',
            'price': 31.20,
            'volume_surge_ratio': 3.1,
            'revenue_growth_yoy': 42.0,
            'short_float_pct': 4.5,
            'rsi_14': 62.0,
            'golden_cross': True,
            'catalyst_type': 'S&P 500 Inclusion & Government AI Contracts'
        },
        {
            'ticker': 'RKLB',
            'company': 'Rocket Lab USA',
            'sector': 'Aerospace & Launch',
            'price': 7.60,
            'volume_surge_ratio': 3.6,
            'revenue_growth_yoy': 71.0,
            'short_float_pct': 14.2,
            'rsi_14': 59.0,
            'golden_cross': True,
            'catalyst_type': 'Neutron Rocket Engine Hot-Fire Test'
        },
        {
            'ticker': 'CRWD',
            'company': 'CrowdStrike Holdings',
            'sector': 'Cybersecurity',
            'price': 275.40,
            'volume_surge_ratio': 2.1,
            'revenue_growth_yoy': 33.0,
            'short_float_pct': 3.2,
            'rsi_14': 56.0,
            'golden_cross': True,
            'catalyst_type': 'Enterprise SecOps Contract Renewals'
        },
        {
            'ticker': 'TEM',
            'company': 'Tempus AI Inc.',
            'sector': 'Healthcare AI',
            'price': 48.90,
            'volume_surge_ratio': 3.9,
            'revenue_growth_yoy': 88.0,
            'short_float_pct': 18.4,
            'rsi_14': 66.5,
            'golden_cross': True,
            'catalyst_type': 'Pharma Precision Medicine Deals'
        }
    ]

    analyzed = [calculate_stock_explosion_score(s) for s in raw_stocks]
    analyzed.sort(key=lambda x: x['explosion_score'], reverse=True)
    return analyzed

if __name__ == "__main__":
    stocks = get_preset_explosion_stocks()
    print("Stock Explosion Radar Picks:")
    for s in stocks:
        print(f"[{s['ticker']:<5}] {s['company']:<25} | Score: {s['explosion_score']:>4.1f}/100 | Target Upside: +{s['target_upside_pct']:>5.1f}% | Catalyst: {s['catalyst_type']}")
