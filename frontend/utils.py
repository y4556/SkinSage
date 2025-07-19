import base64
import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS injection
def inject_custom_css():
         st.markdown(
        """
        <style>
        :root {
            --primary1: #b993d6;
            --primary2: #8ca6db;
            --primary-dark: #6a4fb8;
            --accent1: #ffbfae;
            --accent2: #ffe2eb;
            --text-dark: #3A3A3A;
            --text-light: #F5F5F5;
    }
            
        /* Reset all padding and margins */
        html, body, .stApp {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        
        /* Main container */
        .stApp {
            background-color: #FAFAF8;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Login page background */
        .login-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://images.unsplash.com/photo-1620916297394-9b5b8a5a9c1f');
            background-size: cover;
            background-position: center center;
            opacity: 0.12;
            z-index: -1;
        }
        
        /* Title container - HORIZONTAL CENTERING */
        .title-container {
            text-align: center;
            padding: 20px 0 10px;
            width: 100%;
            animation: fadeIn 1s ease-in;
        }
        
        /* Branding */
        .brand-title {
            font-size: 5rem;
            font-weight: 900;
            letter-spacing: 3px;
            background: linear-gradient(90deg, var(--primary-dark), var(--primary1));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            text-shadow: 4px 4px 8px rgba(186,147,214,0.15);
            font-family: 'Montserrat', sans-serif;
            line-height: 1;
            position: relative;
        }
        
        .brand-title::after {
            content: '';
            display: block;

            width: 100%;      
            max-width: 100%;
            height: 6px;
            background: linear-gradient(90deg, var(--accent1), var(--primary2));
            margin: 10px auto;
            border-radius: 2px;
        }
        
        .brand-tagline {
            font-size: 1.4rem;
            color: var(--primary-dark);
            margin-top: 8px;
            font-weight: 500;
            letter-spacing: 1.2px;
            animation: slideIn 0.8s ease-out;
        }
        
        /* Form container - HORIZONTAL CENTERING */
        .form-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px;
            padding: 36px;
            box-shadow: 0 16px 40px 0 rgba(137, 164, 219, 0.15);
            border: 1px solid rgba(138, 154, 91, 0.3);
            max-width: 500px;
            width: 100%;
            margin: 20px auto 40px;
            position: relative;
            overflow: hidden;
            animation: floatUp 0.8s ease-out;
        }
        
        .form-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
             background: linear-gradient(90deg, var(--primary-dark), var(--accent1));
       }
        
        /* Remove Streamlit header space */
        .st-emotion-cache-18ni7ap {
            padding-top: 0 !important;
        }
        
        /* Beautiful Buttons */
        .stButton>button {
            background: linear-gradient(90deg, var(--primary-dark), var(--primary1));
            color: white !important;
            border: none !important;
            border-radius: 30px !important;
            padding: 14px 40px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 6px 16px rgba(137, 164, 219, 0.2) !important;
            font-size: 1.1rem !important;
            margin-top: 1rem !important;
            width: 100% !important;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, var(--accent1), var(--primary-dark));
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 8px 24px rgba(137, 164, 219, 0.25) !important;
        }
        .stButton>button::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 0;
            height: 100%;
            background: #f9ccb6;
            transition: width 0.5s ease;
            z-index: -1;
        }
        
        .stButton>button:hover::before {
            width: 100%;
        }
        
        .stButton>button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 20px rgba(122, 140, 105, 0.4) !important;
        }
        
        /* Form titles */
        .form-title {
            color: var(--primary-dark) !important;
            text-align: center;
            margin-bottom: 1.8rem !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
            letter-spacing: 1px !important;
            position: relative;
            padding-bottom: 12px;
        }
        
        .form-title::after {
            content: '';
            display: block;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, var(--accent1), var(--primary2), var(--accent2));
            margin: 10px auto 0;
            border-radius: 2px;
        }
        
        /* Input fields */
        .stTextInput>div>div>input, .stTextInput>div>div>textarea {
            border-radius: 18px !important;
            border: 1.5px solid var(--primary1) !important;
            padding: 14px 20px !important;
            font-size: 1.07rem !important;
            box-shadow: 0 2px 12px rgba(185,147,214,0.09) !important;
            background: #fff !important;
            transition: all 0.3s;
}
        
        .stTextInput>div>div>input:focus, .stTextInput>div>div>textarea:focus {
            border-color: var(--primary-dark) !important;
            box-shadow: 0 0 0 2px rgba(137, 164, 219, 0.18) !important;
            transform: scale(1.02);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        @keyframes floatUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        /* Add Google Font */
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
        </style>
        """,
        unsafe_allow_html=True
    )
# Authentication functions
def authenticate(email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.session_state.current_user = email
            st.session_state.analyzed = False
            return True
        return False
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return False

def signup_user(user_data: dict) -> bool:
    try:
        response = requests.post(
            f"{API_BASE_URL}/signup",
            json=user_data
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")
        return False

def get_auth_header():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def logout():
    st.session_state.token = None
    st.session_state.current_user = None
    st.session_state.messages = []
    st.session_state.report = None
    st.session_state.analyzed = False
    st.session_state.routine_data = None
    st.session_state.trending_products = None
    st.success("Logged out successfully!")
    time.sleep(1)
    st.rerun()

# Routine functions
def get_saved_routines():
    try:
        response = requests.get(
            f"{API_BASE_URL}/saved-routines",
            headers=get_auth_header()
        )
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Error loading routines: {str(e)}")
        return []

def display_routine(routine_data):
    st.subheader(f"{'🌞 Morning' if routine_data['time_of_day'] == 'AM' else '🌙 Evening'} Routine")
    st.caption(f"Created for {routine_data['skin_type'].capitalize()} skin")
    
    for step in routine_data.get("routine", []):
        with st.expander(f"**{step['step'].capitalize()}: {step['product']}**"):
            st.markdown(f"**Description:** {step.get('description', '')}")
            if step.get("reason"):
                st.info(f"**Why this product:** {step['reason']}")
            if step.get("link"):
                st.markdown(f"[🔗 Product Link]({step['link']})")

# Comparison functions
def display_product_card(overall, is_better):
    """Display product summary card"""
    card_color = "#e6f4ea" if is_better else "#f9f9f9"
    border = "4px solid #4CAF50" if is_better else "1px solid #ddd"
    
    st.markdown(
        f"""
        <div style="
            background-color: {card_color};
            border: {border};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        ">
            <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 10px;">
                Overall Assessment
            </div>
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div style="font-weight: 500;">Safety</div>
                    <div>{overall.get('safety_rating', 'N/A').capitalize()}</div>
                </div>
                <div>
                    <div style="font-weight: 500;">Barrier</div>
                    <div>{overall.get('barrier_impact', 'N/A').capitalize()}</div>
                </div>
                <div>
                    <div style="font-weight: 500;">Allergy</div>
                    <div>{overall.get('allergy_risk', 'N/A').capitalize()}</div>
                </div>
            </div>
            <div style="margin-top: 15px; text-align: center;">
                <div style="font-size: 2.5rem; color: {'#4CAF50' if is_better else '#333'};">
                    {overall.get('suitability_score', 'N/A')}
                </div>
                <div style="font-size: 0.9rem; color: #666;">
                    Suitability Score
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def compare_metrics(p1, p2):
    """Compare key metrics visually"""
    metrics = [
        ("safety_rating", "Safety"),
        ("barrier_impact", "Barrier Impact"),
        ("allergy_risk", "Allergy Risk"),
        ("suitability_score", "Suitability")
    ]
    
    for metric, label in metrics:
        p1_val = p1.get(metric, "N/A")
        p2_val = p2.get(metric, "N/A")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"**{p1_val}**")
        
        with col2:
            st.markdown(f"**{label}**")
            if isinstance(p1_val, (int, float)) and isinstance(p2_val, (int, float)):
                max_val = max(p1_val, p2_val)
                p1_width = (p1_val / max_val) * 100 if max_val > 0 else 50
                p2_width = (p2_val / max_val) * 100 if max_val > 0 else 50
                
                st.markdown(
                    f"""
                    <div style="display: flex; height: 30px; margin: 5px 0;">
                        <div style="background: #4CAF50; width: {p1_width}%; 
                                    display: flex; align-items: center; padding-left: 5px;">
                            P1
                        </div>
                        <div style="background: #2196F3; width: {p2_width}%; 
                                    display: flex; justify-content: flex-end; 
                                    align-items: center; padding-right: 5px;">
                            P2
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with col3:
            st.markdown(f"**{p2_val}**")
        
        st.markdown("---")

def display_comparison_results(comparison, analyses):
    """Display comparison results in a user-friendly format"""
    st.title("🏆 Product Comparison Results")
    
    # Extract product data
    p1 = analyses["product1"]
    p2 = analyses["product2"]
    p1_overall = p1["overall_assessment"]
    p2_overall = p2["overall_assessment"]
    
    # Show recommended product
    better_idx = comparison.get("better_product", 1)
    st.success(f"✨ **Recommended Product: {'1' if better_idx == 1 else '2'}**")
    
    # Product cards side-by-side
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧴 Product 1")
        display_product_card(p1_overall, better_idx == 1)
        
    with col2:
        st.subheader("🧴 Product 2")
        display_product_card(p2_overall, better_idx == 2)
    
    # Key metrics comparison
    st.subheader("📊 Key Metrics Comparison")
    compare_metrics(p1_overall, p2_overall)
    
    # Personalized notes
    st.subheader("💬 Personalized Notes")
    notes_col1, notes_col2 = st.columns(2)
    with notes_col1:
        st.info(p1_overall.get("personalized_notes", "No notes available"))
    with notes_col2:
        st.info(p2_overall.get("personalized_notes", "No notes available"))
    
    # Key concerns
    st.subheader("⚠️ Key Concerns")
    concerns_col1, concerns_col2 = st.columns(2)
    with concerns_col1:
        if p1_overall.get("key_concerns"):
            for concern in p1_overall["key_concerns"]:
                st.error(f"- {concern}")
        else:
            st.info("No major concerns")
    with concerns_col2:
        if p2_overall.get("key_concerns"):
            for concern in p2_overall["key_concerns"]:
                st.error(f"- {concern}")
        else:
            st.info("No major concerns")
    
    # Show alternatives for the recommended product
    st.subheader("♻️ Recommended Alternatives")
    better_product = p1 if better_idx == 1 else p2
    if better_product.get("alternative_products"):
        for alt in better_product["alternative_products"]:
            with st.expander(f"**{alt.get('brand', 'Unknown')} - {alt.get('product', 'Unknown')}**"):
                st.markdown(f"**Why better:** {alt.get('reason', 'N/A')}")
                st.markdown(f"**Key ingredients:** {', '.join(alt.get('key_ingredients', []))}")
    else:
        st.info("No alternative products found")
    pass