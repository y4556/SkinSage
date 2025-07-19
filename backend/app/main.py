from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from backend.app.ocr import extract_ingredients
from backend.app.analysis import analyze_ingredients
from backend.app.chat import get_chat_response
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from backend.app.routine import generate_routine_with_groq
from backend.app.agent import SkincareAgent
from backend.app.comparison import compare_products
from fastapi.security import OAuth2PasswordBearer,  OAuth2PasswordRequestForm
import os
import re
from fastapi import BackgroundTasks
from dotenv import load_dotenv
from typing import Optional, List
import asyncio
from backend.app.web_scraper import get_ingredients_by_product_name
from backend.app.email import send_welcome_email, send_routine_email
# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = "mongodb://root:salva123@localhost:27017/"
DB_NAME = "skincare_db"

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_very_strong_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(
    title="Personalized Skincare Analyzer",
    description="API for skincare analysis with MongoDB persistence",
    version="2.3.0",
    docs_url="/docs",
    redoc_url=None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client setup
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
routines_collection = db["routines"]

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    skin_type: str
    concerns: List[str]

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    email: str
    skin_type: str
    concerns: List[str]

class ChatRequest(BaseModel):
    question: str

class Token(BaseModel):
    access_token: str
    token_type: str
class RoutineRequest(BaseModel):
    time_of_day: str  # "AM" or "PM"

class TrendingRequest(BaseModel):
    product_type: str

class RoutineStep(BaseModel):
    step: str
    product: str
    brand: str
    price: str
    url: str
    rating: str
    reviews: str
# Helper functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
class RoutineDocument(BaseModel):
    time_of_day: str
    routine: List[RoutineStep]  
    skin_type: str
    concerns: List[str]
    created_at: datetime = datetime.utcnow()
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def send_email_with_routine(to_email: str, time_of_day: str, routine: list, skin_type: str, concerns: list):
    routine_data = {
        "time_of_day": time_of_day,
        "routine": routine
    }
    send_routine_email(
        user_email=to_email,
        skin_type=skin_type,
        concerns=concerns,
        routine_data=routine_data
    )
async def get_user(email: str) -> Optional[dict]:
    return await db.users.find_one({"email": email})

async def create_user(user: UserCreate) -> str:
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "skin_type": user.skin_type,
        "concerns": user.concerns,
        "hashed_password": hashed_password,
        "last_report": None
    }
    result = await db.users.insert_one(user_data)
    return str(result.inserted_id)

async def save_report(email: str, report: dict) -> None:
    await db.users.update_one(
        {"email": email},
        {"$set": {"last_report": report}}
    )

async def get_report(email: str) -> Optional[dict]:
    user = await get_user(email)
    return user.get("last_report") if user else None

# Authentication functions
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if token.startswith("Bearer "):
            token = token[7:]
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        expire = payload.get("exp")
        if expire is None or datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise credentials_exception
    
    user = await get_user(email)
    if user is None:
        raise credentials_exception
    return user

# Endpoints
@app.post("/signup", response_model=dict)
async def signup(user_data: UserCreate,background_tasks: BackgroundTasks) -> dict:
    """Create a new user account"""
    existing_user = await get_user(user_data.email)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = await create_user(user_data)
    background_tasks.add_task(
        send_welcome_email,
        user_email=user_data.email,
        skin_type=user_data.skin_type,
        concerns=user_data.concerns
    )
    return {"message": "User created successfully", "user_id": user_id}

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """Authenticate user and return token"""
    user = await get_user(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )

    logger.info(f"Generated token for {user['email']}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current user profile"""
    return {
        "email": current_user["email"],
        "skin_type": current_user["skin_type"],
        "concerns": current_user["concerns"]
    }

@app.post("/analyze-product", response_model=dict)
async def analyze_product_from_image(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Extract ingredients from image and analyze them"""
    try:
        contents = await image.read()
        ingredients = await extract_ingredients(contents)
        logger.info(f"Extracted ingredients: {ingredients}")
        
        # Handle empty ingredients case
        if not ingredients or ingredients.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No ingredients found in image"
            )
        
        analysis = await analyze_ingredients(
            ingredients,
            skin_type=current_user["skin_type"],
            concerns=current_user["concerns"]
        )
        
        report = {
            "extracted_ingredients": ingredients,
            "analysis": analysis
        }
        
        await save_report(current_user["email"], report)
        return report
        
    except HTTPException as he:
        # Re-raise HTTPExceptions (like our 400 error)
        raise he
    except Exception as e:
        logger.error(f"Product analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not analyze product from image"
        )
    
@app.post("/chat", response_model=dict)
async def chat_about_product(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get responses to skincare questions"""
    try:
        report = await get_report(current_user["email"])
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analysis available"
            )
        
        return await get_chat_response(
            request.question,
            report["analysis"],
            skin_type=current_user["skin_type"],
            concerns=current_user["concerns"]
        )
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat service unavailable"
        )

@app.get("/report", response_model=dict)
async def get_report_endpoint(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get the current analysis report"""
    report = await get_report(current_user["email"])
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report available"
        )
    return report
# Add new imports
import asyncio

# Add new models
class RoutineRequest(BaseModel):
    time_of_day: str  # "AM" or "PM"

class TrendingRequest(BaseModel):
    product_type: str

@app.post("/generate-routine", response_model=dict)
async def generate_skincare_routine(
    request: RoutineRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
) -> dict:
    try:
        skin_type = current_user["skin_type"]
        concerns = current_user["concerns"]
        
        routine_data = await generate_routine_with_groq(
            request.time_of_day,
            skin_type,
            concerns
        )
        
        if not routine_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate routine"
            )
        #saving routine to MongoDB
        routine_doc = {
            "email": current_user["email"],
            "time_of_day": request.time_of_day,
            "skin_type": skin_type,
            "concerns": concerns,
            "routine": routine_data.get("routine", []),
            "created_at": datetime.utcnow()
        }
        await routines_collection.insert_one(routine_doc)
        background_tasks.add_task(
            send_email_with_routine,  
            to_email=current_user["email"],
            time_of_day=request.time_of_day,
            routine=routine_data.get("routine", []),
            skin_type=skin_type,
            concerns=concerns
        )

        return {
            "time_of_day": request.time_of_day,
            "skin_type": skin_type,
            "concerns": concerns,
            "routine": routine_data.get("routine", [])
        }
    except Exception as e:
        logger.error(f"Routine generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not generate skincare routine"
        )

@app.get("/saved-routines", response_model=List[dict])
async def get_saved_routines(
    current_user: dict = Depends(get_current_user)
) -> List[dict]:
    """Get all saved routines for current user"""
    cursor = routines_collection.find(
        {"email": current_user["email"]},
        {"_id": 0}  # Exclude MongoDB ID
    ).sort("created_at", -1)  # Newest first
    
    routines = []
    async for document in cursor:
        # Convert ObjectId to string if needed
        document["id"] = str(document.pop("_id")) 
        routines.append(document)
        
    return routines
@app.post("/analyze-product-by-name", response_model=dict)
async def analyze_product_by_name(
    request: dict,  # Expecting {"product_name": "..."}
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Search for product and analyze its ingredients"""
    try:
        product_name = request.get("product_name")
        if not product_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product name is required"
            )
        
        logger.info(f"Searching for product: {product_name}")
        
        # Get ingredients from web
        ingredients, source_url = get_ingredients_by_product_name(product_name)
        
        if not ingredients:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find product ingredients"
            )
        
        logger.info(f"Extracted ingredients: {ingredients[:100]}...")
        
        # Analyze ingredients
        analysis = await analyze_ingredients(
            ingredients,
            skin_type=current_user["skin_type"],
            concerns=current_user["concerns"]
        )
        
        report = {
            "product_name": product_name,
            "source_url": source_url,
            "extracted_ingredients": ingredients,
            "analysis": analysis
        }
        
        await save_report(current_user["email"], report)
        return report
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Product analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not analyze product by name"
        )

@app.post("/analyze-product-agent", response_model=dict)
async def analyze_product_agent(
    request: dict,  # {"input_type": "image/text", "input_data": "..."}
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Agent-based product analysis endpoint"""
    agent = SkincareAgent({
        "skin_type": current_user["skin_type"],
        "concerns": current_user["concerns"]
    })
    return await agent.process_input(
        request["input_type"],
        request["input_data"]
    )

@app.post("/compare-products", response_model=dict)
async def compare_products_endpoint(
    products: dict,  # {"product1": analysis1, "product2": analysis2}
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Compare two analyzed products"""
    return compare_products(
        products["product1"],
        products["product2"],
        current_user["skin_type"],
        current_user["concerns"]
    )
async def startup_event() -> None:
    """Initialize database on startup"""
    try:
        await db.command("ping")
        logger.info("✅ Connected to MongoDB")
        await db.users.create_index("email", unique=True)
        logger.info("✅ Created database indexes")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {str(e)}")
        raise RuntimeError("MongoDB connection failed") from e

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)