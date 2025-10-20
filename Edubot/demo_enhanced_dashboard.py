#!/usr/bin/env python3
"""
Demo script showing the enhanced admin dashboard features
Shows what the bar charts and reports will look like
"""

import matplotlib.pyplot as plt
import pandas as pd
from utils.analytics import get_analytics_manager

def create_demo_charts():
    """Create demo charts to show what the dashboard will display"""
    print("🎨 Creating demo charts for the enhanced admin dashboard...\n")
    
    try:
        # Get analytics data
        analytics_manager = get_analytics_manager()
        analytics = analytics_manager.get_dashboard_analytics("30")
        
        # 1. Analytics Report Bar Chart
        print("1. 📊 Analytics Report Chart:")
        metrics_data = {
            'Total Users': analytics.get('total_users', 0),
            'Active Users': analytics.get('active_users', 0),
            'Total Quizzes': analytics.get('quiz_stats', {}).get('total_quizzes', 0),
            'Documents Processed': analytics.get('document_stats', {}).get('total_documents', 0),
            'Questions Answered': analytics.get('quiz_stats', {}).get('total_questions', 0)
        }
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(metrics_data.keys(), metrics_data.values(), color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        plt.title('📊 Key Analytics Metrics', fontsize=16, pad=20)
        plt.ylabel('Count', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('analytics_report_demo.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"   ✅ Metrics: {metrics_data}")
        print("   📁 Saved as: analytics_report_demo.png\n")
        
        # 2. User Activity Chart
        print("2. 👥 User Activity Chart:")
        activity_data = analytics_manager.get_user_activity_details(days=30)
        
        if activity_data:
            activity_df = pd.DataFrame(activity_data)
            if 'activity_type' in activity_df.columns:
                activity_counts = activity_df['activity_type'].value_counts()
                
                plt.figure(figsize=(12, 6))
                bars = plt.bar(activity_counts.index, activity_counts.values, 
                             color=['#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22'])
                plt.title('👥 User Activity Distribution (Last 30 Days)', fontsize=16, pad=20)
                plt.ylabel('Activity Count', fontsize=12)
                plt.xlabel('Activity Type', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig('user_activity_demo.png', dpi=150, bbox_inches='tight')
                plt.close()
                print(f"   ✅ Activity Types: {dict(activity_counts)}")
                print("   📁 Saved as: user_activity_demo.png\n")
        
        # 3. Charts Data Overview
        print("3. 📈 Charts Data Overview:")
        charts_data = {
            'Feature Usage': len(analytics.get('feature_usage', {})),
            'Education Levels': len(analytics.get('users_by_education', {})),
            'Registration Records': len(analytics.get('registrations_over_time', [])),
            'Login Records': len(analytics.get('login_activity', [])),
            'Top Active Users': len(analytics.get('top_active_users', []))
        }
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(charts_data.keys(), charts_data.values(), 
                      color=['#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22'])
        plt.title('📈 Available Chart Data Records', fontsize=16, pad=20)
        plt.ylabel('Record Count', fontsize=12)
        plt.xlabel('Data Category', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('charts_data_demo.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"   ✅ Data Records: {charts_data}")
        print("   📁 Saved as: charts_data_demo.png\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating demo charts: {e}")
        return False

def show_dashboard_features():
    """Show what features are available in the enhanced dashboard"""
    print("✨ Enhanced Admin Dashboard Features:\n")
    
    print("📊 ANALYTICS REPORT TAB:")
    print("  ├── 📈 Interactive bar chart showing key metrics")
    print("  ├── 💾 Download CSV report with comprehensive data")
    print("  └── 🎯 Visual representation of system performance\n")
    
    print("👥 USER ACTIVITY TAB:")
    print("  ├── 📊 Activity type distribution chart")
    print("  ├── 💾 Download user activity data as CSV")
    print("  └── 🔍 Visual breakdown of user engagement\n")
    
    print("📈 CHARTS DATA TAB:")
    print("  ├── 📋 Overview of available data records")
    print("  ├── 💾 Download chart data as CSV")
    print("  └── 🗂️ Data availability visualization\n")
    
    print("🚀 ENHANCED FEATURES:")
    print("  ├── 🎨 Color-coded bar charts for better visualization")
    print("  ├── 📑 Organized tab layout for easy navigation")
    print("  ├── 🔄 Real-time data refresh capability")
    print("  ├── 📱 Responsive design for different screen sizes")
    print("  └── 🎯 Interactive plotly charts with hover details\n")

def main():
    """Run the demo"""
    print("🎭 Enhanced Admin Dashboard Demo\n")
    print("=" * 50)
    
    # Show features
    show_dashboard_features()
    
    # Create demo charts
    if create_demo_charts():
        print("🎉 Demo completed successfully!")
        print("\n📖 How to access the enhanced dashboard:")
        print("1. Run: streamlit run app.py")
        print("2. Go to: http://localhost:8501?admin=login")
        print("3. Login with admin credentials")
        print("4. Navigate to the '📈 Reports' tab")
        print("5. Explore the three report tabs with charts and download options")
        
        print("\n🖼️ Demo chart files created:")
        print("   • analytics_report_demo.png")
        print("   • user_activity_demo.png") 
        print("   • charts_data_demo.png")
    else:
        print("❌ Demo failed. Please check your setup.")

if __name__ == "__main__":
    main()
