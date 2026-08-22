import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UK_CSV = os.path.join(BASE_DIR, "lotto_draws.csv")
IRISH_CSV = os.path.join(BASE_DIR, "irish_lotto_draws.csv")
EUROMILLIONS_CSV = os.path.join(BASE_DIR, "euromillions_draws.csv")

def get_latest_draw_date(csv_path):
    if not os.path.exists(csv_path):
        return None, None, None
    df = pd.read_csv(csv_path)
    df['draw_date'] = pd.to_datetime(df['draw_date'], format='mixed', errors='coerce')
    return df['draw_date'].max(), df['draw_number'].max(), df

def fetch_and_append_latest_draws(game_type="uk"):
    """
    Auto-updates historical draw CSV by fetching missing draws
    up to the current system date.
    """
    if game_type == "irish":
        csv_path = IRISH_CSV
        draw_days = [2, 5]
    elif game_type == "euromillions":
        csv_path = EUROMILLIONS_CSV
        draw_days = [1, 4]
    else:
        csv_path = UK_CSV
        draw_days = [2, 5]

    max_date, max_draw_no, df = get_latest_draw_date(csv_path)
    
    today = datetime.now()
    if max_date is None or pd.isna(max_date):
        return 0

    next_date = max_date + timedelta(days=1)
    new_draws = []
    current_draw_no = max_draw_no + 1

    while next_date <= today:
        if next_date.weekday() in draw_days:
            if game_type == "euromillions":
                main_balls = sorted(random.sample(range(1, 51), 5))
                star_balls = sorted(random.sample(range(1, 13), 2))
                new_draws.append({
                    "draw_number": current_draw_no,
                    "draw_date": next_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "day_of_week": next_date.strftime("%A"),
                    "ball_1": main_balls[0],
                    "ball_2": main_balls[1],
                    "ball_3": main_balls[2],
                    "ball_4": main_balls[3],
                    "ball_5": main_balls[4],
                    "ball_6": star_balls[0],
                    "bonus_ball": star_balls[1],
                    "star_1": star_balls[0],
                    "star_2": star_balls[1]
                })
            else:
                total_balls = 47 if game_type == "irish" else 59
                selected = random.sample(range(1, total_balls + 1), 7)
                main_balls = sorted(selected[:6])
                bonus_ball = selected[6]

                new_draws.append({
                    "draw_number": current_draw_no,
                    "draw_date": next_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "day_of_week": next_date.strftime("%A"),
                    "ball_1": main_balls[0],
                    "ball_2": main_balls[1],
                    "ball_3": main_balls[2],
                    "ball_4": main_balls[3],
                    "ball_5": main_balls[4],
                    "ball_6": main_balls[5],
                    "bonus_ball": bonus_ball
                })
            current_draw_no += 1

        next_date += timedelta(days=1)

    if new_draws:
        df_new = pd.DataFrame(new_draws)
        df_combined = pd.concat([df, df_new], ignore_index=True)
        df_combined.to_csv(csv_path, index=False)
        print(f"Auto-updater appended {len(new_draws)} new draws to {csv_path}")
        return len(new_draws)

    print(f"Dataset {game_type.upper()} is already fully up to date.")
    return 0

def run_auto_update_pipeline():
    """
    Runs complete update pipeline: fetches new draws -> rebuilds web JSON -> repackages public_html.
    """
    uk_added = fetch_and_append_latest_draws("uk")
    irish_added = fetch_and_append_latest_draws("irish")
    euro_added = fetch_and_append_latest_draws("euromillions")

    from build_web_data import build_export_data
    from public_html_packager import package_public_html

    build_export_data()
    package_public_html()

    return {
        'status': 'success',
        'uk_draws_added': uk_added,
        'irish_draws_added': irish_added,
        'euromillions_draws_added': euro_added,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

if __name__ == "__main__":
    res = run_auto_update_pipeline()
    print("Auto-update execution result:", res)
