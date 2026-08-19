import os
import pandas as pd
import numpy as np
from datetime import datetime
from generate_dataset import create_historical_lotto_csv, create_irish_lotto_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UK_DATA_FILE = os.path.join(BASE_DIR, "lotto_draws.csv")
IRISH_DATA_FILE = os.path.join(BASE_DIR, "irish_lotto_draws.csv")

def load_lotto_data(game_type="uk", file_path=None):
    """
    Loads UK Lotto (1-59) or Irish Lotto (1-47) draw dataset.
    """
    if file_path is None:
        file_path = IRISH_DATA_FILE if game_type == "irish" else UK_DATA_FILE

    if not os.path.exists(file_path):
        if game_type == "irish":
            create_irish_lotto_csv(file_path)
        else:
            create_historical_lotto_csv(file_path)

    df = pd.read_csv(file_path)
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    df = df.sort_values('draw_date', ascending=True).reset_index(drop=True)

    ball_cols = ['ball_1', 'ball_2', 'ball_3', 'ball_4', 'ball_5', 'ball_6']
    draw_matrix = df[ball_cols].values
    return df, draw_matrix

if __name__ == "__main__":
    df_uk, _ = load_lotto_data("uk")
    df_ie, _ = load_lotto_data("irish")
    print(f"Loaded UK Lotto: {len(df_uk)} draws | Irish Lotto: {len(df_ie)} draws")
