import gradio as gr
import requests

FLASK_API_URL = "https://Kiruba11-NEWS-TTS-Backend.hf.space/analyze_news"


def analyze_news(company_name):
    """Fetch news analysis from Flask API."""
    if not company_name.strip():
        return "⚠️ Please enter a valid company name.", None

    try:
        response = requests.post(FLASK_API_URL, json={"company": company_name})
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            return f"❌ Error: {data['error']}", None

        audio_url = data.get("Audio", None)
        result = {
            "Company": company_name,
            "Articles": data.get("Articles", []),
            "Comparative Sentiment Score": {
                "Sentiment Distribution": data.get("Comparative Sentiment Score", {}).get("Sentiment Distribution", {}),
                "Coverage Differences": data.get("Comparative Sentiment Score", {}).get("Coverage Differences", []),
                "Topic Overlap": data.get("Comparative Sentiment Score", {}).get("Topic Overlap", {})
            },
            "Final Sentiment Analysis": data.get("Final Sentiment Analysis", "N/A"),
        }

        return result, audio_url if audio_url else ""

    except requests.exceptions.RequestException as e:
        return f"❌ Failed to connect to the API: {str(e)}", None


iface = gr.Interface(
    fn=analyze_news,
    inputs=gr.Textbox(label="Enter Company Name"),
    outputs=[
        gr.JSON(label="News Analysis"),
        gr.Audio(label="Generated Audio", type="filepath" if FLASK_API_URL.startswith("http") else "url", 
                 interactive=False)
    ],
    title="📰 News Sentiment Analysis",
    description="Enter a company name to analyze recent news sentiment and generate speech output in Hindi."
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=None)
