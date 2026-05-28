from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import WebhookPayload, MLResponse
from ml_engine import process_user_feedback_loop

app = FastAPI(
    title="MeatMatch ML Engine",
    description="Predictive consumption API for BBQ planning",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://seu-dominio-futuro.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "system": "MeatMatch ML Engine Active"}

@app.post("/api/ml/train", response_model=MLResponse)
def train_user_model(payload: WebhookPayload):
    """
    Webhook endpoint triggered by the Next.js frontend after a user saves receipt actuals.
    It triggers the ML pipeline to recalculate and store user-specific consumption multipliers.
    """
    try:
        updated_items = process_user_feedback_loop(payload.user_id)
        return MLResponse(
            status="success", 
            message="Model trained and multipliers updated successfully.", 
            updated_items=updated_items
        )
    except Exception as e:
        # Return a 500 Internal Server Error if the ML pipeline fails
        raise HTTPException(status_code=500, detail=str(e))