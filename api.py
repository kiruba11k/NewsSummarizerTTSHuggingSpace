import os
from flask import Flask, request, jsonify, send_file
from nltk.stem import WordNetLemmatizer
from deep_translator import GoogleTranslator
from itertools import combinations
from utils import fetch_articles, analyze_sentiment, extract_topics, clean_and_shorten_text, text_to_speech
from waitress import serve

app = Flask(__name__)
lemmatizer = WordNetLemmatizer()
TEMP_DIR = "/tmp/" 
os.makedirs(TEMP_DIR, exist_ok=True)


@app.route("/get_audio", methods=["GET"])
def get_audio():
    """Serve the generated audio file dynamically."""
    filename = request.args.get("file_path")

    if not filename:
        return jsonify({"error": "No file specified."}), 400

    file_path = os.path.join(TEMP_DIR, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": " File not found."}), 404

    return send_file(file_path, mimetype="audio/mpeg")


@app.route("/analyze_news", methods=["POST"])
def analyze_news():
    """Fetch news, perform sentiment analysis, extract topics, compare articles, and generate Hindi speech."""
    data = request.get_json()
    company = data.get("company", "").strip()

    if not company:
        return jsonify({"error": "Company name is required"}), 400

    articles = fetch_articles(company)
    if not articles or "error" in articles[0]:
        return jsonify({"error": f"No articles found for {company}."}), 404

    processed_articles = []
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment = analyze_sentiment(article["summary"])
        topics = extract_topics(article["summary"])
        sentiment_counts[sentiment] += 1

        processed_articles.append({
            "Title": article["title"],
            "Summary": article["summary"],
            "Sentiment": sentiment,
            "Topics": topics,
        })

    if len(processed_articles) < 2:
        final_sentiment = (
            f"{company}’s latest news coverage is mostly positive."
            if sentiment_counts["Positive"] > sentiment_counts["Negative"]
            else f"{company}’s latest news coverage is mixed or negative."
        )

        # Translate the final sentiment to Hindi
        final_summary = clean_and_shorten_text(final_sentiment)
        translated_summary = GoogleTranslator(source="en", target="hi").translate(final_summary)
        audio_url = text_to_speech(translated_summary, lang="hi")

        return jsonify({
            "Company": company,
            "Articles": processed_articles,
            "Final Sentiment Analysis": final_sentiment,
            "Audio": audio_url,
        }), 200

    # Topic overlap and coverage differences
    coverage_differences = []
    topic_overlap = {
        "Common Topics": list(set.intersection(*(set(a["Topics"]) for a in processed_articles))),
        "Unique Topics per Article": [
            list(set(a["Topics"]) - set.intersection(*(set(b["Topics"]) for b in processed_articles)))
            for a in processed_articles
        ]
    }

    for (idx1, article1), (idx2, article2) in combinations(enumerate(processed_articles), 2):
        sentiment1, sentiment2 = article1["Sentiment"], article2["Sentiment"]
        comparison = (f"Article {idx1 + 1} discusses {sentiment1} aspects, while Article {idx2 + 1} discusses "
                      f"{sentiment2} aspects.")

        if sentiment1 == "Positive" and sentiment2 == "Negative":
            impact = "This contrast suggests controversy, potentially impacting investor confidence."
        elif sentiment1 == "Negative" and sentiment2 == "Positive":
            impact = "The differing viewpoints indicate uncertainty, requiring further investigation."
        elif sentiment1 == sentiment2 == "Positive":
            impact = "Consistently positive coverage strengthens public trust in the company."
        elif sentiment1 == sentiment2 == "Negative":
            impact = "Negative coverage may raise concerns among stakeholders."
        else:
            impact = "The coverage presents a neutral stance, offering a balanced perspective."

        impact += " The articles share similar topics but offer different perspectives." if set(
            article1["Topics"]) & set(
            article2["Topics"]) else " The coverage spans multiple areas, providing a broader industry outlook."

        coverage_differences.append({"Comparison": comparison, "Impact": impact})

    final_sentiment = f"{company}’s latest news coverage leans {max(sentiment_counts, key=sentiment_counts.get)}."
    impact_summary = " ".join([item["Impact"] for item in coverage_differences])
    final_summary = f"{company} का समाचार विश्लेषण: {final_sentiment}. प्रभाव का सारांश: {impact_summary}"
    final_summary = clean_and_shorten_text(final_summary)
    translated_summary = GoogleTranslator(source="en", target="hi").translate(final_summary)
    audio_url = text_to_speech(translated_summary, lang="hi")

    return jsonify({
        "Company": company,
        "Articles": processed_articles,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_counts,
            "Coverage Differences": coverage_differences,
            "Topic Overlap": topic_overlap
        },
        "Final Sentiment Analysis": final_sentiment,
        "Audio": audio_url,
    }), 200


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=7860)
