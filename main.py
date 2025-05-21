from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel
import base64
import os
import uuid
from selenium_lens_scraper import run_google_lens_search
from bs4_small_scraper import scrape_first_urls
from llm_analysis import get_llm_analysis
import logging
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create necessary directories
Config.create_dirs()

app = FastAPI(title="Google Lens Scraper API")

class ImageRequest(BaseModel):
    image: str  # base64 encoded image

def remove_files(request_id: str):
    if Config.REMOVE_IMAGES:
        image_path = f"{Config.IMAGE_DIR}/image_{request_id}.{Config.IMAGE_FILE_EXTENSION}"
        if os.path.exists(image_path):
            os.remove(image_path)
            logger.info(f"Removed image file: {image_path}")
    if Config.REMOVE_CSVS:
        csv_path = f"{Config.CSV_DIR}/results_{request_id}.csv"
        if os.path.exists(csv_path):
            os.remove(csv_path)
            logger.info(f"Removed CSV file: {csv_path}")
    if Config.REMOVE_TXT:
        txt_path = f"{Config.TXT_DIR}/content_{request_id}.txt"
        if os.path.exists(txt_path):
            os.remove(txt_path)
            logger.info(f"Removed text file: {txt_path}")


@app.get("/")
async def root():
    return {"message": "Google Lens Scraper API is running. Use /analyze endpoint with a base64 encoded image."}

@app.post("/analyze")
async def process_image(request: ImageRequest, background_tasks: BackgroundTasks):
    try:
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())
        logger.info(f"Processing new request: {request_id}")
        
        # Decode and save base64 image
        image_path = f"{Config.IMAGE_DIR}/image_{request_id}.{Config.IMAGE_FILE_EXTENSION}"
        try:
            with open(image_path, "wb") as img_file:
                img_data = base64.b64decode(request.image)
                img_file.write(img_data)
            logger.info(f"Image saved at {image_path}")
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            raise HTTPException(status_code=400, detail="Invalid base64 image")
        
        # Run Google Lens search
        csv_path = f"{Config.CSV_DIR}/results_{request_id}.csv"
        logger.info(f"Starting Google Lens search for image")
        result = run_google_lens_search(image_path, csv_path)
        if not result:
            raise HTTPException(status_code=500, detail="Google Lens search failed")
        logger.info(f"Google Lens results saved to {csv_path}")
        
        # Scrape content from URLs
        txt_path = f"{Config.TXT_DIR}/content_{request_id}.txt"
        logger.info(f"Scraping content from top URLs")
        scraped_content = scrape_first_urls(
            csv_path, 
            txt_path, 
            max_urls=Config.MAX_URLS_TO_SCRAPE, 
            char_limit=Config.MAX_CHARACTERS_IN_SUMMARY
        )
        logger.info(f"Scraped content saved to {txt_path}")
        
        # Get OpenAI analysis
        logger.info(f"Sending content to LLM for analysis")
        analysis = get_llm_analysis(scraped_content)
        logger.info(f"Analysis received from LLM")
        
        background_tasks.add_task(func=remove_files, request_id=request_id)
        return {"analysis": analysis}
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")