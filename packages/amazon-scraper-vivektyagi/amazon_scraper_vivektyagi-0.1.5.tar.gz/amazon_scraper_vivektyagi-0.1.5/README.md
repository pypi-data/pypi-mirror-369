# amazon_scraper

A simple and powerful Amazon.in product scraper built using Python and Selenium.  
It fetches product **title**, **price**, **rating**, **reviews**, and **image URL** using ASIN.

---

## 🚀 Features

- 🔍 Scrape product details from [Amazon India](https://www.amazon.in)
- 📦 Supports single or multiple ASINs
- 🧼 Automatically handles browser setup and teardown
- 💡 Lightweight and easy to use

---

## 📦 Installation

### From PyPI (Public):
```bash
pip install amazon-scraper-vivektyagi

Scrape a single product

from amazon_scraper_vivektyagi import get_amazon_product_details
data = get_amazon_product_details("B0C1234567")
print(data)

Scrape multiple products

from amazon_scraper_vivektyagi import get_multiple_product_details
asins = ["B0C1234567", "B0D7654321"]
results = get_multiple_product_details(asins)

for product in results:
    print(product)

✅ Output Format
{
    'ASIN': 'B0C1234567',
    'Title': 'Sample Product Title',
    'Price': '₹1,299.00',
    'Rating': '4.3 out of 5 stars',
    'Reviews': '345',
    'Image': 'https://m.media-amazon.com/images/I/xxxxx.jpg'
}

📄 Requirements

Python 3.6 or higher

Google Chrome installed

ChromeDriver (auto-installed via webdriver-manager)

Install dependencies:

pip install selenium beautifulsoup4 webdriver-manager

🔐 Private Access Option

If you want to limit access:

✅ Upload to a private GitHub repo and install with a personal token

✅ Use tools like AWS CodeArtifact, JFrog Artifactory, or Cloudsmith

✅ Or publish on TestPyPI instead of public PyPI

Want help with private publishing? Message the author.

👤 Author
Vivek Tyagi


📄 License
This project is licensed under the MIT License.

⚠️ Disclaimer
This tool is for educational purposes. Scraping Amazon may violate their terms of service. Use responsibly.