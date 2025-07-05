from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import os
from email_alert import alert_system

app = Flask(__name__)

# 🛡️ Updated headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
}


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
            # 📄 Fetch page
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')

            # 🏷️ Get product title
            title_element = (
                soup.find("span", class_="VU-ZEz") or 
                soup.find("span", class_="B_NuCI") or 
                soup.find("h1")
            )
            product_title = title_element.get_text().strip() if title_element else "Unknown Product"

            # 💰 Try multiple price selectors (Flipkart changes often)
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
                # DEBUGGING: print HTML to console
                print("------ DEBUG: PAGE HTML START ------")
                print(soup.prettify()[:2000])  # Only first 2000 chars
                print("------ DEBUG: PAGE HTML END ------")
                result = "❌ Could not find the price on the page. Flipkart layout may have changed or blocked the request."

        except Exception as e:
            result = f"⚠️ Error: {e}"

    return render_template('index.html', result=result)


# 🔌 Required for Render deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
