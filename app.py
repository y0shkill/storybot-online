python
    from flask import Flask, request, jsonify
    import os, pathlib, datetime, requests
    
    app = Flask(name)
    
    @app.route("/webhook/gumroad", methods=["POST"])
    def gumroad_webhook():
        try:
            # Dados enviados pelo Gumroad (campos customizados)
            name = request.form.get("custom_child_name", "Child").strip()
            theme = request.form.get("custom_theme", "adventure").strip()
            language = request.form.get("custom_language", "English").strip()
    
            # Prompt que será enviado à OpenRouter
            prompt = (
                f"Write a magical story (150-200 words) for a child named '{name}'. "
                f"Theme: {theme}. Language: {language}. "
                f"Style: Whimsical, emotional, with a gentle moral. "
                f"Format: Markdown. End with: 'The End – Sweet Dreams, {name}!'"
            )
    
            # Cabeçalhos da API
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            }
    
            payload = {
                "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400
            }
    
            # Chamada à OpenRouter
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            story = response.json()["choices"][0]["message"]["content"]
    
            # Salva a história em /stories (pasta criada dinamicamente)
            pathlib.Path("stories").mkdir(exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.md"
            pathlib.Path(f"stories/{filename}").write_text(story, encoding="utf-8")
    
            # URL pública de download (Railway expõe a pasta /stories)
            download_url = f"https://{os.getenv('RAILWAY_STATIC_DOMAIN', request.host)}/stories/{filename}"
            return jsonify({"status": "ok", "file": filename, "download_url": download_url}), 200
    
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    
    @app.route("/")
    def home():
        return "StoryBot Online! Ready for webhooks."
    
    
    if name == "main":
        # Railway passa a porta via variável de ambiente PORT
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
