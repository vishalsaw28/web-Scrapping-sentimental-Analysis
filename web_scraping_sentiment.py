

import os
import sys
import pandas as pd
from datetime import datetime
import argparse

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.scraper import BestBuyScraper
from utils.sentiment import SentimentAnalyzer
import config


def create_directories():
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    

def scrape_reviews(product_urls, max_reviews=100):
    all_reviews = []
    
    for url in product_urls:
        print(f"\n{'='*50}")
        print(f"Scraping reviews from: {url}")
        print(f"{'='*50}")
        
        scraper = BestBuyScraper(
            headless=config.HEADLESS,
            max_reviews=max_reviews
        )
        
        reviews = scraper.scrape_product_reviews(url)
        all_reviews.extend(reviews)
        
        print(f"Scraped {len(reviews)} reviews from this product")
        
        # Add delay between products
        scraper.random_delay('medium')
    
    return all_reviews


def analyze_sentiment(reviews):
    print(f"\n{'='*50}")
    print("Performing Sentiment Analysis")
    print(f"{'='*50}")
    
    # Convert to DataFrame
    df = pd.DataFrame(reviews)
    
    if df.empty:
        print("No reviews to analyze")
        return df
        
    # Initialize sentiment analyzer
    analyzer = SentimentAnalyzer(thresholds=config.SENTIMENT_THRESHOLDS)
    
    # Add sentiment analysis
    df = analyzer.add_sentiment_to_reviews(df)
    
    # Get summary
    summary = analyzer.get_sentiment_summary(df)
    
    # Print summary
    print(f"\nSentiment Analysis Summary:")
    print(f"Total Reviews: {summary['total_reviews']}")
    print(f"Positive: {summary['positive_count']} ({summary['positive_percentage']:.1f}%)")
    print(f"Negative: {summary['negative_count']} ({summary['negative_percentage']:.1f}%)")
    print(f"Neutral: {summary['neutral_count']} ({summary['neutral_percentage']:.1f}%)")
    if summary['avg_rating']:
        print(f"Average Rating: {summary['avg_rating']:.2f}")
    else:
        print("No ratings found")
    print(f"Average Polarity: {summary['avg_polarity']:.3f}")
    
    return df


def generate_insights(df):
    print(f"\n{'='*50}")
    print("Business Insights")
    print(f"{'='*50}")
    
    if df.empty:
        print("No data for insights generation")
        return
        
    # Remove duplicates based on review text
    df = df.drop_duplicates(subset=['review_text'], keep='first')
    
    # Top positive reviews (filter by actual positive sentiment)
    positive_reviews = df[(df['sentiment_label'] == 'Positive') & (df['rating'] >= 4)].sort_values('sentiment_polarity', ascending=False)
    negative_reviews = df[(df['sentiment_label'] == 'Negative') & (df['rating'] <= 2)].sort_values('sentiment_polarity', ascending=True)
    
    print(f"\n🔹 Top Positive Aspects (High Rating + Positive Sentiment):")
    if not positive_reviews.empty:
        for i, (_, review) in enumerate(positive_reviews.head(3).iterrows()):
            title_preview = review['title'][:80] + "..." if len(review['title']) > 80 else review['title']
            rating = review.get('rating', 'N/A')
            print(f"   {i+1}. ⭐ {rating}/5 - {title_preview}")
            # Show a snippet of the review text
            text_preview = review['review_text'][:100] + "..." if len(review['review_text']) > 100 else review['review_text']
            print(f"      \"{text_preview}\"")
    else:
        print("   No strongly positive reviews found")
    
    print(f"\n🔹 Top Negative Aspects (Low Rating + Negative Sentiment):")
    if not negative_reviews.empty:
        for i, (_, review) in enumerate(negative_reviews.head(3).iterrows()):
            title_preview = review['title'][:80] + "..." if len(review['title']) > 80 else review['title']
            rating = review.get('rating', 'N/A')
            print(f"   {i+1}. ⭐ {rating}/5 - {title_preview}")
            # Show a snippet of the review text
            text_preview = review['review_text'][:100] + "..." if len(review['review_text']) > 100 else review['review_text']
            print(f"      \"{text_preview}\"")
    else:
        print("   No strongly negative reviews found")
    
    # Rating distribution
    if 'rating' in df.columns:
        rating_dist = df['rating'].value_counts().sort_index()
        print(f"\n📊 Rating Distribution:")
        for rating, count in rating_dist.items():
            percentage = (count / len(df)) * 100
            stars = "⭐" * int(rating)
            print(f"   {stars} {rating} stars: {count} reviews ({percentage:.1f}%)")
    
    # Sentiment vs Rating analysis
    print(f"\n🎯 Sentiment vs Rating Analysis:")
    sentiment_by_rating = df.groupby('rating')['sentiment_label'].value_counts().unstack(fill_value=0)
    print(sentiment_by_rating)


def main():
    print("HanuAI ML Assignment - Task 1")
    print("Web Scraping & Sentiment Analysis")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape BestBuy reviews and perform sentiment analysis')
    parser.add_argument('--url', type=str, help='Specific product URL to scrape')
    parser.add_argument('--max-reviews', type=int, default=config.MAX_REVIEWS, 
                       help='Maximum number of reviews to scrape')
    parser.add_argument('--headless', action='store_true', default=config.HEADLESS,
                       help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    # Determine which URLs to scrape
    if args.url:
        product_urls = [args.url]
    else:
        product_urls = config.PRODUCT_URLS
    
    try:
        # Step 1: Scrape reviews
        reviews = scrape_reviews(product_urls, args.max_reviews)
        
        if not reviews:
            print("No reviews were scraped. Exiting.")
            return
            
        # Step 2: Analyze sentiment
        df = analyze_sentiment(reviews)
        
        # Step 3: Save results
        output_file = config.OUTPUT_CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n💾 Results saved to: {output_file}")
        
        # Step 4: Generate insights
        generate_insights(df)
        
        # Step 5: Create report
        create_report(df, output_file)
        
        print(f"\n{'='*50}")
        print("✅ Task 1 Completed Successfully!")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"❌ Error in main execution: {str(e)}")
        import traceback
        traceback.print_exc()


def create_report(df, output_file):
    positive_count = len(df[df['sentiment_label'] == 'Positive'])
    negative_count = len(df[df['sentiment_label'] == 'Negative'])
    neutral_count = len(df[df['sentiment_label'] == 'Neutral'])
    
    # Calculate percentages
    total = len(df)
    positive_pct = (positive_count / total) * 100 if total > 0 else 0
    negative_pct = (negative_count / total) * 100 if total > 0 else 0
    neutral_pct = (neutral_count / total) * 100 if total > 0 else 0
    
    report_content = f"""
# HanuAI ML Assignment - Task 1 Report
## Web Scraping & Sentiment Analysis

### Executive Summary
- **Total Reviews Scraped**: {len(df)}
- **Date of Analysis**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source**: BestBuy Canada

### Sentiment Analysis Results
- **Positive Reviews**: {positive_count} ({positive_pct:.1f}%)
- **Negative Reviews**: {negative_count} ({negative_pct:.1f}%)
- **Neutral Reviews**: {neutral_count} ({neutral_pct:.1f}%)

### Key Findings
Based on the analysis of {len(df)} customer reviews:

#### 👍 What Customers Love:
- High-rated products with positive sentiment indicate satisfied customers
- Positive aspects typically relate to product quality, features, and value

#### 👎 Areas for Improvement:
- Negative reviews highlight specific pain points
- Common issues may include product defects, missing features, or poor support

### Anti-Scraping Measures Implemented
1. Random delays between requests
2. User-Agent rotation
3. Headless browser execution
4. Respectful crawling patterns
5. Error handling and retries

### Files Generated
- `{output_file}`: Contains all scraped reviews with sentiment analysis
- This report: Summary of findings and methodology

### Recommendations
1. **Monitor sentiment trends** over time to track product perception
2. **Address common issues** mentioned in negative reviews
3. **Leverage positive feedback** for marketing and product positioning
4. **Consider product improvements** based on recurring themes in reviews

### Technical Details
- **Scraping Method**: Selenium WebDriver with BeautifulSoup
- **Sentiment Analysis**: TextBlob with custom thresholds
- **Data Processing**: Pandas for analysis and CSV export
"""
    
    report_file = "reports/task1_summary_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📄 Summary report saved to: {report_file}")


if __name__ == "__main__":
    main()