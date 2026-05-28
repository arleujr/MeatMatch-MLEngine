import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from the .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in .env file.")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_events(user_id: str):
    """
    Fetches all completed BBQ events for a specific user to train the ML model.
    We only fetch events that have 'actual_data' (meaning the receipt was filled).
    """
    response = supabase.table("bbq_events").select("*").eq("user_id", user_id).not_.is_null("actual_data").execute()
    return response.data

def update_user_multipliers(user_id: str, item_category: str, new_weight: float):
    """
    Upserts the new personalized multiplier weight for a specific item into the database.
    """
    data = {
        "user_id": user_id,
        "item_category": item_category,
        "weight_modifier": new_weight
    }
    # Uses upsert: if the row exists, it updates. If not, it inserts.
    response = supabase.table("user_ml_multipliers").upsert(data).execute()
    return response.data