# Google Lens Result Scraper + AI Image Analysis Pipeline + FastAPI end-to-end service

This project provides a full python pipeline for analyzing images using Google Lens output. and generating an analysis using a large language model. The LLM provider could be any OpenAI SDK compatible LLM provider. I personally use [OpenRouter](https://openrouter.ai/docs/quickstart) wich can give easy access free llm providers. 

With `run_api.sh` you can run a really small api to which you can upload base64 encoded images, and get a analysis of it has a response, depending on the system prompt. Every configuration can be done my modifying `config.py`, from LLM provider, scrapping sizes, selenium headless mode, to prompting settings like sytem prompt and temperature. 

The main part is the Google Lens scrapping. I'm aware that a web-scrapping doesn't respect the rules of usage of most website, particularly Google. However this project aims to make a non production tools for people to make experiment with image analysis, making new datasets, all for free without any local computations.
## Project Overview

The pipeline consists of three main modules that can be run independently or together:

1. **Selenium Google Lens Module**: Uploads an image to Google Lens and extracts search result links
2. **Web Scraper Module**: Scrapes content from the search result URLs
3. **LLM Analysis Module**: Sends the scraped content to a large language model for analysis

## Installation

### Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Chromedriver matching your Chrome version

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the `secrets.py` file with your OpenRouter API key.

## Configuration

The project's behavior can be customized through the `config.py` file:

```python
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

```


## Usage

### Running the Complete Pipeline (API)

Start the FastAPI server:

```bash
./run_api.sh
```

The API will be available at http://localhost:8000

Send a request with a base64-encoded image:

```bash
BASE64_IMAGE=$(base64 -w 0 google.png)

# Create a temporary JSON file
JSON_FILE=$(mktemp)
echo "{\"image\":\"$BASE64_IMAGE\"}" > "$JSON_FILE"

# Send the request to the API using the correct endpoint and method
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d @"$JSON_FILE"

# Remove the temporary file
rm "$JSON_FILE"
```

### Running Modules Independently

#### 1. Google Lens Search

```bash
python selenium_utils.py --image path/to/image.jpg --output results.csv
```

#### 2. Web Scraper

```bash
python scraper.py --csv path/to/results.csv --output content.txt --max-urls 5 --char-limit 1000
```

#### 3. LLM Analysis

```bash
python openai_client.py --txt path/to/content.txt --output analysis.txt
```

## Troubleshooting

### Chrome Issues

If you encounter issues with Chrome:

1. Make sure your Chrome and chromedriver versions match

### API Connection Issues

If OpenRouter connections fail:

1. Check your API key in `secrets.py`
2. Verify your internet connection
3. Check the OpenRouter service status

## License

No License
