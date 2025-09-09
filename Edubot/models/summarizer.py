from transformers import pipeline
import streamlit as st
from config.settings import T5_MODEL_CONFIG
from typing import Dict, Any
import re

class TextSummarizer:
    """T5-based text summarization model"""
    
    def __init__(self):
        self.config = T5_MODEL_CONFIG
        self.summarizer = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the summarization model"""
        try:
            # Use T5 model for summarization
            self.summarizer = pipeline(
                "summarization",
                model=self.config['model_name'],
                tokenizer=self.config['model_name']
            )
            st.success("✅ Summarization model loaded successfully")
        except Exception as e:
            st.error(f"❌ Error loading summarization model: {e}")
            # Fallback to mock summarizer for development
            self.summarizer = None
    
    def summarize(self, text: str, max_length: int = None, min_length: int = None) -> str:
        """Generate summary from input text"""
        
        if not text or not text.strip():
            return "Error: No text provided for summarization"
        
        # Use provided lengths or defaults
        max_len = max_length or self.config.get('max_length', 150)
        min_len = min_length or self.config.get('min_length', 50)
        
        # Ensure min_len is less than max_len
        if min_len >= max_len:
            min_len = max_len - 10
        
        try:
            if self.summarizer is None:
                # Mock summarization for development/demo
                return self._mock_summarize(text, max_len)
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # T5 requires "summarize: " prefix
            if not cleaned_text.startswith("summarize:"):
                cleaned_text = "summarize: " + cleaned_text
            
            # Generate summary
            summary_result = self.summarizer(
                cleaned_text,
                max_length=max_len,
                min_length=min_len,
                do_sample=True,
                temperature=self.config.get('temperature', 0.7)
            )
            
            summary_text = summary_result[0]['summary_text']
            
            # Post-process summary
            summary = self._postprocess_summary(summary_text)
            
            return summary
            
        except Exception as e:
            st.error(f"Error during summarization: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess input text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Limit text length to avoid token limits (roughly 512 tokens for T5-small)
        max_chars = 2000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    
    def _postprocess_summary(self, summary: str) -> str:
        """Post-process generated summary"""
        # Clean up the summary
        summary = summary.strip()
        
        # Ensure proper sentence ending
        if summary and not summary.endswith('.'):
            summary += '.'
        
        # Capitalize first letter
        if summary:
            summary = summary[0].upper() + summary[1:]
        
        return summary
    
    def _mock_summarize(self, text: str, max_length: int = 150) -> str:
        """Mock summarization for development/demo purposes"""
        sentences = text.split('. ')
        
        # Take first few sentences as a simple summary
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
    
    def get_summary_stats(self, original_text: str, summary: str) -> Dict[str, Any]:
        """Get statistics about the summarization"""
        original_words = len(original_text.split())
        summary_words = len(summary.split())
        
        compression_ratio = (original_words - summary_words) / original_words if original_words > 0 else 0
        
        return {
            'original_word_count': original_words,
            'summary_word_count': summary_words,
            'compression_ratio': round(compression_ratio * 100, 1),
            'original_char_count': len(original_text),
            'summary_char_count': len(summary)
        }

# Global instance
_summarizer_instance = None

def get_summarizer():
    """Get global summarizer instance"""
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = TextSummarizer()
    return _summarizer_instance
