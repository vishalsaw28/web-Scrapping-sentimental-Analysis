
# Sentiment analysis utilities for review data
from textblob import TextBlob
import pandas as pd
from typing import Dict, List
import re


class SentimentAnalyzer:
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or {
            'positive': 0.1,
            'negative': -0.1
        }
        
    def clean_text(self, text):
        """Clean and preprocess text for sentiment analysis"""
        if not isinstance(text, str):
            return ""
            
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()
        
    def analyze_sentiment(self, text):
        """Analyze sentiment of text using TextBlob"""
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text:
            return {'polarity': 0, 'subjectivity': 0, 'label': 'Neutral'}
            
        try:
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment label
            if polarity > self.thresholds['positive']:
                label = 'Positive'
            elif polarity < self.thresholds['negative']:
                label = 'Negative'
            else:
                label = 'Neutral'
                
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'label': label
            }
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {'polarity': 0, 'subjectivity': 0, 'label': 'Neutral'}
            
    def add_sentiment_to_reviews(self, reviews_df):
        """Add sentiment analysis to reviews dataframe"""
        sentiments = []
        
        for _, review in reviews_df.iterrows():
            text = f"{review.get('title', '')} {review.get('review_text', '')}"
            sentiment = self.analyze_sentiment(text)
            sentiments.append(sentiment)
            
        # Add sentiment columns
        reviews_df['sentiment_polarity'] = [s['polarity'] for s in sentiments]
        reviews_df['sentiment_subjectivity'] = [s['subjectivity'] for s in sentiments]
        reviews_df['sentiment_label'] = [s['label'] for s in sentiments]
        
        return reviews_df
        
    def get_sentiment_summary(self, reviews_df):
        """Get summary statistics of sentiment analysis"""
        if 'sentiment_label' not in reviews_df.columns:
            reviews_df = self.add_sentiment_to_reviews(reviews_df)
            
        summary = {
            'total_reviews': len(reviews_df),
            'positive_count': len(reviews_df[reviews_df['sentiment_label'] == 'Positive']),
            'negative_count': len(reviews_df[reviews_df['sentiment_label'] == 'Negative']),
            'neutral_count': len(reviews_df[reviews_df['sentiment_label'] == 'Neutral']),
            'avg_rating': reviews_df['rating'].mean() if 'rating' in reviews_df.columns else None,
            'avg_polarity': reviews_df['sentiment_polarity'].mean(),
            'avg_subjectivity': reviews_df['sentiment_subjectivity'].mean()
        }
        
        summary['positive_percentage'] = (summary['positive_count'] / summary['total_reviews']) * 100
        summary['negative_percentage'] = (summary['negative_count'] / summary['total_reviews']) * 100
        summary['neutral_percentage'] = (summary['neutral_count'] / summary['total_reviews']) * 100
        
        return summary