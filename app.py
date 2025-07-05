from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import os
from email_alert import alert_system

app = Flask(__name__)  # ✅ define app BEFORE using @app.route

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1",
    "Connection": "close"
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
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')

            # Get product title
            title_element = soup.find("span", class_="VU-ZEz")
            product_title = title_element.get_text().strip() if title_element else "Unknown Product"

            # Get price
            price_element = soup.find("div", class_="Nx9bqj CxhGGd")
            if price_element:
                price_text = price_element.get_text().strip()
                price_number = float(price_text.replace('₹', '').replace(',', ''))

                if price_number <= set_price:
                    alert_system(product_title, url, user_email)
                    result = f"✅ Price dropped! Email sent to {user_email} for: {product_title} (₹{price_number})"
                else:
                    result = f"ℹ️ Price is still ₹{price_number}, above your target of ₹{set_price}."
            else:
                result = "❌ Could not find the price on the page. Flipkart layout may have changed."

        except Exception as e:
            result = f"⚠️ Error: {e}"

    return render_template('index.html', result=result)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render provides a PORT env variable
    app.run(host='0.0.0.0', port=port)
