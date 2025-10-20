import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import streamlit as st
from config.settings import PERFORMANCE_MODEL_CONFIG
from typing import List, Dict, Any, Tuple
import plotly.graph_objects as go
import plotly.express as px

class PerformanceAnalyzer:
    """Performance analysis using machine learning models"""
    
    def __init__(self):
        self.config = PERFORMANCE_MODEL_CONFIG
        self.models = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = ['score', 'total_marks', 'percentage', 'subject_rank']
    
    def prepare_data(self, performance_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training"""
        if not performance_data:
            return np.array([]), np.array([])
        
        # Convert to DataFrame
        df = pd.DataFrame(performance_data)
        
        # Calculate additional features
        df['percentage'] = (df['score'] / df['total_marks']) * 100
        df['subject_rank'] = df.groupby('subject')['percentage'].rank(ascending=False)
        
        # Create target variable (weak/strong classification)
        df['target'] = (df['percentage'] >= 70).astype(int)  # 70% threshold
        
        # Select features
        features = df[self.feature_names].values
        targets = df['target'].values
        
        return features, targets
    
    def train_models(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train multiple performance analysis models"""
        
        features, targets = self.prepare_data(performance_data)
        
        if len(features) == 0:
            return {"error": "No data available for training"}
        
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, targets, 
                test_size=self.config['test_size'],
                random_state=self.config['random_state']
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Initialize models
            self.models = {
                'logistic_regression': LogisticRegression(random_state=self.config['random_state']),
                'decision_tree': DecisionTreeClassifier(random_state=self.config['random_state']),
                'random_forest': RandomForestClassifier(random_state=self.config['random_state'], n_estimators=100)
            }
            
            # Train models
            results = {}
            for name, model in self.models.items():
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                
                accuracy = accuracy_score(y_test, y_pred)
                results[name] = {
                    'accuracy': accuracy,
                    'model': model,
                    'predictions': y_pred,
                    'true_values': y_test
                }
            
            self.is_trained = True
            return results
            
        except Exception as e:
            st.error(f"Error training models: {e}")
            return {"error": str(e)}
    
    def predict_performance(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict student performance classification"""
        
        if not self.is_trained:
            return {"error": "Models not trained yet"}
        
        try:
            # Prepare input features
            features = np.array([
                student_data.get('score', 0),
                student_data.get('total_marks', 100),
                (student_data.get('score', 0) / student_data.get('total_marks', 100)) * 100,
                student_data.get('subject_rank', 1)
            ]).reshape(1, -1)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get predictions from all models
            predictions = {}
            probabilities = {}
            
            for name, model_info in self.models.items():
                model = model_info['model']
                pred = model.predict(features_scaled)[0]
                prob = model.predict_proba(features_scaled)[0]
                
                predictions[name] = "Strong" if pred == 1 else "Weak"
                probabilities[name] = {
                    "Weak": prob[0],
                    "Strong": prob[1]
                }
            
            # Ensemble prediction (majority vote)
            ensemble_pred = "Strong" if sum(1 for p in predictions.values() if p == "Strong") >= 2 else "Weak"
            
            return {
                'predictions': predictions,
                'probabilities': probabilities,
                'ensemble_prediction': ensemble_pred,
                'confidence': max(probabilities['random_forest'].values())
            }
            
        except Exception as e:
            st.error(f"Error making prediction: {e}")
            return {"error": str(e)}
    
    def analyze_trends(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        
        if not performance_data:
            return {"error": "No performance data available"}
        
        try:
            df = pd.DataFrame(performance_data)
            df['date'] = pd.to_datetime(df.get('created_at', pd.Timestamp.now()))
            df['percentage'] = (df['score'] / df['total_marks']) * 100
            
            # Calculate trends
            trends = {
                'overall_average': df['percentage'].mean(),
                'subject_averages': df.groupby('subject')['percentage'].mean().to_dict(),
                'performance_trend': self._calculate_trend(df),
                'weakest_subjects': self._get_weakest_subjects(df),
                'strongest_subjects': self._get_strongest_subjects(df),
                'improvement_areas': self._identify_improvement_areas(df)
            }
            
            return trends
            
        except Exception as e:
            st.error(f"Error analyzing trends: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, df: pd.DataFrame) -> str:
        """Calculate overall performance trend"""
        if len(df) < 2:
            return "Insufficient data"
        
        # Sort by date and calculate trend
        df_sorted = df.sort_values('date')
        recent_avg = df_sorted.tail(5)['percentage'].mean()
        earlier_avg = df_sorted.head(5)['percentage'].mean()
        
        if recent_avg > earlier_avg + 5:
            return "Improving"
        elif recent_avg < earlier_avg - 5:
            return "Declining"
        else:
            return "Stable"
    
    def _get_weakest_subjects(self, df: pd.DataFrame, top_n: int = 3) -> List[str]:
        """Get weakest subjects based on average performance"""
        subject_avg = df.groupby('subject')['percentage'].mean()
        return subject_avg.nsmallest(top_n).index.tolist()
    
    def _get_strongest_subjects(self, df: pd.DataFrame, top_n: int = 3) -> List[str]:
        """Get strongest subjects based on average performance"""
        subject_avg = df.groupby('subject')['percentage'].mean()
        return subject_avg.nlargest(top_n).index.tolist()
    
    def _identify_improvement_areas(self, df: pd.DataFrame) -> List[str]:
        """Identify areas that need improvement"""
        improvement_areas = []
        
        # Subjects with low performance
        low_performance_subjects = self._get_weakest_subjects(df)
        improvement_areas.extend(low_performance_subjects)
        
        # Topics with consistent low scores
        topic_performance = df.groupby('topic')['percentage'].mean()
        low_performance_topics = topic_performance[topic_performance < 60].index.tolist()
        improvement_areas.extend(low_performance_topics[:3])  # Top 3
        
        return list(set(improvement_areas))  # Remove duplicates
    
    def generate_performance_report(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        if not performance_data:
            return {"error": "No performance data available"}
        
        try:
            # Train models
            training_results = self.train_models(performance_data)
            
            # Analyze trends
            trends = self.analyze_trends(performance_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(trends)
            
            report = {
                'training_results': training_results,
                'trends': trends,
                'recommendations': recommendations,
                'summary': self._create_summary(trends, recommendations)
            }
            
            return report
            
        except Exception as e:
            st.error(f"Error generating report: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on trends"""
        recommendations = []
        
        if 'weakest_subjects' in trends:
            for subject in trends['weakest_subjects']:
                recommendations.append(f"Focus on improving {subject} performance")
        
        if 'improvement_areas' in trends:
            for area in trends['improvement_areas'][:3]:
                recommendations.append(f"Practice more on {area} topics")
        
        if trends.get('performance_trend') == "Declining":
            recommendations.append("Consider reviewing study strategies")
        
        if trends.get('overall_average', 0) < 70:
            recommendations.append("Seek additional academic support")
        
        return recommendations
    
    def _create_summary(self, trends: Dict[str, Any], recommendations: List[str]) -> str:
        """Create a summary of the performance analysis"""
        summary = f"Overall Performance: {trends.get('overall_average', 0):.1f}%\n"
        summary += f"Trend: {trends.get('performance_trend', 'Unknown')}\n"
        summary += f"Strongest Subject: {trends.get('strongest_subjects', ['None'])[0]}\n"
        summary += f"Needs Improvement: {trends.get('weakest_subjects', ['None'])[0]}\n"
        summary += f"Key Recommendations: {len(recommendations)} areas identified"
        
        return summary
    
    def create_performance_visualizations(self, performance_data: List[Dict[str, Any]]) -> Dict[str, go.Figure]:
        """Create performance visualization charts"""
        
        if not performance_data:
            return {}
        
        try:
            df = pd.DataFrame(performance_data)
            df['percentage'] = (df['score'] / df['total_marks']) * 100
            
            visualizations = {}
            
            # Subject performance bar chart
            subject_avg = df.groupby('subject')['percentage'].mean().reset_index()
            fig_subject = px.bar(
                subject_avg, 
                x='subject', 
                y='percentage',
                title='Average Performance by Subject',
                labels={'percentage': 'Average Score (%)', 'subject': 'Subject'}
            )
            visualizations['subject_performance'] = fig_subject
            
            # Performance over time
            df['date'] = pd.to_datetime(df.get('created_at', pd.Timestamp.now()))
            df_sorted = df.sort_values('date')
            fig_trend = px.line(
                df_sorted, 
                x='date', 
                y='percentage',
                title='Performance Trend Over Time',
                labels={'percentage': 'Score (%)', 'date': 'Date'}
            )
            visualizations['performance_trend'] = fig_trend
            
            # Performance distribution histogram
            fig_dist = px.histogram(
                df, 
                x='percentage',
                title='Performance Distribution',
                labels={'percentage': 'Score (%)', 'count': 'Number of Tests'},
                nbins=20
            )
            visualizations['performance_distribution'] = fig_dist
            
            return visualizations
            
        except Exception as e:
            st.error(f"Error creating visualizations: {e}")
            return {}

# Global performance analyzer instance
@st.cache_resource
def get_performance_analyzer():
    """Get cached performance analyzer instance"""
    return PerformanceAnalyzer()






