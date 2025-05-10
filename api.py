from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import re
import requests

app = Flask(__name__)
CORS(app)

def extract_views(text):
    try:
        digits = re.sub(r"[^\d]", "", text)
        return int(digits)
    except:
        return 0

def get_reels_data(profile_url, max_reels=100):
    links = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(profile_url, timeout=60000)
            page.wait_for_timeout(3000)

            scrolls = 0
            while len(links) < max_reels and scrolls < 30:
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(2000)
                scrolls += 1

                reel_elems = page.locator('a[href*="/reel/"]')
                urls = reel_elems.evaluate_all("els => els.map(e => e.href)")
                links = list(dict.fromkeys(urls))

            reels = []
            for link in links[:max_reels]:
                try:
                    page.goto(link, timeout=30000)
                    page.wait_for_timeout(2000)
                    views_elem = page.locator('span:has-text("просмотров")')
                    views_text = views_elem.first.inner_text()
                    views_num = extract_views(views_text)
                    reels.append({
                        "url": link,
                        "views": views_num,
                        "views_text": views_text
                    })
                except:
                    reels.append({
                        "url": link,
                        "views": 0,
                        "views_text": "не удалось получить"
                    })

            browser.close()
            sorted_top = sorted(reels, key=lambda r: r['views'], reverse=True)
            return sorted_top[:10]

        except Exception as e:
            browser.close()
            return {"error": str(e)}

@app.route("/")
def index():
    return "🟢 Сервер работает. Отправь POST-запрос на /get-reels с JSON: {'url': 'https://instagram.com/...'}"

@app.route("/get-reels", methods=["POST"])
def get_reels():
    data = request.get_json()
    url = data.get("url")

    if not url or not url.startswith("http"):
        return jsonify({"error": "Некорректный URL"}), 400

    result = get_reels_data(url, max_reels=100)

    # Отправляем результат на Webhook в Make
    webhook_url = "https://hook.us2.make.com/n1ko8dtvjhn7vt32igsdhoobmtc5jnce"
    try:
        requests.post(webhook_url, json={"reels": result})
    except Exception as e:
        print(f"Ошибка при отправке в Make: {e}")

    return jsonify({"status": "ok", "sent_to_make": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
