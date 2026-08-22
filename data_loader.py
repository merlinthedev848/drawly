import os
import pandas as pd
import numpy as np
from datetime import datetime
from generate_dataset import create_historical_lotto_csv, create_irish_lotto_csv, create_euromillions_lotto_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UK_DATA_FILE = os.path.join(BASE_DIR, "lotto_draws.csv")
IRISH_DATA_FILE = os.path.join(BASE_DIR, "irish_lotto_draws.csv")
EUROMILLIONS_DATA_FILE = os.path.join(BASE_DIR, "euromillions_draws.csv")

def load_lotto_data(game_type="uk", file_path=None):
    """
    Loads UK Lotto (1-59), Irish Lotto (1-47), or EuroMillions (1-50 main + 2 stars) draw dataset.
    Handles mixed date formats robustly.
    """
    if file_path is None:
        if game_type == "irish":
            file_path = IRISH_DATA_FILE
        elif game_type == "euromillions":
            file_path = EUROMILLIONS_DATA_FILE
        else:
            file_path = UK_DATA_FILE

    if not os.path.exists(file_path):
        if game_type == "irish":
            create_irish_lotto_csv(file_path)
        elif game_type == "euromillions":
            create_euromillions_lotto_csv(file_path)
        else:
            create_historical_lotto_csv(file_path)

    df = pd.read_csv(file_path)
    df['draw_date'] = pd.to_datetime(df['draw_date'], format='mixed', errors='coerce')
    df = df.sort_values('draw_date', ascending=True).reset_index(drop=True)

    if game_type == "euromillions":
        ball_cols = ['ball_1', 'ball_2', 'ball_3', 'ball_4', 'ball_5']
    else:
        ball_cols = ['ball_1', 'ball_2', 'ball_3', 'ball_4', 'ball_5', 'ball_6']

    draw_matrix = df[ball_cols].values
    return df, draw_matrix

if __name__ == "__main__":
    df_uk, _ = load_lotto_data("uk")
    df_ie, _ = load_lotto_data("irish")
    df_euro, _ = load_lotto_data("euromillions")
    print(f"Loaded UK Lotto: {len(df_uk)} draws | Irish Lotto: {len(df_ie)} draws | EuroMillions: {len(df_euro)} draws")
