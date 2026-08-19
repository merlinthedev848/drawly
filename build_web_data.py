import json
import os
import numpy as np
import pandas as pd
from data_loader import load_lotto_data
from stats_engine import (
    compute_ball_frequencies, 
    compute_gap_statistics, 
    compute_cooccurrence_matrix, 
    perform_chi_square_test,
    compute_number_likelihoods,
    TOTAL_BALLS,
    THEO_DRAW_PROB,
    EXPECTED_GAP
)
from horse_racing_engine import get_preset_races, calculate_horse_likelihoods

def build_export_data():
    df_raw, draw_matrix = load_lotto_data()
    
    df_freq = compute_ball_frequencies(draw_matrix)
    df_gaps = compute_gap_statistics(draw_matrix)
    cooc_matrix = compute_cooccurrence_matrix(draw_matrix)
    chi_square = perform_chi_square_test(df_freq, len(df_raw))
    
    df_lh_harmonic = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model="harmonic")
    df_lh_hot = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model="hot")
    df_lh_cold = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model="cold")

    # Format draws for JSON
    recent_draws = []
    for idx, row in df_raw.iloc[::-1].iterrows():
        recent_draws.append({
            'draw_number': int(row['draw_number']),
            'date': row['draw_date'].strftime('%Y-%m-%d'),
            'day': row['day_of_week'],
            'balls': [int(row[f'ball_{i}']) for i in range(1, 7)],
            'bonus': int(row['bonus_ball'])
        })

    # Prepare ball statistics array (1 to 59)
    ball_stats = []
    for b in range(1, TOTAL_BALLS + 1):
        f_row = df_freq[df_freq['ball'] == b].iloc[0]
        g_row = df_gaps[df_gaps['ball'] == b].iloc[0]
        lh_harm = df_lh_harmonic[df_lh_harmonic['ball'] == b].iloc[0]['likelihood_pct']
        lh_hot = df_lh_hot[df_lh_hot['ball'] == b].iloc[0]['likelihood_pct']
        lh_cold = df_lh_cold[df_lh_cold['ball'] == b].iloc[0]['likelihood_pct']
        
        # Top 3 pairs for this ball
        pairs = cooc_matrix[b - 1]
        top_pair_indices = np.argsort(pairs)[::-1]
        top_pairs = []
        for idx in top_pair_indices:
            if idx + 1 != b and len(top_pairs) < 3:
                top_pairs.append({'partner': int(idx + 1), 'count': int(pairs[idx])})

        ball_stats.append({
            'ball': b,
            'count': int(f_row['count']),
            'rate_pct': float(np.round(f_row['rate_pct'], 2)),
            'current_gap': int(g_row['current_gap']),
            'max_gap': int(g_row['max_gap']),
            'mean_gap': float(g_row['mean_gap']),
            'gap_ratio': float(g_row['gap_ratio']),
            'likelihood_harmonic': float(lh_harm),
            'likelihood_hot': float(lh_hot),
            'likelihood_cold': float(lh_cold),
            'likelihood_equal': float(np.round(THEO_DRAW_PROB * 100, 2)),
            'top_pairs': top_pairs
        })

    # Build horse racing preset datasets
    preset_races = get_preset_races()
    for race in preset_races:
        race['analyzed_runners'] = calculate_horse_likelihoods(race['runners'])

    data_payload = {
        'total_draws': len(df_raw),
        'start_date': df_raw['draw_date'].min().strftime('%Y-%m-%d'),
        'end_date': df_raw['draw_date'].max().strftime('%Y-%m-%d'),
        'expected_gap': EXPECTED_GAP,
        'theo_draw_prob': float(np.round(THEO_DRAW_PROB * 100, 2)),
        'chi_square': chi_square,
        'ball_stats': ball_stats,
        'cooccurrence_matrix': cooc_matrix.tolist(),
        'recent_draws': recent_draws[:50],  # top 50 recent draws
        'horse_racing': {
            'preset_races': preset_races
        }
    }
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(out_dir, "lotto_data.json")
    with open(json_path, "w") as f:
        json.dump(data_payload, f, indent=2)
        
    print(f"Exported dataset JSON with Horse Racing to {json_path}")
    return data_payload

if __name__ == "__main__":
    build_export_data()
