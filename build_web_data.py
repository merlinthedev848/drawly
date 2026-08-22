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
    compute_number_likelihoods
)
from horse_racing_engine import get_preset_races, calculate_horse_likelihoods
from stock_explosion_engine import get_preset_explosion_stocks
from football_predictor_engine import get_preset_football_matches
from casino_games_engine import analyze_roulette_wheel, analyze_baccarat_probabilities
from sports_expanded_engine import (
    calculate_euromillions_stats, predict_tennis_match, predict_basketball_nba, 
    predict_greyhound_race, predict_darts_match, predict_snooker_match,
    predict_golf_matchup, predict_cricket_match, predict_boxing_match,
    predict_ufc_match, predict_baseball_mlb, predict_nfl_match
)
from next_draw_predictor import predict_next_draw
from live_fetcher import fetch_live_lotto_data

def process_lotto_game(game_type="uk", total_balls=59):
    balls_drawn = 5 if game_type in ["euromillions", "irish"] else 6
    df_raw, draw_matrix = load_lotto_data(game_type)
    theo_draw_prob = float(balls_drawn) / total_balls
    expected_gap = total_balls / float(balls_drawn)

    df_freq = compute_ball_frequencies(draw_matrix, total_balls=total_balls, balls_drawn=balls_drawn)
    df_gaps = compute_gap_statistics(draw_matrix, total_balls=total_balls, balls_drawn=balls_drawn)
    cooc_matrix = compute_cooccurrence_matrix(draw_matrix, total_balls=total_balls)
    chi_square = perform_chi_square_test(df_freq, len(df_raw), total_balls=total_balls, balls_drawn=balls_drawn)

    df_lh_harmonic = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model="harmonic", total_balls=total_balls, balls_drawn=balls_drawn)
    df_lh_hot = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model="hot", total_balls=total_balls, balls_drawn=balls_drawn)
    df_lh_cold = compute_number_likelihoods(df_freq, df_gaps, cooc_matrix, model="cold", total_balls=total_balls, balls_drawn=balls_drawn)

    recent_draws = []
    hist_balls = 6 if game_type == "irish" else balls_drawn
    for idx, row in df_raw.iloc[-25:][::-1].iterrows():
        draw_obj = {
            'draw_number': int(row['draw_number']),
            'date': row['draw_date'].strftime('%Y-%m-%d'),
            'day': row['day_of_week'],
            'balls': [int(row[f'ball_{i}']) for i in range(1, hist_balls + 1)],
            'bonus': int(row['star_1']) if game_type == "euromillions" else int(row['bonus_ball'])
        }
        if game_type == "euromillions" and 'star_1' in row and 'star_2' in row:
            draw_obj['stars'] = [int(row['star_1']), int(row['star_2'])]
        recent_draws.append(draw_obj)

    ball_stats = []
    for b in range(1, total_balls + 1):
        f_row = df_freq[df_freq['ball'] == b].iloc[0]
        g_row = df_gaps[df_gaps['ball'] == b].iloc[0]
        lh_harm = df_lh_harmonic[df_lh_harmonic['ball'] == b].iloc[0]['likelihood_pct']
        lh_hot = df_lh_hot[df_lh_hot['ball'] == b].iloc[0]['likelihood_pct']
        lh_cold = df_lh_cold[df_lh_cold['ball'] == b].iloc[0]['likelihood_pct']

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
            'likelihood_equal': float(np.round(theo_draw_prob * 100, 2)),
            'top_pairs': top_pairs
        })

    next_draw_pred = predict_next_draw(game_type)

    return {
        'game_type': game_type,
        'total_balls': total_balls,
        'balls_drawn': balls_drawn,
        'total_draws': len(df_raw),
        'start_date': df_raw['draw_date'].min().strftime('%Y-%m-%d'),
        'end_date': df_raw['draw_date'].max().strftime('%Y-%m-%d'),
        'expected_gap': float(np.round(expected_gap, 2)),
        'theo_draw_prob': float(np.round(theo_draw_prob * 100, 2)),
        'chi_square': chi_square,
        'ball_stats': ball_stats,
        'recent_draws': recent_draws,
        'next_draw_prediction': next_draw_pred
    }

def build_export_data():
    uk_lotto = process_lotto_game("uk", 59)
    irish_lotto = process_lotto_game("irish", 47)
    euromillions_lotto = process_lotto_game("euromillions", 50)
    live_meta = fetch_live_lotto_data()

    preset_races = get_preset_races()
    for race in preset_races:
        race['analyzed_runners'] = calculate_horse_likelihoods(race['runners'])

    preset_stocks = get_preset_explosion_stocks()
    preset_football = get_preset_football_matches()

    roulette_data = analyze_roulette_wheel()
    baccarat_data = analyze_baccarat_probabilities()
    euromillions_data = calculate_euromillions_stats()
    tennis_match = predict_tennis_match("Jannik Sinner", "Carlos Alcaraz", surface="Hard", rank_a=1, rank_b=3)
    nba_game = predict_basketball_nba("Boston Celtics", "Denver Nuggets", line_spread=-4.5, line_total=221.0)
    greyhound_race = predict_greyhound_race()
    darts_match = predict_darts_match()
    snooker_match = predict_snooker_match()
    golf_match = predict_golf_matchup()
    cricket_match = predict_cricket_match()
    boxing_match = predict_boxing_match()
    ufc_match = predict_ufc_match()
    baseball_match = predict_baseball_mlb()
    nfl_match = predict_nfl_match()

    data_payload = {
        'live_meta': live_meta,
        'total_draws': uk_lotto['total_draws'],
        'start_date': uk_lotto['start_date'],
        'end_date': uk_lotto['end_date'],
        'expected_gap': uk_lotto['expected_gap'],
        'theo_draw_prob': uk_lotto['theo_draw_prob'],
        'chi_square': uk_lotto['chi_square'],
        'ball_stats': uk_lotto['ball_stats'],
        'recent_draws': uk_lotto['recent_draws'],
        'next_draw_prediction': uk_lotto['next_draw_prediction'],
        'lotto_games': {
            'uk': uk_lotto,
            'irish': irish_lotto,
            'euromillions': euromillions_lotto
        },
        'horse_racing': {
            'preset_races': preset_races
        },
        'stock_radar': {
            'stocks': preset_stocks
        },
        'football_predictor': {
            'matches': preset_football
        },
        'casino': {
            'roulette': roulette_data,
            'baccarat': baccarat_data
        },
        'expanded_sports': {
            'euromillions': euromillions_data,
            'tennis': tennis_match,
            'nba': nba_game,
            'greyhound': greyhound_race,
            'darts': darts_match,
            'snooker': snooker_match,
            'golf': golf_match,
            'cricket': cricket_match,
            'boxing': boxing_match,
            'ufc': ufc_match,
            'baseball': baseball_match,
            'nfl': nfl_match
        }
    }
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(out_dir, "lotto_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_payload, f, separators=(',', ':'))
        
    print(f"Exported dataset JSON with Live Next Draw Predictions to {json_path}")
    return data_payload

if __name__ == "__main__":
    build_export_data()
