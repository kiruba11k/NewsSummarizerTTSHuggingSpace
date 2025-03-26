import os
import re
import string
from typing import List, Dict, Any
from urllib.parse import quote
import requests
import nltk
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gtts import gTTS
from googletrans import Translator
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from flask import Flask, request

app = Flask(__name__)

# Use NLTK data
nltk.data.path.append('/usr/local/nltk_data')

# Initialize tools
lemmatizer = WordNetLemmatizer()
sia = SentimentIntensityAnalyzer()
translator = Translator()

AUDIO_SAVE_DIR = "/tmp/"

os.makedirs(AUDIO_SAVE_DIR, exist_ok=True)


def fetch_articles(company: str, max_articles=10) -> List[Dict[str, Any]]:
    """Fetches news articles using Google News RSS feed."""
    encoded_query = quote(company)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://news.google.com/"
    }

    try:
        response = requests.get(rss_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        articles = []

        for item in soup.find_all("item")[:max_articles]:
            title = item.find("title").text.strip() if item.find("title") else "No Title"
            link = item.find("link").text.strip() if item.find("link") else "No Link"
            summary = item.find("description").text.strip() if item.find("description") else "No summary available."

            articles.append({"title": title, "summary": summary, "url": link})

        return articles if articles else [{"error": f"No articles found for {company}"}]

    except requests.exceptions.RequestException as e:
        return [{"error": f"Failed to fetch news: {str(e)}"}]


def extract_topics(text: str, num_topics: int = 5) -> list:
    """Extracts important topics from a text using TF IDF."""
    if not text:
        return ["No valid text provided"]

    # Unescape HTML entities & remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove numbers, punctuation, and convert to lowercase
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation)).lower()

    # Tokenization
    words = re.findall(r'\b\w+\b', text)

    # Stopword removal & lemmatization
    stop_words = set(stopwords.words('english'))
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words and len(word) > 3]

    if len(words) < num_topics:
        return words

    # Apply TF IDF for keyword extraction
    vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([" ".join(words)])
    feature_names = vectorizer.get_feature_names_out()

    # Rank words based on TF IDF score
    word_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))
    sorted_topics = sorted(word_scores, key=word_scores.get, reverse=True)

    # Normalize topics (lemmatization)
    sorted_topics = [lemmatizer.lemmatize(topic.lower()) for topic in sorted_topics]

    return sorted_topics[:num_topics]


def analyze_sentiment(text: str) -> str:
    """Analyzes the sentiment of a given text."""
    if not text:
        return "Neutral"

    compound_score = sia.polarity_scores(text)['compound']

    if compound_score > 0.05:
        return "Positive"
    elif compound_score < -0.05:
        return "Negative"
    return "Neutral"


TEMP_DIR = "/tmp/"
os.makedirs(TEMP_DIR, exist_ok=True)


def text_to_speech(text, lang="hi"):
    """Convert text to speech and return a public URL for accessing the generated audio."""
    if not text.strip():
        return None

    filename = f"{hash(text)}.mp3"
    file_path = os.path.join(TEMP_DIR, filename)

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)
    except Exception as e:
        return {"error": f"⚠️ Failed to generate audio: {str(e)}"}

    # Generate a publicly accessible URL
    public_url = f"{request.host_url}get_audio?file_path={filename}"
    return public_url


def clean_and_shorten_text(text, max_length=5000):
    """ Cleans the text by removing duplicate sentences and truncating to max_length."""

    # Split text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    # Remove duplicate sentences while maintaining order
    seen = set()
    unique_sentences = [s for s in sentences if not (s in seen or seen.add(s))]

    # Reconstruct text
    cleaned_text = " ".join(unique_sentences)

    # Truncate if it exceeds max_length
    return cleaned_text[:max_length] if len(cleaned_text) > max_length else cleaned_text
