#!/usr/bin/env python3
"""
Test script to verify CSV format for charts data download
Shows what the CSV structure will look like
"""

import pandas as pd
from utils.analytics import get_analytics_manager
from datetime import datetime

def test_charts_csv_format():
    """Test the CSV format for charts data"""
    print("🧪 Testing Charts Data CSV Format\n")
    
    try:
        # Get analytics data
        analytics_manager = get_analytics_manager()
        analytics = analytics_manager.get_dashboard_analytics("30")
        
        # Prepare charts data for CSV format (same logic as in admin_components.py)
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
        
        # Convert to DataFrame
        if charts_csv_data:
            charts_df = pd.DataFrame(charts_csv_data)
            
            print("📊 Charts Data CSV Structure:")
            print(f"✅ Total Records: {len(charts_csv_data)}")
            print(f"✅ Columns: {list(charts_df.columns)}")
            print("\n📋 Sample Data:")
            print(charts_df.head(10).to_string(index=False))
            
            print(f"\n📊 Data Categories Summary:")
            category_counts = charts_df['Data_Category'].value_counts()
            for category, count in category_counts.items():
                print(f"   • {category}: {count} records")
            
            # Generate sample CSV file for verification
            csv_data = charts_df.to_csv(index=False)
            sample_filename = f"sample_charts_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            
            with open(sample_filename, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            
            print(f"\n💾 Sample CSV file saved: {sample_filename}")
            
            # Show first few lines of CSV
            print(f"\n📄 First few lines of CSV:")
            csv_lines = csv_data.split('\n')[:6]  # Header + 5 data rows
            for line in csv_lines:
                if line.strip():
                    print(f"   {line}")
            
            return True
            
        else:
            print("❌ No chart data found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CSV format: {e}")
        return False

def compare_formats():
    """Compare the old JSON format vs new CSV format"""
    print(f"\n🔄 Format Comparison:")
    
    print("📄 OLD JSON Format:")
    print("   • Structure: Nested objects and arrays")
    print("   • File Extension: .json")
    print("   • MIME Type: application/json")
    print("   • Usage: Harder to analyze in spreadsheet tools")
    print("   • Data Access: Requires JSON parsing")
    
    print("\n📊 NEW CSV Format:")
    print("   • Structure: Flat table with clear columns")
    print("   • File Extension: .csv")
    print("   • MIME Type: text/csv")
    print("   • Usage: Easy to open in Excel, Google Sheets")
    print("   • Data Access: Direct import into analytics tools")
    print("   • Columns: Data_Category, Item_Name, Count, Type")

def main():
    """Run the test"""
    print("📈 Charts Data CSV Format Test\n")
    print("=" * 50)
    
    if test_charts_csv_format():
        print(f"\n✅ CSV format test successful!")
        compare_formats()
        
        print(f"\n🎯 Benefits of CSV Format:")
        print("   ✅ Easy to open in Excel or Google Sheets")
        print("   ✅ Simple to import into data analysis tools")
        print("   ✅ Clear column structure for filtering/sorting")
        print("   ✅ Standardized format for data exchange")
        print("   ✅ Human-readable and machine-processable")
        
        print(f"\n📖 How to use the CSV data:")
        print("1. Download the CSV from the admin dashboard")
        print("2. Open in Excel, Google Sheets, or any CSV viewer")
        print("3. Filter by 'Data_Category' to focus on specific data")
        print("4. Sort by 'Count' to see top performers")
        print("5. Use 'Type' column to understand what each count represents")
        
    else:
        print(f"\n❌ CSV format test failed")

if __name__ == "__main__":
    main()
