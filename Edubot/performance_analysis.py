import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Any
import random

# Sample resource mapping for topics (you can expand this or load from JSON file)
TOPIC_RESOURCES = {
    "Sorting Algorithms": {
        "quiz_link": "https://www.geeksforgeeks.org/quiz-corner-gq/",
        "video_link": "https://www.youtube.com/watch?v=kPRA0W1kECg",
        "study_material": "https://www.geeksforgeeks.org/sorting-algorithms/",
        "description": "Master different sorting techniques like QuickSort, MergeSort, and BubbleSort"
    },
    "Data Structures": {
        "quiz_link": "https://www.hackerrank.com/domains/data-structures",
        "video_link": "https://www.youtube.com/watch?v=RBSGKlAvoiM",
        "study_material": "https://www.tutorialspoint.com/data_structures_algorithms/",
        "description": "Understand arrays, linked lists, stacks, queues, and trees"
    },
    "Machine Learning": {
        "quiz_link": "https://www.kaggle.com/learn",
        "video_link": "https://www.youtube.com/watch?v=aircAruvnKk",
        "study_material": "https://scikit-learn.org/stable/tutorial/index.html",
        "description": "Learn supervised, unsupervised, and reinforcement learning concepts"
    },
    "Database Management": {
        "quiz_link": "https://www.w3schools.com/sql/sql_quiz.asp",
        "video_link": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
        "study_material": "https://www.w3schools.com/sql/",
        "description": "Master SQL queries, database design, and normalization"
    },
    "Web Development": {
        "quiz_link": "https://www.w3schools.com/html/html_quiz.asp",
        "video_link": "https://www.youtube.com/watch?v=UB1O30fR-EE",
        "study_material": "https://developer.mozilla.org/en-US/docs/Learn",
        "description": "Build modern web applications with HTML, CSS, JavaScript, and frameworks"
    },
    "Operating Systems": {
        "quiz_link": "https://www.sanfoundry.com/operating-system-questions-answers/",
        "video_link": "https://www.youtube.com/watch?v=26QPDBe-NB8",
        "study_material": "https://www.tutorialspoint.com/operating_system/",
        "description": "Understand processes, memory management, and file systems"
    },
    "Computer Networks": {
        "quiz_link": "https://www.sanfoundry.com/computer-networks-questions-answers/",
        "video_link": "https://www.youtube.com/watch?v=IPvYjXCsTg8",
        "study_material": "https://www.tutorialspoint.com/data_communication_computer_network/",
        "description": "Learn about TCP/IP, routing, switching, and network protocols"
    },
    "Algorithms": {
        "quiz_link": "https://www.hackerrank.com/domains/algorithms",
        "video_link": "https://www.youtube.com/watch?v=0IAPZzGSbME",
        "study_material": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/",
        "description": "Master algorithmic thinking and problem-solving techniques"
    },
    "Python Programming": {
        "quiz_link": "https://www.w3schools.com/python/python_quiz.asp",
        "video_link": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
        "study_material": "https://docs.python.org/3/tutorial/",
        "description": "Learn Python fundamentals, OOP, and advanced concepts"
    },
    "Mathematics": {
        "quiz_link": "https://www.khanacademy.org/math",
        "video_link": "https://www.youtube.com/watch?v=fNk_zzaMoSs",
        "study_material": "https://www.khanacademy.org/math/algebra",
        "description": "Strengthen your mathematical foundation for computer science"
    }
}

def analyze_performance(performance_data: List[Dict]) -> Dict[str, Any]:
    """
    Analyze student performance and identify weak topics (< 60%)
    
    Args:
        performance_data: List of performance entries with subject, topic, score, total_marks
        
    Returns:
        Dictionary containing analysis results including weak topics
    """
    if not performance_data:
        return {
            "total_entries": 0,
            "overall_average": 0,
            "weak_topics": [],
            "strong_topics": [],
            "subject_averages": {},
            "needs_improvement": False
        }
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(performance_data)
    df['percentage'] = (df['score'] / df['total_marks']) * 100
    
    # Calculate topic-wise averages
    topic_averages = df.groupby('topic')['percentage'].mean().to_dict()
    
    # Identify weak topics (< 60%)
    weak_topics = {topic: avg for topic, avg in topic_averages.items() if avg < 60}
    strong_topics = {topic: avg for topic, avg in topic_averages.items() if avg >= 60}
    
    # Calculate subject averages
    subject_averages = df.groupby('subject')['percentage'].mean().to_dict()
    
    # Overall statistics
    overall_average = df['percentage'].mean()
    
    return {
        "total_entries": len(performance_data),
        "overall_average": overall_average,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "topic_averages": topic_averages,
        "subject_averages": subject_averages,
        "needs_improvement": len(weak_topics) > 0 or overall_average < 70,
        "performance_trend": calculate_trend(df) if len(df) > 1 else "Insufficient data"
    }

def calculate_trend(df: pd.DataFrame) -> str:
    """Calculate performance trend over time"""
    if 'created_at' in df.columns:
        df['date'] = pd.to_datetime(df['created_at'], errors='coerce')
        df_sorted = df.dropna(subset=['date']).sort_values('date')
        
        if len(df_sorted) >= 2:
            recent_avg = df_sorted.tail(3)['percentage'].mean()
            earlier_avg = df_sorted.head(3)['percentage'].mean()
            
            if recent_avg > earlier_avg + 5:
                return "📈 Improving"
            elif recent_avg < earlier_avg - 5:
                return "📉 Declining"
            else:
                return "📊 Stable"
    
    return "📊 Stable"

def generate_recommendations(weak_topics: Dict[str, float], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate personalized recommendations for weak topics
    
    Args:
        weak_topics: Dictionary of weak topics with their average scores
        analysis: Performance analysis results
        
    Returns:
        List of recommendation cards with resources
    """
    recommendations = []
    
    if not weak_topics:
        # If no weak topics, provide motivational message
        return [{
            "type": "motivation",
            "title": "🎉 Excellent Performance!",
            "message": "You're performing well across all topics! Keep up the great work and consider exploring advanced topics.",
            "action": "Continue practicing to maintain your strong performance!"
        }]
    
    # Sort weak topics by score (lowest first)
    sorted_weak = sorted(weak_topics.items(), key=lambda x: x[1])
    
    for topic, score in sorted_weak[:5]:  # Top 5 weakest topics
        # Check if we have specific resources for this topic
        resources = TOPIC_RESOURCES.get(topic, {
            "quiz_link": "https://www.khanacademy.org/",
            "video_link": "https://www.youtube.com/",
            "study_material": "https://www.google.com/search?q=" + topic.replace(" ", "+"),
            "description": f"Practice and improve your understanding of {topic}"
        })
        
        # Create motivational message based on score
        if score < 30:
            motivation = f"Don't worry about {topic}! Everyone starts somewhere. These resources will help you build a strong foundation."
            urgency = "🔴 High Priority"
        elif score < 45:
            motivation = f"You're making progress in {topic}! With focused practice, you'll see significant improvement."
            urgency = "🟡 Medium Priority"
        else:
            motivation = f"You're close to mastering {topic}! Just a little more practice will get you there."
            urgency = "🟢 Low Priority"
        
        recommendation = {
            "type": "improvement",
            "topic": topic,
            "current_score": f"{score:.1f}%",
            "urgency": urgency,
            "motivation": motivation,
            "quiz_link": resources["quiz_link"],
            "video_link": resources["video_link"],
            "study_material": resources["study_material"],
            "description": resources["description"]
        }
        
        recommendations.append(recommendation)
    
    # Add general study tips if overall performance needs improvement
    if analysis["overall_average"] < 70:
        general_tips = {
            "type": "general_tips",
            "title": "💡 General Study Tips",
            "tips": [
                "Create a structured study schedule",
                "Practice active recall techniques",
                "Form study groups with classmates",
                "Take regular breaks using the Pomodoro technique",
                "Seek help from instructors when needed"
            ]
        }
        recommendations.append(general_tips)
    
    return recommendations

def create_recommendation_card(recommendation: Dict[str, Any]) -> None:
    """Create a styled recommendation card in Streamlit"""
    
    if recommendation["type"] == "motivation":
        st.success(f"""
        ### {recommendation['title']}
        {recommendation['message']}
        
        **{recommendation['action']}**
        """)
        return
    
    if recommendation["type"] == "general_tips":
        with st.expander(f"💡 {recommendation['title']}", expanded=False):
            for tip in recommendation['tips']:
                st.write(f"• {tip}")
        return
    
    # Improvement recommendation card
    topic = recommendation['topic']
    score = recommendation['current_score']
    urgency = recommendation['urgency']
    motivation = recommendation['motivation']
    
    # Create card with colored border based on urgency
    border_color = "#ff4444" if "High" in urgency else "#ffaa00" if "Medium" in urgency else "#44ff44"
    
    card_html = f"""
    <div style="
        border-left: 5px solid {border_color};
        background-color: #f8f9fa;
        padding: 20px;
        margin: 15px 0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <h3 style="color: #333; margin-top: 0;">📚 {topic}</h3>
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="background: {border_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.8em; margin-right: 15px;">
                {urgency}
            </span>
            <span style="background: #e9ecef; padding: 4px 12px; border-radius: 15px; font-size: 0.8em;">
                Current Score: {score}
            </span>
        </div>
        <p style="color: #666; font-style: italic; margin-bottom: 15px;">{motivation}</p>
        <p style="color: #555; margin-bottom: 15px;">{recommendation['description']}</p>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <a href="{recommendation['quiz_link']}" target="_blank" style="text-decoration: none;">
            <div style="
                background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 10px 15px;
                border-radius: 25px;
                text-align: center;
                margin: 5px;
                transition: transform 0.2s;
                cursor: pointer;
            ">
                🧠 Take Quiz
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{recommendation['video_link']}" target="_blank" style="text-decoration: none;">
            <div style="
                background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 10px 15px;
                border-radius: 25px;
                text-align: center;
                margin: 5px;
                transition: transform 0.2s;
                cursor: pointer;
            ">
                🎥 Watch Tutorial
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{recommendation['study_material']}" target="_blank" style="text-decoration: none;">
            <div style="
                background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 10px 15px;
                border-radius: 25px;
                text-align: center;
                margin: 5px;
                transition: transform 0.2s;
                cursor: pointer;
            ">
                📖 Study Notes
            </div>
        </a>
        """, unsafe_allow_html=True)

def create_performance_visualizations(analysis: Dict[str, Any]) -> None:
    """Create performance visualization charts"""
    
    if not analysis["topic_averages"]:
        st.info("📊 Add some performance data to see visualizations!")
        return
    
    # Topic Performance Bar Chart
    st.subheader("📊 Topic-wise Performance")
    
    topics = list(analysis["topic_averages"].keys())
    scores = list(analysis["topic_averages"].values())
    
    # Color code based on performance
    colors = ['#ff4444' if score < 60 else '#ffaa00' if score < 80 else '#44ff44' for score in scores]
    
    fig = go.Figure(data=[
        go.Bar(
            x=topics,
            y=scores,
            marker_color=colors,
            text=[f'{score:.1f}%' for score in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Performance by Topic",
        xaxis_title="Topics",
        yaxis_title="Average Score (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        showlegend=False
    )
    
    # Add threshold line at 60%
    fig.add_hline(y=60, line_dash="dash", line_color="red", 
                  annotation_text="Weak Threshold (60%)")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Subject Performance if multiple subjects
    if len(analysis["subject_averages"]) > 1:
        st.subheader("📈 Subject-wise Performance")
        
        subjects = list(analysis["subject_averages"].keys())
        subject_scores = list(analysis["subject_averages"].values())
        
        fig_subjects = px.pie(
            values=subject_scores,
            names=subjects,
            title="Performance Distribution by Subject"
        )
        
        st.plotly_chart(fig_subjects, use_container_width=True)

def create_sample_data() -> List[Dict]:
    """Create sample performance data for demonstration"""
    sample_topics = [
        "Sorting Algorithms", "Data Structures", "Machine Learning", 
        "Database Management", "Web Development", "Operating Systems",
        "Computer Networks", "Algorithms", "Python Programming", "Mathematics"
    ]
    
    sample_subjects = ["Computer Science", "Mathematics", "Programming", "Theory"]
    
    sample_data = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(15):  # Generate 15 sample entries
        topic = random.choice(sample_topics)
        subject = random.choice(sample_subjects)
        
        # Simulate some topics being weaker than others
        if topic in ["Sorting Algorithms", "Machine Learning", "Mathematics"]:
            score = random.randint(35, 65)  # Weaker topics
        else:
            score = random.randint(60, 95)  # Stronger topics
            
        total_marks = 100
        entry_date = base_date + timedelta(days=random.randint(0, 90))
        
        sample_data.append({
            "subject": subject,
            "topic": topic,
            "score": score,
            "total_marks": total_marks,
            "created_at": entry_date.isoformat()
        })
    
    return sample_data

def main():
    """Main function to run the Performance Analysis page"""
    
    # Page configuration
    st.set_page_config(
        page_title="EduBot - Performance Analysis",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Performance Analysis & Recommendations</h1>
        <p>Analyze your academic performance and get personalized study recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for data input
    st.sidebar.header("📝 Add Performance Entry")
    
    with st.sidebar.form("performance_form"):
        subject = st.selectbox("Subject", [
            "Computer Science", "Mathematics", "Programming", 
            "Theory", "Physics", "Chemistry", "English"
        ])
        
        topic = st.text_input("Topic", placeholder="e.g., Sorting Algorithms")
        
        col1, col2 = st.columns(2)
        with col1:
            score = st.number_input("Score Obtained", min_value=0, max_value=1000, value=75)
        with col2:
            total_marks = st.number_input("Total Marks", min_value=1, max_value=1000, value=100)
        
        submit_btn = st.form_submit_button("➕ Add Entry", use_container_width=True)
        
        if submit_btn and topic.strip():
            if 'performance_data' not in st.session_state:
                st.session_state.performance_data = []
            
            new_entry = {
                "subject": subject,
                "topic": topic.strip(),
                "score": score,
                "total_marks": total_marks,
                "created_at": datetime.now().isoformat()
            }
            
            st.session_state.performance_data.append(new_entry)
            st.sidebar.success("✅ Entry added successfully!")
            st.rerun()
    
    # Sample data button
    if st.sidebar.button("🎲 Load Sample Data", use_container_width=True):
        st.session_state.performance_data = create_sample_data()
        st.sidebar.success("📊 Sample data loaded!")
        st.rerun()
    
    # Clear data button
    if st.sidebar.button("🗑️ Clear All Data", use_container_width=True):
        st.session_state.performance_data = []
        st.sidebar.success("🧹 Data cleared!")
        st.rerun()
    
    # Initialize performance data
    if 'performance_data' not in st.session_state:
        st.session_state.performance_data = []
    
    performance_data = st.session_state.performance_data
    
    if not performance_data:
        st.info("👈 Add some performance entries using the sidebar, or load sample data to get started!")
        return
    
    # Analyze performance
    analysis = analyze_performance(performance_data)
    
    # Display key metrics
    st.subheader("📈 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Overall Average",
            value=f"{analysis['overall_average']:.1f}%",
            delta=f"{analysis['overall_average'] - 75:.1f}%" if analysis['overall_average'] != 75 else None
        )
    
    with col2:
        st.metric(
            label="📚 Total Entries",
            value=analysis['total_entries']
        )
    
    with col3:
        st.metric(
            label="❌ Weak Topics",
            value=len(analysis['weak_topics']),
            delta=f"-{len(analysis['weak_topics'])}" if analysis['weak_topics'] else "0"
        )
    
    with col4:
        st.metric(
            label="✅ Strong Topics",
            value=len(analysis['strong_topics']),
            delta=f"+{len(analysis['strong_topics'])}" if analysis['strong_topics'] else "0"
        )
    
    # Performance trend
    if analysis['performance_trend'] != "Insufficient data":
        st.info(f"📊 **Performance Trend:** {analysis['performance_trend']}")
    
    # Create visualizations
    create_performance_visualizations(analysis)
    
    # Generate and display recommendations
    st.subheader("🎯 Personalized Recommendations")
    
    if analysis['weak_topics']:
        st.warning(f"📌 Found {len(analysis['weak_topics'])} topics that need improvement (score < 60%)")
    else:
        st.success("🎉 Great job! You're performing well in all topics!")
    
    recommendations = generate_recommendations(analysis['weak_topics'], analysis)
    
    # Display recommendations
    for recommendation in recommendations:
        create_recommendation_card(recommendation)
    
    # Data table
    st.subheader("📋 Performance History")
    
    if st.checkbox("Show detailed data"):
        df = pd.DataFrame(performance_data)
        df['percentage'] = (df['score'] / df['total_marks'] * 100).round(1)
        df['status'] = df['percentage'].apply(lambda x: '✅ Strong' if x >= 60 else '❌ Weak')
        
        # Sort by date (newest first)
        df = df.sort_values('created_at', ascending=False)
        
        st.dataframe(
            df[['created_at', 'subject', 'topic', 'score', 'total_marks', 'percentage', 'status']],
            use_container_width=True
        )
        
        # Export functionality
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Performance Data (CSV)",
            data=csv,
            file_name=f"performance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
