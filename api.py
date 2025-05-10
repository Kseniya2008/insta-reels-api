from playwright.sync_api import sync_playwright
from flask import Flask, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

def scrape_reels(instagram_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(instagram_url, timeout=60000)
            page.wait_for_selector('article', timeout=10000)
            reel_elements = page.query_selector_all('a[href*="/reel/"]')
            reels = []

            for el in reel_elements:
                href = el.get_attribute("href")
                if href and "/reel/" in href:
                    reels.append(f"https://www.instagram.com{href}")

            return reels[:10]  # Возвращаем только 10 ссылок
        except Exception as e:
            return {"error": str(e)}
        finally:
            browser.close()

@app.route('/')
def index():
    return '🟢 Сервер работает! Отправь POST-запрос на /get-reels'

@app.route('/get-reels', methods=['POST'])
def get_reels():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return {"error": "URL не передан"}, 400
    result = scrape_reels(url)
    return json.dumps(result, ensure_ascii=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
