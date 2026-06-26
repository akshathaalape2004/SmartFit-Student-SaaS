# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import datetime
import models

app = FastAPI(title="AI Fitness SaaS Backend")

# Enable cross-origin communication for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./fitness.db"
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Automatically create tables on execution
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---

@app.post("/register")
def register(payload: dict, db: Session = Depends(get_db)):
    username = payload.get("username")
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists.")
    
    new_user = models.User(
        username=username,
        email=payload.get("email"),
        password_hash=payload.get("password")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Success"}

@app.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.get("username")).first()
    if not user or user.password_hash != payload.get("password"):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {
        "user_id": user.id, "username": user.username,
        "profile": {"age": user.age, "weight_kg": user.weight_kg, "height_cm": user.height_cm, "gender": user.gender, "goal": user.goal, "diet_preference": user.diet_preference, "budget": user.budget}
    }

@app.put("/update-profile/{user_id}")
def update_profile(user_id: int, payload: dict, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    for key, val in payload.items():
        setattr(user, key, val)
    db.commit()
    return {"profile": {"age": user.age, "weight_kg": user.weight_kg, "height_cm": user.height_cm, "gender": user.gender, "goal": user.goal, "diet_preference": user.diet_preference, "budget": user.budget}}

@app.post("/log-metrics/{user_id}")
def log_metrics(user_id: int, water_ml: int, calories: int, db: Session = Depends(get_db)):
    new_log = models.ProgressLog(user_id=user_id, water_ml=water_ml, calories_consumed=calories, timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    db.add(new_log)
    db.commit()
    return {"status": "success"}

# Global temporary in-memory list fallback for forum feed display safety
FORUM_MEM_DB = []

@app.post("/forum-posts")
def create_post(payload: dict):
    post = {
        "username": payload.get("username", "Anonymous"),
        "content": payload.get("content", ""),
        "category": payload.get("category", "General"),
        "timestamp": datetime.datetime.now().strftime("%I:%M %p")
    }
    FORUM_MEM_DB.insert(0, post)
    return {"status": "success"}

@app.get("/forum-posts")
def get_posts():
    return FORUM_MEM_DB

@app.post("/generate-plan/{user_id}")
def generate_plan(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # 📊 Machine Learning Rule-Based Calculation Layer
    modifier = 1.2 if user.goal == "muscle_gain" else 0.8 if user.goal == "weight_loss" else 1.0
    bmr = (10 * user.weight_kg) + (6.25 * user.height_cm) - (5 * user.age)
    target_calories = int(bmr * modifier)
    
    # Mocked Llama-Synthesized Strategic Response Output
    return {
        "calculated_macros": {"Daily Target Calories": f"{target_calories} kcal", "Protein Goal": f"{int(user.weight_kg * 1.8)}g", "Fats Target": "65g"},
        "ai_generated_plan": f"### 🏋️ AI Personalized {user.goal.replace('_',' ')} Routine\n- **Cardio Kick**: 15 min HIIT routine tailored to student dorm constraints.\n- **Compound Sets**: 4 sets of bodyweight squats & diamond pressups.\n- **Diet Tip**: Optimized for **{user.diet_preference}** choices within a **{user.budget}** cost framework.",
        "shopping_list": f"### 🛒 Budget Grocery Checklist ({user.budget} Cost Selection)\n- Whole eggs or Tofu Blocks\n- Bulk Brown Rice & Canned Chickpeas\n- Frozen Medley Greens (High Micronutrient Yield/Low Cost)"
    }