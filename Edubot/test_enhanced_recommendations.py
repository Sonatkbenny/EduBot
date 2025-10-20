"""
Test script for enhanced performance analysis with personalized recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.pages import analyze_weak_topics, generate_topic_recommendations
import json

def test_enhanced_recommendations():
    """Test the enhanced recommendation system"""
    
    # Sample performance data similar to what you showed in the screenshot
    sample_data = [
        {"topic": "CNN", "subject": "AI", "score": 0, "total_marks": 40, "percentage": 0.0},
        {"topic": "CNN", "subject": "AI", "score": 10, "total_marks": 40, "percentage": 25.0},
        {"topic": "CNN", "subject": "AI", "score": 15, "total_marks": 40, "percentage": 37.5},
        {"topic": "Machine Learning", "subject": "AI", "score": 35, "total_marks": 50, "percentage": 70.0},
        {"topic": "Python Programming", "subject": "Programming", "score": 45, "total_marks": 50, "percentage": 90.0},
        {"topic": "Data Structures", "subject": "Computer Science", "score": 20, "total_marks": 40, "percentage": 50.0},
    ]
    
    print("🎯 Testing Enhanced Performance Analysis System")
    print("=" * 60)
    
    # Test 1: Analyze weak topics
    print("\n1️⃣ Testing Weak Topic Analysis:")
    weak_topics = analyze_weak_topics(sample_data)
    print(f"   Identified weak topics: {json.dumps(weak_topics, indent=2)}")
    
    # Test 2: Generate recommendations
    print("\n2️⃣ Testing Recommendation Generation:")
    recommendations = generate_topic_recommendations(weak_topics)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   Recommendation {i}:")
        print(f"   📚 Topic: {rec['topic']}")
        print(f"   📊 Score: {rec['current_score']}")
        print(f"   🎯 Priority: {rec['urgency']}")
        print(f"   💭 Message: {rec['motivation'][:80]}...")
        print(f"   🔗 Quiz: {rec['quiz_link'][:50]}...")
        print(f"   🎥 Video: {rec['video_link'][:50]}...")
        print(f"   📖 Study: {rec['study_material'][:50]}...")
    
    print("\n✅ Test completed successfully!")
    print("\nThe enhanced performance analysis system is ready to be integrated into your EduBot!")
    
    return True

if __name__ == "__main__":
    test_enhanced_recommendations()
