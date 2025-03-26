# News Summarization and Text-to-Speech(TTS) Application

## Overview
This project provides a web-based application that extracts key details from multiple news articles related
to a given company, performs sentiment analysis, conducts a comparative analysis, and
generates a text-to-speech (TTS) output in Hindi.. The system consists of two main components:

- **Frontend (Gradio UI):** Hosted on Hugging Face Spaces, providing an interactive UI for users to enter a company name and retrieve sentiment analysis and an audio summary.
- **Backend (Flask API):** Hosted separately on Hugging Face Spaces, responsible for fetching news articles, performing sentiment analysis, extracting topics, comparing news coverage, and generating an audio summary.

## Features
- Fetches recent news articles for a given company.
- Performs sentiment analysis using NLTK's Vader Sentiment Analyzer.
- Extracts key topics using TF IDF.
- Compares sentiment scores across articles.
- Translates the summary into Hindi using Google Translator.
- Converts the translated text into Hindi speech using Google Text-to-Speech (gTTS).

## Project Structure
```
NEWS-Summarizer-TTS/

│   ├── app.py  # Gradio UI

│   ├── api.py  # Flask API for processing news and generating TTS
│   ├── utils.py  # Helper functions for fetching, analyzing, and processing data

```

## Installation and Setup
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Hugging Face account to deploy on Spaces
- Virtual environment (recommended)
- Required Python dependencies

### Clone the Repository
```sh
git clone https://github.com/kiruba11k/NewsSummarizerTTSHuggingSpace.git
cd NewsSummarizerTTSHuggingSpace
```

### Set Up 

1. Create a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the Flask API locally:
   ```sh
   python api.py
   ```
4. If deploying on Hugging Face Spaces, create a `requirements.txt` and `DockerFile` and push the backend code.

---

## Dependencies
- **Backend:**
  - Flask
  - nltk
  - requests
  - deep_translator
  - gtts
  - waitress
  - bs4
  - scikit-learn
- **Frontend:**
  - Gradio
  - Requests

Install all dependencies using:
```sh
pip install -r requirements.txt
```

---

## API Endpoints
| Endpoint         | Method | Description |
|-----------------|--------|-------------|
| `/analyze_news` | POST   | Fetches news, analyzes sentiment, extracts topics, and generates TTS. |
| `/get_audio`    | GET    | Serves the generated Hindi speech audio file. |

---

## Deployment
### Deploy Backend on Hugging Face Spaces
1. Create a new Space(Gradio) for the backend on Hugging Face.
2. Upload `api.py`, `utils.py`, `requirements.txt`, and `DockerFile`.
3. Set the Space to `Flask` and deploy.
4. Copy the backend URL (`https://huggingface.co/spaces/Kiruba11/NEWS-TTS-Backend/analyze_news`).

### Deploy Frontend on Hugging Face Spaces
1. Create a new Space(Docker) for the frontend.
2. Upload `app.py`, `requirements.txt`, and `DockerFile`.
3. Update `FLASK_API_URL` in `app.py` to match your backend URL.
4. Deploy the frontend Space.

---


## Backend  (Flask API)

 The API will be available at `https://huggingface.co/spaces/Kiruba11/NEWS-TTS-Backend/analyze_news`

## Frontend  (Gradio UI)

 The UI will be available at `https://huggingface.co/spaces/Kiruba11/NEWS-Summarizer-TTS/`

## API Endpoints
### 1. `/analyze_news` (POST)
#### Request Body:
```json
{
  "company": "Tesla"
}
```
#### Response:
```json
{
  "Company": "Tesla",
  "Articles": [...],
  "Comparative Sentiment Score": {...},
  "Final Sentiment Analysis": "Tesla's latest news coverage leans Positive.",
  "Audio": "https://huggingface.co/spaces/Kiruba11/NEWS-TTS-Backend/get_audio?file_path=tesla_summary.mp3"
}
```

### 2. `/get_audio` (GET)
#### Query Parameter:
`file_path`: The path to the generated audio file.
#### Response:
Returns the MP3 file for playback.

## How It Works
1. The **frontend** (Gradio UI) sends a request to the **backend** with a company name.
2. The **backend** fetches news articles from Google News, performs **sentiment analysis**, and extracts **key topics**.
3. It compares sentiment across articles and summarizes the findings in **Hindi**.
4. The summary is converted to **speech (MP3)** and made available via a URL.
5. The **frontend** displays the JSON output and plays the generated speech.


## Notes
- The backend may require a `requirements.txt` file listing all dependencies for proper deployment on Hugging Face.
- Google News RSS may have rate limits; consider caching results for efficiency.
- Ensure that the backend Space has sufficient permissions to execute Python scripts and access external APIs.

## Author
**Kirubakaran Periyasamy**  
GitHub: [kiruba11k](https://github.com/kiruba11k)  

---
