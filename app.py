from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import os
from email_alert import alert_system

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        url = request.form['url']
        user_email = request.form['email']

        try:
            set_price = float(request.form['price'])
        except ValueError:
            return render_template('index.html', result="❌ Invalid price input.")

        try:
            # ✅ ScraperAPI setup
            SCRAPER_API_KEY = os.getenv("a7fe103cc9df4e22a62801faf89a4e74")
            if not SCRAPER_API_KEY:
                return render_template('index.html', result="❌ Missing ScraperAPI key.")

            # 🧠 Use ScraperAPI with JS rendering enabled
            scrape_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={url}&render=true"
            page = requests.get(scrape_url)
            soup = BeautifulSoup(page.content, 'html.parser')

            # 🏷️ Get product title
            title_element = (
                soup.find("span", class_="VU-ZEz") or 
                soup.find("span", class_="B_NuCI") or 
                soup.find("h1")
            )
            product_title = title_element.get_text().strip() if title_element else "Unknown Product"

            # 💰 Try multiple price selectors (dynamic + legacy)
            price_element = (
                soup.find("div", class_="_30jeq3 _16Jk6d") or
                soup.find("div", class_="_1_WHN1") or
                soup.find("div", class_="_25b18c") or
                soup.find("div", class_="CEmiEU") or
                soup.find("div", string=lambda text: text and "₹" in text)
            )

            if price_element:
                price_text = price_element.get_text().strip()
                price_number = float(price_text.replace('₹', '').replace(',', ''))

                if price_number <= set_price:
                    alert_system(product_title, url, user_email)
                    result = f"✅ Price dropped! Email sent to {user_email} for: {product_title} (₹{price_number})"
                else:
                    result = f"ℹ️ Price is still ₹{price_number}, above your target of ₹{set_price}."
            else:
                # Optional debug output (can comment out)
                print("------ DEBUG: PAGE HTML START ------")
                print(soup.prettify()[:2000])
                print("------ DEBUG: PAGE HTML END ------")
                result = "❌ Could not find the price on the page. Even with ScraperAPI."

        except Exception as e:
            result = f"⚠️ Error: {e}"

    return render_template('index.html', result=result)


# 🟢 Make it work on Render (bind to 0.0.0.0 and dynamic port)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
