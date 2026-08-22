import numpy as np
import pandas as pd

def parse_form_string(form_str):
    """
    Parses last 5 form figures (e.g. '1-2-1-3-F') into a numerical score.
    1st = 10, 2nd = 7, 3rd = 5, 4th = 3, 5th = 1, others/F/P/U = 0.
    """
    if not form_str:
        return 5.0
    
    clean_form = [c for c in str(form_str).upper() if c in '1234567890FPU']
    if not clean_form:
        return 5.0

    scores = []
    weight = 1.0  # Most recent runs weighed higher
    total_w = 0.0
    weighted_score = 0.0

    for item in reversed(clean_form[-5:]):
        if item == '1':
            s = 10.0
        elif item == '2':
            s = 7.0
        elif item == '3':
            s = 5.0
        elif item == '4':
            s = 3.0
        elif item in ['5', '6']:
            s = 1.5
        else:  # F, P, U or >6
            s = 0.0

        weighted_score += s * weight
        total_w += weight
        weight *= 0.85

    return np.round(weighted_score / max(total_w, 0.1), 2)

def calculate_horse_likelihoods(runners, weights=None):
    """
    Calculates logical win probabilities, composite rating scores, and fair odds for a field of horses.
    Runners is a list of dicts:
    [
       {
          'name': 'Red Rum Legend',
          'form': '1-2-1-3',
          'official_rating': 145,
          'weight_lbs': 160,
          'cd_winner': 'C&D',  # 'C&D', 'C', 'D', 'None'
          'jockey_win_pct': 18.5,
          'trainer_strike_rate': 22.0,
          'days_since_run': 21,
          'bookie_odds_dec': 4.5
       }, ...
    ]
    """
    if weights is None:
        weights = {
            'form': 0.30,
            'rating': 0.30,
            'cd_bonus': 0.15,
            'jockey_trainer': 0.15,
            'rest_recency': 0.10
        }

    if not runners:
        return []

    # Find max official rating for normalization
    ratings = [r.get('official_rating', 100) for r in runners]
    max_rating = max(ratings) if max(ratings) > 0 else 100
    min_rating = min(ratings) if min(ratings) > 0 else 50

    scored_runners = []
    raw_scores = []

    for r in runners:
        # 1. Recent Form Score (0 - 10)
        form_score = parse_form_string(r.get('form', '3-2-1'))

        # 2. Rating Score (0 - 10)
        or_val = r.get('official_rating', 100)
        if max_rating == min_rating:
            rating_score = 5.0
        else:
            rating_score = 5.0 + 5.0 * ((or_val - min_rating) / max(max_rating - min_rating, 1))

        # 3. Course & Distance Bonus (0 - 10)
        cd = str(r.get('cd_winner', 'None')).upper()
        if 'C&D' in cd:
            cd_score = 10.0
        elif 'C' in cd:
            cd_score = 7.0
        elif 'D' in cd:
            cd_score = 6.0
        else:
            cd_score = 2.0

        # 4. Jockey & Trainer Score (0 - 10)
        j_win = r.get('jockey_win_pct', 12.0)
        t_strike = r.get('trainer_strike_rate', 15.0)
        jt_score = min(10.0, (j_win * 0.25) + (t_strike * 0.25))

        # 5. Rest / Recency Score (0 - 10)
        days = r.get('days_since_run', 25)
        if 14 <= days <= 45:
            rest_score = 10.0
        elif 7 <= days < 14:
            rest_score = 8.0
        elif 46 <= days <= 90:
            rest_score = 6.0
        else:  # Long layoff or over-raced
            rest_score = 3.0

        # Calculate composite weighted score
        w_f = weights.get('form', 0.30)
        w_r = weights.get('rating', 0.30)
        w_cd = weights.get('cd_bonus', 0.15)
        w_jt = weights.get('jockey_trainer', 0.15)
        w_rst = weights.get('rest_recency', 0.10)

        total_w = w_f + w_r + w_cd + w_jt + w_rst
        if total_w == 0:
            total_w = 1.0

        composite_score = (w_f * form_score + w_r * rating_score + w_cd * cd_score + w_jt * jt_score + w_rst * rest_score) / total_w
        raw_scores.append(composite_score)

        scored_runners.append({
            'name': r.get('name', 'Unknown Runner'),
            'form': r.get('form', '-'),
            'official_rating': or_val,
            'cd_winner': cd,
            'jockey': r.get('jockey', 'Jockey'),
            'trainer': r.get('trainer', 'Trainer'),
            'bookie_odds_dec': r.get('bookie_odds_dec', 5.0),
            'form_score': np.round(form_score, 1),
            'rating_score': np.round(rating_score, 1),
            'composite_score': np.round(composite_score, 2)
        })

    # Convert composite scores into normalized probability distribution (Softmax-like scaling)
    exp_scores = np.exp(np.array(raw_scores) / 2.5)
    win_probs = exp_scores / np.sum(exp_scores)

    for i, sr in enumerate(scored_runners):
        prob_pct = np.round(win_probs[i] * 100, 2)
        fair_odds = np.round(100.0 / max(prob_pct, 0.1), 2)
        bookie_odds = sr['bookie_odds_dec']
        
        # Value Edge Calculation
        value_edge = np.round(((bookie_odds - fair_odds) / fair_odds) * 100, 1) if fair_odds > 0 else 0.0
        
        if value_edge >= 15.0:
            value_status = "High Value Overlay"
        elif value_edge >= 0.0:
            value_status = "Fair Value"
        else:
            value_status = "Underpriced / Short"

        sr['win_prob_pct'] = prob_pct
        sr['fair_odds_dec'] = fair_odds
        sr['value_edge_pct'] = value_edge
        sr['value_status'] = value_status

    # Sort runners by highest win probability
    scored_runners.sort(key=lambda x: x['win_prob_pct'], reverse=True)
    return scored_runners

def get_preset_races():
    """
    Returns preset active races with current William Hill market locator paths.
    """
    return [
        {
            'race_id': 'york_juddmonte',
            'race_name': 'York 15:35 - Juddmonte International Stakes (Group 1)',
            'race_date_str': 'Saturday, Aug 22, 2026 - 15:35 BST',
            'course': 'York',
            'distance': '1m 2f 56y',
            'going': 'Good to Firm',
            'william_hill_path': 'William Hill -> Horse Racing -> Meetings -> York -> 15:35 Race -> Win & Each Way',
            'william_hill_url': 'https://sports.williamhill.com/betting/en-gb/horse-racing/meetings/today',
            'runners': [
                {'name': 'City Of Troy', 'form': '1-1-1-1', 'official_rating': 124, 'cd_winner': 'C&D', 'jockey': 'R. L. Moore', 'trainer': 'A. P. O\'Brien', 'jockey_win_pct': 25.0, 'trainer_strike_rate': 26.0, 'days_since_run': 28, 'bookie_odds_dec': 2.10},
                {'name': 'Calandagan', 'form': '1-1-2-1', 'official_rating': 121, 'cd_winner': 'D', 'jockey': 'S. Pasquier', 'trainer': 'F. Graffard', 'jockey_win_pct': 19.0, 'trainer_strike_rate': 22.0, 'days_since_run': 35, 'bookie_odds_dec': 4.50},
                {'name': 'Ghostwriter', 'form': '1-3-3-3', 'official_rating': 117, 'cd_winner': 'D', 'jockey': 'R. Hornby', 'trainer': 'C. Cox', 'jockey_win_pct': 16.0, 'trainer_strike_rate': 18.0, 'days_since_run': 21, 'bookie_odds_dec': 8.50},
                {'name': 'Zarakem', 'form': '1-2-1-7', 'official_rating': 118, 'cd_winner': 'None', 'jockey': 'M. Guyon', 'trainer': 'J. Reynier', 'jockey_win_pct': 18.0, 'trainer_strike_rate': 19.0, 'days_since_run': 42, 'bookie_odds_dec': 11.00},
                {'name': 'Bluestocking', 'form': '2-1-2-1', 'official_rating': 116, 'cd_winner': 'D', 'jockey': 'R. Ryan', 'trainer': 'R. Beckett', 'jockey_win_pct': 20.0, 'trainer_strike_rate': 21.0, 'days_since_run': 30, 'bookie_odds_dec': 13.00}
            ]
        },
        {
            'race_id': 'newmarket_hopeful',
            'race_name': 'Newmarket 14:25 - Hopeful Stakes (Listed Race)',
            'race_date_str': 'Saturday, Aug 22, 2026 - 14:25 BST',
            'course': 'Newmarket',
            'distance': '6f',
            'going': 'Good',
            'william_hill_path': 'William Hill -> Horse Racing -> Meetings -> Newmarket -> 14:25 Race -> Win & Each Way',
            'william_hill_url': 'https://sports.williamhill.com/betting/en-gb/horse-racing/meetings/today',
            'runners': [
                {'name': 'Kinross', 'form': '1-2-1-2', 'official_rating': 118, 'cd_winner': 'C&D', 'jockey': 'L. Dettori', 'trainer': 'R. Beckett', 'jockey_win_pct': 22.0, 'trainer_strike_rate': 23.0, 'days_since_run': 21, 'bookie_odds_dec': 2.75},
                {'name': 'Art Power', 'form': '1-4-1-8', 'official_rating': 116, 'cd_winner': 'C&D', 'jockey': 'D. Allan', 'trainer': 'T. Easterby', 'jockey_win_pct': 15.0, 'trainer_strike_rate': 16.0, 'days_since_run': 28, 'bookie_odds_dec': 5.00},
                {'name': 'Shouldvebeenaring', 'form': '2-1-3-1', 'official_rating': 114, 'cd_winner': 'C', 'jockey': 'S. Levey', 'trainer': 'R. Hannon', 'jockey_win_pct': 18.0, 'trainer_strike_rate': 19.0, 'days_since_run': 14, 'bookie_odds_dec': 6.50},
                {'name': 'Commanche Falls', 'form': '4-1-2-3', 'official_rating': 112, 'cd_winner': 'D', 'jockey': 'C. Beasley', 'trainer': 'M. Dods', 'jockey_win_pct': 16.0, 'trainer_strike_rate': 17.0, 'days_since_run': 18, 'bookie_odds_dec': 9.00}
            ]
        }
    ]

if __name__ == "__main__":
    races = get_preset_races()
    res = calculate_horse_likelihoods(races[0]['runners'])
    print("Cheltenham Gold Cup Logical Ratings & Probability:")
    for r in res:
        print(f"Horse: {r['name']:<20} | Prob: {r['win_prob_pct']:>5.2f}% | Fair Odds: {r['fair_odds_dec']:>5.2f} | Bookie Odds: {r['bookie_odds_dec']:>5.2f} | Value: {r['value_status']}")
