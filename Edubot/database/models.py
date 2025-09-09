from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

@dataclass
class User:
    """User model"""
    id: Optional[int]
    username: str
    email: str
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=data.get('id'),
            username=data['username'],
            email=data['email'],
            created_at=datetime.fromisoformat(data['created_at'])
        )

@dataclass
class Document:
    """Document model for storing uploaded files and summaries"""
    id: Optional[int]
    user_id: int
    filename: str
    content: str
    summary: Optional[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'content': self.content,
            'summary': self.summary,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            filename=data['filename'],
            content=data['content'],
            summary=data.get('summary'),
            created_at=datetime.fromisoformat(data['created_at'])
        )

@dataclass
class Quiz:
    """Quiz model for storing generated quizzes"""
    id: Optional[int]
    user_id: int
    topic: str
    questions: List[Dict[str, Any]]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'questions': self.questions,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quiz':
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            topic=data['topic'],
            questions=data['questions'] if isinstance(data['questions'], list) else json.loads(data['questions']),
            created_at=datetime.fromisoformat(data['created_at'])
        )

@dataclass
class Performance:
    """Performance model for storing student performance data"""
    id: Optional[int]
    user_id: int
    subject: str
    topic: str
    score: float
    total_marks: float
    classification: Optional[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'topic': self.topic,
            'score': self.score,
            'total_marks': self.total_marks,
            'classification': self.classification,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Performance':
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            subject=data['subject'],
            topic=data['topic'],
            score=float(data['score']),
            total_marks=float(data['total_marks']),
            classification=data.get('classification'),
            created_at=datetime.fromisoformat(data['created_at'])
        )

@dataclass
class Recommendation:
    """Recommendation model for storing personalized recommendations"""
    id: Optional[int]
    user_id: int
    topic: str
    resource_type: str
    resource_url: str
    title: str
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'resource_type': self.resource_type,
            'resource_url': self.resource_url,
            'title': self.title,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recommendation':
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            topic=data['topic'],
            resource_type=data['resource_type'],
            resource_url=data['resource_url'],
            title=data['title'],
            created_at=datetime.fromisoformat(data['created_at'])
        )

@dataclass
class UserProfile:
    """User profile model for storing user preferences and interests"""
    user_id: int
    interests: List[str]
    weak_topics: List[str]
    learning_style: str
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'interests': self.interests,
            'weak_topics': self.weak_topics,
            'learning_style': self.learning_style,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        return cls(
            user_id=data['user_id'],
            interests=data['interests'] if isinstance(data['interests'], list) else json.loads(data['interests']),
            weak_topics=data['weak_topics'] if isinstance(data['weak_topics'], list) else json.loads(data['weak_topics']),
            learning_style=data['learning_style'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )



