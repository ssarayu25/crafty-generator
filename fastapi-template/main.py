from fastapi import FastAPI, File, UploadFile, HTTPException, Body, status
from fastapi.responses import Response
from pydantic import BaseModel, Field, validator
from models import MsgPayload
import logging
import shutil
from fastapi.middleware.cors import CORSMiddleware
import time
import cv2
import numpy as np
from test_model import load_model_and_tokenizer, generate_pattern
import torch
import os
from functools import lru_cache
import hashlib
from typing import List, Optional
import filetype
import base64
from PIL import Image
import io
import json
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
try:
    import emoji
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False
# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log emoji library availability at startup
logger.info(f"Emoji library available: {EMOJI_AVAILABLE}")
if EMOJI_AVAILABLE:
    import emoji
    logger.info(f"Emoji library version: {emoji.__version__}")

# Optional dependencies for RAG pipeline
try:
    import faiss
    import pickle
    from sentence_transformers import SentenceTransformer
    RAG_AVAILABLE = True
except ImportError:
    logger.warning("RAG dependencies not available (faiss, sentence-transformers)")
    RAG_AVAILABLE = False
import google.generativeai as genai
from transformers import AutoModel, AutoTokenizer
import sqlite3
from pattern_generator import CrochetPatternGenerator

# Logging already configured above

# Try importing optional dependencies
try:
    from skimage.feature import local_binary_pattern
except ImportError:
    logger.warning("scikit-image not available, using basic texture analysis")

app = FastAPI(title="Yarn Master API", description="AI-Powered Crochet Pattern Generator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8081", "http://127.0.0.1:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Skip loading old T5 model - we'll use pattern generator instead
model, tokenizer = None, None
logger.info("Skipping T5 model - using pattern generator only")

# Valid pattern styles
VALID_STYLES = [
    "standard", "modern", "beginner-friendly", "advanced", 
    "amigurumi", "traditional", "minimalist"
]

# Available models (like Yarn Master's approach)
AVAILABLE_MODELS = {
    "yarn_bachelor": "Basic T5 Model (Fast)",
    "yarn_master": "Enhanced Pattern Generator (Recommended)", 
    "yarn_phd": "Advanced with Pattern Matching (Most Accurate)",
    "gemini_rag": "Gemini with RAG Pipeline (Most Advanced)"
}

# Initialize RAG components
class RAGPipeline:
    def __init__(self):
        if not RAG_AVAILABLE:
            self.text_encoder = None
            self.vector_db = None
            self.pattern_db = []
            return
            
        self.text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.image_encoder = None
        self.vector_db = None
        self.pattern_db = None
        self.load_vector_db()
    
    def load_vector_db(self):
        if not RAG_AVAILABLE:
            return
            
        try:
            if os.path.exists('pattern_vectors.faiss'):
                self.vector_db = faiss.read_index('pattern_vectors.faiss')
                with open('pattern_metadata.pkl', 'rb') as f:
                    self.pattern_db = pickle.load(f)
                logger.info("Vector database loaded successfully")
            else:
                logger.warning("Vector database not found, creating empty one")
                self.vector_db = faiss.IndexFlatIP(384)  # MiniLM embedding size
                self.pattern_db = []
        except Exception as e:
            logger.error(f"Error loading vector database: {e}")
            self.vector_db = faiss.IndexFlatIP(384)
            self.pattern_db = []
    
    def retrieve_similar_patterns(self, query_text: str, k: int = 3) -> List[dict]:
        if not RAG_AVAILABLE or not self.pattern_db:
            return []
        
        query_embedding = self.text_encoder.encode([query_text])
        scores, indices = self.vector_db.search(query_embedding, min(k, len(self.pattern_db)))
        
        similar_patterns = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.pattern_db):
                pattern = self.pattern_db[idx].copy()
                pattern['similarity_score'] = float(score)
                similar_patterns.append(pattern)
        
        return similar_patterns

rag_pipeline = RAGPipeline()
# Initialize pattern generator
try:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        pattern_generator = None
    else:
        pattern_generator = CrochetPatternGenerator(api_key)
    logger.info(f"Pattern generator initialized with {len(pattern_generator.training_data)} training examples")
except Exception as e:
    logger.error(f"Failed to initialize pattern generator: {e}")
    pattern_generator = None

class PatternRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=1000)
    style: str = Field(default="standard")
    model_type: str = Field(default="yarn_master")

    @validator('style')
    def validate_style(cls, v):
        normalized = v.lower().strip()
        if normalized not in VALID_STYLES:
            return "standard"
        return normalized
    
    @validator('model_type')
    def validate_model(cls, v):
        if v not in AVAILABLE_MODELS:
            return "yarn_master"
        return v

class PatternResponse(BaseModel):
    success: bool
    pattern: str
    generation_time: str
    style_used: str
    model_used: str
    materials: Optional[List[str]] = None
    difficulty: Optional[str] = None
    estimated_time: Optional[str] = None
    error: Optional[str] = None

@lru_cache(maxsize=100)
def generate_cached_pattern(description: str, style: str) -> str:
    """Use pattern generator instead of old T5 model"""
    if pattern_generator:
        skill_level = "BEGINNER" if "beginner" in style else "INTERMEDIATE"
        return pattern_generator.generate_pattern(description, skill_level)
    else:
        return "Pattern generator not available"

def get_file_hash(file_path: str) -> str:
    """Generate hash of file contents for caching"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def validate_image(file_path: str) -> bool:
    """Validate if file is a supported image format"""
    kind = filetype.guess(file_path)
    if kind is None:
        return False
    return kind.mime.startswith('image/')

def analyze_image_with_gemini(image_path: str) -> dict:
    """Enhanced Gemini Vision API for detailed crochet image analysis"""
    try:
        # Use the same API key as pattern generator
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY not set")
            return {"item_type": "crochet item", "description": "API key not configured"}
        genai.configure(api_key=api_key)
        vision_model = genai.GenerativeModel('gemini-1.5-flash')
        
        image = Image.open(image_path)
        
        prompt = """Analyze this crochet image in detail. Describe what you see:
        1. What type of crochet item is this? (scarf, blanket, amigurumi, hat, etc.)
        2. What colors do you see?
        3. What stitch patterns are visible?
        4. What size does it appear to be?
        5. What skill level would this require?
        6. What materials would be needed?
        
        Provide a detailed description for creating a crochet pattern."""
        
        response = vision_model.generate_content([prompt, image])
        result = response.text.strip()
        
        # Extract item type from the response
        item_type = "crochet item"
        result_lower = result.lower()
        for item in ["scarf", "blanket", "hat", "amigurumi", "sweater", "bag", "dishcloth", "coaster"]:
            if item in result_lower:
                item_type = item
                break
        
        logger.info(f"Gemini analysis successful: {item_type}")
        return {"item_type": item_type, "description": result}
        
    except Exception as e:
        logger.error(f"Gemini analysis failed: {str(e)}")
        return {"item_type": "crochet item", "description": f"Unable to analyze image: {str(e)}"}

def generate_pattern_with_rag(description: str, style: str, model_type: str) -> str:
    """Generate pattern using RAG pipeline"""
    if model_type == "gemini_rag":
        # Retrieve similar patterns
        similar_patterns = rag_pipeline.retrieve_similar_patterns(description, k=3)
        
        # Build context from similar patterns
        context = ""
        if similar_patterns:
            context = "\n\nSimilar patterns for reference:\n"
            for i, pattern in enumerate(similar_patterns, 1):
                context += f"\n{i}. {pattern.get('title', 'Pattern')}:\n"
                context += f"   Materials: {pattern.get('materials', 'N/A')}\n"
                context += f"   Instructions: {pattern.get('instructions', 'N/A')[:200]}...\n"
        
        # Use Gemini for pattern generation with context
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""Create a detailed crochet pattern for: {description}
                Style: {style}
                
                {context}
                
                Generate a complete pattern including:
                - Materials list with specific yarn weights and hook sizes
                - Gauge information
                - Abbreviations
                - Step-by-step instructions
                - Finishing details
                
                Make it {style} style and suitable for the described skill level."""
                
                response = model.generate_content(prompt)
                return response.text
        except Exception as e:
            logger.error(f"Gemini RAG generation failed: {e}")
    
    # Fallback to existing model
    return generate_cached_pattern(description, style)

def analyze_image_content_enhanced(image_path: str) -> str:
    """Enhanced OpenCV analysis focused on crochet items"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return "Unable to analyze image"
        
        # Simple but effective crochet detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect if image has organic/rounded shapes (amigurumi)
        contours, _ = cv2.findContours(cv2.Canny(gray, 50, 150), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # High circularity = likely amigurumi/toy
                if circularity > 0.7:
                    return "amigurumi toy"
                elif circularity > 0.4:
                    return "rounded crochet item"
        
        # Check aspect ratio for basic shape detection
        height, width = image.shape[:2]
        aspect_ratio = width / height
        
        if 0.8 <= aspect_ratio <= 1.2:
            return "square granny square"
        elif aspect_ratio > 2.0:
            return "long scarf"
        else:
            return "rectangular blanket"
            
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return "crochet item"

def analyze_image_content(image_path: str) -> str:
    """Enhanced crochet-specific image analysis"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return "Unable to analyze image"
        
        height, width = image.shape[:2]
        analysis_parts = []
        
        # 1. Shape and size analysis
        aspect_ratio = width / height
        if aspect_ratio > 2.0:
            shape = "long rectangular item like a scarf or table runner"
        elif aspect_ratio < 0.5:
            shape = "tall narrow item like a bookmark or belt"
        elif 0.8 <= aspect_ratio <= 1.2:
            shape = "square item like a dishcloth, coaster, or granny square"
        else:
            shape = "rectangular item like a blanket, placemat, or panel"
        
        # 2. Enhanced color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        dominant_colors = []
        
        # Analyze hue distribution
        hue_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        dominant_hues = np.argsort(hue_hist.flatten())[-3:][::-1]
        
        for hue in dominant_hues:
            if hue < 15 or hue > 165: dominant_colors.append("red")
            elif 15 <= hue < 45: dominant_colors.append("yellow/orange")
            elif 45 <= hue < 75: dominant_colors.append("green")
            elif 75 <= hue < 135: dominant_colors.append("blue")
            elif 135 <= hue <= 165: dominant_colors.append("purple/pink")
        
        color_desc = ", ".join(dominant_colors[:2]) if dominant_colors else "neutral tones"
        
        # 3. Texture and stitch pattern analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection for stitch definition
        edges = cv2.Canny(gray, 30, 100)
        edge_density = np.sum(edges > 0) / (height * width)
        
        # Texture analysis using Local Binary Patterns
        from skimage.feature import local_binary_pattern
        lbp = local_binary_pattern(gray, 8, 1, method='uniform')
        lbp_hist = np.histogram(lbp.ravel(), bins=10)[0]
        texture_variance = np.var(lbp_hist)
        
        # Pattern recognition
        if edge_density > 0.15 and texture_variance > 1000:
            stitch_pattern = "intricate stitch pattern with cables, bobbles, or lace work"
        elif edge_density > 0.08:
            stitch_pattern = "textured stitches like shells, clusters, or ripples"
        elif texture_variance > 500:
            stitch_pattern = "varied stitch pattern with color changes or simple textures"
        else:
            stitch_pattern = "solid stitches like single or double crochet"
        
        # 4. Enhanced object detection
        # Look for circular/round shapes (could be amigurumi)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        item_type = "crochet item"
        is_amigurumi = False
        
        if contours:
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Check if it's roughly circular (amigurumi)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if circularity > 0.6:  # Fairly circular
                    is_amigurumi = True
                    item_type = "amigurumi toy or stuffed item"
        
        # If not amigurumi, use shape analysis
        if not is_amigurumi:
            if "square" in shape and min(width, height) < max(width, height) * 1.2:
                if max(width, height) < 800:
                    item_type = "small square like a coaster, granny square, or dishcloth"
                else:
                    item_type = "large square like a pillow cover or afghan square"
            elif "rectangular" in shape:
                if aspect_ratio > 3:
                    item_type = "long narrow piece like a scarf, bookmark, or trim"
                elif aspect_ratio > 1.5:
                    item_type = "rectangular piece like a placemat, panel, or small blanket"
                else:
                    item_type = "blanket, throw, or large rectangular piece"
        
        # 5. Skill level estimation
        complexity_score = edge_density * 10 + (texture_variance / 1000)
        if complexity_score > 2.5:
            skill_level = "advanced"
        elif complexity_score > 1.0:
            skill_level = "intermediate"
        else:
            skill_level = "beginner"
        
        # Combine analysis
        analysis = f"This appears to be a {skill_level}-level {item_type} featuring {stitch_pattern}. The piece shows {color_desc} colors and has a {shape} overall form."
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return "Crochet item with standard stitches"

def extract_materials_from_pattern(pattern_text: str) -> List[str]:
    """Extract materials list from generated pattern"""
    materials = []
    lines = pattern_text.split('\n')
    in_materials = False
    
    for line in lines:
        if 'MATERIALS' in line.upper():
            in_materials = True
            continue
        elif in_materials and ('GAUGE' in line.upper() or 'ABBREVIATIONS' in line.upper()):
            break
        elif in_materials and line.strip() and not line.startswith('-'):
            materials.append(line.strip())
    
    return materials[:5]  # Return first 5 materials

def estimate_difficulty_and_time(pattern_text: str) -> tuple:
    """Estimate difficulty and completion time from pattern"""
    text_lower = pattern_text.lower()
    
    # Difficulty estimation
    if any(term in text_lower for term in ['beginner', 'easy', 'simple', 'basic']):
        difficulty = "Beginner"
        time_estimate = "2-4 hours"
    elif any(term in text_lower for term in ['intermediate', 'moderate']):
        difficulty = "Intermediate" 
        time_estimate = "4-8 hours"
    elif any(term in text_lower for term in ['advanced', 'complex', 'intricate']):
        difficulty = "Advanced"
        time_estimate = "8-16 hours"
    else:
        difficulty = "Intermediate"
        time_estimate = "4-6 hours"
    
    return difficulty, time_estimate

@app.post("/generate-pattern", response_model=PatternResponse, status_code=status.HTTP_200_OK)
async def generate_crochet_pattern(
    file: UploadFile = File(...),
    style: str = Body("standard"),
    model_type: str = Body("yarn_master"),
    user_prompt: str = Body("")
):
    try:
        logger.info(f"Processing uploaded file: {file.filename}")
        start_time = time.time()



        # Validate and normalize style
        normalized_style = style.lower().strip()
        if normalized_style not in VALID_STYLES:
            normalized_style = "standard"
            logger.warning(f"Invalid style '{style}' normalized to 'standard'")

        # Create upload directory if needed
        os.makedirs("uploaded_files", exist_ok=True)

        # Save and validate file
        temp_path = f"uploaded_files/{file.filename}"
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )

        if not validate_image(temp_path):
            os.remove(temp_path)
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Invalid or corrupted image file"
            )

        # Process image with enhanced analysis
        try:
            image = cv2.imread(temp_path)
            if image is None:
                raise ValueError("Unable to process image")

            # Enhanced image analysis
            image_analysis = analyze_image_content(temp_path)
            
            # Get detailed analysis from Gemini
            gemini_analysis = analyze_image_with_gemini(temp_path)
            item_type = gemini_analysis.get('item_type', 'crochet item')
            detailed_description = gemini_analysis.get('description', '')
            
            if user_prompt:
                clean_prompt = f"Create a crochet pattern for: {user_prompt}. Additional context: {detailed_description}"
            else:
                clean_prompt = f"Create a crochet {item_type} pattern. Description: {detailed_description}"
            
            # Use pattern generator for all requests
            skill_level = "BEGINNER" if "beginner" in normalized_style else "INTERMEDIATE"
            if pattern_generator:
                pattern_text = pattern_generator.generate_pattern(clean_prompt, skill_level)
            else:
                pattern_text = "Pattern generator not available"
            
            # Extract additional information
            materials = extract_materials_from_pattern(pattern_text)
            difficulty, time_estimate = estimate_difficulty_and_time(pattern_text)
            
            generation_time = time.time() - start_time
            logger.info(f"Pattern generated in {generation_time:.2f} seconds using {model_type}")

            return PatternResponse(
                success=True,
                pattern=pattern_text,
                generation_time=f"{generation_time:.2f}s",
                style_used=normalized_style,
                model_used=AVAILABLE_MODELS[model_type],
                materials=materials,
                difficulty=difficulty,
                estimated_time=time_estimate
            )

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing image: {str(e)}"
            )
        finally:
            # Cleanup temporary files
            try:
                os.remove(temp_path)
            except:
                pass

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/generate-pattern-from-text", response_model=PatternResponse)
async def generate_pattern_from_text(request: PatternRequest):
    try:
        logger.info(f"Generating pattern from text: {request.description}")
        start_time = time.time()

        if not pattern_generator:
            return PatternResponse(
                success=False,
                pattern="",
                generation_time="0s",
                style_used=request.style,
                error="Pattern generator not initialized",
                model_used="Error"
            )

        # Use the improved pattern generator
        skill_level = "BEGINNER" if "beginner" in request.style else "INTERMEDIATE"
        pattern_text = pattern_generator.generate_pattern(request.description, skill_level)
        
        # Extract additional information
        materials = extract_materials_from_pattern(pattern_text)
        difficulty, time_estimate = estimate_difficulty_and_time(pattern_text)
        
        generation_time = time.time() - start_time
        logger.info(f"Pattern generated in {generation_time:.2f} seconds using improved generator")

        return PatternResponse(
            success=True,
            pattern=pattern_text,
            generation_time=f"{generation_time:.2f}s",
            style_used=request.style,
            model_used="Improved Pattern Generator with Training Data",
            materials=materials,
            difficulty=difficulty,
            estimated_time=time_estimate
        )
    except Exception as e:
        logger.error(f"Error generating pattern: {str(e)}")
        return PatternResponse(
            success=False,
            pattern="",
            generation_time="0s",
            style_used=request.style,
            error=str(e),
            model_used=AVAILABLE_MODELS.get(request.model_type, "Unknown")
        )

@app.get("/models")
async def get_available_models():
    """Get list of available models"""
    return {
        "models": AVAILABLE_MODELS,
        "styles": VALID_STYLES,
        "default_model": "yarn_master",
        "default_style": "standard"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pattern_generator_loaded": pattern_generator is not None,
        "training_examples": len(pattern_generator.training_data) if pattern_generator else 0,
        "timestamp": time.time()
    }

@app.get("/debug-env")
async def debug_environment():
    """Debug endpoint to check Python environment"""
    import sys
    import subprocess
    
    try:
        import reportlab
        reportlab_version = reportlab.Version
        reportlab_available = True
    except ImportError as e:
        reportlab_version = None
        reportlab_available = False
        reportlab_error = str(e)
    
    # Check pip list for reportlab
    try:
        pip_result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True)
        pip_packages = pip_result.stdout
    except:
        pip_packages = "Could not get pip list"
    
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "python_path": sys.path,
        "reportlab_available": reportlab_available,
        "reportlab_version": reportlab_version,
        "reportlab_error": reportlab_error if not reportlab_available else None,
        "pip_packages": pip_packages,
        "working_directory": os.getcwd()
    }

@app.post("/generate-simple-pattern")
async def generate_simple_pattern(request: dict = Body(...)):
    """Generate pattern using training data"""
    try:
        description = request.get('description', '')
        skill_level = request.get('skill_level', 'INTERMEDIATE')
        
        logger.info(f"Generating pattern for: {description} (skill: {skill_level})")
        logger.info(f"Training data loaded: {len(pattern_generator.training_data)} examples")
        
        pattern = pattern_generator.generate_pattern(description, skill_level)
        
        logger.info(f"Generated pattern length: {len(pattern)} characters")
        
        return {
            "success": True,
            "pattern": pattern,
            "description": description,
            "skill_level": skill_level,
            "training_examples_used": len(pattern_generator.training_data)
        }
    except Exception as e:
        logger.error(f"Error in generate_simple_pattern: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Yarn Master API",
        "version": "1.0.0",
        "description": "AI-Powered Crochet Pattern Generator",
        "endpoints": {
            "/generate-pattern": "Generate pattern from image",
            "/generate-pattern-from-text": "Generate pattern from text description",
            "/generate-simple-pattern": "Generate pattern using training data",
            "/generate-pdf": "Generate PDF from pattern",
            "/models": "Get available models and styles",
            "/health": "Health check"
        }
    }