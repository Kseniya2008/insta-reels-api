from flask import Flask, request, jsonify
import asyncio
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def extract_date_from_html(html):
    match = re.search(r'"uploadDate":"([\d\-T:]+)', html)
    if match:
        try:
            return datetime.fromisoformat(match.group(1).split('T')[0])
        except:
            return None
    return None

async def get_top_reels(profile_url, max_reels=50):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        await page.goto(profile_url)
        await asyncio.sleep(2)

        for _ in range(15):
            await page.mouse.wheel(0, 2000)
            await asyncio.sleep(1)

        reel_links = await page.locator("a[href*='/reel/']").all()
        urls = []
        for a in reel_links:
            href = await a.get_attribute("href")
            if href and href not in urls:
                urls.append("https://www.instagram.com" + href)
            if len(urls) >= max_reels:
                break

        results = []
        one_year_ago = datetime.now() - timedelta(days=365)

        for link in urls:
            await page.goto(link)
            await asyncio.sleep(1.5)
            content = await page.content()

            post_date = extract_date_from_html(content)
            if not post_date or post_date < one_year_ago:
                continue

            match = re.search(r'([\d,.]+)\s+просмотров', content)
            if match:
                views_text = match.group(1).replace(',', '').replace('.', '')
                try:
                    views = int(views_text)
                    results.append({
                        'url': link,
                        'views': views,
                        'date': post_date.strftime('%d.%m.%Y')
                    })
                except:
                    pass

        await browser.close()
        results.sort(key=lambda x: x['views'], reverse=True)
        return results[:10]

@app.route("/get-reels", methods=["POST"])
def get_reels():
    data = request.get_json()
    url = data.get("url", "")
    if not url.startswith("https://www.instagram.com/"):
        return jsonify({"error": "Неверный формат ссылки"}), 400

    try:
        result = asyncio.run(get_top_reels(url))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def hello():
    return "👋 Сервер работает! Отправляй POST-запрос на /get-reels"

if __name__ == "__main__":
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

