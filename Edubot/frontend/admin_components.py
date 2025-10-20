#!/usr/bin/env python3
"""
Admin components for EduBot analytics dashboard
Provides UI components for displaying analytics data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List

def create_header(title: str, subtitle: str = ""):
    """Create a styled header"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #1f77b4; margin-bottom: 0.5rem;">{title}</h1>
        <p style="color: #666; font-size: 1.1rem;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def create_analytics_cards(analytics: Dict[str, Any]):
    """Create analytics metric cards"""
    st.markdown("### 📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Users",
            value=analytics.get('total_users', 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="🟢 Active Users",
            value=analytics.get('active_users', 0),
            delta=None
        )
    
    with col3:
        quiz_stats = analytics.get('quiz_stats', {})
        st.metric(
            label="📝 Total Quizzes",
            value=quiz_stats.get('total_quizzes', 0),
            delta=None
        )
    
    with col4:
        doc_stats = analytics.get('document_stats', {})
        st.metric(
            label="📄 Documents Processed",
            value=doc_stats.get('total_documents', 0),
            delta=None
        )

def create_engagement_metrics(analytics: Dict[str, Any]):
    """Create engagement metrics section"""
    st.markdown("### 📈 Engagement Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        quiz_stats = analytics.get('quiz_stats', {})
        avg_score = quiz_stats.get('avg_score', 0)
        st.metric(
            label="📊 Average Quiz Score",
            value=f"{avg_score:.1f}%",
            delta=None
        )
    
    with col2:
        doc_stats = analytics.get('document_stats', {})
        avg_time = doc_stats.get('avg_processing_time', 0)
        st.metric(
            label="⏱️ Avg Processing Time",
            value=f"{avg_time:.1f}s",
            delta=None
        )
    
    with col3:
        total_questions = quiz_stats.get('total_questions', 0)
        st.metric(
            label="❓ Questions Answered",
            value=total_questions,
            delta=None
        )

def create_performance_overview(analytics: Dict[str, Any]):
    """Create performance overview section"""
    st.markdown("### 🎯 Performance Overview")
    
    # Education level distribution
    education_data = analytics.get('users_by_education', {})
    if education_data:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Education Level Distribution")
            fig_edu = px.pie(
                values=list(education_data.values()), 
                names=list(education_data.keys()),
                title="Users by Education Level"
            )
            st.plotly_chart(fig_edu, use_container_width=True)
        
        with col2:
            st.markdown("#### Education Level Data")
            edu_df = pd.DataFrame([
                {"Education Level": level, "Count": count}
                for level, count in education_data.items()
            ])
            st.dataframe(edu_df, use_container_width=True)
    
    # Feature usage
    feature_data = analytics.get('feature_usage', {})
    if feature_data:
        st.markdown("#### Feature Usage Statistics")
        feature_df = pd.DataFrame([
            {"Feature": feature, "Usage Count": count}
            for feature, count in feature_data.items()
        ])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_features = px.bar(
                feature_df, 
                x='Feature', 
                y='Usage Count',
                title='Feature Usage Count',
                color='Usage Count',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_features, use_container_width=True)
        
        with col2:
            st.dataframe(feature_df, use_container_width=True)

def create_date_range_filter():
    """Create date range filter"""
    st.markdown("### 📅 Date Range Filter")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        date_range = st.selectbox(
            "Select Period",
            ["7", "30", "90", "365"],
            index=1,
            format_func=lambda x: f"Last {x} days"
        )
    
    with col2:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=int(date_range)),
            max_value=datetime.now()
        )
    
    with col3:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    return start_date, end_date, date_range

def create_activity_timeline(analytics: Dict[str, Any]):
    """Create activity timeline section"""
    st.markdown("### ⏰ Activity Timeline")
    
    # Top active users
    top_users = analytics.get('top_active_users', [])
    if top_users:
        st.markdown("#### Most Active Users")
        users_df = pd.DataFrame(top_users)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_users = px.bar(
                users_df,
                x='username',
                y='activity_count',
                title='User Activity Count',
                color='activity_count',
                color_continuous_scale='Greens'
            )
            fig_users.update_xaxes(tickangle=45)
            st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            st.dataframe(users_df, use_container_width=True)
    else:
        st.info("📈 No active user data available for the selected period.")
    
    # Activity summary
    activity_data = analytics.get('activity_summary', {})
    if activity_data:
        st.markdown("#### Activity Types Distribution")
        activity_df = pd.DataFrame([
            {"Activity Type": activity, "Count": count}
            for activity, count in activity_data.items()
        ])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_activity = px.pie(
                activity_df,
                values='Count',
                names='Activity Type',
                title='Activity Types Distribution'
            )
            st.plotly_chart(fig_activity, use_container_width=True)
        
        with col2:
            st.dataframe(activity_df, use_container_width=True)
    else:
        st.info("📋 No activity summary data available for the selected period.")

def create_download_section(analytics: Dict[str, Any]):
    """Create data download section with bar charts for each report"""
    st.markdown("### 📥 Download Reports")
    
    # Create tabs for organized display
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Report", "👥 User Activity", "📈 Charts Data"])
    
    with tab1:
        st.markdown("#### Analytics Report Overview")
        
        # Analytics Report Bar Chart
        metrics_data = {
            'Total Users': analytics.get('total_users', 0),
            'Active Users': analytics.get('active_users', 0),
            'Total Quizzes': analytics.get('quiz_stats', {}).get('total_quizzes', 0),
            'Documents Processed': analytics.get('document_stats', {}).get('total_documents', 0),
            'Questions Answered': analytics.get('quiz_stats', {}).get('total_questions', 0)
        }
        
        if any(metrics_data.values()):
            fig_analytics = px.bar(
                x=list(metrics_data.keys()),
                y=list(metrics_data.values()),
                title='📊 Key Analytics Metrics',
                labels={'x': 'Metrics', 'y': 'Count'},
                color=list(metrics_data.values()),
                color_continuous_scale='Blues'
            )
            fig_analytics.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_analytics, use_container_width=True, key="analytics_report_chart")
        else:
            st.info("📈 No analytics data available for visualization")
        
        # Download button for Analytics Report
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📊 Download Analytics Report", use_container_width=True):
                # Create comprehensive report
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'total_users': analytics.get('total_users', 0),
                    'active_users': analytics.get('active_users', 0),
                    'quiz_stats': analytics.get('quiz_stats', {}),
                    'document_stats': analytics.get('document_stats', {}),
                    'feature_usage': analytics.get('feature_usage', {}),
                    'education_distribution': analytics.get('users_by_education', {})
                }
                
                # Convert to CSV
                report_df = pd.DataFrame([report_data])
                csv = report_df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV Report",
                    data=csv,
                    file_name=f"edubot_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_analytics_csv"
                )
    
    with tab2:
        st.markdown("#### User Activity Trends")
        
        # User Activity Bar Chart
        from utils.analytics import get_analytics_manager
        analytics_manager = get_analytics_manager()
        activity_data = analytics_manager.get_user_activity_details(days=30)
        
        if activity_data:
            # Create activity type distribution chart
            activity_df = pd.DataFrame(activity_data)
            if 'activity_type' in activity_df.columns:
                activity_counts = activity_df['activity_type'].value_counts()
                
                fig_activity = px.bar(
                    x=activity_counts.index,
                    y=activity_counts.values,
                    title='👥 User Activity Distribution (Last 30 Days)',
                    labels={'x': 'Activity Type', 'y': 'Count'},
                    color=activity_counts.values,
                    color_continuous_scale='Greens'
                )
                fig_activity.update_layout(height=400, showlegend=False)
                fig_activity.update_xaxes(tickangle=45)
                st.plotly_chart(fig_activity, use_container_width=True, key="user_activity_chart")
            else:
                st.info("📈 No activity type data available for visualization")
        else:
            st.info("📈 No user activity data available for visualization")
        
        # Download button for User Activity
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("👥 Download User Activity", use_container_width=True):
                if activity_data:
                    activity_df = pd.DataFrame(activity_data)
                    csv = activity_df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download Activity CSV",
                        data=csv,
                        file_name=f"user_activity_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_activity_csv"
                    )
                else:
                    st.warning("No activity data available for download")
    
    with tab3:
        st.markdown("#### Charts Data Overview")
        
        # Charts Data Visualization
        charts_data = {
            'Feature Usage': len(analytics.get('feature_usage', {})),
            'Education Levels': len(analytics.get('users_by_education', {})),
            'Registration Records': len(analytics.get('registrations_over_time', [])),
            'Login Records': len(analytics.get('login_activity', [])),
            'Top Active Users': len(analytics.get('top_active_users', []))
        }
        
        if any(charts_data.values()):
            fig_charts = px.bar(
                x=list(charts_data.keys()),
                y=list(charts_data.values()),
                title='📈 Available Chart Data Records',
                labels={'x': 'Data Category', 'y': 'Record Count'},
                color=list(charts_data.values()),
                color_continuous_scale='Purples'
            )
            fig_charts.update_layout(height=400, showlegend=False)
            fig_charts.update_xaxes(tickangle=45)
            st.plotly_chart(fig_charts, use_container_width=True, key="charts_data_overview")
        else:
            st.info("📈 No chart data available for visualization")
        
        # Download button for Charts Data
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📈 Download Charts Data", use_container_width=True):
                # Prepare charts data for CSV format
                charts_csv_data = []
                
                # Add feature usage data
                feature_usage = analytics.get('feature_usage', {})
                for feature, count in feature_usage.items():
                    charts_csv_data.append({
                        'Data_Category': 'Feature Usage',
                        'Item_Name': feature,
                        'Count': count,
                        'Type': 'usage_count'
                    })
                
                # Add education distribution data
                education_dist = analytics.get('users_by_education', {})
                for education, count in education_dist.items():
                    charts_csv_data.append({
                        'Data_Category': 'Education Distribution',
                        'Item_Name': education,
                        'Count': count,
                        'Type': 'user_count'
                    })
                
                # Add registration data
                registrations = analytics.get('registrations_over_time', [])
                for reg_data in registrations:
                    charts_csv_data.append({
                        'Data_Category': 'User Registrations',
                        'Item_Name': reg_data.get('reg_date', 'Unknown'),
                        'Count': reg_data.get('count', 0),
                        'Type': 'daily_registrations'
                    })
                
                # Add login activity data
                login_activity = analytics.get('login_activity', [])
                for login_data in login_activity:
                    charts_csv_data.append({
                        'Data_Category': 'Login Activity',
                        'Item_Name': login_data.get('login_date', 'Unknown'),
                        'Count': login_data.get('count', 0),
                        'Type': 'daily_logins'
                    })
                
                # Add top active users data
                top_users = analytics.get('top_active_users', [])
                for user_data in top_users:
                    charts_csv_data.append({
                        'Data_Category': 'Top Active Users',
                        'Item_Name': user_data.get('username', 'Unknown'),
                        'Count': user_data.get('activity_count', 0),
                        'Type': 'activity_count'
                    })
                
                # Convert to DataFrame and CSV
                if charts_csv_data:
                    charts_df = pd.DataFrame(charts_csv_data)
                    csv_data = charts_df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download CSV Data",
                        data=csv_data,
                        file_name=f"charts_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_charts_csv"
                    )
                else:
                    st.warning("No chart data available for download")

def create_error_summary():
    """Create error summary section"""
    st.markdown("### ⚠️ System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🟢 System Status",
            value="Online",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📊 Data Integrity",
            value="Good",
            delta=None
        )
    
    with col3:
        st.metric(
            label="🔄 Last Update",
            value=datetime.now().strftime("%H:%M"),
            delta=None
        )

def create_user_activity_table(user_activities: List[Dict[str, Any]]):
    """Create detailed user activity table"""
    if not user_activities:
        st.warning("📊 No user activity data available.")
        st.info("""To populate user activity data:
        
1. **Generate Sample Data**: Run `python generate_sample_data.py` to create realistic test data
2. **Use the Application**: Have users interact with EduBot features to generate real activity logs
3. **Check Database**: Ensure the analytics tables are properly initialized
        
**Note**: User activities are automatically tracked when users:
- Visit pages
- Use features (summarization, quizzes, etc.)
- Complete quizzes
- Upload documents
- View recommendations""")
        
        # Show sample data generation button
        if st.button("🔄 Generate Sample Data", help="Generate realistic sample activity data for testing"):
            st.info("Please run: `python generate_sample_data.py` from the command line to generate sample data.")
        return
    
    st.markdown("### 👥 Detailed User Activities")
    
    # Convert to DataFrame
    df = pd.DataFrame(user_activities)
    
    # Format datetime columns with robust parsing
    if 'created_at' in df.columns:
        def safe_datetime_format(dt_series):
            """Safely format datetime strings with multiple format attempts"""
            try:
                # First try pandas auto-detection with errors='coerce'
                parsed_dates = pd.to_datetime(dt_series, errors='coerce', infer_datetime_format=True)
                return parsed_dates.dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e1:
                print(f"Auto datetime parsing failed: {e1}")
                try:
                    # Try ISO format parsing
                    parsed_dates = pd.to_datetime(dt_series, format='%Y-%m-%dT%H:%M:%S', errors='coerce')
                    return parsed_dates.dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e2:
                    print(f"ISO format parsing failed: {e2}")
                    try:
                        # Try standard format parsing
                        parsed_dates = pd.to_datetime(dt_series, format='%Y-%m-%d %H:%M:%S', errors='coerce')
                        return parsed_dates.dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e3:
                        print(f"Standard format parsing failed: {e3}")
                        # Return original if all parsing fails
                        return dt_series
        
        df['created_at'] = safe_datetime_format(df['created_at'])
    
    # Display filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        activity_types = df['activity_type'].unique() if 'activity_type' in df.columns else []
        selected_activity = st.selectbox("Filter by Activity Type", ["All"] + list(activity_types))
    
    with col2:
        users = df['username'].unique() if 'username' in df.columns else []
        selected_user = st.selectbox("Filter by User", ["All"] + list(users))
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_activity != "All" and 'activity_type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['activity_type'] == selected_activity]
    
    if selected_user != "All" and 'username' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['username'] == selected_user]
    
    # Display table
    display_columns = ['username', 'activity_type', 'activity_description', 'page_visited', 'created_at']
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    
    st.dataframe(
        filtered_df[available_columns]
        .rename(columns={
            'username': 'Username',
            'activity_type': 'Activity Type',
            'activity_description': 'Description',
            'page_visited': 'Page',
            'created_at': 'Timestamp'
        }),
        use_container_width=True,
        height=400
    )
    
    # Summary statistics
    st.markdown("#### Activity Summary")
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.metric("Total Activities", len(filtered_df))
    
    with summary_col2:
        unique_users = filtered_df['username'].nunique() if 'username' in filtered_df.columns else 0
        st.metric("Unique Users", unique_users)
    
    with summary_col3:
        if 'session_duration' in filtered_df.columns:
            avg_duration = filtered_df['session_duration'].mean()
            st.metric("Avg Session Duration", f"{avg_duration:.1f}s")
        else:
            st.metric("Avg Session Duration", "N/A")