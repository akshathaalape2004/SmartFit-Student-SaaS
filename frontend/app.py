# frontend/app.py
import streamlit as st
import requests

st.set_page_config(page_title="AI Fitness SaaS Platform", layout="centered")

BACKEND_URL = "http://127.0.0.1:8000"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.profile = {}

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.title("🔐 Welcome to AI Fitness SaaS")
    auth_mode = st.radio("Choose Action:", ["Login", "Register"])
    
    with st.form("auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if auth_mode == "Register":
            email = st.text_input("Email Address")
        submit_auth = st.form_submit_button(auth_mode)
        
    if submit_auth:
        if auth_mode == "Register":
            payload = {"username": username, "email": email, "password": password}
            try:
                res = requests.post(f"{BACKEND_URL}/register", json=payload)
                if res.status_code == 200: st.success("Account created! Switch to Login mode.")
                else: st.error(res.json().get("detail", "Registration failed"))
            except: st.error("Backend offline. Cannot register.")
                
        elif auth_mode == "Login":
            payload = {"username": username, "password": password}
            try:
                res = requests.post(f"{BACKEND_URL}/login", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.logged_in = True
                    st.session_state.user_id = data["user_id"]
                    st.session_state.username = data["username"]
                    st.session_state.profile = data["profile"]
                    st.rerun()
                else: st.error("Invalid credentials.")
            except: st.error("Backend Server Unreachable.")

# --- MAIN DASHBOARD ---
else:
    st.sidebar.title(f"👋 Hi, {st.session_state.username}!")
    st.sidebar.write("**Target Niche:** Budget Student SaaS")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.title("🏋️‍♂️ Your AI Personal Coaching Dashboard")
    
    # ⚙️ PROFILE SECTION
    with st.expander("⚙️ Edit / Complete Your Fitness Profile Metrics"):
        p = st.session_state.profile
        db_age = int(p.get("age", 22))
        default_age = db_age if db_age >= 10 else 22
        db_w = float(p.get("weight_kg", 70.0))
        default_w = db_w if db_w >= 30.0 else 70.0
        db_h = float(p.get("height_cm", 175.0))
        default_h = db_h if db_h >= 100.0 else 175.0

        with st.form("profile_update_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_age = st.number_input("Age", min_value=10, max_value=100, value=default_age)
                new_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=default_w)
                new_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=default_h)
                new_gender = st.selectbox("Gender", ["Male", "Female"], index=0 if p.get("gender") == "Male" else 1)
            with col2:
                new_goal = st.selectbox("Fitness Goal", ["weight_loss", "muscle_gain", "maintenance"], index=["weight_loss", "muscle_gain", "maintenance"].index(p.get("goal", "weight_loss")))
                new_diet = st.selectbox("Diet Preference", ["Vegetarian", "Vegan", "Non-Vegetarian"], index=["Vegetarian", "Vegan", "Non-Vegetarian"].index(p.get("diet_preference", "Vegetarian")))
                new_budget = st.selectbox("Budget", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(p.get("budget", "Low")))
            
            if st.form_submit_button("Save & Update Metrics"):
                update_payload = {"age": new_age, "weight_kg": new_weight, "height_cm": new_height, "gender": new_gender, "goal": new_goal, "diet_preference": new_diet, "budget": new_budget}
                res = requests.put(f"{BACKEND_URL}/update-profile/{st.session_state.user_id}", json=update_payload)
                if res.status_code == 200:
                    st.session_state.profile = res.json()["profile"]
                    st.success("Profile saved successfully!")
                    st.rerun()

    st.write("---")
    tab1, tab2, tab3 = st.tabs(["🤖 AI Planner", "📈 Daily Trackers", "💬 Community Forum"])
    
    with tab1:
        st.subheader("📋 Generate your Custom Budget Fitness Strategy")
        curr_p = st.session_state.profile
        st.info(f"🧬 **Current Profile:** Goal: {curr_p.get('goal','').replace('_',' ')} | Diet: {curr_p.get('diet_preference')} | Budget: {curr_p.get('budget')}")
        
        if st.button("Generate My Dynamic AI Plan", type="primary"):
            with st.spinner("Analyzing profile configurations..."):
                try:
                    res = requests.post(f"{BACKEND_URL}/generate-plan/{st.session_state.user_id}")
                    if res.status_code == 200:
                        st.session_state.latest_plan = res.json()
                        st.rerun()
                except Exception as e: st.error(f"Network error: {e}")
                    
        if "latest_plan" in st.session_state:
            data = st.session_state.latest_plan
            st.subheader("📊 Target Macros (Calculated via ML)")
            st.json(data["calculated_macros"])
            col_plan, col_shop = st.columns(2)
            with col_plan: st.markdown(data["ai_generated_plan"])
            with col_shop: st.markdown(data["shopping_list"])
                    
    with tab2:
        st.subheader("📈 Your Daily Intake Logs")
        if "session_water" not in st.session_state: st.session_state.session_water = 0
        if "session_calories" not in st.session_state: st.session_state.session_calories = 0
        if "log_success_msg" not in st.session_state: st.session_state.log_success_msg = False

        col_w, col_c = st.columns(2)
        col_w.metric("💧 Total Water Drunk", f"{st.session_state.session_water} mL")
        col_c.metric("🔥 Calories Logged", f"{st.session_state.session_calories} kcal")
        
        if st.session_state.log_success_msg:
            st.success("✔️ Data successfully written to database records!")
            st.session_state.log_success_msg = False

        with st.form("metric_logger_final", clear_on_submit=True):
            add_water = st.number_input("Add Water Intake (mL)", min_value=0, step=250, value=0)
            add_calories = st.number_input("Add Meal Calories (kcal)", min_value=0, step=50, value=0)
            if st.form_submit_button("Log Entry to Database"):
                if int(add_water) == 0 and int(add_calories) == 0:
                    st.warning("⚠️ Enter a value greater than 0.")
                else:
                    try:
                        log_res = requests.post(f"{BACKEND_URL}/log-metrics/{st.session_state.user_id}?water_ml={int(add_water)}&calories={int(add_calories)}")
                        if log_res.status_code == 200:
                            st.session_state.session_water += int(add_water)
                            st.session_state.session_calories += int(add_calories)
                            st.session_state.log_success_msg = True
                            st.rerun()
                    except Exception as e: st.error(f"Sync failed: {e}")
        
    with tab3:
        st.subheader("💬 Student Community Hub")
        with st.form("community_post_form", clear_on_submit=True):
            post_category = st.selectbox("Select Category", ["🛒 Cheap Grocery Finds", "🍳 5-Minute Meal Prep", "🏋️ Dorm Workout Routines"])
            post_content = st.text_area("What's on your mind?", max_chars=280)
            if st.form_submit_button("Post to Forum") and post_content.strip():
                try:
                    requests.post(f"{BACKEND_URL}/forum-posts", json={"username": st.session_state.username, "content": post_content, "category": post_category})
                    st.rerun()
                except: st.error("Failed to sync post.")

        st.write("---")
        try:
            feed_res = requests.get(f"{BACKEND_URL}/forum-posts")
            if feed_res.status_code == 200:
                for post in feed_res.json():
                    with st.container(border=True):
                        st.markdown(f"**👤 {post.get('username')}** | ` {post.get('category')} `")
                        st.write(post.get('content'))
        except: st.error("Could not load live feed.")