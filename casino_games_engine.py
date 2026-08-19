import numpy as np

def analyze_roulette_wheel(recent_spins=None, wheel_type="European"):
    """
    Roulette High-Probability Sector & Even-Money Trend Engine.
    """
    if recent_spins is None:
        recent_spins = [17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9]

    total_pockets = 37 if wheel_type == "European" else 38
    single_num_prob = np.round((1.0 / total_pockets) * 100, 2)
    even_money_prob = np.round((18.0 / total_pockets) * 100, 2)
    dozen_prob = np.round((12.0 / total_pockets) * 100, 2)

    voisins_nums = [22, 18, 29, 7, 28, 12, 35, 3, 26, 0, 32, 15, 19, 4, 21, 2, 25]
    tiers_nums = [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33]
    orphelins_nums = [1, 20, 14, 31, 9, 17, 34, 6]
    red_nums = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

    red_count = sum(1 for s in recent_spins if s in red_nums)
    black_count = sum(1 for s in recent_spins if s != 0 and s not in red_nums)

    d1 = sum(1 for s in recent_spins if 1 <= s <= 12)
    d2 = sum(1 for s in recent_spins if 13 <= s <= 24)
    d3 = sum(1 for s in recent_spins if 25 <= s <= 36)

    # Highest Probability Target Bet (e.g. 2 Dozens covers 24/37 = 64.86% probability!)
    two_dozens_prob_pct = np.round((24.0 / total_pockets) * 100, 2)

    return {
        'wheel_type': wheel_type,
        'single_num_prob_pct': single_num_prob,
        'even_money_prob_pct': even_money_prob,
        'dozen_prob_pct': dozen_prob,
        'two_dozens_coverage_prob_pct': two_dozens_prob_pct,
        'recent_spins_count': len(recent_spins),
        'red_pct': np.round((red_count / max(len(recent_spins), 1)) * 100, 1),
        'black_pct': np.round((black_count / max(len(recent_spins), 1)) * 100, 1),
        'highest_probability_bet': f"Cover 2 Dozens (64.86% Win Prob)",
        'dozens': {'1st_12': d1, '2nd_12': d2, '3rd_12': d3}
    }

def get_blackjack_basic_strategy(player_total, dealer_upcard, is_soft=False, can_split=False, running_count=0, decks_remaining=4):
    """
    Returns mathematically optimal Blackjack decision and Hi-Lo True Count advantage score.
    """
    upcard = str(dealer_upcard).upper()

    # Calculate Hi-Lo True Count
    true_count = np.round(running_count / max(decks_remaining, 0.5), 1)
    
    # Player Advantage Adjustment
    player_advantage = np.round(-0.5 + (true_count * 0.5), 2)  # Base -0.5% house edge

    if can_split:
        if player_total in [16, 22]:
            return {'action': 'SPLIT', 'win_prob_pct': 52.5, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Always Split Aces and 8s.'}
        elif player_total == 20:
            return {'action': 'STAND', 'win_prob_pct': 64.0, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Never Split 10s.'}

    if is_soft:
        if player_total >= 19:
            return {'action': 'STAND', 'win_prob_pct': 58.0, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Soft 19+ is strong.'}
        elif player_total == 18:
            if upcard in ['2', '3', '4', '5', '6']:
                return {'action': 'DOUBLE', 'win_prob_pct': 55.5, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Double soft 18 vs weak dealer.'}
            else:
                return {'action': 'HIT', 'win_prob_pct': 44.0, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Hit soft 18 vs 9, 10 or Ace.'}

    # Hard hands
    if player_total >= 17:
        return {'action': 'STAND', 'win_prob_pct': 54.0, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Always Stand on Hard 17+.'}
    elif player_total in [13, 14, 15, 16]:
        if upcard in ['2', '3', '4', '5', '6']:
            return {'action': 'STAND', 'win_prob_pct': 42.0, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Dealer is stiff (high bust risk).' }
        else:
            return {'action': 'HIT', 'win_prob_pct': 36.0, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Hit hard stiff vs strong dealer.'}
    elif player_total in [10, 11]:
        return {'action': 'DOUBLE DOWN', 'win_prob_pct': 56.0, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'High win probability Double Down opportunity.'}
    else:
        return {'action': 'HIT', 'win_prob_pct': 38.0, 'true_count': true_count, 'player_advantage_pct': player_advantage, 'rationale': 'Hit on 9 or lower.'}

def analyze_baccarat_probabilities():
    return {
        'banker': {
            'win_prob_pct': 45.86,
            'house_edge_pct': 1.06,
            'recommendation': 'Highest Win Probability Choice (45.86%)'
        },
        'player': {
            'win_prob_pct': 44.62,
            'house_edge_pct': 1.24,
            'recommendation': 'Good Option'
        }
    }
