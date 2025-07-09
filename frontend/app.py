# import streamlit as st
# import requests
# import os
# from dotenv import load_dotenv
# import time
# import io
# import base64

# # Load environment variables
# load_dotenv()

# # API configuration
# API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# # Initialize session state
# if "token" not in st.session_state:
#     st.session_state.token = None
# if "current_user" not in st.session_state:
#     st.session_state.current_user = None
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "report" not in st.session_state:
#     st.session_state.report = None
# if "auth_page" not in st.session_state:
#     st.session_state.auth_page = "login"

# # Custom CSS for styling
# def inject_custom_css():
#     st.markdown(
#         """
#         <style>
#         :root {
#             --primary: #6a5acd;
#             --secondary: #ff7eb9;
#             --accent: #7afcff;
#             --light: #f5f5f5;
#             --dark: #333333;
#         }
        
#         /* Main container */
#         .stApp {
#             background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
#         }
        
#         /* Sidebar */
#         [data-testid="stSidebar"] {
#             background: linear-gradient(180deg, #ffffff 0%, #f8f9ff 100%);
#             border-right: 1px solid #e6ecf8;
#         }
        
#         /* Headers */
#         h1, h2, h3 {
#             color: var(--primary) !important;
#         }
        
#         /* Buttons */
#         .stButton>button {
#             background: linear-gradient(45deg, var(--primary), var(--secondary)) !important;
#             color: white !important;
#             border: none !important;
#             border-radius: 8px !important;
#             padding: 10px 24px !important;
#             font-weight: 600 !important;
#             transition: all 0.3s ease !important;
#         }
        
#         .stButton>button:hover {
#             transform: translateY(-2px);
#             box-shadow: 0 4px 8px rgba(106, 90, 205, 0.3) !important;
#         }
        
#         /* File uploader */
#         [data-testid="stFileUploader"] {
#             border: 2px dashed var(--primary) !important;
#             border-radius: 12px !important;
#             padding: 20px !important;
#             background: rgba(255, 255, 255, 0.7) !important;
#         }
        
#         /* Chat bubbles */
#         .stChatMessage {
#             padding: 12px 16px;
#             border-radius: 16px;
#             margin-bottom: 8px;
#             max-width: 80%;
#         }
        
#         .stChatMessage[data-testid="chatMessageUser"] {
#             background-color: #e6f7ff;
#             margin-left: 20%;
#         }
        
#         .stChatMessage[data-testid="chatMessageAssistant"] {
#             background-color: #f9f0ff;
#             margin-right: 20%;
#         }
        
#         /* Cards */
#         .card {
#             background: white;
#             border-radius: 12px;
#             box-shadow: 0 4px 12px rgba(0,0,0,0.05);
#             padding: 20px;
#             margin-bottom: 20px;
#         }
        
#         /* Progress spinner */
#         .stSpinner > div {
#             border-color: var(--primary) transparent transparent transparent !important;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

# # Helper functions
# def authenticate(email: str, password: str) -> bool:
#     """Authenticate user and store token"""
#     try:
#         response = requests.post(
#             f"{API_BASE_URL}/login",
#             data={"username": email, "password": password},
#             headers={"Content-Type": "application/x-www-form-urlencoded"}
#         )
#         if response.status_code == 200:
#             st.session_state.token = response.json()["access_token"]
#             st.session_state.current_user = email
#             return True
#         return False
#     except Exception as e:
#         st.error(f"Authentication failed: {str(e)}")
#         return False

# def signup_user(user_data: dict) -> bool:
#     """Create new user account"""
#     try:
#         response = requests.post(
#             f"{API_BASE_URL}/signup",
#             json=user_data
#         )
#         return response.status_code == 200
#     except Exception as e:
#         st.error(f"Signup failed: {str(e)}")
#         return False

# def get_auth_header():
#     """Get authorization header with token"""
#     return {"Authorization": f"Bearer {st.session_state.token}"}

# # Page functions
# def login_page():
#     """Login form"""
#     st.title("✨ Skincare Analyzer")
#     st.subheader("Sign in to your account")
    
#     with st.form("login_form"):
#         email = st.text_input("Email", placeholder="your@email.com")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("Login", use_container_width=True)
        
#         if submitted:
#             if authenticate(email, password):
#                 st.success("Login successful!")
#                 time.sleep(1)
#                 st.rerun()
    
#     st.markdown("---")
#     st.write("Don't have an account?")
#     if st.button("Create Account", use_container_width=True):
#         st.session_state.auth_page = "signup"
#         st.rerun()

# def signup_page():
#     """Signup form"""
#     st.title("✨ Create Account")
    
#     with st.form("signup_form"):
#         email = st.text_input("Email", placeholder="your@email.com")
#         password = st.text_input("Password", type="password")
#         skin_type = st.selectbox(
#             "Skin Type",
#             ["Normal", "Dry", "Oily", "Combination", "Sensitive"]
#         )
#         concerns = st.multiselect(
#             "Skin Concerns",
#             ["Acne", "Aging", "Hyperpigmentation", "Redness", "Dryness", "Oiliness", "Sensitivity"]
#         )
#         submitted = st.form_submit_button("Create Account", use_container_width=True)
        
#         if submitted:
#             user_data = {
#                 "email": email,
#                 "password": password,
#                 "skin_type": skin_type.lower(),
#                 "concerns": [c.lower() for c in concerns]
#             }
#             if signup_user(user_data):
#                 # Automatically log in after signup
#                 if authenticate(email, password):
#                     st.success("Account created and logged in successfully!")
#                     time.sleep(1)
#                     st.rerun()
#                 else:
#                     st.error("Account created but login failed. Please log in manually.")
#             else:
#                 st.error("Account creation failed. Please try again.")
    
#     st.markdown("---")
#     st.write("Already have an account?")
#     if st.button("Back to Login", use_container_width=True):
#         st.session_state.auth_page = "login"
#         st.rerun()


# def analyze_product_page():
#     """Product analysis interface"""
#     st.title("🔍 Analyze Skincare Product")
#     st.markdown("Upload an image of a skincare product's ingredient list to get personalized analysis")
    
#     uploaded_file = st.file_uploader(
#         "**Drag & drop or browse files** (INGREDIENTS LIST MUST BE VISIBLE)",
#         type=["jpg", "jpeg", "png"],
#         label_visibility="collapsed"
#     )
    
#     if uploaded_file is not None:
#         col1, col2 = st.columns([1, 2])
#         with col1:
#             st.image(uploaded_file, caption="Uploaded Product", width=200)
#         with col2:
#             st.info("Tips for best results:")
#             st.markdown("- 📸 Capture in good lighting")
#             st.markdown("- 🔍 Ensure text is clear and in focus")
#             st.markdown("- 📜 Flat surfaces work best")
        
#         if st.button("Analyze Ingredients", use_container_width=True):
#             with st.spinner("🔬 Analyzing ingredients..."):
#                 try:
#                     # Create file-like object from bytes
#                     file_bytes = uploaded_file.getvalue()
#                     files = {"image": (uploaded_file.name, file_bytes, uploaded_file.type)}
                    
#                     # Send to API as multipart form data
#                     response = requests.post(
#                         f"{API_BASE_URL}/analyze-product",
#                         headers=get_auth_header(),
#                         files=files
#                     )
                    
#                     if response.status_code == 200:
#                         st.session_state.report = response.json()
#                         st.success("🎉 Analysis complete! View report in the 'View Report' section")
#                         st.balloons()
#                         time.sleep(1)
#                         st.rerun()
#                     elif response.status_code == 400:
#                         # Specific error for no ingredients found
#                         st.error("⚠️ No ingredients found in the image. Please ensure:")
#                         st.markdown("- The ingredient list is clearly visible")
#                         st.markdown("- Text is not blurry or obscured")
#                         st.markdown("- Try capturing in better lighting")
#                     else:
#                         error_detail = response.json().get("detail", "Unknown error")
#                         st.error(f"Analysis failed: {error_detail}")
#                 except Exception as e:
#                     st.error(f"Error: {str(e)}")


# def chat_page():
#     """Chat interface"""
#     st.title("💬 Skincare Assistant")
#     st.caption("Ask questions about your skincare products and get personalized advice")
    
#     # Display chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
    
#     # Handle user input
#     if prompt := st.chat_input("Ask about your skincare product..."):
#         # Add user message to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         # Display user message
#         with st.chat_message("user"):
#             st.markdown(prompt)
        
#         # Get assistant response
#         with st.spinner("Thinking..."):
#             try:
#                 response = requests.post(
#                     f"{API_BASE_URL}/chat",
#                     headers=get_auth_header(),
#                     json={"question": prompt}
#                 )
                
#                 if response.status_code == 200:
#                     response_data = response.json()
#                     assistant_response = response_data.get("response", "I couldn't process that request")
                    
#                     # Add assistant response to chat history
#                     st.session_state.messages.append({
#                         "role": "assistant",
#                         "content": assistant_response
#                     })
                    
#                     # Display assistant response
#                     with st.chat_message("assistant"):
#                         st.markdown(assistant_response)
#                 else:
#                     st.error("Failed to get response from assistant")
#             except Exception as e:
#                 st.error(f"Error: {str(e)}")

# def report_page():
#     """Display analysis report"""
#     st.title("📝 Product Analysis Report")
    
#     if not st.session_state.report:
#         st.warning("No analysis report available. Please analyze a product first.")
#         return
    
#     report = st.session_state.report
#     analysis = report.get("analysis", {})
#     overall = analysis.get("overall_assessment", {})
#     ingredients = analysis.get("ingredients", [])
    
#     # Safety indicators
#     safety_rating = overall.get("safety_rating", "").lower()
#     safety_color = {
#         "safe": "🟢",
#         "caution": "🟡",
#         "unsafe": "🔴"
#     }.get(safety_rating, "⚪")
    
#     # Display overall assessment
#     st.subheader("Overall Assessment")
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.metric("Safety Rating", f"{safety_color} {overall.get('safety_rating', 'N/A')}")
#     with col2:
#         st.metric("Suitability Score", f"{overall.get('suitability_score', 'N/A')}/5")
#     with col3:
#         st.metric("Barrier Impact", overall.get("barrier_impact", "N/A"))
#     with col4:
#         st.metric("Allergy Risk", overall.get("allergy_risk", "N/A"))
    
#     # Key concerns card
#     with st.expander("📌 Key Concerns", expanded=True):
#         concerns = overall.get("key_concerns", [])
#         if concerns:
#             for concern in concerns:
#                 st.markdown(f"- ⚠️ {concern}")
#         else:
#             st.info("No significant concerns identified for your skin profile")
    
#     # Personalized notes card
#     with st.expander("💡 Personalized Notes", expanded=True):
#         st.write(overall.get("personalized_notes", "No notes available"))
    
#     # Display ingredient analysis
#     st.subheader("🧪 Ingredient Analysis")
#     for ingredient in ingredients:
#         with st.expander(f"{ingredient.get('name', 'Unknown Ingredient')}", expanded=False):
#             cols = st.columns([1, 1, 2])
#             with cols[0]:
#                 st.subheader("Properties")
#                 st.metric("Function", ingredient.get("function", "N/A"))
#                 st.metric("Safety", ingredient.get("safety", "N/A"))
#                 st.metric("Barrier Impact", ingredient.get("barrier_impact", "N/A"))
#                 st.metric("Allergy Potential", ingredient.get("allergy_potential", "N/A"))
            
#             with cols[1]:
#                 st.subheader("Alternatives")
#                 alternatives = ingredient.get("natural_alternatives", [])
#                 if alternatives:
#                     for alt in alternatives:
#                         st.markdown(f"- 🌿 {alt}")
#                 else:
#                     st.info("No alternatives suggested")
                
#                 st.subheader("Concerns")
#                 concerns = ingredient.get("special_concerns", [])
#                 if concerns:
#                     for concern in concerns:
#                         st.markdown(f"- ⚠️ {concern}")
#                 else:
#                     st.info("No special concerns")
            
#             with cols[2]:
#                 st.subheader("Personalized Notes")
#                 st.write(ingredient.get("personalized_notes", "No specific notes"))

# def profile_page():
#     """User profile management"""
#     st.title("👤 Your Profile")
    
#     try:
#         response = requests.get(
#             f"{API_BASE_URL}/profile",
#             headers=get_auth_header()
#         )
        
#         if response.status_code == 200:
#             profile = response.json()
            
#             col1, col2 = st.columns([1, 3])
#             with col1:
#                 # Profile avatar (using initials)
#                 initials = ''.join([n[0] for n in profile.get("email", "").split("@")[0].split(".")])
#                 st.markdown(
#                     f"""
#                     <div style="
#                         background: linear-gradient(45deg, #6a5acd, #ff7eb9);
#                         width: 120px;
#                         height: 120px;
#                         border-radius: 50%;
#                         display: flex;
#                         align-items: center;
#                         justify-content: center;
#                         font-size: 48px;
#                         color: white;
#                         margin: 0 auto;
#                     ">{initials.upper()}</div>
#                     """,
#                     unsafe_allow_html=True
#                 )
            
#             with col2:
#                 st.subheader("Email")
#                 st.code(profile.get("email", ""), language="text")
                
#                 st.subheader("Skin Type")
#                 st.info(profile.get("skin_type", "").capitalize())
                
#                 st.subheader("Skin Concerns")
#                 concerns = [c.capitalize() for c in profile.get("concerns", [])]
#                 if concerns:
#                     st.info(", ".join(concerns))
#                 else:
#                     st.info("None specified")
#         else:
#             st.error("Failed to load profile data")
#     except Exception as e:
#         st.error(f"Error: {str(e)}")
    
#     if st.button("Logout", use_container_width=True, type="primary"):
#         st.session_state.token = None
#         st.session_state.current_user = None
#         st.session_state.messages = []
#         st.session_state.report = None
#         st.success("Logged out successfully!")
#         time.sleep(1)
#         st.rerun()

# # Main app logic
# def main():
#     """Main application flow"""
#     # Apply custom CSS
#     inject_custom_css()
    
#     # Configure page
#     st.set_page_config(
#         page_title="Personalized Skincare Analyzer",
#         page_icon="✨",
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )
    
#     # Sidebar header
#     with st.sidebar:
#         st.image("https://via.placeholder.com/200x60/6a5acd/ffffff?text=Skincare+AI", use_container_width=True)
#         st.markdown("---")
        
#         # Navigation
#         if st.session_state.token:
#             st.subheader(f"👋 Hi, {st.session_state.current_user.split('@')[0]}")
#             nav_options = {
#                 "🔍 Analyze Product": "analyze",
#                 "💬 Skincare Assistant": "chat",
#                 "📝 View Report": "report",
#                 "👤 Profile": "profile"
#             }
#             selection = st.radio("Navigation", list(nav_options.keys()))
#             page = nav_options[selection]
#         else:
#             st.info("Please sign in to access all features")
    
#     # Page content
#     if not st.session_state.token:
#         # Show login or signup based on auth_page state
#         if st.session_state.auth_page == "login":
#             login_page()
#         else:
#             signup_page()
#     else:
#         # Show selected page
#         if page == "analyze":
#             analyze_product_page()
#         elif page == "chat":
#             chat_page()
#         elif page == "report":
#             report_page()
#         elif page == "profile":
#             profile_page()
            
#     # Footer
#     st.markdown("---")
#     st.caption("© 2025 Personalized Skincare Analyzer | AI-Powered Skincare Analysis")

# if __name__ == "__main__":
#     main()
import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time
import io
import base64

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
    """Authenticate user and store token"""
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
    """Create new user account"""
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
    """Get authorization header with token"""
    return {"Authorization": f"Bearer {st.session_state.token}"}

def logout():
    """Logout user"""
    st.session_state.token = None
    st.session_state.current_user = None
    st.session_state.messages = []
    st.session_state.report = None
    st.session_state.analyzed = False
    st.success("Logged out successfully!")
    time.sleep(1)
    st.rerun()

# Page functions
def login_page():
    """Login form"""
    st.title("✨ Welcome to Skinsage")
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
        if st.button("Create Account", use_container_width=True):
            st.session_state.auth_page = "signup"
            st.rerun()
    else:
        with st.form("signup_form"):
            st.subheader("Create your account")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            skin_type = st.selectbox(
                "Skin Type",
                ["Normal", "Dry", "Oily", "Combination", "Sensitive"]
            )
            concerns = st.multiselect(
                "Skin Concerns",
                ["Acne", "Aging", "Hyperpigmentation", "Redness", "Dryness", "Oiliness", "Sensitivity"]
            )
            custom_concerns_input = st.text_area(
            "Or describe your skin concerns (separate multiple concerns with commas)",
            placeholder="e.g., large pores, tanning, uneven texture")
        
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                custom_concerns = [
                c.strip().lower()
                for c in custom_concerns_input.split(",")
                if c.strip()
            ]
                all_concerns = [c.lower() for c in concerns] + custom_concerns
                
                user_data = {
                    "email": email,
                    "password": password,
                    "skin_type": skin_type.lower(),
                    "concerns": [c.lower() for c in concerns]
                }
                if signup_user(user_data):
                    # Automatically log in after signup
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
        if st.button("Back to Login", use_container_width=True):
            st.session_state.auth_page = "login"
            st.rerun()

def home_page():
    """Main home page with all functionality"""
    # Top bar with title and logout button
    col_title, col_logout = st.columns([5, 1])
    with col_title:
        st.title("Skinsage - Your Personalized Skincare Assistant")
    with col_logout:
        st.write("")  # Spacer
        st.write("")  # Spacer
        if st.button("Logout", use_container_width=True):
            logout()
    
    # User profile info
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
    
    # Product analysis section
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-header-icon">🔍</span><h2>Analyze Skincare Product</h2></div>', unsafe_allow_html=True)
    st.markdown("Upload an image of a skincare product's ingredient list to get personalized analysis")
    
    uploaded_file = st.file_uploader(
        "**Drag & drop or browse files** (INGREDIENTS LIST MUST BE VISIBLE)",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded_file, caption="Uploaded Product", width=250)
        with col2:
            st.info("Tips for best results:")
            st.markdown("- 📸 Capture in good lighting")
            st.markdown("- 🔍 Ensure text is clear and in focus")
            st.markdown("- 📜 Flat surfaces work best")
        
        if st.button("Analyze Ingredients", use_container_width=True):
            with st.spinner("🔬 Analyzing ingredients. This may take 15-30 seconds..."):
                try:
                    # Create file-like object from bytes
                    file_bytes = uploaded_file.getvalue()
                    files = {"image": (uploaded_file.name, file_bytes, uploaded_file.type)}
                    
                    # Send to API as multipart form data
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
                        # Specific error for no ingredients found
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
    
    # Display report if available
    if st.session_state.analyzed and st.session_state.report:
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><span class="section-header-icon">📝</span><h2>Product Analysis Report</h2></div>', unsafe_allow_html=True)
        
        report = st.session_state.report
        analysis = report.get("analysis", {})
        overall = analysis.get("overall_assessment", {})
        ingredients = analysis.get("ingredients", [])
        
        # Safety indicators
        safety_rating = overall.get("safety_rating", "").lower()
        safety_color = {
            "safe": "🟢",
            "caution": "🟡",
            "unsafe": "🔴"
        }.get(safety_rating, "⚪")
        
        # Display overall assessment
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
        
        # Personalized notes card
        with st.expander("💡 Personalized Summary", expanded=True):
            st.write(overall.get("personalized_notes", "No notes available"))
        
        # Display ingredient analysis
        st.subheader("Ingredient Analysis")
        st.caption(f"Found {len(ingredients)} ingredients")
        
        # Filter out ingredients without concerns
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
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span class="section-header-icon">💬</span><h2>Ask Skincare Assistant</h2></div>', unsafe_allow_html=True)
    st.caption("Ask questions about your skincare products and get personalized advice")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("Ask about your skincare product..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
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
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.markdown(assistant_response)
                else:
                    st.error("Failed to get response from assistant")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main app logic
def main():
    """Main application flow"""
    # Apply custom CSS
    inject_custom_css()
    
    # Configure page
    st.set_page_config(
        page_title="Skinsage - Personalized Skincare Assistant",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main content
    if not st.session_state.token:
        login_page()
    else:
        home_page()
    
    # Footer
    st.markdown("---")
    st.caption("© 2025 Skinsage | AI-Powered Skincare Analysis")

if __name__ == "__main__":
    main()