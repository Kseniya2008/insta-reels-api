from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "🟢 Сервер работает. Отправь POST-запрос на /get-reels с JSON: {'url': 'https://instagram.com/...'}"

@app.route("/get-reels", methods=["POST"])
def get_reels():
    data = request.get_json()
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "URL не передан"}), 400
    
    return jsonify({
        "status": "ok",
        "message": "сервер отвечает",
        "url": url
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
