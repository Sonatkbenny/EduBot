import pandas as pd
import numpy as np
from typing import Dict, List, Any
import streamlit as st

# Sample resource mapping for topics (expandable)
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
    },
    "Object-Oriented Programming": {
        "quiz_link": "https://www.sanfoundry.com/object-oriented-programming-questions-answers/",
        "video_link": "https://www.youtube.com/watch?v=pTB0EiLXUC8",
        "study_material": "https://www.tutorialspoint.com/object_oriented_analysis_design/",
        "description": "Master OOP concepts like inheritance, polymorphism, and encapsulation"
    }
}

def analyze_student_performance(performance_data: List[Dict]) -> Dict[str, Any]:
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
            "weak_topics": {},
            "strong_topics": {},
            "topic_averages": {},
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
        "needs_improvement": len(weak_topics) > 0 or overall_average < 70
    }

def generate_personalized_recommendations(weak_topics: Dict[str, float], overall_average: float) -> List[Dict[str, Any]]:
    """
    Generate personalized recommendations for weak topics
    
    Args:
        weak_topics: Dictionary of weak topics with their average scores
        overall_average: Overall performance average
        
    Returns:
        List of recommendation objects with resources and motivational messages
    """
    recommendations = []
    
    if not weak_topics:
        # If no weak topics, provide motivational message
        return [{
            "type": "success",
            "title": "🎉 Excellent Performance!",
            "message": "You're performing well across all topics! Keep up the great work and consider exploring advanced topics.",
            "action": "Continue practicing to maintain your strong performance!"
        }]
    
    # Sort weak topics by score (lowest first)
    sorted_weak = sorted(weak_topics.items(), key=lambda x: x[1])
    
    for topic, score in sorted_weak[:5]:  # Top 5 weakest topics
        # Get resources for this topic
        resources = TOPIC_RESOURCES.get(topic, {
            "quiz_link": "https://www.khanacademy.org/",
            "video_link": "https://www.youtube.com/",
            "study_material": f"https://www.google.com/search?q={topic.replace(' ', '+')}",
            "description": f"Practice and improve your understanding of {topic}"
        })
        
        # Create motivational message based on score
        if score < 30:
            motivation = f"Don't worry about {topic}! Everyone starts somewhere. These resources will help you build a strong foundation."
            urgency = "🔴 High Priority"
            color = "#ff4444"
        elif score < 45:
            motivation = f"You're making progress in {topic}! With focused practice, you'll see significant improvement."
            urgency = "🟡 Medium Priority"
            color = "#ffaa00"
        else:
            motivation = f"You're close to mastering {topic}! Just a little more practice will get you there."
            urgency = "🟢 Low Priority"
            color = "#44ff44"
        
        recommendation = {
            "type": "improvement",
            "topic": topic,
            "current_score": f"{score:.1f}%",
            "urgency": urgency,
            "color": color,
            "motivation": motivation,
            "quiz_link": resources["quiz_link"],
            "video_link": resources["video_link"],
            "study_material": resources["study_material"],
            "description": resources["description"]
        }
        
        recommendations.append(recommendation)
    
    # Add general study tips if overall performance needs improvement
    if overall_average < 70:
        general_tips = {
            "type": "tips",
            "title": "💡 General Study Tips",
            "tips": [
                "Create a structured study schedule and stick to it",
                "Practice active recall techniques instead of passive reading", 
                "Form study groups with classmates for peer learning",
                "Take regular breaks using the Pomodoro technique (25min study, 5min break)",
                "Seek help from instructors when you're stuck on concepts",
                "Use multiple learning resources (videos, books, practice problems)"
            ]
        }
        recommendations.append(general_tips)
    
    return recommendations

def display_recommendation_card(recommendation: Dict[str, Any]) -> None:
    """
    Display a styled recommendation card in Streamlit
    
    Args:
        recommendation: Recommendation object containing all card information
    """
    if recommendation["type"] == "success":
        st.success(f"""
        ### {recommendation['title']}
        {recommendation['message']}
        
        **{recommendation['action']}**
        """)
        return
    
    if recommendation["type"] == "tips":
        with st.expander(f"💡 {recommendation['title']}", expanded=False):
            for tip in recommendation['tips']:
                st.write(f"• {tip}")
        return
    
    # Improvement recommendation card
    topic = recommendation['topic']
    score = recommendation['current_score']
    urgency = recommendation['urgency']
    motivation = recommendation['motivation']
    color = recommendation['color']
    
    # Create attractive card with colored border
    card_html = f"""
    <div style="
        border-left: 5px solid {color};
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        margin: 15px 0;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h3 style="color: #333; margin-top: 0; font-weight: 600;">📚 {topic}</h3>
        <div style="display: flex; align-items: center; margin-bottom: 15px; flex-wrap: wrap;">
            <span style="background: {color}; color: white; padding: 6px 15px; border-radius: 20px; font-size: 0.85em; margin-right: 15px; font-weight: 500;">
                {urgency}
            </span>
            <span style="background: #6c757d; color: white; padding: 6px 15px; border-radius: 20px; font-size: 0.85em; font-weight: 500;">
                Current Score: {score}
            </span>
        </div>
        <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            <p style="color: #495057; font-style: italic; margin: 0; font-size: 1.05em;">{motivation}</p>
        </div>
        <p style="color: #666; margin-bottom: 20px; font-size: 0.95em;">{recommendation['description']}</p>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Create action buttons in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <a href="{recommendation['quiz_link']}" target="_blank" style="text-decoration: none;">
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 25px;
                text-align: center;
                margin: 5px;
                transition: transform 0.3s ease;
                cursor: pointer;
                font-weight: 500;
                box-shadow: 0 3px 6px rgba(102, 126, 234, 0.3);
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                🧠 Take Quiz
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{recommendation['video_link']}" target="_blank" style="text-decoration: none;">
            <div style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 25px;
                text-align: center;
                margin: 5px;
                transition: transform 0.3s ease;
                cursor: pointer;
                font-weight: 500;
                box-shadow: 0 3px 6px rgba(240, 147, 251, 0.3);
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                🎥 Watch Tutorial
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{recommendation['study_material']}" target="_blank" style="text-decoration: none;">
            <div style="
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 25px;
                text-align: center;
                margin: 5px;
                transition: transform 0.3s ease;
                cursor: pointer;
                font-weight: 500;
                box-shadow: 0 3px 6px rgba(79, 172, 254, 0.3);
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                📖 Study Notes
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    # Add separator
    st.markdown("<hr style='margin: 30px 0; border: none; height: 1px; background: #e9ecef;'>", unsafe_allow_html=True)

def display_performance_recommendations(performance_data: List[Dict]) -> None:
    """
    Main function to analyze performance and display recommendations
    
    Args:
        performance_data: List of performance entries
    """
    if not performance_data:
        st.info("📊 Add some performance data to see personalized recommendations!")
        return
    
    # Analyze performance
    analysis = analyze_student_performance(performance_data)
    
    # Display key metrics first
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
    
    # Display recommendations
    st.subheader("🎯 Personalized Learning Recommendations")
    
    if analysis['weak_topics']:
        st.warning(f"📌 Found {len(analysis['weak_topics'])} topics that need improvement (score < 60%)")
    else:
        st.success("🎉 Great job! You're performing well in all topics!")
    
    recommendations = generate_personalized_recommendations(
        analysis['weak_topics'], 
        analysis['overall_average']
    )
    
    # Display each recommendation
    for recommendation in recommendations:
        display_recommendation_card(recommendation)

# Cache the module for performance
@st.cache_resource
def get_enhanced_performance_analyzer():
    """Get cached enhanced performance analyzer"""
    return {
        'analyze': analyze_student_performance,
        'recommend': generate_personalized_recommendations,
        'display_card': display_recommendation_card,
        'display_all': display_performance_recommendations
    }
