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

def run_backtest(test_draws=100, tickets_per_draw=5, model="harmonic"):
    """
    Simulates ticket generation strategy over the last `test_draws` historical draws.
    Measures match distributions: 3 matches, 4 matches, 5 matches, 6 matches.
    """
    df_raw, draw_matrix = load_lotto_data()
    total_available = len(draw_matrix)

    test_draws = min(test_draws, total_available - 50)
    start_idx = total_available - test_draws

    match_counts = {3: 0, 4: 0, 5: 0, 6: 0}
    total_tickets_tested = 0

    for idx in range(start_idx, total_available):
        actual_draw = set(draw_matrix[idx])
        
        # Build dataset available prior to this draw
        sub_matrix = draw_matrix[:idx]
        df_f = compute_ball_frequencies(sub_matrix)
        df_g = compute_gap_statistics(sub_matrix)
        cooc = compute_cooccurrence_matrix(sub_matrix)

        df_lh = compute_number_likelihoods(df_f, df_g, cooc, model=model)
        probs = df_lh['draw_prob'].values
        balls = df_lh['ball'].values
        norm_probs = probs / np.sum(probs)

        # Generate ticket lines
        for _ in range(tickets_per_draw):
            total_tickets_tested += 1
            ticket = set(np.random.choice(balls, size=6, replace=False, p=norm_probs))
            matches = len(ticket.intersection(actual_draw))
            if matches in match_counts:
                match_counts[matches] += 1

    results = {
        'test_draws': test_draws,
        'model': model,
        'tickets_per_draw': tickets_per_draw,
        'total_tickets': total_tickets_tested,
        'matches_3': match_counts[3],
        'matches_4': match_counts[4],
        'matches_5': match_counts[5],
        'matches_6': match_counts[6],
        'hit_rate_3_plus': np.round(((match_counts[3] + match_counts[4] + match_counts[5] + match_counts[6]) / max(total_tickets_tested, 1)) * 100, 2)
    }
    return results

if __name__ == "__main__":
    print("Running quick backtest...")
    res = run_backtest(test_draws=30, tickets_per_draw=3, model="harmonic")
    print("Backtest results:", res)
