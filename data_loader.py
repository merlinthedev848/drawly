import os
import pandas as pd
import numpy as np
from datetime import datetime
from generate_dataset import create_historical_lotto_csv

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lotto_draws.csv")

def load_lotto_data(file_path=DATA_FILE, include_bonus=False):
    """
    Loads UK Lotto historical draw data from CSV.
    Ensures dataset is sorted by date ascending.
    Returns:
        df (DataFrame): Full raw dataframe
        draw_matrix (np.ndarray): 2D array of shape (N_draws, 6) or (N_draws, 7) containing main/bonus ball numbers.
    """
    if not os.path.exists(file_path):
        create_historical_lotto_csv(file_path)

    df = pd.read_csv(file_path)
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    df = df.sort_values('draw_date', ascending=True).reset_index(drop=True)

    ball_cols = ['ball_1', 'ball_2', 'ball_3', 'ball_4', 'ball_5', 'ball_6']
    if include_bonus:
        ball_cols.append('bonus_ball')

    draw_matrix = df[ball_cols].values
    return df, draw_matrix

def filter_data_by_window(df, window_size=None, start_date=None, end_date=None):
    """
    Filters draw dataframe by a rolling window count (e.g. last N draws) or date range.
    """
    filtered_df = df.copy()

    if start_date:
        filtered_df = filtered_df[filtered_df['draw_date'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['draw_date'] <= pd.to_datetime(end_date)]

    if window_size and window_size < len(filtered_df):
        filtered_df = filtered_df.iloc[-window_size:]

    filtered_df = filtered_df.reset_index(drop=True)
    ball_cols = ['ball_1', 'ball_2', 'ball_3', 'ball_4', 'ball_5', 'ball_6']
    matrix = filtered_df[ball_cols].values
    return filtered_df, matrix

if __name__ == "__main__":
    df, matrix = load_lotto_data()
    print(f"Loaded {len(df)} draws from {df['draw_date'].min().strftime('%Y-%m-%d')} to {df['draw_date'].max().strftime('%Y-%m-%d')}")
    print("Sample matrix row:", matrix[-1])
