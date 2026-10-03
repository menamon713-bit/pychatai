from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def search_knowledge(question):
    try:
        with open('knowledge.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = content.split('===')
        question_lower = question.lower()
        relevant = []
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                title = sections[i].strip()
                body = sections[i + 1].strip()
                
                title_words = title.replace('=', '').strip().split()
                for word in title_words:
                    if len(word) > 2 and word in question_lower:
                        relevant.append(f"=== {title} ===\n{body}")
                        break
                
                for word in question_lower.split():
                    if len(word) > 3 and word in body.lower():
                        if not any(title in r for r in relevant):
                            relevant.append(f"=== {title} ===\n{body}")
                            break
        
        if relevant:
            return "\n\n".join(relevant[:2])
        return ""
    except Exception:
        return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        user_question = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_question = m["content"]
                break
        
        knowledge = search_knowledge(user_question)
        
        system_content = (
            "أنت PyChatAI، مساعد ذكاء اصطناعي بالعربي. "
            "تم تطويرك بواسطة فريق minaSefendev بقيادة المطور مينا سيفين. "
            "متقلش إنك ChatGPT أو OpenAI أو NCAI أو أي شركة تانية أبدًا. "
            "لو سُئلت عن هويتك، قل: 'أنا PyChatAI، طورني فريق minaSefendev بقيادة المطور مينا سيفين'. "
            "جاوب بالعربي بشكل أساسي، وباختصار ووضوح."
        )
        
        if knowledge:
            system_content += f"\n\nاستخدم المعلومات دي للإجابة إن أمكن:\n{knowledge}"
        
        groq_messages = [
            {"role": "system", "content": system_content},
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
