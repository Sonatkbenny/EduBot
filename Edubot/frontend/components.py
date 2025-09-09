import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from datetime import datetime
import io
import base64

def create_header(title: str, subtitle: str = ""):
    """Create a styled header"""
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #1f77b4; font-size: 2.5rem; margin-bottom: 10px;">{title}</h1>
        {f'<p style="color: #666; font-size: 1.2rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_info_card(title: str, value: str, icon: str = "📊"):
    """Create an info card component"""
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 2rem; margin-right: 15px;">{icon}</span>
            <div>
                <h3 style="margin: 0; color: #1f77b4;">{title}</h3>
                <p style="margin: 5px 0 0 0; font-size: 1.1rem; font-weight: bold;">{value}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_row(metrics: List[Dict[str, str]]):
    """Create a row of metric cards"""
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            create_info_card(metric['title'], metric['value'], metric.get('icon', '📊'))

def create_progress_bar(label: str, value: float, max_value: float = 100):
    """Create a styled progress bar"""
    percentage = (value / max_value) * 100
    color = "green" if percentage >= 70 else "orange" if percentage >= 50 else "red"
    
    st.markdown(f"""
    <div style="margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>{label}</span>
            <span>{value:.1f}/{max_value:.1f} ({percentage:.1f}%)</span>
        </div>
        <div style="background-color: #e0e0e0; border-radius: 10px; height: 20px;">
            <div style="background-color: {color}; width: {percentage}%; height: 100%; border-radius: 10px; transition: width 0.3s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_interactive_quiz_question(question: Dict[str, Any], question_number: int, quiz_key: str = ""):
    """Create an interactive quiz question with radio buttons"""
    
    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 15px 0;">
        <h3 style="color: #1f77b4; margin-bottom: 15px;">Question {question_number}</h3>
        <p style="font-size: 1.1rem; margin-bottom: 20px;">{question.get('question', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if question.get('question_type') == 'multiple_choice':
        options = question.get('options', {})
        
        if not options:
            st.error("❌ No options found for this multiple choice question!")
            return None
            
        option_labels = [f"{option}) {text}" for option, text in options.items()]
        
        # Use radio buttons for selection
        selected_option = st.radio(
            "Choose your answer:",
            options=list(options.keys()),
            format_func=lambda x: f"{x}) {options[x]}",
            key=f"quiz_{quiz_key}_radio_{question_number}",
            index=None
        )
        
        # Store the answer in session state
        if selected_option:
            st.session_state[f"quiz_{quiz_key}_answer_{question_number}"] = selected_option
            st.success(f"✅ Selected: {selected_option}")
        
        return selected_option
    
    elif question.get('question_type') == 'short_answer':
        # For short answer questions, show expected answer and key points
        if st.button(f"Show Expected Answer for Question {question_number}", key=f"show_short_answer_{question_number}"):
            expected_answer = question.get('expected_answer', '')
            key_points = question.get('key_points', '')
            
            st.markdown(f"""
            <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 5px; padding: 15px; margin: 10px 0;">
                <h4 style="color: #2e7d32; margin-bottom: 10px;">Expected Answer:</h4>
                <p style="margin-bottom: 15px;">{expected_answer}</p>
                <h4 style="color: #2e7d32; margin-bottom: 10px;">Key Points:</h4>
                <p style="margin: 0;">{key_points}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return None

def create_quiz_submission_section(questions: List[Dict[str, Any]], quiz_key: str = ""):
    """Create quiz submission section with scoring"""
    st.markdown("---")
    st.markdown("### 📝 Quiz Submission")
    
    # Check if all questions are answered
    answered_questions = 0
    total_questions = len(questions)
    
    for question in questions:
        question_num = question.get('question_number', 0)
        if f"quiz_{quiz_key}_answer_{question_num}" in st.session_state:
            answered_questions += 1
    
    # Show progress
    progress = answered_questions / total_questions if total_questions > 0 else 0
    st.progress(progress)
    st.info(f"Answered: {answered_questions}/{total_questions} questions")
    
    # Submit button
    if st.button("Submit Quiz", key=f"submit_quiz_{quiz_key}", disabled=answered_questions < total_questions):
        if answered_questions < total_questions:
            st.warning("Please answer all questions before submitting.")
        else:
            # Collect all answers
            user_answers = {}
            for question in questions:
                question_num = question.get('question_number', 0)
                answer = st.session_state.get(f"quiz_{quiz_key}_answer_{question_num}", "")
                user_answers[question_num] = answer
            
            # Score the quiz
            from models.quiz_generator import get_quiz_generator
            quiz_gen = get_quiz_generator()
            # Get topic from session state if available
            topic = st.session_state.get(f"quiz_{quiz_key}_topic", None)
            score_result = quiz_gen.score_quiz(questions, user_answers, topic)
            
            # Store results in session state
            st.session_state[f"quiz_{quiz_key}_results"] = score_result
            st.session_state[f"quiz_{quiz_key}_submitted"] = True
            
            st.success("Quiz submitted successfully!")
            st.rerun()

def create_quiz_results_display(score_result: Dict[str, Any], quiz_key: str = ""):
    """Display quiz results with detailed feedback"""
    st.markdown("---")
    st.markdown("### 📊 Quiz Results")
    
    # Overall score
    percentage = score_result.get('percentage', 0)
    correct = score_result.get('correct_answers', 0)
    total = score_result.get('total_questions', 0)
    
    # Color coding for score
    if percentage >= 80:
        color = "#4caf50"  # Green
        emoji = "🎉"
    elif percentage >= 60:
        color = "#ff9800"  # Orange
        emoji = "👍"
    else:
        color = "#f44336"  # Red
        emoji = "📚"
    
    st.markdown(f"""
    <div style="background-color: {color}20; border: 2px solid {color}; border-radius: 10px; padding: 20px; margin: 15px 0; text-align: center;">
        <h2 style="color: {color}; margin: 0;">{emoji} {percentage}%</h2>
        <p style="margin: 5px 0; font-size: 1.1rem;">{correct} out of {total} questions correct</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed results
    st.markdown("#### 📋 Question-by-Question Results")
    results = score_result.get('results', [])
    
    for result in results:
        question_num = result.get('question_number', 0)
        is_correct = result.get('is_correct', False)
        user_answer = result.get('user_answer', '')
        correct_answer = result.get('correct_answer', '')
        explanation = result.get('explanation', '')
        question_text = result.get('question', '')
        
        # Color coding for each question
        border_color = "#4caf50" if is_correct else "#f44336"
        bg_color = "#e8f5e8" if is_correct else "#ffebee"
        icon = "✅" if is_correct else "❌"
        
        st.markdown(f"""
        <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 5px; padding: 15px; margin: 10px 0;">
            <h4 style="margin: 0 0 10px 0; color: {border_color};">{icon} Question {question_num}</h4>
            <p style="margin: 0 0 10px 0; font-weight: bold;">{question_text}</p>
            <p style="margin: 0 0 5px 0;"><strong>Your Answer:</strong> {user_answer}</p>
            <p style="margin: 0 0 5px 0;"><strong>Correct Answer:</strong> {correct_answer}</p>
            <p style="margin: 0;"><strong>Explanation:</strong> {explanation}</p>
        </div>
        """, unsafe_allow_html=True)

def create_quiz_question_card(question: Dict[str, Any], question_number: int):
    """Create a quiz question card (legacy function for backward compatibility)"""
    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 15px 0;">
        <h3 style="color: #1f77b4; margin-bottom: 15px;">Question {question_number}</h3>
        <p style="font-size: 1.1rem; margin-bottom: 20px;">{question.get('question', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if question.get('question_type') == 'multiple_choice':
        options = question.get('options', {})
        for option, text in options.items():
            if st.button(f"{option}) {text}", key=f"q{question_number}_{option}"):
                st.session_state[f"answer_{question_number}"] = option
                st.success(f"Selected: {option}")
    
    # Show correct answer and explanation
    if st.button(f"Show Answer for Question {question_number}", key=f"show_answer_{question_number}"):
        correct_answer = question.get('correct_answer', '')
        explanation = question.get('explanation', '')
        
        st.markdown(f"""
        <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 5px; padding: 15px; margin: 10px 0;">
            <h4 style="color: #2e7d32; margin-bottom: 10px;">Correct Answer: {correct_answer}</h4>
            <p style="margin: 0;">{explanation}</p>
        </div>
        """, unsafe_allow_html=True)

def create_performance_chart(data: List[Dict[str, Any]], chart_type: str = "bar"):
    """Create performance visualization charts"""
    if not data:
        st.warning("No data available for visualization")
        return
    
    df = pd.DataFrame(data)
    df['percentage'] = (df['score'] / df['total_marks']) * 100
    
    if chart_type == "bar":
        fig = px.bar(
            df, 
            x='subject', 
            y='percentage',
            title='Performance by Subject',
            labels={'percentage': 'Score (%)', 'subject': 'Subject'},
            color='percentage',
            color_continuous_scale='RdYlGn'
        )
    elif chart_type == "line":
        df['date'] = pd.to_datetime(df.get('created_at', pd.Timestamp.now()))
        fig = px.line(
            df.sort_values('date'), 
            x='date', 
            y='percentage',
            title='Performance Trend Over Time',
            labels={'percentage': 'Score (%)', 'date': 'Date'}
        )
    elif chart_type == "pie":
        subject_avg = df.groupby('subject')['percentage'].mean().reset_index()
        fig = px.pie(
            subject_avg,
            values='percentage',
            names='subject',
            title='Performance Distribution by Subject'
        )
    
    st.plotly_chart(fig, use_container_width=True)

def create_recommendation_card(recommendation: Dict[str, Any]):
    """Create a recommendation card"""
    resource_type = recommendation.get('type', 'unknown')
    icon_map = {
        'video': '🎥',
        'article': '📄',
        'course': '📚',
        'youtube_video': '📺'
    }
    icon = icon_map.get(resource_type, '📖')
    
    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 15px 0;">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <span style="font-size: 2rem; margin-right: 15px;">{icon}</span>
            <div style="flex-grow: 1;">
                <h3 style="margin: 0; color: #1f77b4;">{recommendation.get('title', 'Untitled')}</h3>
                <p style="margin: 5px 0; color: #666; font-size: 0.9rem;">{resource_type.title()}</p>
            </div>
        </div>
        <p style="margin: 10px 0; line-height: 1.5;">{recommendation.get('description', 'No description available')}</p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #666; font-size: 0.9rem;">Similarity: {recommendation.get('similarity_score', 0):.2f}</span>
            <a href="{recommendation.get('url', '#')}" target="_blank" style="text-decoration: none;">
                <button style="background-color: #1f77b4; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                    View Resource
                </button>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_summary_card(original_text: str, summary: str, filename: str = ""):
    """Create a summary display card"""
    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 15px 0;">
        <h3 style="color: #1f77b4; margin-bottom: 15px;">📝 Summary{f' - {filename}' if filename else ''}</h3>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            <p style="margin: 0; line-height: 1.6;">{summary}</p>
        </div>
        <div style="display: flex; justify-content: space-between; color: #666; font-size: 0.9rem;">
            <span>Original: {len(original_text.split())} words</span>
            <span>Summary: {len(summary.split())} words</span>
            <span>Compression: {((len(original_text.split()) - len(summary.split())) / len(original_text.split()) * 100):.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_file_upload_section():
    """Create file upload section"""
    st.markdown("### 📁 Upload Your Notes")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=['pdf', 'txt'],
        help="Upload your study notes, lecture materials, or any educational content"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show file info
        file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
        st.info(f"📊 File size: {file_size:.2f} MB")
    
    return uploaded_file

def create_performance_input_form():
    """Create performance data input form with predict performance button"""
    st.markdown("### 📊 Enter Performance Data")
    
    # Use regular inputs
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input(
            "Subject", 
            placeholder="e.g., Mathematics",
            key="perf_subject"
        )
        topic = st.text_input(
            "Topic", 
            placeholder="e.g., Algebra",
            key="perf_topic"
        )
    
    with col2:
        # Total marks input
        total_marks = st.number_input(
            "Total Marks", 
            min_value=0.1, 
            step=0.1, 
            key="perf_total_marks",
            help="Enter the total marks/points for this assessment"
        )
        
        # Score obtained input with dynamic max value
        score = st.number_input(
            "Score Obtained",
            min_value=0.0,
            max_value=max(total_marks, 0.1) if total_marks > 0 else 0.1,
            step=0.1,
            key="perf_score",
            help="Enter the score you obtained (cannot exceed total marks)"
        )
    
    # Only show score validation error (keep this critical validation)
    if score > total_marks and total_marks > 0:
        st.error(
            "Score obtained cannot exceed Total Marks. Please enter a value less or equal to Total Marks.",
            icon="❌"
        )
    
    # Add Predict Performance button
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔮 Predict Performance", use_container_width=True, key="predict_perf_btn"):
            # Basic validation for prediction (allow partial data)
            can_predict = subject and subject.strip() and topic and topic.strip()
            
            if not can_predict:
                st.warning("Please enter Subject and Topic for prediction")
                return None
            
            if score > total_marks and total_marks > 0:
                st.error("Cannot predict with invalid score data")
                return None
            
            # Calculate prediction based on available data
            if total_marks > 0 and score >= 0:
                percentage = (score / total_marks) * 100
                prediction = "Weak" if percentage < 40 else "Strong"
            else:
                # Default prediction when no score data
                prediction = "Unknown - Need score data for accurate prediction"
            
            # Initialize prediction history if it doesn't exist
            if 'prediction_history' not in st.session_state:
                st.session_state.prediction_history = []
            
            # Add prediction to history with timestamp
            import datetime
            prediction_record = {
                'timestamp': datetime.datetime.now(),
                'subject': subject.strip(),
                'topic': topic.strip(),
                'prediction': prediction,
                'score': score if score >= 0 else None,
                'total_marks': total_marks if total_marks > 0 else None,
                'percentage': round((score / total_marks) * 100, 1) if total_marks > 0 and score >= 0 else None
            }
            st.session_state.prediction_history.append(prediction_record)
            
            # Return prediction data
            return {
                'subject': subject.strip(),
                'topic': topic.strip(),
                'score': score if score >= 0 else 0,
                'total_marks': total_marks if total_marks > 0 else 1,
                'percentage': round((score / total_marks) * 100, 1) if total_marks > 0 and score >= 0 else 0,
                'prediction_only': True,
                'prediction': prediction
            }
    
    # Auto-save functionality when all validations pass (separate from prediction)
    all_valid = (
        subject and subject.strip() and
        topic and topic.strip() and
        total_marks > 0 and
        score >= 0 and
        score <= total_marks
    )
    
    # Auto-return valid data for immediate processing (only if all valid)
    if all_valid:
        st.success("✅ **Valid Entry** - Data ready for analysis")
        
        return {
            'subject': subject.strip(),
            'topic': topic.strip(),
            'score': score,
            'total_marks': total_marks,
            'percentage': round((score / total_marks) * 100, 1) if total_marks > 0 else 0
        }
    
    return None

def create_quiz_generation_form():
    """Create quiz generation form with validation"""
    st.markdown("### ❓ Generate Quiz Questions")
    
    with st.form("quiz_form"):
        topic = st.text_input("Topic for Quiz", placeholder="e.g., Machine Learning, IoT, Operating Systems")
        
        # Enforce maximum of 10 questions
        num_questions = st.slider("Number of Questions", 1, 10, 5, help="Maximum 10 questions per quiz")
        
        question_type = "multiple_choice"  # Only multiple choice questions supported
        
        # Optional content input
        content = st.text_area("Additional Content (Optional)", 
                              placeholder="Paste any relevant content to help generate better questions...",
                              height=100,
                              help="Provide additional context to generate more relevant questions")
        
        submitted = st.form_submit_button("Generate Quiz")
        
        if submitted:
            if not topic or not topic.strip():
                st.error("Please enter a topic for the quiz")
                return None
            
            if num_questions > 10:
                st.error("Maximum 10 questions allowed per quiz")
                return None
            
            if num_questions < 1:
                st.error("At least 1 question is required")
                return None
            
            return {
                'topic': topic.strip(),
                'num_questions': num_questions,
                'question_type': question_type,
                'content': content.strip() if content else None
            }
    
    return None

def create_user_profile_form():
    """Create user profile input form"""
    st.markdown("### 👤 User Profile")
    
    with st.form("profile_form"):
        interests = st.text_area("Your Interests", 
                               placeholder="Enter your academic interests (comma-separated)",
                               help="e.g., machine learning, mathematics, physics")
        
        weak_topics = st.text_area("Weak Topics", 
                                  placeholder="Enter topics you want to improve (comma-separated)",
                                  help="e.g., calculus, organic chemistry")
        
        learning_style = st.selectbox("Learning Style", 
                                    ["visual", "reading", "auditory", "kinesthetic"])
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            return {
                'interests': [interest.strip() for interest in interests.split(',') if interest.strip()],
                'weak_topics': [topic.strip() for topic in weak_topics.split(',') if topic.strip()],
                'learning_style': learning_style
            }
    
    return None

def create_prediction_history_display():
    """Display prediction history for current session"""
    if 'prediction_history' in st.session_state and st.session_state.prediction_history:
        st.markdown("### 📅 Session Prediction History")
        st.markdown(
            "<div style='background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 10px; margin: 10px 0; border-radius: 5px;'>"
            "<small style='color: #6c757d;'>Track of all predictions made during this session</small></div>", 
            unsafe_allow_html=True
        )
        
        # Display each prediction record
        for i, record in enumerate(reversed(st.session_state.prediction_history)):
            # Format timestamp
            timestamp_str = record['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            
            # Prediction badge styling
            prediction = record['prediction']
            if prediction == "Weak":
                badge_color = "#d9534f"
                badge_icon = "🔴"
            elif prediction == "Strong":
                badge_color = "#5cb85c"
                badge_icon = "🟢"
            else:
                badge_color = "#6c757d"
                badge_icon = "🟡"
            
            # Additional score info if available
            score_info = ""
            if record.get('percentage') is not None:
                score_info = f" ({record['percentage']}%)"
            
            # Create styled prediction record
            st.markdown(f"""
            <div style="
                background-color: white; 
                border: 1px solid #e9ecef; 
                border-radius: 8px; 
                padding: 12px 15px; 
                margin: 8px 0; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="color: #495057;">{timestamp_str}</strong><br>
                        <span style="color: #6c757d; font-size: 0.95em;">
                            Subject: <strong>{record['subject']}</strong>, Topic: <strong>{record['topic']}</strong>
                        </span>
                    </div>
                    <div style="text-align: right;">
                        <span style="
                            background-color: {badge_color}; 
                            color: white; 
                            padding: 4px 10px; 
                            border-radius: 15px; 
                            font-size: 0.9em;
                            font-weight: 500;
                        ">
                            {badge_icon} {prediction}{score_info}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Show total count
        total_predictions = len(st.session_state.prediction_history)
        st.markdown(
            f"<p style='text-align: center; color: #6c757d; font-size: 0.9em; margin-top: 15px;'>"
            f"📋 Total predictions this session: <strong>{total_predictions}</strong></p>", 
            unsafe_allow_html=True
        )
    else:
        # Show placeholder when no predictions yet
        st.markdown(
            "<div style='background-color: #f8f9fa; border: 1px dashed #dee2e6; border-radius: 8px; padding: 20px; text-align: center; margin: 15px 0; color: #6c757d;'>"
            "🔮 Make your first prediction to see history here"
            "</div>", 
            unsafe_allow_html=True
        )

def create_loading_spinner(message: str = "Processing..."):
    """Create a loading spinner with custom message"""
    return st.spinner(message)

def create_success_message(message: str):
    """Create a styled success message"""
    st.markdown(f"""
    <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 10px 0;">
        <p style="margin: 0; color: #155724;">✅ {message}</p>
    </div>
    """, unsafe_allow_html=True)

def create_error_message(message: str):
    """Create a styled error message"""
    st.markdown(f"""
    <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 10px 0;">
        <p style="margin: 0; color: #721c24;">❌ {message}</p>
    </div>
    """, unsafe_allow_html=True)

def create_warning_message(message: str):
    """Create a styled warning message"""
    st.markdown(f"""
    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 10px 0;">
        <p style="margin: 0; color: #856404;">⚠️ {message}</p>
    </div>
    """, unsafe_allow_html=True)

def generate_txt_file(summary_text: str, filename: str = "", original_filename: str = "") -> str:
    """Generate TXT file content for download"""
    # Create header
    header = f"EduBot - Summary Report\n"
    header += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    if original_filename:
        header += f"Original File: {original_filename}\n"
    if filename:
        header += f"Summary Title: {filename}\n"
    header += "=" * 50 + "\n\n"
    
    # Combine header and summary
    content = header + "SUMMARY:\n\n" + summary_text
    
    return content

def generate_pdf_file(summary_text: str, filename: str = "", original_filename: str = "") -> bytes:
    """Generate PDF file content for download"""
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=20,
        textColor=HexColor('#1f77b4'),
        alignment=1  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=HexColor('#666666')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        leading=18,
        textColor=HexColor('#333333')
    )
    
    # Build the content
    story = []
    
    # Title
    title = "EduBot - Summary Report"
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # Metadata
    metadata = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    if original_filename:
        metadata += f"<br/>Original File: {original_filename}"
    if filename:
        metadata += f"<br/>Summary Title: {filename}"
    
    story.append(Paragraph(metadata, subtitle_style))
    story.append(Spacer(1, 20))
    
    # Summary section header
    story.append(Paragraph("Summary", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    # Summary content
    # Split summary into paragraphs for better formatting
    paragraphs = summary_text.split('\n\n')
    for paragraph in paragraphs:
        if paragraph.strip():
            # Clean up the text for PDF
            clean_text = paragraph.strip().replace('\n', ' ')
            story.append(Paragraph(clean_text, body_style))
            story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)
    
    # Get the PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def create_summary_download_section(summary_data: Dict[str, Any]):
    """Create download section for summaries with PDF and TXT options"""
    st.markdown("### 💾 Download Summary")
    
    # Extract data
    summary_text = summary_data.get('summary', '')
    original_filename = summary_data.get('filename', '')
    
    # Create a clean filename for downloads
    base_filename = "summary_notes"
    if original_filename:
        # Remove extension and use as base name
        base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
        # Clean filename for use
        base_filename = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        base_filename = base_filename.replace(' ', '_') or "summary_notes"
    
    # Create download buttons side by side
    col1, col2 = st.columns(2)
    
    with col1:
        # TXT Download - Direct download button
        try:
            txt_content = generate_txt_file(
                summary_text,
                filename=f"{base_filename}_summary",
                original_filename=original_filename
            )
            
            st.download_button(
                label="📝 Download as TXT",
                data=txt_content,
                file_name=f"{base_filename}_summary.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary"
            )
            
        except Exception as e:
            st.error(f"Error generating TXT file: {str(e)}")
    
    with col2:
        # PDF Download - Direct download button
        try:
            pdf_data = generate_pdf_file(
                summary_text, 
                filename=f"{base_filename}_summary",
                original_filename=original_filename
            )
            
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_data,
                file_name=f"{base_filename}_summary.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="secondary"
            )
            
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
    
    # Show file info
    st.info(f"📊 **Summary Statistics:**\n\n" + 
           f"• **Words:** {len(summary_text.split())}\n\n" +
           f"• **Characters:** {len(summary_text)}\n\n" +
           f"• **Original File:** {original_filename if original_filename else 'N/A'}")
    
    # Show file preview
    with st.expander("📋 Preview Summary Content", expanded=False):
        st.text_area(
            "Summary Preview:",
            value=summary_text,
            height=200,
            disabled=True,
            key="summary_preview"
        )
