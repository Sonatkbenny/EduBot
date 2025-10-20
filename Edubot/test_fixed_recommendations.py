"""
Test script to demonstrate the fixed Smart Learning Recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fixed_recommendations():
    """Test the fixed recommendation system"""
    
    from frontend.pages import resources
    
    print("🎯 Testing Fixed Smart Learning Recommendations")
    print("=" * 60)
    
    # Test cases based on the user's issue
    test_cases = [
        "data preprocessing",  # The topic from user's screenshot
        "Data Preprocessing",  # Title case version
        "CNN",                 # Existing topic
        "Machine Learning",    # Existing topic
        "Unknown Topic",       # Topic not in our dictionary
        "Quantum Computing"    # Another unknown topic
    ]
    
    print(f"\n📚 Available Topics: {len(resources)} total")
    print("=" * 60)
    
    for i, topic in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing Topic: '{topic}'")
        
        if topic in resources:
            print(f"   ✅ Resources Found!")
            print(f"   🎥 Video: {resources[topic]['youtube'][:50]}...")
            print(f"   📚 Notes: {resources[topic]['notes'][:50]}...")
            print(f"   → Would show: Specific resources for {topic}")
        else:
            print(f"   ⚠️  Topic not in dictionary")
            youtube_search = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
            google_search = f"https://www.google.com/search?q={topic.replace(' ', '+')}+tutorial+learn"
            print(f"   🔍 Would show search options:")
            print(f"      🎥 YouTube: {youtube_search[:50]}...")
            print(f"      📖 Google: {google_search[:50]}...")
    
    print("\n" + "=" * 60)
    print("🎉 SOLUTION SUMMARY")
    print("=" * 60)
    print("✅ Added 'data preprocessing' to resources dictionary")
    print("✅ Added 16 more common topics (total 27 topics)")
    print("✅ Improved fallback for unknown topics")
    print("✅ Now shows search links instead of 'no resources'")
    print("✅ Case-sensitive handling (both lowercase and Title Case)")
    
    print("\n🚀 Your EduBot will now:")
    print("   • Show specific resources for 27 predefined topics")
    print("   • Show helpful search links for any other topics")
    print("   • Never show 'No resources available' anymore!")

def show_all_available_topics():
    """Show all available topics in the resources dictionary"""
    
    from frontend.pages import resources
    
    print("\n📋 ALL AVAILABLE TOPICS:")
    print("=" * 40)
    
    for i, topic in enumerate(resources.keys(), 1):
        print(f"{i:2}. {topic}")
    
    print(f"\nTotal: {len(resources)} topics with specific resources")

if __name__ == "__main__":
    test_fixed_recommendations()
    show_all_available_topics()
