import numpy as np
import pandas as pd
from scipy import stats

def compute_ball_frequencies(draw_matrix, total_balls=59, balls_drawn=6):
    """
    Computes empirical frequency count, rate, and ratio for all balls (1 to total_balls).
    """
    num_draws = len(draw_matrix)
    counts = np.zeros(total_balls + 1, dtype=int)
    theo_draw_prob = float(balls_drawn) / total_balls

    for row in draw_matrix:
        for ball in row:
            if 1 <= ball <= total_balls:
                counts[ball] += 1

    counts = counts[1:]
    expected_count = num_draws * theo_draw_prob
    rates = counts / max(num_draws, 1)
    ratios = counts / max(expected_count, 1e-6)

    df_freq = pd.DataFrame({
        'ball': np.arange(1, total_balls + 1),
        'count': counts,
        'rate': rates,
        'rate_pct': rates * 100,
        'expected_count': expected_count,
        'freq_ratio': ratios
    })
    return df_freq

def compute_gap_statistics(draw_matrix, total_balls=59, balls_drawn=6):
    """
    Computes recency gap statistics for each ball (1 to total_balls).
    """
    num_draws = len(draw_matrix)
    expected_gap = total_balls / float(balls_drawn)
    current_gaps = np.zeros(total_balls + 1, dtype=int)
    max_gaps = np.zeros(total_balls + 1, dtype=int)
    gap_lists = [[] for _ in range(total_balls + 1)]

    last_seen = np.full(total_balls + 1, -1, dtype=int)

    for idx, row in enumerate(draw_matrix):
        drawn_set = set(row)
        for ball in range(1, total_balls + 1):
            if ball in drawn_set:
                if last_seen[ball] != -1:
                    gap = idx - last_seen[ball] - 1
                    gap_lists[ball].append(gap)
                    if gap > max_gaps[ball]:
                        max_gaps[ball] = gap
                last_seen[ball] = idx

    for ball in range(1, total_balls + 1):
        if last_seen[ball] == -1:
            current_gaps[ball] = num_draws
        else:
            current_gaps[ball] = num_draws - 1 - last_seen[ball]

    mean_gaps = np.zeros(total_balls + 1, dtype=float)
    for ball in range(1, total_balls + 1):
        if len(gap_lists[ball]) > 0:
            mean_gaps[ball] = np.mean(gap_lists[ball])
        else:
            mean_gaps[ball] = expected_gap

    df_gaps = pd.DataFrame({
        'ball': np.arange(1, total_balls + 1),
        'current_gap': current_gaps[1:],
        'max_gap': max_gaps[1:],
        'mean_gap': np.round(mean_gaps[1:], 2),
        'expected_gap': np.round(expected_gap, 2),
        'gap_ratio': np.round(current_gaps[1:] / expected_gap, 2)
    })
    return df_gaps

def compute_cooccurrence_matrix(draw_matrix, total_balls=59):
    """
    Computes pair co-occurrence matrix for total_balls.
    """
    matrix = np.zeros((total_balls, total_balls), dtype=int)
    for row in draw_matrix:
        valid_balls = [b - 1 for b in row if 1 <= b <= total_balls]
        for i in range(len(valid_balls)):
            for j in range(i + 1, len(valid_balls)):
                b1, b2 = valid_balls[i], valid_balls[j]
                matrix[b1, b2] += 1
                matrix[b2, b1] += 1
    return matrix

def perform_chi_square_test(df_freq, num_draws, total_balls=59, balls_drawn=6):
    """
    Performs Chi-Square Goodness-of-Fit test against uniform expected frequencies.
    """
    observed = df_freq['count'].values
    expected = np.full(total_balls, float(np.sum(observed)) / float(total_balls))
    
    chi2_stat, p_val = stats.chisquare(f_obs=observed, f_exp=expected)
    return {
        'chi2_stat': float(chi2_stat),
        'p_value': float(p_val),
        'dof': total_balls - 1,
        'is_uniform': bool(p_val > 0.05)
    }

def compute_number_likelihoods(df_freq, df_gaps, cooc_matrix=None, model="harmonic", weights=None, total_balls=59, balls_drawn=6):
    """
    Calculates likelihood probabilities P(ball_i drawn) for total_balls.
    """
    if weights is None:
        weights = {'base': 0.3, 'hot': 0.3, 'cold': 0.3, 'pair': 0.1}

    theo_draw_prob = float(balls_drawn) / total_balls
    num_draws = df_freq['count'].sum() / float(balls_drawn) if balls_drawn > 0 else 1.0

    p_base = np.full(total_balls, theo_draw_prob)

    raw_hot = df_freq['rate'].values
    p_hot = (raw_hot / np.sum(raw_hot)) * float(balls_drawn) if np.sum(raw_hot) > 0 else p_base

    gap_ratios = df_gaps['gap_ratio'].values
    raw_cold = np.exp(0.5 * gap_ratios)
    p_cold = (raw_cold / np.sum(raw_cold)) * float(balls_drawn)

    if cooc_matrix is not None:
        raw_pair = np.sum(cooc_matrix, axis=1) / max(num_draws, 1)
        p_pair = (raw_pair / np.sum(raw_pair)) * float(balls_drawn) if np.sum(raw_pair) > 0 else p_base
    else:
        p_pair = p_base

    if model == "equal":
        p_final = p_base
    elif model == "hot":
        p_final = p_hot
    elif model == "cold":
        p_final = p_cold
    elif model == "harmonic":
        p_final = (0.25 * p_base) + (0.35 * p_hot) + (0.3 * p_cold) + (0.1 * p_pair)
    else:
        p_final = p_base

    p_final = np.clip(p_final, 0.001, 0.99)
    p_final = (p_final / np.sum(p_final)) * float(balls_drawn)

    df_likelihood = pd.DataFrame({
        'ball': np.arange(1, total_balls + 1),
        'likelihood_pct': np.round(p_final * 100, 2),
        'draw_prob': p_final,
        'freq_count': df_freq['count'].values,
        'current_gap': df_gaps['current_gap'].values,
        'gap_ratio': df_gaps['gap_ratio'].values
    })
    return df_likelihood.sort_values('draw_prob', ascending=False).reset_index(drop=True)
