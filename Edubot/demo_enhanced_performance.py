import streamlit as st
from models.enhanced_performance import get_enhanced_performance_analyzer
from frontend.components import create_enhanced_recommendation_card
import random
from datetime import datetime, timedelta

def create_sample_performance_data():
    """Create sample performance data for demo purposes"""
    sample_topics = [
        "Sorting Algorithms", "Data Structures", "Machine Learning", 
        "Database Management", "Web Development", "Operating Systems",
        "Computer Networks", "Algorithms", "Python Programming", 
        "Mathematics", "Object-Oriented Programming"
    ]
    
    sample_subjects = ["Computer Science", "Mathematics", "Programming", "Theory"]
    
    sample_data = []
    base_date = datetime.now() - timedelta(days=60)
    
    for i in range(20):  # Generate 20 sample entries
        topic = random.choice(sample_topics)
        subject = random.choice(sample_subjects)
        
        # Simulate some topics being weaker than others
        if topic in ["Sorting Algorithms", "Machine Learning", "Mathematics", "Database Management"]:
            score = random.randint(25, 58)  # Weaker topics (< 60%)
        else:
            score = random.randint(65, 95)  # Stronger topics (>= 60%)
            
        total_marks = 100
        entry_date = base_date + timedelta(days=random.randint(0, 60))
        
        sample_data.append({
            "subject": subject,
            "topic": topic,
            "score": score,
            "total_marks": total_marks,
            "created_at": entry_date.isoformat(),
            "percentage": score  # For compatibility
        })
    
    return sample_data

def main():
    """Main demo function"""
    st.set_page_config(
        page_title="EduBot - Enhanced Performance Analysis Demo",
        page_icon="🎯",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Enhanced Performance Analysis Demo</h1>
        <p>Experience personalized learning recommendations based on your weak topics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo explanation
    st.markdown("""
    ## 🎉 What's New in Your EduBot?
    
    Your Performance Analysis page now includes **personalized learning recommendations**! Here's what's been enhanced:
    
    ### ✨ New Features:
    - **🔍 Smart Analysis**: Automatically identifies weak topics (score < 60%)
    - **🎯 Personalized Recommendations**: Custom study resources for each weak topic
    - **📚 Resource Links**: Direct access to quizzes, YouTube tutorials, and study materials
    - **💬 Motivational Messages**: Encouraging feedback based on your performance level
    - **🎨 Beautiful UI**: Modern cards with interactive buttons
    
    ### 📊 Priority Levels:
    - **🔴 High Priority**: < 30% - "Don't worry! Everyone starts somewhere..."
    - **🟡 Medium Priority**: 30-45% - "You're making progress! Keep practicing..."
    - **🟢 Low Priority**: 45-60% - "You're close to mastering this!"
    """)
    
    st.markdown("---")
    
    # Load sample data button
    if st.button("🎲 Load Sample Performance Data", type="primary"):
        sample_data = create_sample_performance_data()
        st.session_state.demo_performance_data = sample_data
        st.success("📊 Sample data loaded! Check out the recommendations below.")
        st.rerun()
    
    # Check if we have data to demo
    if 'demo_performance_data' not in st.session_state:
        st.info("👆 Click the button above to load sample performance data and see the enhanced recommendations in action!")
        return
    
    performance_data = st.session_state.demo_performance_data
    
    # Use the enhanced performance analyzer
    st.markdown("## 🚀 Enhanced Analysis in Action")
    
    analyzer = get_enhanced_performance_analyzer()
    analyzer['display_all'](performance_data)
    
    # Show implementation details
    st.markdown("---")
    st.markdown("## 🛠️ Implementation Details")
    
    with st.expander("📋 View Sample Data Structure", expanded=False):
        st.json(performance_data[:3])  # Show first 3 entries
    
    with st.expander("🔧 Code Integration", expanded=False):
        st.markdown("""
        ### Files Modified in Your EduBot Project:
        
        1. **`models/enhanced_performance.py`** - New analysis engine
        2. **`frontend/pages.py`** - Updated performance page  
        3. **`frontend/components.py`** - New recommendation cards
        
        ### Key Functions:
        ```python
        # Analyze performance and identify weak topics
        analyze_student_performance(performance_data)
        
        # Generate personalized recommendations  
        generate_personalized_recommendations(weak_topics, overall_average)
        
        # Display beautiful recommendation cards
        display_recommendation_card(recommendation)
        ```
        
        The enhanced system is **fully integrated** with your existing EduBot project!
        """)
    
    # Clear data button
    if st.button("🗑️ Clear Demo Data"):
        if 'demo_performance_data' in st.session_state:
            del st.session_state.demo_performance_data
        st.success("Demo data cleared!")
        st.rerun()

if __name__ == "__main__":
    main()
