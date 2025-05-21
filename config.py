"""
Configuration module for Google Lens Scraper
"""
import os

class Config:
    # Selenium settings
    HEADLESS_MODE = True
    
    # Image settings (this is only when usung the fastapi backend)
    IMAGE_FILE_EXTENSION = "png"
    
    # Scraper settings
    MAX_URLS_TO_SCRAPE = 10
    MAX_CHARACTERS_IN_SUMMARY = 2000
    
    # Directories
    IMAGE_DIR = "images"
    CSV_DIR = "csv"
    TXT_DIR = "txt"
    
    #What to remove at the end of pipeline
    REMOVE_IMAGES = True
    REMOVE_CSVS = True 
    REMOVE_TXT = False
    
    # LLM Client settings
    # by default, OpenRouter API is used
    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL = "meta-llama/llama-4-scout:free"
    
    #LLM parameters
    TEMPERATURE = 0.8
    
    #LLM Prompt
    SYSTEM_PROMPT = "You are given text content from websites found after a google lens research on an image, that means that the website content is related to the image " \
                   "The order of the result matters " \
                   "You do not talk to any user " \
                    "Your goal is to make in a few words (less than 25) a precise description of what the image is most likely, including the image type (drawing, screenshot painting, photo of a painting.... ) Not more than this" \
                    "Format the response in this way: " \
                     "description: <description>, nothing else "  
                     
    
    # OTHER_SYSTEM_PROMPT = "You are given text content from websites found after a google lens research on an image, that means that the website content is related to the image " \
    #                "The order of the result matters " \
    #                "You do not talk to any user " \
    #                 "You need to give a very  small specify the type of image (photo, drawing, painting, etc.) You can make assumption on this " \
    #                 "Make a small and precise description of the image, no sentences, just a few words, but with all infos that best describe what the image probably is" \
    #               "Your goal is to give the most precise description of the image based of thoses infos. You give a description of what the image is most likely " \
    #                 "The description could be any length from a few word to 90 chars (depending on the given infos), but the title should be short and precise,  " \
    #                 "You can make (not mendatory ) small assumption about the image , but not too much, if you have engouht info do not make somes" \
    #                 "Do not over describe the image, only the most important things about it" \
    #                "Give the response in this format: title: <title> " \
    #                  "description: <description> "\
    #                 "consticency : pourcent (%) about how all sources make sense togethers " \
    #                  "and not in any other format " \
    #                 "Do not make any assumption about the image, just describe it, " 
    
    # Make directories if they don't exist
    @classmethod
    def create_dirs(cls):
        for dir_path in [cls.IMAGE_DIR, cls.CSV_DIR, cls.TXT_DIR]:
            os.makedirs(dir_path, exist_ok=True)
        return True

# OpenAI system prompt
