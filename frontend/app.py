
import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "report" not in st.session_state:
    st.session_state.report = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "routine_data" not in st.session_state:
    st.session_state.routine_data = None
if "trending_products" not in st.session_state:
    st.session_state.trending_products = None

# Custom CSS for styling
def inject_custom_css():
    st.markdown(
        """
        <style>
        :root {
            --primary: #6a5acd;
            --secondary: #ff7eb9;
            --accent: #7afcff;
            --light: #f5f5f5;
            --dark: #333333;
        }
        
        /* Main container */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
            padding: 0 1rem;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: var(--primary) !important;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(45deg, var(--primary), var(--secondary)) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(106, 90, 205, 0.3) !important;
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            border: 2px dashed var(--primary) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            background: rgba(255, 255, 255, 0.7) !important;
        }
        
        /* Chat bubbles */
        .stChatMessage {
            padding: 12px 16px;
            border-radius: 16px;
            margin-bottom: 8px;
            max-width: 80%;
        }
        
        .stChatMessage[data-testid="chatMessageUser"] {
            background-color: #e6f7ff;
            margin-left: 20%;
        }
        
        .stChatMessage[data-testid="chatMessageAssistant"] {
            background-color: #f9f0ff;
            margin-right: 20%;
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .ingredient-card {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            border-left: 4px solid var(--primary);
        }
        
        .ingredient-name {
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 5px;
        }
        
        .ingredient-function {
            color: #555;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        
        .ingredient-concern {
            color: #e74c3c;
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        /* Progress spinner */
        .stSpinner > div {
            border-color: var(--primary) transparent transparent transparent !important;
        }
        
        /* Section styling */
        .section {
            background: rgba(255, 255, 255, 0.85);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        
        .section-header {
            border-bottom: 2px solid var(--primary);
            padding-bottom: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        
        .section-header-icon {
            font-size: 28px;
            margin-right: 12px;
        }
        
        .metric-card {
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666;
        }
        
        .chat-container {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Helper functions
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

# Page functions
def login_page():
    st.title("✨ Welcome to SkinSage")
    st.subheader("Your Personalized Skincare Assistant")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("https://images.unsplash.com/photo-1596462502278-27bfdc403348?q=80&w=1480", 
                 caption="Personalized Skincare Analysis", use_container_width=True)
    with col2:
        st.markdown("""
        <div style="padding: 20px; background: rgba(255,255,255,0.7); border-radius: 15px;">
            <h3 style="color: #6a5acd;">How it works:</h3>
            <ol>
                <li>Sign in or create an account</li>
                <li>Upload a photo of skincare ingredients</li>
                <li>Get personalized analysis instantly</li>
                <li>Chat with our skincare assistant</li>
            </ol>
            <p style="color: #6a5acd; font-weight: 500;">Get insights tailored to your skin type!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sephora-aligned skin concerns
    CONCERNS = [
        "Acne / Blemishes",
        "Anti Aging",
        "Dark Circles & Puffiness",
        "Large & Visible Pores",
        "Blackheads",
        "Damaged Skin Barrier",
        "Hyperpigmentation & Dark Spots",
        "Redness"
    ]
    
    if st.session_state.auth_page == "login":
        with st.form("login_form"):
            st.subheader("Sign in to your account")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if authenticate(email, password):
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
        
        st.markdown("---")
        st.write("Don't have an account?")
        if st.button("Create Account", use_container_width=True, key="create_account_btn"):
            st.session_state.auth_page = "signup"
            st.rerun()
    else:
        with st.form("signup_form"):
            st.subheader("Create your account")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            
            # Skin type selection
            skin_type = st.selectbox(
                "Skin Type",
                ["Normal", "Dry", "Oily", "Combination", "Sensitive"],
                index=0
            )
            
            # Skin concerns with Sephora-aligned options
            st.subheader("Skin Concerns")
            st.caption("Select all that apply to you")
            
            concerns = st.multiselect(
                "Common Skin Concerns:",
                CONCERNS,
                help="These align with Sephora's concern categories for better recommendations"
            )
            
            # Optional custom concerns
            with st.expander("+ Add Specific Concerns (Optional)"):
                custom_concerns = st.text_area(
                    "Describe any specific skin concerns not listed above:",
                    placeholder="e.g., rosacea, eczema, melasma",
                    help="Our AI will map these to the closest Sephora categories"
                )
            
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                # Process custom concerns
                custom_list = []
                if custom_concerns:
                    custom_list = [c.strip().lower() for c in custom_concerns.split(",") if c.strip()]
                
                # Combine concerns
                all_concerns = [c.lower() for c in concerns] + custom_list

                user_data = {
                    "email": email,
                    "password": password,
                    "skin_type": skin_type.lower(),
                    "concerns": all_concerns
                }
                
                if signup_user(user_data):
                    if authenticate(email, password):
                        st.success("Account created and logged in successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Account created but login failed. Please log in manually.")
                else:
                    st.error("Account creation failed. Please try again.")
        
        st.markdown("---")
        st.write("Already have an account?")
        if st.button("Back to Login", use_container_width=True, key="back_to_login"):
            st.session_state.auth_page = "login"
            st.rerun()
def analyze_product_page():
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-header-icon">🔍</span><h2>Analyze Skincare Product</h2></div>', unsafe_allow_html=True)
    st.markdown("Upload an image of a skincare product's ingredient list to get personalized analysis")
    
    uploaded_file = st.file_uploader(
        "**Drag & drop or browse files** (INGREDIENTS LIST MUST BE VISIBLE)",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.subheader("🔍 Or search by product name")
    
    with st.form("product_search_form"):
        product_name = st.text_input(
            "Enter product name (e.g., 'CeraVe Foaming Facial Cleanser')",
            placeholder="Brand + Product Name"
        )
        submitted = st.form_submit_button("Search and Analyze", use_container_width=True)
        
        if submitted and product_name:
            with st.spinner(f"🔍 Searching for {product_name} and analyzing ingredients..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/analyze-product-by-name",
                        headers=get_auth_header(),
                        json={"product_name": product_name}
                    )
                    
                    if response.status_code == 200:
                        st.session_state.report = response.json()
                        st.session_state.analyzed = True
                        st.success("🎉 Analysis complete!")
                        st.balloons()
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Analysis failed: {error_detail}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if uploaded_file is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded_file, caption="Uploaded Product", width=250)
        with col2:
            st.info("Tips for best results:")
            st.markdown("- 📸 Capture in good lighting")
            st.markdown("- 🔍 Ensure text is clear and in focus")
            st.markdown("- 📜 Flat surfaces work best")
        
        if st.button("Analyze Ingredients", use_container_width=True, key="analyze_btn"):
            with st.spinner("🔬 Analyzing ingredients. This may take 15-30 seconds..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    files = {"image": (uploaded_file.name, file_bytes, uploaded_file.type)}
                    
                    response = requests.post(
                        f"{API_BASE_URL}/analyze-product",
                        headers=get_auth_header(),
                        files=files
                    )
                    
                    if response.status_code == 200:
                        st.session_state.report = response.json()
                        st.session_state.analyzed = True
                        st.success("🎉 Analysis complete!")
                        st.balloons()
                    elif response.status_code == 400:
                        st.error("⚠️ No ingredients found in the image. Please ensure:")
                        st.markdown("- The ingredient list is clearly visible")
                        st.markdown("- Text is not blurry or obscured")
                        st.markdown("- Try capturing in better lighting")
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Analysis failed: {error_detail}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.analyzed and st.session_state.report:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><span class="section-header-icon">📝</span><h2>Product Analysis Report</h2></div>', unsafe_allow_html=True)
        
        report = st.session_state.report
        analysis = report.get("analysis", {})
        overall = analysis.get("overall_assessment", {})
        ingredients = analysis.get("ingredients", [])
        
        safety_rating = overall.get("safety_rating", "").lower()
        safety_color = {
            "safe": "🟢",
            "caution": "🟡",
            "unsafe": "🔴"
        }.get(safety_rating, "⚪")
        
        st.subheader("Overall Assessment")
        
        cols = st.columns(5)
        metrics = [
            ("Safety Rating", f"{safety_color} {overall.get('safety_rating', 'N/A')}"),
            ("Suitability", f"{overall.get('suitability_score', 'N/A')}/5"),
            ("Barrier Impact", overall.get('barrier_impact', 'N/A')),
            ("Allergy Risk", overall.get('allergy_risk', 'N/A')),
            ("Key Concerns", f"{len(overall.get('key_concerns', []))} found")
        ]
        
        for i, (label, value) in enumerate(metrics):
            with cols[i]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with st.expander("💡 Personalized Summary", expanded=True):
            st.write(overall.get("personalized_notes", "No notes available"))

        if analysis.get("alternative_products"):
            st.subheader("♻️ Recommended Alternative Products")
            st.markdown("Here are products that might work better for your skin type:")
            
            for alt in analysis["alternative_products"]:
                with st.expander(f"**{alt['brand']} - {alt['product']}** ({alt.get('type', 'commercial').capitalize()})"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown("**Why better?**")
                    with col2:
                        st.markdown(alt['reason'])
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown("**Key ingredients:**")
                    with col2:
                        st.markdown(", ".join(alt['key_ingredients']))
        st.subheader("⚠️ Ingredient Compatibility Guide")
        st.markdown("""
        | Active Ingredient | Ideal Time | Don't Mix With                 |
        |-------------------|------------|--------------------------------|
        | Vitamin C         | AM         | Retinol, Benzoyl Peroxide, AHA/BHA |
        | Niacinamide       | AM/PM      | (Caution with L-Ascorbic Acid) |
        | Retinol           | PM         | Vitamin C, AHA/BHA, Benzoyl Peroxide |
        | AHA/BHA           | PM         | Retinol, Vitamin C             |
        | Benzoyl Peroxide  | AM         | Retinol, Vitamin C             |
        """)
        st.caption("Note: Always patch test new products and consult a dermatologist for personalized advice.")


        st.subheader("Ingredient Analysis")
        st.caption(f"Found {len(ingredients)} ingredients")
        
        concerning_ingredients = [i for i in ingredients if i.get('special_concerns')]
        safe_ingredients = [i for i in ingredients if not i.get('special_concerns')]
        
        if concerning_ingredients:
            st.subheader("⚠️ Ingredients with Concerns", anchor="concerns")
            for ingredient in concerning_ingredients:
                concerns = ingredient.get('special_concerns', [])
                st.markdown(
                    f"""
                    <div class="ingredient-card">
                        <div class="ingredient-name">{ingredient.get('name', 'Unknown')}</div>
                        <div class="ingredient-function">Function: {ingredient.get('function', 'N/A')}</div>
                        <div class="ingredient-concern">Concerns: {', '.join(concerns)}</div>
                        <div class="ingredient-notes">Notes: {ingredient.get('personalized_notes', 'N/A')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        if safe_ingredients:
            st.subheader("✅ Safe Ingredients")
            for ingredient in safe_ingredients:
                st.markdown(
                    f"""
                    <div class="ingredient-card">
                        <div class="ingredient-name">{ingredient.get('name', 'Unknown')}</div>
                        <div class="ingredient-function">Function: {ingredient.get('function', 'N/A')}</div>
                        <div class="ingredient-notes">Notes: {ingredient.get('personalized_notes', 'N/A')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-header-icon">💬</span><h2>Ask Skincare Assistant</h2></div>', unsafe_allow_html=True)
    st.caption("Ask questions about your skincare products and get personalized advice")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about your skincare product..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    headers=get_auth_header(),
                    json={"question": prompt}
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    assistant_response = response_data.get("response", "I couldn't process that request")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    
                    with st.chat_message("assistant"):
                        st.markdown(assistant_response)
                else:
                    st.error("Failed to get response from assistant")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def profile_page():
    st.title("👤 Your Profile")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/profile",
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            profile = response.json()
            
            col1, col2 = st.columns([1, 3])
            with col1:
                initials = ''.join([n[0] for n in profile.get("email", "").split("@")[0].split(".")])
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(45deg, #6a5acd, #ff7eb9);
                        width: 120px;
                        height: 120px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 48px;
                        color: white;
                        margin: 0 auto;
                    ">{initials.upper()}</div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                st.subheader("Email")
                st.code(profile.get("email", ""), language="text")
                
                st.subheader("Skin Type")
                st.info(profile.get("skin_type", "").capitalize())
                
                st.subheader("Skin Concerns")
                concerns = [c.capitalize() for c in profile.get("concerns", [])]
                if concerns:
                    st.info(", ".join(concerns))
                else:
                    st.info("None specified")
        else:
            st.error("Failed to load profile data")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        
    if st.button("Logout", use_container_width=True, key="profile_logout"):
        logout()

def routine_page():
    st.title("✨ Your Personalized Skincare Routine")
    
    try:
        profile = requests.get(
            f"{API_BASE_URL}/profile",
            headers=get_auth_header()
        ).json()
        skin_type = profile["skin_type"].capitalize()
        concerns = [c.capitalize() for c in profile["concerns"]]
        
        st.subheader(f"🧴 Skin Profile: {skin_type} skin")
        st.caption(f"⚡ Concerns: {', '.join(concerns) if concerns else 'None'}")
    except:
        st.warning("Could not load skin profile")
        return
    
    if st.button("🔄 Generate Routine", use_container_width=True):
        st.session_state.routine_data = None
    
    if "routine_data" not in st.session_state or not st.session_state.routine_data:
        with st.spinner("🧪 Creating your personalized routine with AI..."):
            try:
                # Generate AM routine
                am_response = requests.post(
                    f"{API_BASE_URL}/generate-routine",
                    headers=get_auth_header(),
                    json={"time_of_day": "AM"}
                )
                am_data = am_response.json() if am_response.status_code == 200 else None
                
                # Generate PM routine
                pm_response = requests.post(
                    f"{API_BASE_URL}/generate-routine",
                    headers=get_auth_header(),
                    json={"time_of_day": "PM"}
                )
                pm_data = pm_response.json() if pm_response.status_code == 200 else None
                
                st.session_state.routine_data = {
                    "AM": am_data,
                    "PM": pm_data
                }
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.session_state.get("routine_data"):
        am_data = st.session_state.routine_data.get("AM")
        pm_data = st.session_state.routine_data.get("PM")
        
        am_col, pm_col = st.columns(2)
        
        with am_col:
          if am_data and "routine" in am_data:
            st.subheader("🌞 Morning Routine (AM)")
            for step in am_data["routine"]:
                st.markdown(f"**{step['step'].capitalize()}: {step['product']}**")
                st.write(step["description"])
                url = step.get("brand_url") or step.get("link") or "#"
                if url != "#":
                  st.markdown(f"[Visit Brand Website]({url})")
                st.markdown("---")
                
        with pm_col:
          if pm_data and "routine" in pm_data:
            st.subheader("🌙 Evening Routine (PM)")
            for step in pm_data["routine"]:
                st.markdown(f"**{step['step'].capitalize()}: {step['product']}**")
                st.write(step["description"])
                url = step.get("brand_url") or step.get("link") or "#"
                if url != "#":
                  st.markdown(f"[Visit Brand Website]({url})")
                st.markdown("---")

def home_page():
    col_title, col_logout = st.columns([5, 1])
    with col_title:
        st.title("SkinSage - Your Personalized Skincare Assistant")
    with col_logout:
        st.write("")
        st.write("")
        if st.button("Logout", use_container_width=True, key="top_logout"):
            logout()

    with st.sidebar:
        st.subheader("Navigation")
        nav_options = {
            "🔍 Analyze Product": "analyze",
            "✨ Your Routine": "routine",
            "👤 Profile": "profile"
        }
        selection = st.radio("Go to", list(nav_options.keys()), key="nav_radio")
        page = nav_options[selection]

    try:
        response = requests.get(
            f"{API_BASE_URL}/profile",
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            profile = response.json()
            st.caption(f"👤 {profile.get('email', '')} | 🧴 {profile.get('skin_type', '').capitalize()} skin | ⚠️ {', '.join([c.capitalize() for c in profile.get('concerns', [])] or 'No concerns')}")
    except:
        pass
    
    st.markdown("---")
    
    if page == "analyze":
        analyze_product_page()
    elif page == "routine":
        routine_page()
    elif page == "profile":
        profile_page()

def main():
    inject_custom_css()
    
    st.set_page_config(
        page_title="SkinSage - Personalized Skincare Assistant",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if not st.session_state.token:
        login_page()
    else:
        home_page()
    
    st.markdown("---")
    st.caption("© 2025 SkinSage | AI-Powered Skincare Analysis")

if __name__ == "__main__":
    main()