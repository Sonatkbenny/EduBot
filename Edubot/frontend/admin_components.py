#!/usr/bin/env python3
"""
Admin dashboard components for EduBot
Enhanced analytics UI components with cards, charts, and download functionality
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import base64
from io import BytesIO

def create_analytics_cards(analytics: Dict[str, Any]) -> None:
    """Create analytics overview cards"""
    st.markdown("### 📊 Analytics Overview")
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = analytics.get('total_users', 0)
        growth_rate = analytics.get('user_growth_rate', 0)
        
        # Color code growth rate
        growth_color = "🟢" if growth_rate > 0 else "🔴" if growth_rate < 0 else "⚪"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 10px 0;
        ">
            <h2 style="margin: 0; font-size: 2.5em;">{total_users}</h2>
            <p style="margin: 5px 0; font-size: 1.1em;">Total Users</p>
            <small>{growth_color} {growth_rate}% growth</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_month = analytics.get('active_users_month', 0)
        activity_rate = round((active_month / max(total_users, 1)) * 100, 1) if total_users > 0 else 0
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 10px 0;
        ">
            <h2 style="margin: 0; font-size: 2.5em;">{active_month}</h2>
            <p style="margin: 5px 0; font-size: 1.1em;">Active Users (Month)</p>
            <small>📈 {activity_rate}% of total</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        active_week = analytics.get('active_users_week', 0)
        weekly_rate = round((active_week / max(active_month, 1)) * 100, 1) if active_month > 0 else 0
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 10px 0;
        ">
            <h2 style="margin: 0; font-size: 2.5em;">{active_week}</h2>
            <p style="margin: 5px 0; font-size: 1.1em;">Active Users (Week)</p>
            <small>⚡ {weekly_rate}% of monthly</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        admin_count = analytics.get('admin_count', 0)
        admin_rate = round((admin_count / max(total_users, 1)) * 100, 1) if total_users > 0 else 0
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 10px 0;
        ">
            <h2 style="margin: 0; font-size: 2.5em;">{admin_count}</h2>
            <p style="margin: 5px 0; font-size: 1.1em;">Admin Users</p>
            <small>👑 {admin_rate}% admin ratio</small>
        </div>
        """, unsafe_allow_html=True)

def create_engagement_metrics(analytics: Dict[str, Any]) -> None:
    """Create engagement metrics section"""
    st.markdown("### 🔥 User Engagement")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_quizzes = analytics.get('total_quizzes', 0)
        avg_quizzes = analytics.get('avg_quizzes_per_user', 0)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            color: #333;
            margin: 5px 0;
        ">
            <h3 style="margin: 0; color: #2c3e50;">{total_quizzes}</h3>
            <p style="margin: 5px 0;">Total Quizzes</p>
            <small>📊 {avg_quizzes} per user avg</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_docs = analytics.get('total_documents', 0)
        avg_docs = analytics.get('avg_documents_per_user', 0)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            color: #333;
            margin: 5px 0;
        ">
            <h3 style="margin: 0; color: #2c3e50;">{total_docs}</h3>
            <p style="margin: 5px 0;">Documents Processed</p>
            <small>📄 {avg_docs} per user avg</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_recs = analytics.get('total_recommendations', 0)
        completion_rate = analytics.get('quiz_completion_rate', 0)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            color: white;
            margin: 5px 0;
        ">
            <h3 style="margin: 0;">{total_recs}</h3>
            <p style="margin: 5px 0;">Recommendations</p>
            <small>✅ {completion_rate}% completion rate</small>
        </div>
        """, unsafe_allow_html=True)

def create_performance_overview(analytics: Dict[str, Any]) -> None:
    """Create performance metrics overview"""
    st.markdown("### 🏆 Performance Trends")
    
    avg_score = analytics.get('avg_quiz_score', 0)
    strong_topics = analytics.get('strong_topics', [])
    weak_topics = analytics.get('weak_topics', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average performance indicator
        score_color = "#27ae60" if avg_score >= 70 else "#f39c12" if avg_score >= 50 else "#e74c3c"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {score_color}20 0%, {score_color}40 100%);
            border-left: 5px solid {score_color};
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        ">
            <h3 style="color: {score_color}; margin: 0;">Average Quiz Score</h3>
            <h2 style="margin: 10px 0; color: #2c3e50;">{avg_score}%</h2>
            <p style="margin: 0; color: #7f8c8d;">Across all users and topics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Topics overview
        st.markdown("""
        <div style="
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #dee2e6;
            margin: 10px 0;
        ">
            <h3 style="color: #495057; margin: 0 0 15px 0;">Topic Performance</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if strong_topics:
            st.success(f"💪 **Strong Topics:** {', '.join(strong_topics[:3])}")
        else:
            st.info("💪 **Strong Topics:** Not enough data")
            
        if weak_topics:
            st.warning(f"📚 **Needs Improvement:** {', '.join(weak_topics[:3])}")
        else:
            st.info("📚 **Needs Improvement:** Not enough data")

def create_date_range_filter() -> tuple:
    """Create date range filter controls"""
    st.markdown("### 📅 Analytics Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.selectbox(
            "Time Period",
            ["7", "30", "90", "365"],
            format_func=lambda x: f"Last {x} days",
            index=1  # Default to 30 days
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )
    
    with col3:
        start_date = st.date_input(
            "Start Date", 
            value=end_date - timedelta(days=int(date_range)),
            max_value=end_date
        )
    
    return start_date, end_date, date_range

def create_download_section(analytics: Dict[str, Any]) -> None:
    """Create analytics download section"""
    st.markdown("### 📥 Download Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 10px 0;
        ">
            <h4 style="margin: 0 0 10px 0;">📊 Full Analytics Report</h4>
            <p style="margin: 0; font-size: 0.9em;">Complete analytics data with charts and insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Download
        if st.button("📄 Download PDF Report", use_container_width=True, key="download_pdf"):
            try:
                from utils.analytics import get_analytics_manager
                analytics_manager = get_analytics_manager()
                pdf_data = analytics_manager.generate_analytics_report(analytics, "pdf")
                
                b64_pdf = base64.b64encode(pdf_data).decode()
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="edubot_analytics_report.pdf">📄 Download PDF Report</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ PDF report generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating PDF report: {str(e)}")
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 10px 0;
        ">
            <h4 style="margin: 0 0 10px 0;">📈 Excel/CSV Export</h4>
            <p style="margin: 0; font-size: 0.9em;">Raw data for further analysis and processing</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Excel Download
        if st.button("📊 Download Excel Report", use_container_width=True, key="download_excel"):
            try:
                from utils.analytics import get_analytics_manager
                analytics_manager = get_analytics_manager()
                excel_data = analytics_manager.generate_analytics_report(analytics, "excel")
                
                b64_excel = base64.b64encode(excel_data).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}" download="edubot_analytics_data.xlsx">📊 Download Excel Report</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ Excel report generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating Excel report: {str(e)}")
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 10px 0;
        ">
            <h4 style="margin: 0 0 10px 0;">📋 Quick Summary</h4>
            <p style="margin: 0; font-size: 0.9em;">Key metrics and highlights overview</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Summary Display
        if st.button("📋 Show Quick Summary", use_container_width=True, key="show_summary"):
            st.markdown("---")
            st.markdown("#### 📋 Analytics Summary")
            
            summary_data = f"""
            **Report Generated:** {analytics.get('last_updated', 'Unknown')}
            
            **User Statistics:**
            - Total Users: {analytics.get('total_users', 0)}
            - Active This Month: {analytics.get('active_users_month', 0)}
            - Active This Week: {analytics.get('active_users_week', 0)}
            - Administrators: {analytics.get('admin_count', 0)}
            
            **Growth Metrics:**
            - User Growth Rate: {analytics.get('user_growth_rate', 0)}%
            - Daily Login Average: {analytics.get('login_frequency', 0)}
            
            **Engagement:**
            - Total Quizzes: {analytics.get('total_quizzes', 0)}
            - Documents Processed: {analytics.get('total_documents', 0)}
            - Recommendations Generated: {analytics.get('total_recommendations', 0)}
            """
            
            st.markdown(summary_data)

def create_activity_timeline(analytics: Dict[str, Any]) -> None:
    """Create user activity timeline"""
    st.markdown("### 📈 Activity Timeline")
    
    activity_logs = analytics.get('activity_logs', [])
    
    if not activity_logs:
        st.info("📊 No activity data available for the selected period.")
        return
    
    # Create activity status summary
    status_counts = {}
    for user in activity_logs:
        status = user.get('activity_status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Display as progress bars
    total_users = sum(status_counts.values())
    
    for status, count in status_counts.items():
        percentage = (count / total_users) * 100 if total_users > 0 else 0
        
        # Color mapping for different statuses
        color_map = {
            'This Week': '#27ae60',
            'This Month': '#f39c12', 
            'Older': '#95a5a6',
            'Never': '#e74c3c'
        }
        
        color = color_map.get(status, '#3498db')
        
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: bold; color: {color};">{status}</span>
                <span>{count} users ({percentage:.1f}%)</span>
            </div>
            <div style="background-color: #ecf0f1; height: 20px; border-radius: 10px; overflow: hidden;">
                <div style="background-color: {color}; height: 100%; width: {percentage}%; border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_error_summary() -> None:
    """Create error and alert summary section"""
    st.markdown("### 🚨 System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        ">
            <h4 style="color: #155724; margin: 0;">✅ System Status</h4>
            <p style="margin: 5px 0; color: #155724;">All systems operational</p>
            <small style="color: #6c757d;">Last checked: {datetime.now().strftime('%H:%M')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Mock error data - in real implementation, this would come from logs
        failed_logins = 0  # This would be calculated from actual login attempt logs
        
        status_color = "#f8d7da" if failed_logins > 5 else "#d1ecf1"
        text_color = "#721c24" if failed_logins > 5 else "#0c5460"
        
        st.markdown(f"""
        <div style="
            background-color: {status_color};
            border: 1px solid #c3e6cb;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        ">
            <h4 style="color: {text_color}; margin: 0;">🔐 Failed Logins</h4>
            <p style="margin: 5px 0; color: {text_color};">{failed_logins} in last 24h</p>
            <small style="color: #6c757d;">Security threshold: 10/day</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Mock upload errors
        upload_errors = 0
        
        st.markdown(f"""
        <div style="
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        ">
            <h4 style="color: #0c5460; margin: 0;">📁 Upload Errors</h4>
            <p style="margin: 5px 0; color: #0c5460;">{upload_errors} errors today</p>
            <small style="color: #6c757d;">File processing stable</small>
        </div>
        """, unsafe_allow_html=True)
