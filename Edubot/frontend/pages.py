import streamlit as st
from frontend.components import (
    create_header, create_info_card, create_metric_row, create_progress_bar,
    create_quiz_question_card, create_interactive_quiz_question, create_quiz_submission_section,
    create_quiz_results_display, create_performance_chart, create_recommendation_card,
    create_summary_card, create_file_upload_section, create_performance_input_form,
    create_quiz_generation_form, create_user_profile_form, create_loading_spinner,
    create_success_message, create_error_message, create_warning_message, create_summary_download_section,
    create_prediction_history_display
)
from models.summarizer import get_summarizer
from models.quiz_generator import get_quiz_generator
from models.recommender import get_recommender
from models.performance import get_performance_analyzer
from utils.file_processor import get_file_processor
from utils.data_processor import get_data_processor

def home_page():
    """Home page with overview and quick actions"""
    create_header("Welcome to EduBot", "Your AI-Powered Learning Assistant")
    
    # Overview section
    st.markdown("### 🎯 What EduBot Can Do")
    
    features = [
        {"icon": "📝", "title": "Text Summarization", "desc": "Generate concise summaries from your study materials"},
        {"icon": "❓", "title": "Quiz Generation", "desc": "Create personalized quizzes based on your weak topics"},
        {"icon": "📊", "title": "Performance Analysis", "desc": "Analyze your academic performance with ML models"},
        {"icon": "📚", "title": "Smart Recommendations", "desc": "Get personalized learning resources and videos"}
    ]
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background-color: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 10px 0;">
                <div style="text-align: center;">
                    <span style="font-size: 3rem;">{feature['icon']}</span>
                    <h3 style="color: #1f77b4; margin: 10px 0;">{feature['title']}</h3>
                    <p style="color: #666; margin: 0;">{feature['desc']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick actions - functional navigation buttons
    st.markdown("### ⚡ Quick Actions")
    st.markdown("*Click any button below to quickly access features:*")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📝 Summarize Notes", use_container_width=True, key="home_summarize_btn"):
            # Store page selection and trigger rerun
            st.session_state["quick_action_page"] = "📝 Text Summarization"
            st.rerun()
    with col2:
        if st.button("❓ Generate Quiz", use_container_width=True, key="home_quiz_btn"):
            st.session_state["quick_action_page"] = "❓ Quiz Generation"
            st.rerun()
    with col3:
        if st.button("📊 Analyze Performance", use_container_width=True, key="home_performance_btn"):
            st.session_state["quick_action_page"] = "📊 Performance Analysis"
            st.rerun()
    with col4:
        if st.button("📚 Get Recommendations", use_container_width=True, key="home_recommendations_btn"):
            st.session_state["quick_action_page"] = "📚 Recommendations"
            st.rerun()
    
    # Recent activity (if any)
    if st.session_state.get('summaries') or st.session_state.get('quizzes') or st.session_state.get('performance_data'):
        st.markdown("### 📈 Recent Activity")
        
        if st.session_state.get('summaries'):
            st.info(f"📝 {len(st.session_state['summaries'])} summaries generated")
        
        if st.session_state.get('quizzes'):
            st.info(f"❓ {len(st.session_state['quizzes'])} quizzes created")
        
        if st.session_state.get('performance_data'):
            st.info(f"📊 {len(st.session_state['performance_data'])} performance entries")

def summarization_page():
    """Text summarization page"""
    create_header("Text Summarization", "Transform your notes into concise summaries")
    
    # File upload section
    uploaded_file = create_file_upload_section()
    
    if uploaded_file is not None:
        file_processor = get_file_processor()
        processed_file = file_processor.process_uploaded_file(uploaded_file)
        
        if processed_file.get("success"):
            # Show file statistics
            stats = file_processor.get_file_statistics(processed_file)
            
            st.markdown("### 📊 File Statistics")
            metrics = [
                {"title": "Word Count", "value": str(stats['word_count']), "icon": "📝"},
                {"title": "Pages", "value": str(stats['total_pages']), "icon": "📄"},
                {"title": "Keywords", "value": ", ".join(stats['keywords'][:3]), "icon": "🔑"}
            ]
            create_metric_row(metrics)
            
            # Summarization options
            st.markdown("### ⚙️ Summarization Options")
            
            col1, col2 = st.columns(2)
            with col1:
                max_length = st.slider("Maximum Summary Length", 50, 500, 150)
            with col2:
                min_length = st.slider("Minimum Summary Length", 20, 200, 50)
            
            if st.button("🚀 Generate Summary", type="primary"):
                with create_loading_spinner("Generating summary..."):
                    summarizer = get_summarizer()
                    summary = summarizer.summarize(
                        processed_file['cleaned_text'],
                        max_length=max_length,
                        min_length=min_length
                    )
                    
                    if summary and not summary.startswith("Error"):
                        # Store in session state
                        if 'summaries' not in st.session_state:
                            st.session_state.summaries = []
                        
                        summary_data = {
                            'original_text': processed_file['cleaned_text'],
                            'summary': summary,
                            'filename': processed_file['filename'],
                            'stats': summarizer.get_summary_stats(processed_file['cleaned_text'], summary)
                        }
                        st.session_state.summaries.append(summary_data)
                        
                        # Display summary
                        create_summary_card(
                            processed_file['cleaned_text'],
                            summary,
                            processed_file['filename']
                        )
                        
                        # Add download section
                        create_summary_download_section(summary_data)
                        
                        create_success_message("Summary generated successfully!")
                    else:
                        create_error_message(f"Error generating summary: {summary}")
        else:
            create_error_message(processed_file.get("error", "Unknown error"))

def quiz_page():
    """Interactive quiz generation and taking page"""
    create_header("Quiz Generation", "Create and take personalized quizzes for better learning")
    
    # Question History Management Section
    st.markdown("### 📊 Question History Management")
    
    if st.button("📈 View History Stats", use_container_width=True, key="view_history_stats"):
        st.session_state["show_history_stats"] = True
    
    # Show history stats
    if st.session_state.get("show_history_stats"):
        st.markdown("#### 📈 Question History Statistics")
        quiz_generator = get_quiz_generator()
        stats = quiz_generator.get_question_history_stats()
        
        if stats["total_topics"] > 0:
            st.info(f"**Total Topics:** {stats['total_topics']} | **Total Questions Served:** {stats['total_questions_served']}")
            
            for topic in stats["topics"]:
                topic_stats = quiz_generator.get_question_history_stats(topic)
                
                # Create columns for better layout
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Questions Served", topic_stats['total_questions_served'])
                
                with col2:
                    st.metric("Quizzes Taken", topic_stats['total_quizzes_taken'])
                
                with col3:
                    st.metric("Average Score", f"{topic_stats['average_score']}%")
                
                with col4:
                    st.metric("Best Score", f"{topic_stats['best_score']}%")
                
                # Show recent quiz results if available
                if topic_stats['quiz_results']:
                    st.markdown(f"**Recent Quiz Results for {topic}:**")
                    
                    # Show last 5 quiz results
                    recent_results = topic_stats['quiz_results'][-5:]
                    for i, result in enumerate(reversed(recent_results)):
                        timestamp = result.get('timestamp', '')
                        if timestamp:
                            # Format timestamp for display
                            from datetime import datetime
                            try:
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                            except:
                                formatted_time = timestamp[:16]  # Fallback
                        else:
                            formatted_time = "Unknown time"
                        
                        score_color = "🟢" if result.get('percentage', 0) >= 80 else "🟡" if result.get('percentage', 0) >= 60 else "🔴"
                        st.write(f"{score_color} {formatted_time}: {result.get('correct_answers', 0)}/{result.get('total_questions', 0)} ({result.get('percentage', 0)}%)")
                
                st.markdown("---")
        else:
            st.info("No question history found. Generate some quizzes to see statistics!")
        
        if st.button("❌ Close Stats", key="close_history_stats"):
            st.session_state["show_history_stats"] = False
            st.rerun()
    
    st.markdown("---")
    
    # Quiz generation form
    quiz_params = create_quiz_generation_form()
    
    if quiz_params:
        # Generate a unique quiz key for this session
        import hashlib
        quiz_key = hashlib.md5(f"{quiz_params['topic']}_{quiz_params['num_questions']}_{quiz_params['question_type']}".encode()).hexdigest()[:8]
        
        with create_loading_spinner("Generating unique quiz questions..."):
            quiz_generator = get_quiz_generator()
            questions = quiz_generator.generate_quiz_questions(
                topic=quiz_params['topic'],
                content=quiz_params['content'],
                num_questions=quiz_params['num_questions'],
                question_type=quiz_params['question_type']
            )
            
            if questions and not questions[0].get('error'):
                # Store in session state
                if 'quizzes' not in st.session_state:
                    st.session_state.quizzes = []
                
                quiz_data = {
                    'topic': quiz_params['topic'],
                    'questions': questions,
                    'params': quiz_params,
                    'quiz_key': quiz_key
                }
                st.session_state.quizzes.append(quiz_data)
                st.session_state[f"current_quiz_{quiz_key}"] = quiz_data
                # Store topic for quiz scoring
                st.session_state[f"quiz_{quiz_key}_topic"] = quiz_params['topic']
                
                # Quiz validation
                validation = quiz_generator.validate_quiz(questions)
                if validation['warnings']:
                    for warning in validation['warnings']:
                        create_warning_message(warning)
                
                create_success_message(f"Generated {len(questions)} unique questions successfully!")
                
                # Show topic statistics
                topic_stats = quiz_generator.get_question_history_stats(quiz_params['topic'])
                st.info(f"📊 **{quiz_params['topic']} Statistics:** {topic_stats['total_questions_served']} total questions served")
            else:
                create_error_message(questions[0].get('error', 'Unknown error'))
                return
    
    # Display current quiz if available
    current_quiz = None
    for quiz_data in st.session_state.get('quizzes', []):
        if f"current_quiz_{quiz_data.get('quiz_key', '')}" in st.session_state:
            current_quiz = quiz_data
            break
    
    if current_quiz:
        questions = current_quiz['questions']
        quiz_key = current_quiz['quiz_key']
        
        st.markdown(f"### 📝 Quiz: {current_quiz['topic']}")
        st.markdown(f"**Questions:** {len(questions)} | **Type:** {current_quiz['params']['question_type'].replace('_', ' ').title()}")
        
        # Check if quiz has been submitted
        if st.session_state.get(f"quiz_{quiz_key}_submitted", False):
            # Show results
            score_result = st.session_state.get(f"quiz_{quiz_key}_results")
            if score_result:
                create_quiz_results_display(score_result, quiz_key)
                
                # Option to retake quiz
                if st.button("🔄 Take Another Quiz", key=f"retake_{quiz_key}"):
                    # Clear quiz state
                    for key in list(st.session_state.keys()):
                        if key.startswith(f"quiz_{quiz_key}"):
                            del st.session_state[key]
                    st.rerun()
        else:
            # Show interactive quiz
            st.markdown("#### Answer the questions below:")
            
            for question in questions:
                create_interactive_quiz_question(question, question.get('question_number', 0), quiz_key)
            
            # Quiz submission section
            create_quiz_submission_section(questions, quiz_key)

def performance_page():
    """Performance analysis page"""
    create_header("Performance Analysis", "Track and analyze your academic progress")
    
    # Load existing performance history (DB first, then session fallback)
    history_rows = []
    try:
        from database.operations import get_db_operations
        db = get_db_operations()
        db_items = db.get_user_performance(1)
        for rec in db_items:
            d = rec.to_dict() if hasattr(rec, 'to_dict') else rec
            percentage = (float(d.get('score', 0)) / max(float(d.get('total_marks', 1)), 1)) * 100
            history_rows.append({
                'created_at': d.get('created_at'),
                'subject': d.get('subject'),
                'topic': d.get('topic'),
                'score': float(d.get('score', 0)),
                'total_marks': float(d.get('total_marks', 1)),
                'percentage': percentage,
                'prediction': d.get('classification') or ("Weak" if percentage < 40 else "Strong")
            })
    except Exception:
        pass
    # Ensure session container exists
    if 'performance_data' not in st.session_state:
        st.session_state.performance_data = []

    # Performance input form
    new_entry = create_performance_input_form()
    
    if new_entry:
        # Handle prediction-only requests
        if new_entry.get('prediction_only'):
            # Show prediction result without saving
            prediction = new_entry.get('prediction', 'Unknown')
            badge_color = "#d9534f" if prediction == "Weak" else "#5cb85c" if prediction == "Strong" else "#6c757d"
            st.markdown(f"""
            <div style="margin-top:10px;">
                <span style="background:{badge_color}; color:white; padding:6px 12px; border-radius:12px; font-size: 1.1em;">
                    🔮 Prediction: {prediction}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            if prediction != "Unknown - Need score data for accurate prediction":
                st.info(f"📈 Performance prediction for {new_entry['subject']} - {new_entry['topic']}: **{prediction}**")
            else:
                st.warning("Please enter valid score data for a more accurate prediction")
    
    # Always display prediction history below the form
    st.markdown("---")
    create_prediction_history_display()
    
    # Return early if we just handled a prediction
    if new_entry and new_entry.get('prediction_only'):
        return
        
        # Handle full entry saves
        # Server-side validation to prevent invalid saves
        if new_entry['score'] > new_entry['total_marks']:
            st.error("Score obtained cannot be greater than total marks. Please enter valid values.")
            # Do NOT add/save; keep form values for correction
            return
        # Compute simple rule-based prediction
        import datetime
        percentage = (new_entry['score'] / max(new_entry['total_marks'], 1))
        prediction = "Weak" if percentage < 0.4 else "Strong"
        timestamp = datetime.datetime.now().isoformat()

        enriched = {
            **new_entry,
            'percentage': percentage * 100,
            'prediction': prediction,
            'created_at': timestamp
        }
        st.session_state.performance_data.append(enriched)
        # Try persisting to DB (best-effort)
        try:
            from database.operations import get_db_operations
            db = get_db_operations()
            db.save_performance(1, new_entry['subject'], new_entry['topic'], float(new_entry['score']), float(new_entry['total_marks']), prediction)
        except Exception:
            pass

        # Immediate feedback badge
        badge_color = "#d9534f" if prediction == "Weak" else "#5cb85c"
        st.markdown(f"""
        <div style="margin-top:10px;">
            <span style="background:{badge_color}; color:white; padding:4px 10px; border-radius:12px;">
                Prediction: {prediction}
            </span>
        </div>
        """, unsafe_allow_html=True)
        create_success_message("Performance entry analyzed and saved!")
    
    # Build combined table (DB + session new entries)
    combined = []
    combined.extend(history_rows)
    # Map session entries to display rows
    for e in st.session_state.get('performance_data', []):
        combined.append({
            'created_at': e.get('created_at'),
            'subject': e.get('subject'),
            'topic': e.get('topic'),
            'score': e.get('score'),
            'total_marks': e.get('total_marks'),
            'percentage': e.get('percentage', (e.get('score',0)/max(e.get('total_marks',1),1))*100),
            'prediction': e.get('prediction') or ("Weak" if (e.get('score',0)/max(e.get('total_marks',1),1)) < 0.4 else "Strong")
        })

    if combined:
        st.markdown("### 📊 Your Performance Data")
        
        # Convert to DataFrame for display
        import pandas as pd
        df = pd.DataFrame(combined)
        # Sort by date desc when available
        if 'created_at' in df.columns:
            try:
                df['created_at_dt'] = pd.to_datetime(df['created_at'])
                df = df.sort_values('created_at_dt', ascending=False)
                df = df.drop(columns=['created_at_dt'])
            except Exception:
                pass
        
        # Nicely formatted columns
        display_df = df.rename(columns={
            'created_at': 'Date/Time',
            'subject': 'Subject',
            'topic': 'Topic',
            'score': 'Score',
            'total_marks': 'Total',
            'percentage': 'Score (%)',
            'prediction': 'Prediction'
        })
        st.dataframe(display_df, use_container_width=True)

        # Export button
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Export Performance History (CSV)",
            data=csv_data,
            file_name="performance_history.csv",
            mime="text/csv"
        )
        
        # Analysis section
        if len(combined) >= 3:
            st.markdown("### 🔍 Performance Analysis")
            
            performance_analyzer = get_performance_analyzer()
            report = performance_analyzer.generate_performance_report(combined)
            
            if 'error' not in report:
                # Display trends
                trends = report['trends']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    create_info_card("Overall Average", f"{trends['overall_average']:.1f}%", "📊")
                with col2:
                    create_info_card("Performance Trend", trends['performance_trend'], "📈")
                with col3:
                    create_info_card("Total Tests", str(trends.get('total_tests', len(st.session_state.performance_data))), "📝")
                
                # Charts
                st.markdown("### 📈 Visualizations")
                create_performance_chart(st.session_state.performance_data, "bar")
                
                # Recommendations
                if report.get('recommendations'):
                    st.markdown("### 💡 Recommendations")
                    for rec in report['recommendations']:
                        st.markdown(f"• {rec}")
            else:
                create_error_message(report['error'])
        else:
            create_warning_message("Add at least 3 entries for trend/graph analysis. Per-entry predictions are shown above.")

def recommendations_page():
    """Enhanced Recommendations page with preferences, filtering, and history"""
    create_header("Learning Recommendations", "Get personalized educational resources")

    # Preferences Section
    st.markdown("### Set Your Preferences")
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            interests_input = st.text_input(
                "Areas of Interest",
                value=", ".join(st.session_state.get("user_profile", {}).get("interests", [])),
                placeholder="e.g., AI, Machine Learning, Python"
            )
            interests = [i.strip() for i in interests_input.split(",") if i.strip()]
        with c2:
            weak_topics_input = st.text_input(
                "Weak Topics",
                value=", ".join(st.session_state.get("user_profile", {}).get("weak_topics", [])),
                placeholder="e.g., Calculus, Linear Algebra, Probability"
            )
            weak_topics = [t.strip() for t in weak_topics_input.split(",") if t.strip()]
    c3, c4 = st.columns([1,1])
    with c3:
        options_ls = ["All", "Video", "Text", "Interactive Quiz"]
        stored_ls = st.session_state.get("user_profile", {}).get("learning_style", "All")
        # Normalize any previously saved lowercase values
        norm_map = {
            "all": "All",
            "video": "Video",
            "text": "Text",
            "interactive quiz": "Interactive Quiz",
        }
        normalized_default = norm_map.get(str(stored_ls).lower(), "All")
        learning_style = st.radio(
            "Preferred Learning Style",
            options=options_ls,
            index=options_ls.index(normalized_default)
        )
    with c4:
        st.markdown("\n")
        save_clicked = st.button("💾 Save Profile", use_container_width=True)

    if save_clicked:
        # Persist to session and DB if available
        st.session_state.user_profile = {
            'interests': interests,
            'weak_topics': weak_topics,
            # Store canonical (title-cased) for UI; convert to lower only when filtering
            'learning_style': learning_style
        }
        try:
            from database.operations import get_db_operations
            db = get_db_operations()
            # Assume user_id=1 for demo; in real app, plug in authenticated user id
            db.save_user_profile(1, interests, weak_topics, st.session_state.user_profile['learning_style'])
            create_success_message("Preferences saved successfully!")
        except Exception as e:
            create_warning_message(f"Saved locally. DB save skipped: {e}")

    st.markdown("---")
    st.markdown("### Your Recommendations")
    colA, colB, colC = st.columns([1,1,1])
    with colA:
        get_clicked = st.button("🎯 Get Recommendations", use_container_width=True)
    with colB:
        refresh_clicked = st.button("🔄 Refresh Suggestions", use_container_width=True)
    with colC:
        stats_clicked = st.button("📊 View Resource Statistics", use_container_width=True)

    # Prepare profile
    profile = st.session_state.get('user_profile', {
        'interests': interests if 'interests' in locals() and interests else [],
        'weak_topics': weak_topics if 'weak_topics' in locals() and weak_topics else [],
        'learning_style': (learning_style if 'learning_style' in locals() else 'All')
    })

    if get_clicked or refresh_clicked:
        if not (profile.get('interests') or profile.get('weak_topics')):
            create_warning_message("Please select at least one interest or weak topic")
        else:
            with create_loading_spinner("Finding personalized recommendations..."):
                recommender = get_recommender()
                recs = recommender.get_personalized_recommendations(profile)
                # Flatten and filter by learning style
                flat = []
                for resources in recs.values():
                    flat.extend(resources)
                style_map = {
                    'video': 'video',
                    'youtube_video': 'video',
                    'article': 'text',
                    'course': 'text',
                    'quiz': 'interactive quiz'
                }
                desired = profile['learning_style']
                if desired.lower() != 'all':
                    flat = [r for r in flat if style_map.get(r.get('type','').lower(), r.get('type','').lower()) == desired.lower()]
                # Score by keyword matches (interests + weak_topics)
                keywords = [*profile['interests'], *profile['weak_topics']]
                def score(res):
                    text = (res.get('title','') + ' ' + res.get('description','')).lower()
                    return sum(1 for k in keywords if k.lower() in text) + float(res.get('similarity_score', 0))
                flat.sort(key=score, reverse=True)

                if not flat:
                    create_info_message = st.info("No matching resources found. Try broadening your preferences.")
                else:
                    for res in flat[:12]:
                        create_recommendation_card(res)
                create_success_message("Recommendations generated successfully!")
                # Save recommendation history to DB (best-effort) and session fallback
                saved_to_db = False
                try:
                    from database.operations import get_db_operations
                    db = get_db_operations()
                    for res in flat[:12]:
                        db.save_recommendation(
                            1,
                            topic=','.join(profile['weak_topics'] or profile['interests'] or ["general"]),
                            resource_type=res.get('type','unknown'),
                            resource_url=res.get('url',''),
                            title=res.get('title','Untitled')
                        )
                    saved_to_db = True
                except Exception as e:
                    saved_to_db = False
                # Always keep an in-session history as a reliable fallback
                import datetime
                if 'recommendation_history' not in st.session_state:
                    st.session_state.recommendation_history = []
                for res in flat[:12]:
                    st.session_state.recommendation_history.append({
                        'created_at': datetime.datetime.now().isoformat(),
                        'title': res.get('title','Untitled'),
                        'resource_type': res.get('type','unknown'),
                        'resource_url': res.get('url','')
                    })

    if stats_clicked:
        try:
            recommender = get_recommender()
            stats = recommender.get_resource_statistics()
            if stats:
                metrics = [
                    {"title": "Total Resources", "value": str(stats['total_resources']), "icon": "📚"},
                    {"title": "Unique Topics", "value": str(stats['unique_topics']), "icon": "🏷️"},
                    {"title": "Resource Types", "value": str(len(stats['resource_types'])), "icon": "📋"}
                ]
                create_metric_row(metrics)
        except Exception as e:
            create_warning_message(f"Stats unavailable: {e}")

    st.markdown("---")
    st.markdown("### Recommendation History")
    # Prefer DB if available; otherwise fallback to session
    rows = []
    used_db = False
    try:
        from database.operations import get_db_operations
        db = get_db_operations()
        history = db.get_user_recommendations(1)
        if history:
            used_db = True
            for rec in history:
                d = rec.to_dict() if hasattr(rec, 'to_dict') else rec
                rows.append({
                    'Date': d.get('created_at'),
                    'Title': d.get('title'),
                    'Type': d.get('resource_type'),
                    'URL': d.get('resource_url'),
                    'Visited': '—'
                })
    except Exception:
        used_db = False
    if not used_db:
        # Use session history
        session_hist = st.session_state.get('recommendation_history', [])
        for d in session_hist:
            rows.append({
                'Date': d.get('created_at'),
                'Title': d.get('title'),
                'Type': d.get('resource_type'),
                'URL': d.get('resource_url'),
                'Visited': '—'
            })
    if rows:
        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No recommendations recorded yet.")

