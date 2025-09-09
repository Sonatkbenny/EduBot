import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from bs4 import BeautifulSoup
from youtubesearchpython import VideosSearch
import streamlit as st
from config.settings import TFIDF_CONFIG
from typing import List, Dict, Any
import json
import re

class ResourceRecommender:
    """TF-IDF based educational resource recommendation system"""
    
    def __init__(self):
        self.config = TFIDF_CONFIG
        self.vectorizer = None
        self.resource_database = []
        self.tfidf_matrix = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize resource database with educational content"""
        self.resource_database = [
            {
                "title": "Introduction to Machine Learning",
                "type": "video",
                "url": "https://www.youtube.com/watch?v=KNAWp2S3w94",
                "description": "Comprehensive introduction to machine learning concepts and algorithms",
                "topics": ["machine learning", "algorithms", "data science", "artificial intelligence"],
                "difficulty": "beginner"
            },
            {
                "title": "Python Programming for Beginners",
                "type": "video", 
                "url": "https://www.youtube.com/watch?v=YYXdXT2l-Gg",
                "description": "Learn Python programming from scratch with practical examples",
                "topics": ["python", "programming", "coding", "software development"],
                "difficulty": "beginner"
            },
            {
                "title": "Statistics and Probability Fundamentals",
                "type": "article",
                "url": "https://www.khanacademy.org/math/statistics-probability",
                "description": "Core concepts in statistics and probability theory",
                "topics": ["statistics", "probability", "mathematics", "data analysis"],
                "difficulty": "intermediate"
            },
            {
                "title": "Deep Learning with Neural Networks",
                "type": "video",
                "url": "https://www.youtube.com/watch?v=aircAruvnKk",
                "description": "Understanding neural networks and deep learning architectures",
                "topics": ["deep learning", "neural networks", "artificial intelligence", "machine learning"],
                "difficulty": "advanced"
            },
            {
                "title": "Data Structures and Algorithms",
                "type": "course",
                "url": "https://www.coursera.org/learn/data-structures",
                "description": "Essential data structures and algorithmic concepts",
                "topics": ["data structures", "algorithms", "computer science", "programming"],
                "difficulty": "intermediate"
            }
        ]
    
    def _prepare_text_data(self, resources: List[Dict[str, Any]]) -> List[str]:
        """Prepare text data for TF-IDF vectorization"""
        text_data = []
        for resource in resources:
            # Combine title, description, and topics
            text = f"{resource['title']} {resource['description']} {' '.join(resource['topics'])}"
            text_data.append(text.lower())
        return text_data
    
    def _build_tfidf_matrix(self):
        """Build TF-IDF matrix from resource database"""
        if not self.resource_database:
            return
        
        text_data = self._prepare_text_data(self.resource_database)
        
        self.vectorizer = TfidfVectorizer(
            max_features=self.config['max_features'],
            ngram_range=self.config['ngram_range'],
            min_df=self.config['min_df'],
            stop_words='english'
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(text_data)
    
    def get_recommendations(self, user_interests: List[str], weak_topics: List[str], 
                          num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get personalized resource recommendations"""
        
        if not self.tfidf_matrix is not None:
            self._build_tfidf_matrix()
        
        # Combine user interests and weak topics
        query_text = " ".join(user_interests + weak_topics)
        
        # Transform query to TF-IDF vector
        query_vector = self.vectorizer.transform([query_text])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top recommendations
        top_indices = similarity_scores.argsort()[-num_recommendations:][::-1]
        
        recommendations = []
        for idx in top_indices:
            if similarity_scores[idx] > 0.1:  # Minimum similarity threshold
                resource = self.resource_database[idx].copy()
                resource['similarity_score'] = float(similarity_scores[idx])
                recommendations.append(resource)
        
        return recommendations
    
    def search_youtube_videos(self, topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for educational YouTube videos"""
        try:
            search_query = f"educational {topic} tutorial"
            videos_search = VideosSearch(search_query, limit=max_results)
            results = videos_search.result()
            
            videos = []
            for video in results.get('result', []):
                video_info = {
                    "title": video.get('title', ''),
                    "type": "youtube_video",
                    "url": video.get('link', ''),
                    "description": video.get('description', ''),
                    "duration": video.get('duration', ''),
                    "views": video.get('viewCount', {}).get('text', ''),
                    "channel": video.get('channel', {}).get('name', ''),
                    "similarity_score": 0.0
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            st.error(f"Error searching YouTube videos: {e}")
            return []
    
    def search_educational_articles(self, topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for educational articles and resources"""
        try:
            # Search in educational websites
            search_urls = [
                f"https://www.khanacademy.org/search?page_search_query={topic}",
                f"https://www.coursera.org/search?query={topic}",
                f"https://www.edx.org/search?q={topic}"
            ]
            
            articles = []
            for url in search_urls:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract article information (simplified)
                        article_info = {
                            "title": f"Educational content about {topic}",
                            "type": "article",
                            "url": url,
                            "description": f"Educational resources and articles about {topic}",
                            "source": url.split('/')[2],
                            "similarity_score": 0.0
                        }
                        articles.append(article_info)
                        
                        if len(articles) >= max_results:
                            break
                            
                except Exception as e:
                    continue
            
            return articles
            
        except Exception as e:
            st.error(f"Error searching educational articles: {e}")
            return []
    
    def get_personalized_recommendations(self, user_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Get comprehensive personalized recommendations"""
        
        user_interests = user_profile.get('interests', [])
        weak_topics = user_profile.get('weak_topics', [])
        learning_style = user_profile.get('learning_style', 'visual')
        
        recommendations = {
            'database_resources': [],
            'youtube_videos': [],
            'articles': [],
            'courses': []
        }
        
        # Get recommendations from database
        if user_interests or weak_topics:
            db_recommendations = self.get_recommendations(
                user_interests, weak_topics, num_recommendations=3
            )
            recommendations['database_resources'] = db_recommendations
        
        # Search for additional resources
        search_topics = weak_topics if weak_topics else user_interests
        
        for topic in search_topics[:3]:  # Limit to top 3 topics
            # YouTube videos
            youtube_videos = self.search_youtube_videos(topic, max_results=2)
            recommendations['youtube_videos'].extend(youtube_videos)
            
            # Articles
            articles = self.search_educational_articles(topic, max_results=2)
            recommendations['articles'].extend(articles)
        
        # Filter by learning style
        if learning_style == 'visual':
            recommendations['youtube_videos'] = recommendations['youtube_videos'][:3]
        elif learning_style == 'reading':
            recommendations['articles'] = recommendations['articles'][:3]
        
        return recommendations
    
    def add_custom_resource(self, resource: Dict[str, Any]):
        """Add custom resource to the database"""
        required_fields = ['title', 'type', 'url', 'description', 'topics']
        
        if all(field in resource for field in required_fields):
            self.resource_database.append(resource)
            # Rebuild TF-IDF matrix
            self._build_tfidf_matrix()
            return True
        else:
            return False
    
    def get_resource_statistics(self) -> Dict[str, Any]:
        """Get statistics about the resource database"""
        if not self.resource_database:
            return {}
        
        resource_types = {}
        difficulty_levels = {}
        topics = []
        
        for resource in self.resource_database:
            # Count resource types
            resource_type = resource.get('type', 'unknown')
            resource_types[resource_type] = resource_types.get(resource_type, 0) + 1
            
            # Count difficulty levels
            difficulty = resource.get('difficulty', 'unknown')
            difficulty_levels[difficulty] = difficulty_levels.get(difficulty, 0) + 1
            
            # Collect topics
            topics.extend(resource.get('topics', []))
        
        return {
            'total_resources': len(self.resource_database),
            'resource_types': resource_types,
            'difficulty_levels': difficulty_levels,
            'unique_topics': len(set(topics)),
            'top_topics': self._get_top_topics(topics)
        }
    
    def _get_top_topics(self, topics: List[str], top_n: int = 5) -> List[str]:
        """Get most common topics"""
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:top_n]]

# Global recommender instance
@st.cache_resource
def get_recommender():
    """Get cached recommender instance"""
    return ResourceRecommender()



