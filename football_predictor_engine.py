import numpy as np
import pandas as pd
from scipy.stats import poisson

def predict_football_match(home_team, away_team, home_attack=1.85, home_defense=0.90, away_attack=1.40, away_defense=1.20, bookie_odds=None):
    """
    Computes Poisson Expected Goals (xG), 1X2 Match Probabilities (Home, Draw, Away), 
    Fair Odds, Correct Score Matrix, and Over/Under 2.5 goals probability.
    """
    if bookie_odds is None:
        bookie_odds = {'home': 2.10, 'draw': 3.40, 'away': 3.60}

    # League Average Goals per match baseline
    LEAGUE_AVG_HOME = 1.55
    LEAGUE_AVG_AWAY = 1.20

    # Calculate Expected Goals (xG)
    xg_home = np.round(home_attack * (away_defense / LEAGUE_AVG_HOME) * LEAGUE_AVG_HOME, 2)
    xg_away = np.round(away_attack * (home_defense / LEAGUE_AVG_AWAY) * LEAGUE_AVG_AWAY, 2)

    max_goals = 6
    score_matrix = np.zeros((max_goals, max_goals))

    for h in range(max_goals):
        for a in range(max_goals):
            prob_h = poisson.pmf(h, xg_home)
            prob_a = poisson.pmf(a, xg_away)
            score_matrix[h, a] = prob_h * prob_a

    # Sum 1X2 probabilities
    p_home = float(np.sum(np.tril(score_matrix, -1)))
    p_draw = float(np.sum(np.diag(score_matrix)))
    p_away = float(np.sum(np.triu(score_matrix, 1)))

    total_p = p_home + p_draw + p_away
    p_home /= total_p
    p_draw /= total_p
    p_away /= total_p

    # Convert to Percentages
    pct_home = np.round(p_home * 100, 1)
    pct_draw = np.round(p_draw * 100, 1)
    pct_away = np.round(p_away * 100, 1)

    # Calculate Fair Odds (1 / P)
    fair_home = np.round(1.0 / max(p_home, 0.01), 2)
    fair_draw = np.round(1.0 / max(p_draw, 0.01), 2)
    fair_away = np.round(1.0 / max(p_away, 0.01), 2)

    # Over / Under 2.5 Goals
    p_under_2_5 = 0.0
    for h in range(3):
        for a in range(3 - h):
            p_under_2_5 += score_matrix[h, a]

    p_over_2_5 = 1.0 - p_under_2_5
    pct_over_2_5 = np.round(p_over_2_5 * 100, 1)
    pct_under_2_5 = np.round(p_under_2_5 * 100, 1)

    # Both Teams to Score (BTTS)
    p_btts_yes = (1.0 - poisson.pmf(0, xg_home)) * (1.0 - poisson.pmf(0, xg_away))
    pct_btts_yes = np.round(p_btts_yes * 100, 1)

    # Top 3 Most Likely Correct Scores
    correct_scores = []
    for h in range(max_goals):
        for a in range(max_goals):
            correct_scores.append({
                'score': f"{h}-{a}",
                'prob_pct': np.round(score_matrix[h, a] * 100, 2)
            })

    correct_scores.sort(key=lambda x: x['prob_pct'], reverse=True)

    # Calculate Value Edge on 1X2
    val_home = np.round(((bookie_odds['home'] - fair_home) / fair_home) * 100, 1)
    val_draw = np.round(((bookie_odds['draw'] - fair_draw) / fair_draw) * 100, 1)
    val_away = np.round(((bookie_odds['away'] - fair_away) / fair_away) * 100, 1)

    best_val_choice = "None"
    best_val_edge = -999.0
    if val_home > best_val_edge:
        best_val_choice = f"Home Win ({home_team})"
        best_val_edge = val_home
    if val_draw > best_val_edge:
        best_val_choice = "Draw"
        best_val_edge = val_draw
    if val_away > best_val_edge:
        best_val_choice = f"Away Win ({away_team})"
        best_val_edge = val_away

    return {
        'home_team': home_team,
        'away_team': away_team,
        'xg_home': xg_home,
        'xg_away': xg_away,
        'pct_home': pct_home,
        'pct_draw': pct_draw,
        'pct_away': pct_away,
        'fair_home': fair_home,
        'fair_draw': fair_draw,
        'fair_away': fair_away,
        'bookie_home': bookie_odds['home'],
        'bookie_draw': bookie_odds['draw'],
        'bookie_away': bookie_odds['away'],
        'val_home_pct': val_home,
        'val_draw_pct': val_draw,
        'val_away_pct': val_away,
        'best_value_pick': best_val_choice,
        'best_value_edge': best_val_edge,
        'pct_over_2_5': pct_over_2_5,
        'pct_under_2_5': pct_under_2_5,
        'pct_btts_yes': pct_btts_yes,
        'top_correct_scores': correct_scores[:4]
    }

def get_preset_football_matches():
    """
    Returns preset featured football fixtures.
    """
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
        },
        {
            'match_id': 'bay_bvb',
            'home_team': 'Bayern Munich',
            'away_team': 'Borussia Dortmund',
            'home_attack': 2.60, 'home_defense': 0.85,
            'away_attack': 1.90, 'away_defense': 1.30,
            'bookie_odds': {'home': 1.45, 'draw': 5.00, 'away': 6.50}
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

if __name__ == "__main__":
    matches = get_preset_football_matches()
    print("Football Match Predictions:")
    for m in matches:
        print(f"{m['home_team']} vs {m['away_team']} | xG: {m['xg_home']} - {m['xg_away']} | 1X2: {m['pct_home']}% - {m['pct_draw']}% - {m['pct_away']}% | Value Pick: {m['best_value_pick']}")
