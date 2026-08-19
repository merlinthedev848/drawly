import numpy as np
import pandas as pd
from scipy.stats import poisson

def predict_football_match(home_team, away_team, home_attack=1.85, home_defense=0.90, away_attack=1.40, away_defense=1.20, bookie_odds=None):
    """
    High-Probability Football Prediction Engine based on Poisson Expected Goals (xG).
    Includes 1X2, Double Chance (1X, X2, 12), Draw No Bet (DNB), Over/Under 1.5 & 2.5 goals,
    and High Conviction Safety Selections.
    """
    if bookie_odds is None:
        bookie_odds = {'home': 2.10, 'draw': 3.40, 'away': 3.60}

    LEAGUE_AVG_HOME = 1.55
    LEAGUE_AVG_AWAY = 1.20

    # Expected Goals (xG)
    xg_home = np.round(home_attack * (away_defense / LEAGUE_AVG_HOME) * LEAGUE_AVG_HOME, 2)
    xg_away = np.round(away_attack * (home_defense / LEAGUE_AVG_AWAY) * LEAGUE_AVG_AWAY, 2)

    max_goals = 6
    score_matrix = np.zeros((max_goals, max_goals))

    for h in range(max_goals):
        for a in range(max_goals):
            prob_h = poisson.pmf(h, xg_home)
            prob_a = poisson.pmf(a, xg_away)
            score_matrix[h, a] = prob_h * prob_a

    # 1X2 Probabilities
    p_home = float(np.sum(np.tril(score_matrix, -1)))
    p_draw = float(np.sum(np.diag(score_matrix)))
    p_away = float(np.sum(np.triu(score_matrix, 1)))

    total_p = p_home + p_draw + p_away
    p_home /= total_p
    p_draw /= total_p
    p_away /= total_p

    # High Probability Double Chance (70%+ Win Probabilities)
    p_1x = np.round((p_home + p_draw) * 100, 1)
    p_x2 = np.round((p_away + p_draw) * 100, 1)
    p_12 = np.round((p_home + p_away) * 100, 1)

    pct_home = np.round(p_home * 100, 1)
    pct_draw = np.round(p_draw * 100, 1)
    pct_away = np.round(p_away * 100, 1)

    fair_home = np.round(1.0 / max(p_home, 0.01), 2)
    fair_draw = np.round(1.0 / max(p_draw, 0.01), 2)
    fair_away = np.round(1.0 / max(p_away, 0.01), 2)

    # Over / Under Goals
    p_under_1_5 = score_matrix[0, 0] + score_matrix[1, 0] + score_matrix[0, 1]
    pct_over_1_5 = np.round((1.0 - p_under_1_5) * 100, 1)

    p_under_2_5 = sum(score_matrix[h, a] for h in range(3) for a in range(3 - h))
    pct_over_2_5 = np.round((1.0 - p_under_2_5) * 100, 1)

    pct_btts_yes = np.round(((1.0 - poisson.pmf(0, xg_home)) * (1.0 - poisson.pmf(0, xg_away))) * 100, 1)

    # Identify Highest Probability Safe Pick (>70% probability)
    safe_picks = []
    if p_1x >= 72.0:
        safe_picks.append({'pick': f"Double Chance {home_team} or Draw (1X)", 'prob_pct': p_1x})
    if p_x2 >= 72.0:
        safe_picks.append({'pick': f"Double Chance {away_team} or Draw (X2)", 'prob_pct': p_x2})
    if pct_over_1_5 >= 75.0:
        safe_picks.append({'pick': "Over 1.5 Match Goals", 'prob_pct': pct_over_1_5})

    safe_picks.sort(key=lambda x: x['prob_pct'], reverse=True)
    best_safe_pick = safe_picks[0] if safe_picks else {'pick': f"Double Chance 1X ({p_1x}%)", 'prob_pct': p_1x}

    # Correct Scores
    correct_scores = []
    for h in range(max_goals):
        for a in range(max_goals):
            correct_scores.append({'score': f"{h}-{a}", 'prob_pct': np.round(score_matrix[h, a] * 100, 2)})
    correct_scores.sort(key=lambda x: x['prob_pct'], reverse=True)

    val_home = np.round(((bookie_odds['home'] - fair_home) / fair_home) * 100, 1)
    val_draw = np.round(((bookie_odds['draw'] - fair_draw) / fair_draw) * 100, 1)
    val_away = np.round(((bookie_odds['away'] - fair_away) / fair_away) * 100, 1)

    return {
        'home_team': home_team,
        'away_team': away_team,
        'xg_home': xg_home,
        'xg_away': xg_away,
        'pct_home': pct_home,
        'pct_draw': pct_draw,
        'pct_away': pct_away,
        'double_chance_1x_pct': p_1x,
        'double_chance_x2_pct': p_x2,
        'pct_over_1_5': pct_over_1_5,
        'pct_over_2_5': pct_over_2_5,
        'pct_btts_yes': pct_btts_yes,
        'highest_probability_pick': best_safe_pick['pick'],
        'highest_probability_pct': best_safe_pick['prob_pct'],
        'fair_home': fair_home,
        'fair_draw': fair_draw,
        'fair_away': fair_away,
        'bookie_home': bookie_odds['home'],
        'bookie_draw': bookie_odds['draw'],
        'bookie_away': bookie_odds['away'],
        'val_home_pct': val_home,
        'val_draw_pct': val_draw,
        'val_away_pct': val_away,
        'top_correct_scores': correct_scores[:4]
    }

def get_preset_football_matches():
    fixtures = [
        {
            'match_id': 'mci_ars',
            'home_team': 'Manchester City',
            'away_team': 'Arsenal',
            'home_attack': 2.30, 'home_defense': 0.80,
            'away_attack': 2.10, 'away_defense': 0.85,
            'bookie_odds': {'home': 1.95, 'draw': 3.60, 'away': 3.80}
        },
        {
            'match_id': 'rma_bar',
            'home_team': 'Real Madrid',
            'away_team': 'FC Barcelona',
            'home_attack': 2.20, 'home_defense': 0.90,
            'away_attack': 2.15, 'away_defense': 0.95,
            'bookie_odds': {'home': 2.10, 'draw': 3.75, 'away': 3.30}
        },
        {
            'match_id': 'liv_mun',
            'home_team': 'Liverpool',
            'away_team': 'Manchester United',
            'home_attack': 2.40, 'home_defense': 0.95,
            'away_attack': 1.50, 'away_defense': 1.35,
            'bookie_odds': {'home': 1.50, 'draw': 4.75, 'away': 6.00}
        }
    ]

    analyzed = []
    for f in fixtures:
        m_res = predict_football_match(
            f['home_team'], f['away_team'],
            f['home_attack'], f['home_defense'],
            f['away_attack'], f['away_defense'],
            f['bookie_odds']
        )
        m_res['match_id'] = f['match_id']
        analyzed.append(m_res)

    return analyzed
