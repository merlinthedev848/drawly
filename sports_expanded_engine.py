import numpy as np

def calculate_euromillions_stats():
    """
    EuroMillions Lottery Odds & Statistical Baseline.
    5 Main Numbers (1 to 50) + 2 Lucky Stars (1 to 12).
    """
    main_prob = 5.0 / 50.0  # 10.0% per ball slot
    star_prob = 2.0 / 12.0  # 16.67% per star slot
    jackpot_odds = 139838160  # 1 in 139.8M

    return {
        'game_name': 'EuroMillions',
        'main_balls': 5,
        'main_range': '1 to 50',
        'lucky_stars': 2,
        'star_range': '1 to 12',
        'main_draw_prob_pct': np.round(main_prob * 100, 2),
        'star_draw_prob_pct': np.round(star_prob * 100, 2),
        'jackpot_odds_one_in': jackpot_odds
    }

def predict_tennis_match(player_a, player_b, surface="Hard", rank_a=4, rank_b=12, h2h_a_wins=3, h2h_b_wins=1, bookie_odds=None):
    """
    Tennis Match Predictor based on ELO rankings, surface specialization, and H2H records.
    """
    if bookie_odds is None:
        bookie_odds = {'player_a': 1.55, 'player_b': 2.45}

    # Base ELO / Rank rating
    rating_a = 2100 - (rank_a * 15) + (h2h_a_wins * 25)
    rating_b = 2100 - (rank_b * 15) + (h2h_b_wins * 25)

    # Surface adjustments
    if surface == "Clay":
        if "NADAL" in player_a.upper() or "ALCARAZ" in player_a.upper():
            rating_a += 80
    elif surface == "Grass":
        if "DJOKOVIC" in player_a.upper() or "SINNER" in player_a.upper():
            rating_a += 60

    # Win probability via Bradley-Terry / ELO logit scale
    prob_a = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
    prob_b = 1.0 - prob_a

    pct_a = np.round(prob_a * 100, 1)
    pct_b = np.round(prob_b * 100, 1)

    fair_a = np.round(1.0 / max(prob_a, 0.01), 2)
    fair_b = np.round(1.0 / max(prob_b, 0.01), 2)

    val_a = np.round(((bookie_odds['player_a'] - fair_a) / fair_a) * 100, 1)
    val_b = np.round(((bookie_odds['player_b'] - fair_b) / fair_b) * 100, 1)

    best_val = player_a if val_a > val_b else player_b
    best_edge = max(val_a, val_b)

    return {
        'player_a': player_a,
        'player_b': player_b,
        'surface': surface,
        'pct_a': pct_a,
        'pct_b': pct_b,
        'fair_a': fair_a,
        'fair_b': fair_b,
        'bookie_a': bookie_odds['player_a'],
        'bookie_b': bookie_odds['player_b'],
        'value_pick': best_val,
        'value_edge_pct': best_edge,
        'set_betting_prediction': f"{player_a} 2-0 Sets" if pct_a > 65.0 else f"{player_a} 2-1 Sets"
    }

def predict_basketball_nba(home_team, away_team, line_spread=-5.5, line_total=224.5, home_off_rating=118.2, away_off_rating=114.5):
    """
    NBA Basketball Point Spread & Game Totals (Over/Under) Predictor.
    """
    home_adv = 3.2  # Home court advantage in NBA points
    expected_margin = (home_off_rating - away_off_rating) + home_adv
    proj_margin = np.round(expected_margin, 1)

    # Win probability from point spread formula
    prob_home_win = 1.0 / (1.0 + 10.0 ** (-proj_margin / 10.5))
    pct_home_win = np.round(prob_home_win * 100, 1)
    pct_away_win = np.round((1.0 - prob_home_win) * 100, 1)

    # Projected Total Points
    proj_total = np.round(home_off_rating + away_off_rating - 8.0, 1)
    total_pick = "OVER" if proj_total > line_total else "UNDER"

    # Spread Pick (e.g. Home -5.5)
    spread_pick = f"{home_team} {line_spread}" if proj_margin > abs(line_spread) else f"{away_team} +{abs(line_spread)}"

    return {
        'home_team': home_team,
        'away_team': away_team,
        'line_spread': line_spread,
        'line_total': line_total,
        'proj_margin': proj_margin,
        'proj_total': proj_total,
        'pct_home_win': pct_home_win,
        'pct_away_win': pct_away_win,
        'recommended_spread_pick': spread_pick,
        'recommended_total_pick': f"{total_pick} {line_total}"
    }

def predict_greyhound_race(track="Romford", distance="400m", runners=None):
    """
    Greyhound Racing Trap Bias & Split Time Predictor.
    """
    if runners is None:
        runners = [
            {'trap': 1, 'dog_name': 'Swift Sparkle', 'split_time_sec': 3.75, 'grade': 'A1', 'win_pct': 24.5, 'bookie_odds': 2.80},
            {'trap': 2, 'dog_name': 'Ballymac Hero', 'split_time_sec': 3.82, 'grade': 'A1', 'win_pct': 21.0, 'bookie_odds': 4.00},
            {'trap': 3, 'dog_name': 'Droopys Jet', 'split_time_sec': 3.88, 'grade': 'A2', 'win_pct': 16.5, 'bookie_odds': 6.50},
            {'trap': 4, 'dog_name': 'Westwell King', 'split_time_sec': 3.90, 'grade': 'A2', 'win_pct': 14.0, 'bookie_odds': 8.00},
            {'trap': 5, 'dog_name': 'Romeo Commander', 'split_time_sec': 3.79, 'grade': 'A1', 'win_pct': 19.0, 'bookie_odds': 5.00},
            {'trap': 6, 'dog_name': 'Slick Sentinel', 'split_time_sec': 3.84, 'grade': 'A2', 'win_pct': 15.0, 'bookie_odds': 7.50}
        ]

    # Calculate Trap Bias (Inside traps 1 & 2 usually have an advantage in tight turns)
    raw_scores = []
    for r in runners:
        trap_bonus = 1.15 if r['trap'] in [1, 2] else (1.05 if r['trap'] == 6 else 1.0)
        split_score = (4.0 - r['split_time_sec']) * 10.0
        score = (split_score * 0.5 + r['win_pct'] * 0.5) * trap_bonus
        raw_scores.append(score)

    total_s = sum(raw_scores)
    analyzed = []
    for i, r in enumerate(runners):
        prob_pct = np.round((raw_scores[i] / total_s) * 100, 1)
        fair_odds = np.round(100.0 / max(prob_pct, 0.1), 2)
        val_edge = np.round(((r['bookie_odds'] - fair_odds) / fair_odds) * 100, 1)

        analyzed.append({
            'trap': r['trap'],
            'dog_name': r['dog_name'],
            'split_time_sec': r['split_time_sec'],
            'grade': r['grade'],
            'win_prob_pct': prob_pct,
            'fair_odds': fair_odds,
            'bookie_odds': r['bookie_odds'],
            'value_edge_pct': val_edge
        })

    analyzed.sort(key=lambda x: x['win_prob_pct'], reverse=True)
    return {
        'track': track,
        'distance': distance,
        'runners': analyzed,
        'forecast_pick': f"Trap {analyzed[0]['trap']} ({analyzed[0]['dog_name']}) & Trap {analyzed[1]['trap']} ({analyzed[1]['dog_name']})"
    }

if __name__ == "__main__":
    print("EuroMillions Stats:", calculate_euromillions_stats())
    print("Tennis Prediction:", predict_tennis_match("Jannik Sinner", "Carlos Alcaraz"))
    print("NBA Prediction:", predict_basketball_nba("Boston Celtics", "LA Lakers"))
    print("Greyhound Race:", predict_greyhound_race())
