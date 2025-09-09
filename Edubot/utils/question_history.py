"""
Question History Management System
Ensures unique questions across sessions and quiz attempts
"""

import json
import os
from typing import List, Dict, Any, Set
from datetime import datetime
import hashlib

class QuestionHistoryManager:
    """Manages question history to ensure uniqueness across sessions"""
    
    def __init__(self, history_file: str = "question_history.json"):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> Dict[str, Dict[str, Any]]:
        """Load question history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_history(self):
        """Save question history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save question history: {e}")
    
    def _generate_question_hash(self, question_text: str, topic: str) -> str:
        """Generate a unique hash for a question"""
        # Normalize the question text for consistent hashing
        normalized_text = question_text.strip().lower()
        # Remove extra whitespace and normalize
        normalized_text = ' '.join(normalized_text.split())
        return hashlib.md5(f"{topic}_{normalized_text}".encode()).hexdigest()
    
    def add_questions(self, topic: str, questions: List[Dict[str, Any]]):
        """Add questions to history for a topic"""
        if topic not in self.history:
            self.history[topic] = {
                "question_hashes": set(),
                "question_count": 0,
                "last_updated": datetime.now().isoformat(),
                "total_questions_served": 0,
                "quiz_results": []
            }
        
        topic_history = self.history[topic]
        added_count = 0
        
        for question in questions:
            question_text = question.get('question', '')
            if question_text:
                question_hash = self._generate_question_hash(question_text, topic)
                
                # Convert set to list for JSON serialization
                if isinstance(topic_history["question_hashes"], set):
                    topic_history["question_hashes"] = list(topic_history["question_hashes"])
                
                if question_hash not in topic_history["question_hashes"]:
                    topic_history["question_hashes"].append(question_hash)
                    added_count += 1
        
        topic_history["question_count"] = len(topic_history["question_hashes"])
        topic_history["total_questions_served"] += added_count
        topic_history["last_updated"] = datetime.now().isoformat()
        
        self._save_history()
        return added_count
    
    def add_quiz_result(self, topic: str, quiz_result: Dict[str, Any]):
        """Add quiz result to history for a topic"""
        if topic not in self.history:
            self.history[topic] = {
                "question_hashes": [],
                "question_count": 0,
                "last_updated": datetime.now().isoformat(),
                "total_questions_served": 0,
                "quiz_results": []
            }
        
        topic_history = self.history[topic]
        
        # Ensure quiz_results is a list
        if "quiz_results" not in topic_history:
            topic_history["quiz_results"] = []
        
        # Add quiz result with timestamp
        quiz_result_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            "score": quiz_result.get("score", 0),
            "total_questions": quiz_result.get("total_questions", 0),
            "correct_answers": quiz_result.get("correct_answers", 0),
            "percentage": quiz_result.get("percentage", 0.0),
            "quiz_type": quiz_result.get("quiz_type", "unknown")
        }
        
        topic_history["quiz_results"].append(quiz_result_with_timestamp)
        topic_history["last_updated"] = datetime.now().isoformat()
        
        self._save_history()
    
    def get_used_question_hashes(self, topic: str) -> Set[str]:
        """Get all used question hashes for a topic"""
        if topic not in self.history:
            return set()
        
        question_hashes = self.history[topic].get("question_hashes", [])
        return set(question_hashes) if question_hashes else set()
    
    def is_question_used(self, topic: str, question_text: str) -> bool:
        """Check if a question has been used before for a topic"""
        question_hash = self._generate_question_hash(question_text, topic)
        used_hashes = self.get_used_question_hashes(topic)
        return question_hash in used_hashes
    
    def filter_unique_questions(self, topic: str, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out questions that have been used before for a topic"""
        used_hashes = self.get_used_question_hashes(topic)
        unique_questions = []
        
        for question in questions:
            question_text = question.get('question', '')
            if question_text:
                question_hash = self._generate_question_hash(question_text, topic)
                if question_hash not in used_hashes:
                    unique_questions.append(question)
        
        return unique_questions
    
    def get_topic_stats(self, topic: str) -> Dict[str, Any]:
        """Get statistics for a topic"""
        if topic not in self.history:
            return {
                "total_questions_served": 0,
                "unique_questions_available": 0,
                "last_updated": None,
                "total_quizzes_taken": 0,
                "average_score": 0.0,
                "best_score": 0.0,
                "quiz_results": []
            }
        
        topic_history = self.history[topic]
        quiz_results = topic_history.get("quiz_results", [])
        
        # Calculate quiz statistics
        total_quizzes = len(quiz_results)
        average_score = 0.0
        best_score = 0.0
        
        if quiz_results:
            total_percentage = sum(result.get("percentage", 0) for result in quiz_results)
            average_score = total_percentage / total_quizzes
            best_score = max(result.get("percentage", 0) for result in quiz_results)
        
        return {
            "total_questions_served": topic_history.get("total_questions_served", 0),
            "unique_questions_available": topic_history.get("question_count", 0),
            "last_updated": topic_history.get("last_updated"),
            "total_quizzes_taken": total_quizzes,
            "average_score": round(average_score, 1),
            "best_score": round(best_score, 1),
            "quiz_results": quiz_results
        }
    
    def get_all_topics(self) -> List[str]:
        """Get all topics that have question history"""
        return list(self.history.keys())
    
    def clear_topic_history(self, topic: str):
        """Clear history for a specific topic"""
        if topic in self.history:
            del self.history[topic]
            self._save_history()
    
    def clear_all_history(self):
        """Clear all question history"""
        self.history = {}
        self._save_history()

# Global instance
_question_history_manager = None

def get_question_history_manager() -> QuestionHistoryManager:
    """Get the global question history manager instance"""
    global _question_history_manager
    if _question_history_manager is None:
        _question_history_manager = QuestionHistoryManager()
    return _question_history_manager
