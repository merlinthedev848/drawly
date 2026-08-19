import random
import numpy as np
import pandas as pd
from data_loader import load_lotto_data
from stats_engine import (
    compute_ball_frequencies,
    compute_gap_statistics,
    compute_cooccurrence_matrix,
    compute_number_likelihoods
)

def is_valid_ticket(balls, game_type="uk", odd_even_filter=True, sum_filter=True):
    sorted_balls = sorted(balls)
    total_sum = sum(sorted_balls)
    
    min_sum = 90 if game_type == "irish" else 115
    max_sum = 195 if game_type == "irish" else 245

    if sum_filter and not (min_sum <= total_sum <= max_sum):
        return False
        
    if odd_even_filter:
        odds = sum(1 for b in sorted_balls if b % 2 != 0)
        if odds not in [2, 3, 4]:
            return False

    return True

def generate_logical_tickets(num_tickets=5, model="harmonic", weights=None, game_type="uk", odd_even_filter=True, sum_filter=True):
    total_balls = 47 if game_type == "irish" else 59
    df_raw, draw_matrix = load_lotto_data(game_type)
    df_freq = compute_ball_frequencies(draw_matrix, total_balls=total_balls)
    df_gaps = compute_gap_statistics(draw_matrix, total_balls=total_balls)
    cooc_matrix = compute_cooccurrence_matrix(draw_matrix, total_balls=total_balls)

    df_lh = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model=model, weights=weights, total_balls=total_balls)

    probs = df_lh['draw_prob'].values
    balls = df_lh['ball'].values
    norm_probs = probs / np.sum(probs)

    tickets = []
    attempts = 0
    max_attempts = 2000

    ball_dict = df_lh.set_index('ball').to_dict(orient='index')

    while len(tickets) < num_tickets and attempts < max_attempts:
        attempts += 1
        chosen = np.random.choice(balls, size=6, replace=False, p=norm_probs)
        chosen_sorted = [int(b) for b in sorted(chosen)]

        if is_valid_ticket(chosen_sorted, game_type=game_type, odd_even_filter=odd_even_filter, sum_filter=sum_filter):
            if any(t['numbers'] == chosen_sorted for t in tickets):
                continue

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
            theo_prob = (6.0 / total_balls) * 100
            harmony_score = np.round((avg_likelihood / theo_prob) * 100, 1)

            tickets.append({
                'id': len(tickets) + 1,
                'game_type': game_type,
                'numbers': chosen_sorted,
                'sum': ticket_sum,
                'odd_even_ratio': f"{odd_count}:{even_count}",
                'avg_likelihood_pct': float(avg_likelihood),
                'harmony_score': float(harmony_score),
                'breakdown': breakdown
            })

    return tickets
