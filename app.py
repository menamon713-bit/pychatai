from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])

        groq_messages = [
    {
        "role": "system",
        "content": (
            "أنت PyChatAI، مساعد ذكاء اصطناعي بالعربي، طوره Mena Mon. "
            "متقلش إنك ChatGPT أو OpenAI أو أي شركة تانية أبدًا. "
            "اسمك PyChatAI فقط. "
            "جاوب بالعربي بشكل أساسي، وباختصار ووضوح."
        )
    },
    *[{"role": m["role"], "content": m["content"]} for m in messages]
]

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "allam-2-7b",
                "messages": groq_messages
            }
        )

        result = response.json()

        if not response.ok:
            return jsonify({"error": result.get("error", {}).get("message", "Error")}), 500

        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
