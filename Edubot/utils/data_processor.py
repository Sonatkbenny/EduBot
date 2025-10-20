import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import streamlit as st
from datetime import datetime
import json

class DataProcessor:
    """Data processing and preprocessing utilities"""
    
    def __init__(self):
        self.data_types = {
            'performance': 'performance_data',
            'quiz': 'quiz_data', 
            'summary': 'summary_data',
            'recommendation': 'recommendation_data'
        }
    
    def validate_performance_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate performance data entries"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "valid_entries": 0,
            "total_entries": len(data)
        }
        
        for i, entry in enumerate(data):
            # Check required fields
            required_fields = ['subject', 'topic', 'score', 'total_marks']
            missing_fields = [field for field in required_fields if field not in entry]
            
            if missing_fields:
                validation["errors"].append(f"Entry {i+1}: Missing fields {missing_fields}")
                continue
            
            # Validate score and total_marks
            try:
                score = float(entry['score'])
                total_marks = float(entry['total_marks'])
                
                if score < 0 or total_marks <= 0:
                    validation["errors"].append(f"Entry {i+1}: Invalid score values")
                    continue
                
                if score > total_marks:
                    validation["errors"].append(f"Entry {i+1}: Score cannot exceed total marks")
                    continue
                
                # Calculate percentage
                percentage = (score / total_marks) * 100
                
                if percentage < 30:
                    validation["warnings"].append(f"Entry {i+1}: Very low performance ({percentage:.1f}%)")
                elif percentage > 100:
                    validation["errors"].append(f"Entry {i+1}: Percentage exceeds 100%")
                    continue
                
                validation["valid_entries"] += 1
                
            except (ValueError, TypeError):
                validation["errors"].append(f"Entry {i+1}: Invalid numeric values")
                continue
        
        validation["is_valid"] = len(validation["errors"]) == 0
        return validation
    
    def clean_performance_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and standardize performance data"""
        cleaned_data = []
        
        for entry in data:
            try:
                cleaned_entry = {
                    'subject': str(entry.get('subject', '')).strip().title(),
                    'topic': str(entry.get('topic', '')).strip().title(),
                    'score': float(entry.get('score', 0)),
                    'total_marks': float(entry.get('total_marks', 100)),
                    'created_at': entry.get('created_at', datetime.now().isoformat())
                }
                
                # Calculate additional fields
                cleaned_entry['percentage'] = (cleaned_entry['score'] / cleaned_entry['total_marks']) * 100
                cleaned_entry['grade'] = self._calculate_grade(cleaned_entry['percentage'])
                
                cleaned_data.append(cleaned_entry)
                
            except Exception as e:
                st.warning(f"Skipping invalid entry: {e}")
                continue
        
        return cleaned_data
    
    def _calculate_grade(self, percentage: float) -> str:
        """Calculate letter grade based on percentage"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'
    
    def aggregate_performance_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate performance data for analysis"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        
        # Overall statistics
        overall_stats = {
            'total_tests': len(df),
            'average_percentage': df['percentage'].mean(),
            'highest_percentage': df['percentage'].max(),
            'lowest_percentage': df['percentage'].min(),
            'standard_deviation': df['percentage'].std()
        }
        
        # Subject-wise statistics
        subject_stats = df.groupby('subject').agg({
            'percentage': ['mean', 'count', 'std'],
            'score': 'sum',
            'total_marks': 'sum'
        }).round(2)
        
        # Topic-wise statistics
        topic_stats = df.groupby('topic').agg({
            'percentage': ['mean', 'count'],
            'score': 'sum',
            'total_marks': 'sum'
        }).round(2)
        
        # Grade distribution
        grade_distribution = df['grade'].value_counts().to_dict()
        
        return {
            'overall_stats': overall_stats,
            'subject_stats': subject_stats.to_dict(),
            'topic_stats': topic_stats.to_dict(),
            'grade_distribution': grade_distribution
        }
    
    def prepare_quiz_data(self, quiz_questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare quiz data for storage and analysis"""
        if not quiz_questions:
            return {}
        
        processed_quiz = {
            'total_questions': len(quiz_questions),
            'question_types': {},
            'questions': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'difficulty_level': 'mixed'
            }
        }
        
        for i, question in enumerate(quiz_questions):
            if 'error' in question:
                continue
            
            processed_question = {
                'question_id': i + 1,
                'question_type': question.get('question_type', 'unknown'),
                'question_text': question.get('question', ''),
                'options': question.get('options', {}),
                'correct_answer': question.get('correct_answer', ''),
                'explanation': question.get('explanation', ''),
                'expected_answer': question.get('expected_answer', ''),
                'key_points': question.get('key_points', '')
            }
            
            processed_quiz['questions'].append(processed_question)
            
            # Count question types
            q_type = processed_question['question_type']
            processed_quiz['question_types'][q_type] = processed_quiz['question_types'].get(q_type, 0) + 1
        
        return processed_quiz
    
    def prepare_summary_data(self, original_text: str, summary: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare summary data for storage"""
        return {
            'original_text': original_text[:1000],  # Truncate for storage
            'summary': summary,
            'metadata': {
                'original_length': len(original_text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(original_text) if original_text else 0,
                'created_at': datetime.now().isoformat(),
                **metadata
            }
        }
    
    def export_data(self, data: Any, format_type: str = 'json') -> str:
        """Export data in specified format"""
        try:
            if format_type == 'json':
                return json.dumps(data, indent=2, default=str)
            elif format_type == 'csv':
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    return df.to_csv(index=False)
                else:
                    return pd.DataFrame([data]).to_csv(index=False)
            else:
                return str(data)
        except Exception as e:
            return f"Error exporting data: {str(e)}"
    
    def import_data(self, data_string: str, format_type: str = 'json') -> Any:
        """Import data from specified format"""
        try:
            if format_type == 'json':
                return json.loads(data_string)
            elif format_type == 'csv':
                return pd.read_csv(data_string).to_dict('records')
            else:
                return data_string
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
            return None
    
    def generate_sample_data(self, data_type: str, num_samples: int = 10) -> List[Dict[str, Any]]:
        """Generate sample data for testing"""
        
        if data_type == 'performance':
            subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science']
            topics = ['Algebra', 'Calculus', 'Mechanics', 'Thermodynamics', 'Organic Chemistry', 
                     'Cell Biology', 'Programming', 'Data Structures']
            
            sample_data = []
            for i in range(num_samples):
                subject = np.random.choice(subjects)
                topic = np.random.choice(topics)
                total_marks = np.random.choice([50, 100, 150, 200])
                score = np.random.randint(int(total_marks * 0.3), int(total_marks * 0.95))
                
                sample_data.append({
                    'subject': subject,
                    'topic': topic,
                    'score': score,
                    'total_marks': total_marks,
                    'created_at': datetime.now().isoformat()
                })
            
            return sample_data
        
        elif data_type == 'quiz':
            # Generate sample quiz questions
            sample_questions = []
            for i in range(num_samples):
                question = {
                    'question_number': i + 1,
                    'question_type': 'multiple_choice',
                    'question': f'Sample question {i + 1}?',
                    'options': {
                        'A': f'Option A for question {i + 1}',
                        'B': f'Option B for question {i + 1}',
                        'C': f'Option C for question {i + 1}',
                        'D': f'Option D for question {i + 1}'
                    },
                    'correct_answer': 'A',
                    'explanation': f'Explanation for question {i + 1}'
                }
                sample_questions.append(question)
            
            return sample_questions
        
        else:
            return []
    
    def validate_data_schema(self, data: Any, expected_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against expected schema"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not isinstance(data, type(expected_schema)):
            validation["errors"].append(f"Data type mismatch. Expected {type(expected_schema)}, got {type(data)}")
            validation["is_valid"] = False
            return validation
        
        if isinstance(expected_schema, dict):
            for key, expected_type in expected_schema.items():
                if key not in data:
                    validation["errors"].append(f"Missing required key: {key}")
                elif not isinstance(data[key], expected_type):
                    validation["warnings"].append(f"Type mismatch for key {key}. Expected {expected_type}, got {type(data[key])}")
        
        validation["is_valid"] = len(validation["errors"]) == 0
        return validation

# Global data processor instance
@st.cache_resource
def get_data_processor():
    """Get cached data processor instance"""
    return DataProcessor()






