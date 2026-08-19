import os
import random
import pandas as pd
from datetime import datetime, timedelta

def create_historical_lotto_csv(output_path="lotto_draws.csv", num_draws=1130, start_date_str="2015-10-10"):
    """
    UK National Lotto: 6 main numbers from 1 to 59 + 1 bonus ball.
    """
    random.seed(42)
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    draws = []
    current_date = start_date
    draw_no = 2066
    
    for i in range(num_draws):
        selected = random.sample(range(1, 60), 7)
        main_balls = sorted(selected[:6])
        bonus_ball = selected[6]
        
        draws.append({
            "draw_number": draw_no,
            "draw_date": current_date.strftime("%Y-%m-%d"),
            "day_of_week": current_date.strftime("%A"),
            "ball_1": main_balls[0],
            "ball_2": main_balls[1],
            "ball_3": main_balls[2],
            "ball_4": main_balls[3],
            "ball_5": main_balls[4],
            "ball_6": main_balls[5],
            "bonus_ball": bonus_ball
        })
        
        draw_no += 1
        if current_date.weekday() == 2:
            current_date += timedelta(days=3)
        else:
            current_date += timedelta(days=4)
            
    df = pd.DataFrame(draws)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} UK Lotto draw records at {output_path}")
    return df

def create_irish_lotto_csv(output_path="irish_lotto_draws.csv", num_draws=1130, start_date_str="2015-09-05"):
    """
    Irish National Lotto: 6 main numbers from 1 to 47 + 1 bonus ball from 47.
    Format introduced in Sept 2015 (47 ball matrix).
    """
    random.seed(88)
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    draws = []
    current_date = start_date
    draw_no = 2700
    
    for i in range(num_draws):
        selected = random.sample(range(1, 48), 7)
        main_balls = sorted(selected[:6])
        bonus_ball = selected[6]
        
        draws.append({
            "draw_number": draw_no,
            "draw_date": current_date.strftime("%Y-%m-%d"),
            "day_of_week": current_date.strftime("%A"),
            "ball_1": main_balls[0],
            "ball_2": main_balls[1],
            "ball_3": main_balls[2],
            "ball_4": main_balls[3],
            "ball_5": main_balls[4],
            "ball_6": main_balls[5],
            "bonus_ball": bonus_ball
        })
        
        draw_no += 1
        if current_date.weekday() == 2:  # Wed -> Sat
            current_date += timedelta(days=3)
        else:  # Sat -> Wed
            current_date += timedelta(days=4)
            
    df = pd.DataFrame(draws)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} Irish Lotto draw records at {output_path}")
    return df

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    create_historical_lotto_csv(os.path.join(out_dir, "lotto_draws.csv"))
    create_irish_lotto_csv(os.path.join(out_dir, "irish_lotto_draws.csv"))
