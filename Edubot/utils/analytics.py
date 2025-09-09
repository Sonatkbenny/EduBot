#!/usr/bin/env python3
"""
Analytics module for EduBot Admin Dashboard
Provides comprehensive data collection and processing for analytics
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from database.user_models import get_user_database
import json
import base64
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class AnalyticsManager:
    """Comprehensive analytics manager for admin dashboard"""
    
    def __init__(self):
        self.user_db = get_user_database()
    
    def get_dashboard_analytics(self, date_range: str = "30") -> Dict[str, Any]:
        """Get all analytics data for dashboard display"""
        try:
            # Get comprehensive analytics from database
            analytics = self.user_db.get_comprehensive_analytics()
            
            # Add engagement metrics
            engagement = self.user_db.get_engagement_metrics()
            analytics.update(engagement)
            
            # Add performance analytics
            performance = self.user_db.get_performance_analytics()
            analytics.update(performance)
            
            # Add activity logs
            activity_logs = self.user_db.get_user_activity_logs(int(date_range))
            analytics['activity_logs'] = activity_logs
            
            # Calculate derived metrics
            analytics['user_growth_rate'] = self._calculate_growth_rate(analytics.get('registrations_over_time', []))
            analytics['login_frequency'] = self._calculate_login_frequency(analytics.get('login_activity', []))
            analytics['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return analytics
            
        except Exception as e:
            print(f"Error getting dashboard analytics: {e}")
            return self._get_default_analytics()
    
    def _calculate_growth_rate(self, registration_data: List[Dict]) -> float:
        """Calculate user growth rate"""
        if len(registration_data) < 2:
            return 0.0
        
        try:
            recent_registrations = sum(day['count'] for day in registration_data[-7:])
            previous_registrations = sum(day['count'] for day in registration_data[-14:-7])
            
            if previous_registrations == 0:
                return 100.0 if recent_registrations > 0 else 0.0
            
            growth_rate = ((recent_registrations - previous_registrations) / previous_registrations) * 100
            return round(growth_rate, 1)
            
        except Exception:
            return 0.0
    
    def _calculate_login_frequency(self, login_data: List[Dict]) -> float:
        """Calculate average daily login frequency"""
        if not login_data:
            return 0.0
        
        total_logins = sum(day['count'] for day in login_data)
        return round(total_logins / len(login_data), 1)
    
    def _get_default_analytics(self) -> Dict[str, Any]:
        """Return default analytics when data retrieval fails"""
        return {
            'total_users': 0,
            'active_users_month': 0,
            'active_users_week': 0,
            'users_by_education': {},
            'registrations_over_time': [],
            'login_activity': [],
            'admin_count': 0,
            'total_quizzes': 0,
            'total_documents': 0,
            'avg_quiz_score': 0,
            'user_growth_rate': 0,
            'login_frequency': 0,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def create_visualization_charts(self, analytics: Dict[str, Any]) -> Dict[str, go.Figure]:
        """Create all visualization charts for the dashboard"""
        charts = {}
        
        # User Registration Over Time
        if analytics.get('registrations_over_time'):
            reg_data = analytics['registrations_over_time']
            df_reg = pd.DataFrame(reg_data)
            charts['registrations'] = px.bar(
                df_reg, 
                x='reg_date', 
                y='count',
                title='User Registrations (Last 30 Days)',
                labels={'reg_date': 'Date', 'count': 'New Users'}
            )
            charts['registrations'].update_layout(height=400)
        
        # Login Activity
        if analytics.get('login_activity'):
            login_data = analytics['login_activity']
            df_login = pd.DataFrame(login_data)
            charts['logins'] = px.line(
                df_login,
                x='login_date',
                y='count',
                title='Daily Login Activity (Last 30 Days)',
                labels={'login_date': 'Date', 'count': 'Logins'}
            )
            charts['logins'].update_layout(height=400)
        
        # Education Level Demographics
        if analytics.get('users_by_education'):
            edu_data = analytics['users_by_education']
            df_edu = pd.DataFrame(list(edu_data.items()), columns=['Education Level', 'Count'])
            charts['education'] = px.pie(
                df_edu,
                values='Count',
                names='Education Level',
                title='Users by Education Level'
            )
            charts['education'].update_layout(height=400)
        
        # User Activity Status
        activity_logs = analytics.get('activity_logs', [])
        if activity_logs:
            activity_summary = {}
            for user in activity_logs:
                status = user.get('activity_status', 'Unknown')
                activity_summary[status] = activity_summary.get(status, 0) + 1
            
            df_activity = pd.DataFrame(list(activity_summary.items()), columns=['Status', 'Count'])
            charts['user_activity'] = px.bar(
                df_activity,
                x='Status',
                y='Count',
                title='User Activity Status',
                color='Status'
            )
            charts['user_activity'].update_layout(height=400)
        
        return charts
    
    def generate_analytics_report(self, analytics: Dict[str, Any], format_type: str = "csv") -> bytes:
        """Generate downloadable analytics report"""
        if format_type.lower() == "pdf":
            return self._generate_pdf_report(analytics)
        else:
            return self._generate_csv_report(analytics)
    
    def _generate_csv_report(self, analytics: Dict[str, Any]) -> bytes:
        """Generate CSV report"""
        try:
            # Create multiple sheets of data
            output = BytesIO()
            
            # User Overview
            overview_data = {
                'Metric': [
                    'Total Users',
                    'Active Users (Month)',
                    'Active Users (Week)', 
                    'Admin Users',
                    'User Growth Rate (%)',
                    'Average Daily Logins'
                ],
                'Value': [
                    analytics.get('total_users', 0),
                    analytics.get('active_users_month', 0),
                    analytics.get('active_users_week', 0),
                    analytics.get('admin_count', 0),
                    analytics.get('user_growth_rate', 0),
                    analytics.get('login_frequency', 0)
                ]
            }
            
            df_overview = pd.DataFrame(overview_data)
            
            # Education Demographics
            edu_data = analytics.get('users_by_education', {})
            df_education = pd.DataFrame(list(edu_data.items()), columns=['Education Level', 'User Count'])
            
            # Activity Logs
            activity_logs = analytics.get('activity_logs', [])
            df_activity = pd.DataFrame(activity_logs)
            
            # Write to Excel with multiple sheets
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_overview.to_excel(writer, sheet_name='Overview', index=False)
                if not df_education.empty:
                    df_education.to_excel(writer, sheet_name='Education Demographics', index=False)
                if not df_activity.empty:
                    df_activity.to_excel(writer, sheet_name='User Activity', index=False)
            
            output.seek(0)
            return output.read()
            
        except Exception as e:
            print(f"Error generating CSV report: {e}")
            # Fallback to simple CSV
            df = pd.DataFrame([analytics])
            return df.to_csv(index=False).encode('utf-8')
    
    def _generate_pdf_report(self, analytics: Dict[str, Any]) -> bytes:
        """Generate PDF report"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("EduBot Analytics Report", title_style))
            story.append(Spacer(1, 20))
            
            # Report metadata
            meta_style = styles['Normal']
            story.append(Paragraph(f"<b>Generated:</b> {analytics.get('last_updated', 'Unknown')}", meta_style))
            story.append(Paragraph(f"<b>Report Period:</b> Last 30 days", meta_style))
            story.append(Spacer(1, 20))
            
            # User Overview Section
            story.append(Paragraph("User Overview", styles['Heading2']))
            
            overview_data = [
                ['Metric', 'Value'],
                ['Total Users', str(analytics.get('total_users', 0))],
                ['Active Users (Month)', str(analytics.get('active_users_month', 0))],
                ['Active Users (Week)', str(analytics.get('active_users_week', 0))],
                ['Admin Users', str(analytics.get('admin_count', 0))],
                ['User Growth Rate', f"{analytics.get('user_growth_rate', 0)}%"],
                ['Average Daily Logins', str(analytics.get('login_frequency', 0))]
            ]
            
            overview_table = Table(overview_data, colWidths=[3*inch, 2*inch])
            overview_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(overview_table)
            story.append(Spacer(1, 20))
            
            # Education Demographics
            edu_data = analytics.get('users_by_education', {})
            if edu_data:
                story.append(Paragraph("Education Level Demographics", styles['Heading2']))
                
                edu_table_data = [['Education Level', 'User Count']]
                for level, count in edu_data.items():
                    edu_table_data.append([level, str(count)])
                
                edu_table = Table(edu_table_data, colWidths=[3*inch, 2*inch])
                edu_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(edu_table)
                story.append(Spacer(1, 20))
            
            # Activity Summary
            activity_logs = analytics.get('activity_logs', [])
            if activity_logs:
                story.append(Paragraph("User Activity Summary", styles['Heading2']))
                
                activity_summary = {}
                for user in activity_logs:
                    status = user.get('activity_status', 'Unknown')
                    activity_summary[status] = activity_summary.get(status, 0) + 1
                
                activity_table_data = [['Activity Status', 'User Count']]
                for status, count in activity_summary.items():
                    activity_table_data.append([status, str(count)])
                
                activity_table = Table(activity_table_data, colWidths=[3*inch, 2*inch])
                activity_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(activity_table)
            
            doc.build(story)
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            # Fallback to simple text
            report_text = f"EduBot Analytics Report\n\nTotal Users: {analytics.get('total_users', 0)}\nActive Users: {analytics.get('active_users_month', 0)}"
            return report_text.encode('utf-8')

# Global analytics manager instance
_analytics_manager = None

def get_analytics_manager() -> AnalyticsManager:
    """Get global analytics manager instance"""
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AnalyticsManager()
    return _analytics_manager
