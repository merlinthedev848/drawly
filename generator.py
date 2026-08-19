import random
import numpy as np
import pandas as pd
from data_loader import load_lotto_data
from stats_engine import (
    compute_ball_frequencies,
    compute_gap_statistics,
    compute_cooccurrence_matrix,
    compute_number_likelihoods,
    TOTAL_BALLS,
    BALLS_PER_DRAW,
    THEO_DRAW_PROB
)

def is_valid_ticket(balls, odd_even_filter=True, sum_filter=True, max_consecutive=2):
    """
    Applies mathematical balance filters to candidate 6-number ticket lines.
    """
    sorted_balls = sorted(balls)
    
    # 1. Sum Range Filter
    total_sum = sum(sorted_balls)
    if sum_filter and not (115 <= total_sum <= 245):
        return False
        
    # 2. Odd / Even Balance Filter
    if odd_even_filter:
        odds = sum(1 for b in sorted_balls if b % 2 != 0)
        # Allow 2:4, 3:3, or 4:2 odd/even split
        if odds not in [2, 3, 4]:
            return False

    # 3. Max Consecutive Numbers Filter
    consec = 1
    max_consec_found = 1
    for i in range(1, len(sorted_balls)):
        if sorted_balls[i] == sorted_balls[i - 1] + 1:
            consec += 1
            max_consec_found = max(max_consec_found, consec)
        else:
            consec = 1
    if max_consec_found > max_consecutive:
        return False

    return True

def generate_logical_tickets(num_tickets=5, model="harmonic", weights=None, odd_even_filter=True, sum_filter=True):
    """
    Generates logical ticket combinations with full statistical rationale breakdown.
    """
    df_raw, draw_matrix = load_lotto_data()
    df_freq = compute_ball_frequencies(draw_matrix)
    df_gaps = compute_gap_statistics(draw_matrix)
    cooc_matrix = compute_cooccurrence_matrix(draw_matrix)

    df_lh = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model=model, weights=weights)

    probs = df_lh['draw_prob'].values
    balls = df_lh['ball'].values
    norm_probs = probs / np.sum(probs)

    tickets = []
    attempts = 0
    max_attempts = 2000

    ball_dict = df_lh.set_index('ball').to_dict(orient='index')

    while len(tickets) < num_tickets and attempts < max_attempts:
        attempts += 1
        # Sample 6 unique balls weighted by calculated likelihood probability
        chosen = np.random.choice(balls, size=6, replace=False, p=norm_probs)
        chosen_sorted = [int(b) for b in sorted(chosen)]

        if is_valid_ticket(chosen_sorted, odd_even_filter=odd_even_filter, sum_filter=sum_filter):
            # Avoid exact duplicate tickets in output batch
            if any(t['numbers'] == chosen_sorted for t in tickets):
                continue

            # Build ball-by-ball rationale breakdown
            breakdown = []
            ticket_sum = sum(chosen_sorted)
            odd_count = sum(1 for b in chosen_sorted if b % 2 != 0)
            even_count = 6 - odd_count
            lh_sum = 0.0

            for b in chosen_sorted:
                info = ball_dict[b]
                lh_pct = float(info['likelihood_pct'])
                lh_sum += lh_pct
                breakdown.append({
                    'ball': b,
                    'likelihood_pct': lh_pct,
                    'count': int(info['freq_count']),
                    'current_gap': int(info['current_gap']),
                    'gap_ratio': float(info['gap_ratio'])
                })

            avg_likelihood = np.round(lh_sum / 6, 2)
            # Harmony score: ratio of average ticket likelihood vs theoretical equal baseline (10.17%)
            harmony_score = np.round((avg_likelihood / (THEO_DRAW_PROB * 100)) * 100, 1)

            tickets.append({
                'id': len(tickets) + 1,
                'numbers': chosen_sorted,
                'sum': ticket_sum,
                'odd_even_ratio': f"{odd_count}:{even_count}",
                'avg_likelihood_pct': float(avg_likelihood),
                'harmony_score': float(harmony_score),
                'breakdown': breakdown
            })

    return tickets

if __name__ == "__main__":
    tkts = generate_logical_tickets(3, model="harmonic")
    for t in tkts:
        print(f"Ticket #{t['id']}: {t['numbers']} | Sum: {t['sum']} | Odd/Even: {t['odd_even_ratio']} | Harmony: {t['harmony_score']}%")
