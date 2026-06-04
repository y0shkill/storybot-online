python
from flask import Flask, request, jsonify
import os, pathlib, datetime, requests

app = Flask(__name__)

@app.route("/webhook/gumroad", methods=["POST"])
def gumroad_webhook():
    try:
        name = request.form.get("custom_child_name", "Child").strip()
        theme = request.form.get("custom_theme", "adventure").strip()
        language = request.form.get("custom_language", "English").strip()

        prompt = (
            f"Write a magical story (150-200 words) for a child named '{name}'. "
            f"Theme: {theme}. Language: {language}. "
            f"Style: Whimsical, emotional, with a gentle moral. "
            f"Format: Markdown. End with: 'The End – Sweet Dreams, {name}!'"
        )

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        story = response.json()["choices"][0]["message"]["content"]

        pathlib.Path("stories").mkdir(exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{name}_{ts}.md"
        pathlib.Path(f"stories/{fname}").write_text(story, encoding="utf-8")

        download_url = f"https://{os.getenv('RAILWAY_STATIC_DOMAIN', request.host)}/stories/{fname}"
        return jsonify({"status": "ok", "file": fname, "download_url": download_url}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/")
def home():
    return "StoryBot Online! Ready for webhooks."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
