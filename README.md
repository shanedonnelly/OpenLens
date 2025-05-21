# Google Lens Result Scrapper + AI Image Analysis Pipeline + FastAPI end-to-end service

This project provides a full python pipeline for analyzing images using Google Lens output. and generating an analysis using a large language model. The LLM provider could be any OpenAI SDK compatible LLM provider. I personally use [OpenRouter](https://openrouter.ai/docs/quickstart) wich can give easy access to free llm providers. You could even use local models like Ollama to use the full pipeline unlimited. 

Quick explaination of the pipeline : 
- from an image, the scrapper upload it on Google Lens and scroll for more content,  wich result in a csv that contains the urls of the related websites (not the images url, this could be in th future) and the url description
- a more simple beautiful soop scrapper scrapps the main inner html body of the top urls (of the csv) and put all together in a txt. (it is the context containing anything that could be usefull)
- everything is send with a special system prompt to a LLM provider of your choice, wich only return text
-the text is then return back by fastapi

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
   git clone https://github.com/shanedonnelly/OpenLens.git
   cd OpenLens
   ```

2. Set yourselft in a python env and install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. If you do the full pipeline, provide your LLM API key in a file called : 
secret_key.py wich would look like :
```python
API_KEY = "<your_key>" 
```
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
....

```


## Usage

### Running the Complete Pipeline (API)

Start the FastAPI server:

```bash
./run_api.sh
```

The API will be available at http://localhost:8000

Send a request with a base64-encoded image like this:

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


## Result 

In this image, it's just one example of a simple output (where we ask for a small description)
with the corresponding image : 
![Screenshot](screenshot.png)
## Troubleshootin

### Chrome Issues

If you encounter issues with Chrome:

1. Make sure your Chrome and chromedriver versions match
2. You might need to modify the way we initialize the chrome driver. 

### API Connection Issues

If OpenRouter connections fail:

1. Check your API key in `secret_key.py`
2. Verify your internet connection
3. Check the OpenRouter service status

## License

No License
