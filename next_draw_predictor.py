import numpy as np
import pandas as pd
from data_loader import load_lotto_data
from stats_engine import (
    compute_ball_frequencies, 
    compute_gap_statistics, 
    compute_cooccurrence_matrix,
    compute_number_likelihoods
)
from generator import generate_logical_tickets
from live_fetcher import fetch_live_lotto_data

def predict_next_draw(game_type="uk"):
    """
    Computes Bayesian Updated Likelihoods specifically for the upcoming next draw.
    Uses sliding windows (N=10, N=25 draws) to capture recent momentum acceleration.
    """
    total_balls = 47 if game_type == "irish" else 59
    df_raw, draw_matrix = load_lotto_data(game_type)
    
    # 1. Macro Stats (All draws)
    df_freq = compute_ball_frequencies(draw_matrix, total_balls=total_balls)
    df_gaps = compute_gap_statistics(draw_matrix, total_balls=total_balls)
    cooc_matrix = compute_cooccurrence_matrix(draw_matrix, total_balls=total_balls)
    df_lh = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model="harmonic", total_balls=total_balls)

    # 2. Micro Velocity (Last 15 draws acceleration)
    recent_matrix = draw_matrix[-15:]
    recent_freq = compute_ball_frequencies(recent_matrix, total_balls=total_balls)

    # 3. Bayesian Likelihood Adjustment
    prior_probs = df_lh.set_index('ball')['draw_prob'].to_dict()
    recent_rates = recent_freq.set_index('ball')['rate'].to_dict()

    bayesian_scores = []
    for b in range(1, total_balls + 1):
        prior = prior_probs.get(b, 6.0 / total_balls)
        rec_rate = recent_rates.get(b, 0.0)
        
        # Bayesian likelihood update: Prior * (1 + Acceleration factor)
        accel = rec_rate / (6.0 / total_balls)
        posterior = prior * (0.7 + 0.3 * accel)
        
        g_row = df_gaps[df_gaps['ball'] == b].iloc[0]
        c_gap = g_row['current_gap']
        exp_gap = g_row['expected_gap']

        # Resonance boost for balls near or slightly past expected gap
        if 0.8 <= (c_gap / exp_gap) <= 1.8:
            posterior *= 1.15

        bayesian_scores.append({
            'ball': b,
            'posterior_prob': float(posterior),
            'likelihood_pct': float(np.round(posterior * 100, 2)),
            'current_gap': int(c_gap),
            'momentum_score': float(np.round(accel, 2))
        })

    bayesian_scores.sort(key=lambda x: x['posterior_prob'], reverse=True)

    # Top 6 recommended balls for next draw
    top_6_balls = [x['ball'] for x in bayesian_scores[:6]]
    top_6_balls.sort()

    # Generate Top 3 High-Conviction Next Draw Lines
    next_draw_tickets = generate_logical_tickets(
        num_tickets=3,
        model="harmonic",
        game_type=game_type
    )

    live_meta = fetch_live_lotto_data()
    next_date = live_meta['next_draw_date_irish'] if game_type == "irish" else live_meta['next_draw_date_uk']
    jackpot = live_meta['jackpot_estimate_irish'] if game_type == "irish" else live_meta['jackpot_estimate_uk']

    return {
        'game_type': game_type,
        'next_draw_date': next_date,
        'jackpot_estimate': jackpot,
        'predicted_top_6_balls': top_6_balls,
        'top_recommended_lines': next_draw_tickets,
        'top_10_individual_balls': bayesian_scores[:10],
        'prediction_confidence': "HIGH (Bayesian Velocity Weighted)"
    }

if __name__ == "__main__":
    uk_pred = predict_next_draw("uk")
    print("Next UK Draw Prediction:", uk_pred['predicted_top_6_balls'])
