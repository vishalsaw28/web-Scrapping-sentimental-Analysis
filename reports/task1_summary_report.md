# 📘 HanuAI ML Assignment – Task 1 Report

## Web Scraping & Sentiment Analysis

**Prepared by:** Vishal Kumar  
**Date:** October 18, 2025

---

## 🧭 Executive Summary

| Metric                    | Value               |
| ------------------------- | ------------------- |
| **Total Reviews Scraped** | 15                  |
| **Source**                | BestBuy Canada      |
| **Date of Analysis**      | 2025-10-18 12:14:21 |
| **Positive Reviews**      | 12 (80.0%)          |
| **Negative Reviews**      | 2 (13.3%)           |
| **Neutral Reviews**       | 1 (6.7%)            |

---

## 💡 Key Findings

### 👍 What Customers Love

- High-rated products with strong customer satisfaction
- Positive comments often highlight **sound quality**, **comfort**, and **noise cancellation**
- Many users recommend the product for its **premium feel** and **performance**

### 👎 Areas for Improvement

- A few negative reviews mention **connectivity issues** or **feature limitations**
- Some dissatisfaction arises from **price sensitivity** or **device compatibility**

---

## 🛡️ Anti-Scraping Measures Implemented

1. Randomized delays between requests to avoid detection
2. Dynamic **User-Agent rotation** to simulate real browsers
3. **Headless browser** execution for dynamic content
4. Respectful crawling intervals and rate limits
5. Retry mechanisms and exception handling for failed requests

---

## 📁 Files Generated

| File                                 | Description                                                   |
| ------------------------------------ | ------------------------------------------------------------- |
| `data/processed/scraped_reviews.csv` | Contains all scraped reviews with sentiment scores and labels |
| `HanuAI_Task1_Summary_Report.pdf`    | Final summary of findings and insights                        |

---

## 🎯 Recommendations

1. **Track sentiment trends** over time to monitor changes in product perception
2. **Investigate negative feedback themes** (e.g., usability or performance)
3. **Leverage positive customer feedback** in marketing materials
4. **Iterate product improvements** based on recurring issues identified in reviews

---

## ⚙️ Technical Implementation

| Component              | Technology Used                                         |
| ---------------------- | ------------------------------------------------------- |
| **Web Scraping**       | Selenium WebDriver + BeautifulSoup                      |
| **Sentiment Analysis** | TextBlob (polarity-based sentiment scoring)             |
| **Data Handling**      | Pandas (for data cleaning, aggregation, and CSV export) |
| **Output Format**      | CSV and Markdown/PDF reports                            |

---

## 🧾 Summary

The sentiment analysis of **15 customer reviews** from **BestBuy Canada** reveals a predominantly **positive perception (80%)** of the product, indicating strong market acceptance.  
However, attention should be given to minor usability issues raised in negative reviews to enhance the customer experience.

---

**Prepared by:** _Vishal Kumar_  
**Date:** _October 18, 2025_
