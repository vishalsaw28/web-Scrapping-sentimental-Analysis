

# Web Scraping Configuration
PRODUCT_URLS = [
"https://www.bestbuy.ca/en-ca/product/apple-airpods-pro-2-noise-cancelling-true-wireless-earbuds-with-usb-c-magsafe-charging-case/17278649 "]

# Scraping Settings
MAX_REVIEWS = 100
HEADLESS = True
MAX_SHOW_MORE_CLICKS = 30

# Timing Settings (in seconds)
SLEEP_SHORT = (1.0, 2.0)
SLEEP_MED = (2.0, 4.0)
SLEEP_LONG = (4.0, 6.0)

# Anti-Scraping Settings
ROTATE_USER_AGENTS = True
RANDOM_DELAYS = True
MAX_RETRIES = 3

# File Paths
OUTPUT_CSV = "data/processed/scraped_reviews.csv"
RAW_HTML_DIR = "data/raw/"

# Sentiment Analysis
SENTIMENT_THRESHOLDS = {
    'positive': 0.1,
    'negative': -0.1
}