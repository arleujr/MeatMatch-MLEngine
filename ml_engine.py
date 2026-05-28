import pandas as pd
from database import get_user_events, update_user_multipliers

def process_user_feedback_loop(user_id: str) -> int:
    """
    Core ML Engine workflow:
    1. Fetches historical BBQ data for the user.
    2. Constructs a Pandas DataFrame to analyze variance (Actual vs Estimated).
    3. Calculates an adjusted moving average for item weights.
    4. Upserts the new multipliers into the database.
    """
    events = get_user_events(user_id)
    if not events:
        return 0
        
    data = []
    
    # Extract data into a flat structure for Pandas
    for event in events:
        estimated = event.get("results_data", {})
        actual = event.get("actual_data", {})
        
        for item, est_qty in estimated.items():
            if item in actual and "actualQty" in actual[item]:
                act_qty = actual[item]["actualQty"]
                if est_qty > 0: # Prevent division by zero
                    data.append({
                        "item": item,
                        "ratio": act_qty / est_qty
                    })
                    
    if not data:
        return 0
        
    # Load into a DataFrame for vectorized operations
    df = pd.DataFrame(data)
    
    # Calculate the mean ratio per item. 
    # For advanced versions, Scikit-learn can be injected here for predictive regression based on seasonality.
    summary = df.groupby("item")["ratio"].mean().reset_index()
    
    updated_count = 0
    for _, row in summary.iterrows():
        item = row["item"]
        raw_weight = row["ratio"]
        
        # Guardrail: Bound the multiplier between 0.5x and 2.0x 
        # This prevents a single crazy party from destroying the algorithm's sanity
        safe_weight = max(0.5, min(2.0, float(raw_weight)))
        
        # Persist the new learned behavior to the database
        update_user_multipliers(user_id, item, safe_weight)
        updated_count += 1
        
    return updated_count