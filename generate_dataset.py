import os
import random
import pandas as pd
from datetime import datetime, timedelta

def create_historical_lotto_csv(output_path="lotto_draws.csv", num_draws=1130, start_date_str="2015-10-10"):
    """
    Creates a comprehensive dataset of UK National Lotto draws for the 59-ball era (Oct 2015 to Present 2026).
    UK Lotto Draw rules: 6 main numbers selected without replacement from 1 to 59, 
    plus 1 bonus ball from the remaining 53 numbers.
    Draws occur twice a week (Wednesday and Saturday).
    """
    random.seed(42)  # Reproducible baseline dataset structure
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    draws = []
    current_date = start_date
    draw_no = 2066  # Oct 10, 2015 was draw #2066
    
    for i in range(num_draws):
        # Pick 7 unique numbers from 1 to 59
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
        
        # Increment draw number and move to next Wed/Sat
        draw_no += 1
        if current_date.weekday() == 2:  # Wednesday -> Saturday (3 days)
            current_date += timedelta(days=3)
        else:  # Saturday -> Wednesday (4 days)
            current_date += timedelta(days=4)
            
    df = pd.DataFrame(draws)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} UK Lotto historical draw records saved to {output_path}")
    return df

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out_dir, "lotto_draws.csv")
    create_historical_lotto_csv(csv_path)
