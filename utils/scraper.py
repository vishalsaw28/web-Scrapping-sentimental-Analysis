
import time
import random
import uuid
import requests
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    ElementClickInterceptedException
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import pandas as pd


class BestBuyScraper:
    def __init__(self, headless=True, max_reviews=100):
        self.headless = headless
        self.max_reviews = max_reviews
        self.driver = None
        self.ua = UserAgent()
        
    def init_driver(self):
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
            
        # Anti-detection configurations
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        chrome_options.add_argument(f"user-agent={self.ua.random}")
        
        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.set_page_load_timeout(30)
        
    def random_delay(self, delay_type='short'):
        delays = {
            'short': (1, 3),
            'medium': (3, 6),
            'long': (5, 10)
        }
        min_d, max_d = delays[delay_type]
        time.sleep(random.uniform(min_d, max_d))
        
    def scroll_to_element(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        self.random_delay('short')
        
    def safe_click(self, element):
        try:
            self.scroll_to_element(element)
            element.click()
            return True
        except ElementClickInterceptedException:
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except:
                return False
        return False
        
    def load_all_reviews(self, url):
        print(f"Loading product page: {url}")
        self.driver.get(url)
        self.random_delay('medium')
        
        # Handle cookie consent if present
        self.handle_cookie_consent()
        
        # Navigate to reviews section
        self.navigate_to_reviews()
        
        # Expand all reviews
        self.expand_reviews()
        
        return self.driver.page_source
        
    def handle_cookie_consent(self):
        try:
            consent_selectors = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Agree')]",
                "//button[contains(@id, 'accept')]",
                "//button[contains(@class, 'accept')]"
            ]
            
            for selector in consent_selectors:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if self.safe_click(button):
                        self.random_delay('short')
                        break
                except:
                    continue
        except:
            pass
            
    def navigate_to_reviews(self):
        review_selectors = [
            "//a[contains(@href, 'reviews')]",
            "//button[contains(text(), 'Reviews')]",
            "//span[contains(text(), 'Reviews')]/..",
            "//*[contains(@data-automation, 'review')]"
        ]
        
        for selector in review_selectors:
            try:
                review_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if self.safe_click(review_tab):
                    self.random_delay('medium')
                    print("Successfully navigated to reviews section")
                    return True
            except:
                continue
                
        print("Could not find reviews tab, continuing with current page...")
        return False
        
    def expand_reviews(self):
        show_more_selectors = [
            "//button[contains(text(), 'Show more')]",
            "//button[contains(text(), 'Load more')]",
            "//button[contains(@class, 'showMore')]",
            "//*[contains(@data-automation, 'show-more')]"
        ]
        
        clicks = 0
        max_clicks = 20
        
        while clicks < max_clicks:
            found_button = False
            
            for selector in show_more_selectors:
                try:
                    show_more_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    if show_more_btn.is_displayed():
                        self.safe_click(show_more_btn)
                        self.random_delay('medium')
                        found_button = True
                        clicks += 1
                        print(f"Clicked 'Show More' ({clicks}/{max_clicks})")
                        break
                        
                except:
                    continue
                    
            if not found_button:
                print("No more 'Show More' buttons found")
                break
                
            # Safety check - don't overload
            if clicks >= max_clicks:
                print("Reached maximum click limit")
                break
                
    def extract_reviews(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        reviews = []
        
        # Multiple strategies to find review containers
        review_containers = []
        
        # Strategy 1: Look for review articles
        review_containers.extend(soup.find_all('article'))
        
        # Strategy 2: Look for elements with review-related classes
        review_classes = ['review', 'reviewItem', 'customerReview']
        for class_name in review_classes:
            review_containers.extend(soup.find_all(class_=lambda x: x and class_name in x.lower()))
            
        # Strategy 3: Look for elements containing star ratings
        star_containers = soup.find_all(attrs={"aria-label": lambda x: x and "star" in str(x).lower()})
        for container in star_containers:
            parent_review = container.find_parent('div') or container.find_parent('article')
            if parent_review and parent_review not in review_containers:
                review_containers.append(parent_review)
                
        print(f"Found {len(review_containers)} potential review containers")
        
        for container in review_containers:
            try:
                review_data = self.parse_review_container(container)
                if review_data and self.is_valid_review(review_data):
                    reviews.append(review_data)
                    
                # Stop if we have enough reviews
                if len(reviews) >= self.max_reviews:
                    break
                    
            except Exception as e:
                continue
                
        return reviews
        
    def parse_review_container(self, container):
        review_id = str(uuid.uuid4())[:8]
        
        # Extract rating
        rating = self.extract_rating(container)
        
        # Extract review text
        review_text = self.extract_review_text(container)
        
        # Extract title
        title = self.extract_title(container)
        
        # Extract date
        date = self.extract_date(container)
        
        # Extract reviewer name
        reviewer_name = self.extract_reviewer_name(container)
        
        return {
            'id': review_id,
            'title': title,
            'review_text': review_text,
            'date': date,
            'rating': rating,
            'source': 'BestBuy Canada',
            'reviewer_name': reviewer_name
        }
        
    def extract_rating(self, container):
        # Method 1: aria-label attribute
        rating_elements = container.find_all(attrs={"aria-label": True})
        for elem in rating_elements:
            aria_label = elem.get('aria-label', '')
            if 'star' in aria_label.lower() and 'out of' in aria_label.lower():
                try:
                    rating_text = aria_label.split('out of')[0].strip()
                    return float(rating_text)
                except:
                    continue
                    
        # Method 2: Look for numeric patterns
        import re
        text_content = container.get_text()
        rating_match = re.search(r'(\d(?:\.\d)?)\s*(?:/5|out of 5|stars?)', text_content, re.IGNORECASE)
        if rating_match:
            try:
                return float(rating_match.group(1))
            except:
                pass
                
        return None
        
    def extract_review_text(self, container):
        # Try multiple selectors for review body
        selectors = [
            '.reviewText', '.review-body', '.review-content',
            '[data-automation="review-body"]', '.comment', '.content'
        ]
        
        for selector in selectors:
            element = container.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 10:
                    return text
                    
        # Fallback: get all text and clean it
        all_text = container.get_text(strip=True)
        if len(all_text) > 50:
            return ' '.join(all_text.split()[:100])  # Limit length
            
        return ""
        
    def extract_title(self, container):
        title_selectors = ['h3', 'h4', '.review-title', '.title']
        for selector in title_selectors:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""
        
    def extract_date(self, container):
        from dateutil import parser
        
        date_selectors = [
            '.review-date', '.date', 'time',
            '[data-automation="review-date"]'
        ]
        
        for selector in date_selectors:
            element = container.select_one(selector)
            if element:
                date_text = element.get_text(strip=True)
                try:
                    # Clean date text
                    date_text = date_text.replace('Reviewed', '').replace('on', '').strip()
                    parsed_date = parser.parse(date_text, fuzzy=True)
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
                    
        return ""
        
    def extract_reviewer_name(self, container):
        name_selectors = [
            '.reviewer-name', '.author', '.user-name',
            '[data-automation="reviewer-name"]'
        ]
        
        for selector in name_selectors:
            element = container.select_one(selector)
            if element:
                return element.get_text(strip=True)
                
        return "Anonymous"
        
    def is_valid_review(self, review_data):
        return (
            review_data.get('review_text') and 
            len(review_data['review_text']) > 10 and
            review_data.get('rating') is not None
        )
        
    def scrape_product_reviews(self, product_url):
        try:
            self.init_driver()
            html_content = self.load_all_reviews(product_url)
            reviews = self.extract_reviews(html_content)
            return reviews
            
        except Exception as e:
            print(f"Error scraping {product_url}: {str(e)}")
            return []
            
        finally:
            if self.driver:
                self.driver.quit()
                
    def save_reviews_to_csv(self, reviews, filename):
        if not reviews:
            print("No reviews to save")
            return
            
        df = pd.DataFrame(reviews)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Saved {len(reviews)} reviews to {filename}")