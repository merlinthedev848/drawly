import numpy as np
import pandas as pd
from scipy import stats

TOTAL_BALLS = 59
BALLS_PER_DRAW = 6
THEO_DRAW_PROB = BALLS_PER_DRAW / TOTAL_BALLS  # 6 / 59 = ~0.1016949 (10.169%)
THEO_SLOT_PROB = 1.0 / TOTAL_BALLS  # 1 / 59 = ~0.016949 (1.695%)
EXPECTED_GAP = 1.0 / THEO_DRAW_PROB  # ~9.8333 draws

def compute_ball_frequencies(draw_matrix):
    """
    Computes empirical frequency count, rate, and ratio vs expected for all 59 balls.
    """
    num_draws = len(draw_matrix)
    counts = np.zeros(TOTAL_BALLS + 1, dtype=int)

    for row in draw_matrix:
        for ball in row:
            if 1 <= ball <= TOTAL_BALLS:
                counts[ball] += 1

    counts = counts[1:]  # 1-indexed to 59
    expected_count = num_draws * THEO_DRAW_PROB
    rates = counts / max(num_draws, 1)
    ratios = counts / max(expected_count, 1e-6)

    df_freq = pd.DataFrame({
        'ball': np.arange(1, TOTAL_BALLS + 1),
        'count': counts,
        'rate': rates,
        'rate_pct': rates * 100,
        'expected_count': expected_count,
        'freq_ratio': ratios
    })
    return df_freq

def compute_gap_statistics(draw_matrix):
    """
    Computes recency gap statistics for each ball:
    - current_gap: draws since last drawn
    - max_gap: maximum draw gap between appearances
    - mean_gap: average gap duration
    - gap_ratio: current_gap / EXPECTED_GAP
    """
    num_draws = len(draw_matrix)
    current_gaps = np.zeros(TOTAL_BALLS + 1, dtype=int)
    max_gaps = np.zeros(TOTAL_BALLS + 1, dtype=int)
    gap_lists = [[] for _ in range(TOTAL_BALLS + 1)]

    last_seen = np.full(TOTAL_BALLS + 1, -1, dtype=int)

    for idx, row in enumerate(draw_matrix):
        drawn_set = set(row)
        for ball in range(1, TOTAL_BALLS + 1):
            if ball in drawn_set:
                if last_seen[ball] != -1:
                    gap = idx - last_seen[ball] - 1
                    gap_lists[ball].append(gap)
                    if gap > max_gaps[ball]:
                        max_gaps[ball] = gap
                last_seen[ball] = idx

    for ball in range(1, TOTAL_BALLS + 1):
        if last_seen[ball] == -1:
            current_gaps[ball] = num_draws
        else:
            current_gaps[ball] = num_draws - 1 - last_seen[ball]

    mean_gaps = np.zeros(TOTAL_BALLS + 1, dtype=float)
    for ball in range(1, TOTAL_BALLS + 1):
        if len(gap_lists[ball]) > 0:
            mean_gaps[ball] = np.mean(gap_lists[ball])
        else:
            mean_gaps[ball] = EXPECTED_GAP

    df_gaps = pd.DataFrame({
        'ball': np.arange(1, TOTAL_BALLS + 1),
        'current_gap': current_gaps[1:],
        'max_gap': max_gaps[1:],
        'mean_gap': np.round(mean_gaps[1:], 2),
        'expected_gap': EXPECTED_GAP,
        'gap_ratio': np.round(current_gaps[1:] / EXPECTED_GAP, 2)
    })
    return df_gaps

def compute_cooccurrence_matrix(draw_matrix):
    """
    Computes 59x59 pair co-occurrence matrix counting how often ball i and ball j appeared together.
    """
    matrix = np.zeros((TOTAL_BALLS, TOTAL_BALLS), dtype=int)
    for row in draw_matrix:
        valid_balls = [b - 1 for b in row if 1 <= b <= TOTAL_BALLS]
        for i in range(len(valid_balls)):
            for j in range(i + 1, len(valid_balls)):
                b1, b2 = valid_balls[i], valid_balls[j]
                matrix[b1, b2] += 1
                matrix[b2, b1] += 1
    return matrix

def perform_chi_square_test(df_freq, num_draws):
    """
    Performs Chi-Square Goodness-of-Fit test against uniform expected frequencies.
    """
    observed = df_freq['count'].values
    expected = np.full(TOTAL_BALLS, num_draws * THEO_DRAW_PROB)
    
    chi2_stat, p_val = stats.chisquare(f_obs=observed, f_exp=expected)
    return {
        'chi2_stat': float(chi2_stat),
        'p_value': float(p_val),
        'dof': TOTAL_BALLS - 1,
        'is_uniform': bool(p_val > 0.05)
    }

def compute_number_likelihoods(df_freq, df_gaps, cooccur_matrix=None, model="harmonic", weights=None):
    """
    Calculates likelihood probabilities P(ball_i drawn in next draw) for all 59 balls under different logic models.
    Models:
    - 'equal': Equal theoretical probability (6/59 = 10.169% for each ball)
    - 'hot': Frequency weighted model
    - 'cold': Overdue gap reversion model
    - 'harmonic': Balanced ensemble model
    - 'custom': User defined weights dict {'base': float, 'hot': float, 'cold': float, 'pair': float}
    """
    if weights is None:
        weights = {'base': 0.3, 'hot': 0.3, 'cold': 0.3, 'pair': 0.1}

    num_draws = df_freq['count'].sum() / BALLS_PER_DRAW

    # 1. Base theoretical
    p_base = np.full(TOTAL_BALLS, THEO_DRAW_PROB)

    # 2. Hot model (normalized empirical rate)
    raw_hot = df_freq['rate'].values
    p_hot = (raw_hot / np.sum(raw_hot)) * BALLS_PER_DRAW if np.sum(raw_hot) > 0 else p_base

    # 3. Cold model (exponential weighting by current_gap / expected_gap)
    gap_ratios = df_gaps['gap_ratio'].values
    raw_cold = np.exp(0.5 * gap_ratios)
    p_cold = (raw_cold / np.sum(raw_cold)) * BALLS_PER_DRAW

    # 4. Pair affinity (average cooccurrence rate across matrix)
    if cooccur_matrix is not None:
        raw_pair = np.sum(cooccur_matrix, axis=1) / max(num_draws, 1)
        p_pair = (raw_pair / np.sum(raw_pair)) * BALLS_PER_DRAW if np.sum(raw_pair) > 0 else p_base
    else:
        p_pair = p_base

    if model == "equal":
        p_final = p_base
    elif model == "hot":
        p_final = p_hot
    elif model == "cold":
        p_final = p_cold
    elif model == "pair":
        p_final = p_pair
    elif model == "harmonic":
        p_final = (0.25 * p_base) + (0.35 * p_hot) + (0.3 * p_cold) + (0.1 * p_pair)
    elif model == "custom":
        w_b = weights.get('base', 0.25)
        w_h = weights.get('hot', 0.25)
        w_c = weights.get('cold', 0.25)
        w_p = weights.get('pair', 0.25)
        total_w = w_b + w_h + w_c + w_p
        if total_w == 0:
            total_w = 1.0
        p_final = (w_b * p_base + w_h * p_hot + w_c * p_cold + w_p * p_pair) / total_w
    else:
        p_final = p_base

    # Clip to valid probability bounds [0.001, 0.999] and scale to total draw expectation of 6 balls
    p_final = np.clip(p_final, 0.001, 0.99)
    p_final = (p_final / np.sum(p_final)) * BALLS_PER_DRAW

    df_likelihood = pd.DataFrame({
        'ball': np.arange(1, TOTAL_BALLS + 1),
        'likelihood_pct': np.round(p_final * 100, 2),
        'draw_prob': p_final,
        'slot_prob': p_final / BALLS_PER_DRAW,
        'freq_count': df_freq['count'].values,
        'current_gap': df_gaps['current_gap'].values,
        'gap_ratio': df_gaps['gap_ratio'].values
    })
    return df_likelihood.sort_values('draw_prob', ascending=False).reset_index(drop=True)

if __name__ == "__main__":
    from data_loader import load_lotto_data
    df_raw, matrix = load_lotto_data()
    df_f = compute_ball_frequencies(matrix)
    df_g = compute_gap_statistics(matrix)
    cooc = compute_cooccurrence_matrix(matrix)
    chi = perform_chi_square_test(df_f, len(df_raw))
    lh = compute_number_likelihoods(df_f, df_g, cooc, model="harmonic")
    print("Chi-square result:", chi)
    print("Top 5 Likelihood Balls (Harmonic Model):")
    print(lh.head(5))
