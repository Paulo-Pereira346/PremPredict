from pathlib import Path
import sys

file_path = Path(__file__).resolve()
root = file_path.parents[0]
sys.path.insert(0, str(root))

from processing_API.update_data import update_epl_data
from processing_API.update_elo import compute_elo
from processing.pre_rolling import pre_rolling_dataset
from processing.rolling_features import rolling_features
from processing.build_match_dataset import build_match_dataset
from src.poisson_prediction import retrain_and_save


def run_full_pipeline():
    print("=== Step 1: Downloading new match data ===")
    has_new_data = update_epl_data()
    
    if not has_new_data:
        print("No new data. Pipeline stopped.")
        return
    
    print("=== Step 2: Recomputing Elo ratings ===")
    compute_elo()
    
    print("=== Step 3: Building pre-rolling dataset ===")
    pre_rolling_dataset()
    
    print("=== Step 4: Computing rolling features ===")
    rolling_features() 
    
    print("=== Step 5: Building final dataset ===")
    build_match_dataset()
    
    print("=== Step 6: Retraining models ===")
    retrain_and_save()
    
    print("=== Pipeline complete ===")

if __name__ == "__main__":
    run_full_pipeline()