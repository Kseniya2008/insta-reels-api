@app.route("/get-reels", methods=["POST"])
def get_reels():
    data = request.get_json()
    url = data.get("url")
    
    return jsonify({"status": "ok", "message": "сервер отвечает", "url": url})
