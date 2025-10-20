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
            
            # Generate summary with proper parameters
            summary_result = self.summarizer(
                cleaned_text,
                max_new_tokens=max_len,
                min_length=min_len,
                do_sample=True,
                temperature=self.config.get('temperature', 0.7),
                num_return_sequences=1
            )
            
            summary_text = summary_result[0]['summary_text']
            
            # Post-process summary
            summary = self._postprocess_summary(summary_text)
            
            # Final length check and adjustment
            summary = self._ensure_proper_length(summary, max_len)
            
            return summary
            
        except Exception as e:
            st.error(f"Error during summarization: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess input text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove any non-printable or problematic characters
        text = re.sub(r'[^\w\s.,!?;:()\[\]"\'-]', ' ', text)
        text = re.sub(r'\s+', ' ', text)  # Clean up extra spaces again
        
        # Limit text length to avoid token limits (roughly 512 tokens for T5-small)
        max_chars = 2000
        if len(text) > max_chars:
            # Find the last complete sentence or at least a word boundary
            truncation_point = max_chars
            
            # Look for sentence endings first
            sentence_endings = ['.', '!', '?']
            for i in range(max_chars - 1, max(0, max_chars - 200), -1):
                if text[i] in sentence_endings and i < len(text) - 1 and text[i + 1] == ' ':
                    truncation_point = i + 1
                    break
            
            # If no sentence ending found, look for word boundary
            if truncation_point == max_chars:
                for i in range(max_chars - 1, max(0, max_chars - 100), -1):
                    if text[i] == ' ':
                        truncation_point = i
                        break
            
            text = text[:truncation_point].strip()
            if not text.endswith(('.', '!', '?')):
                text += "."
        
        return text
    
    def _postprocess_summary(self, summary: str) -> str:
        """Post-process generated summary"""
        # Clean up the summary
        summary = summary.strip()
        
        # Remove any incomplete or meaningless text at the end
        # Look for incomplete sentences or random characters
        words = summary.split()
        if words:
            # Remove the last word if it appears incomplete (less than 2 chars or contains numbers/symbols)
            last_word = words[-1]
            if (len(last_word) < 2 and not last_word in ['.', '!', '?']) or \
               re.search(r'[0-9]{3,}|[^\w\s.,!?;:()\[\]"\'-]', last_word):
                words = words[:-1]
            
            # Check for incomplete sentences - if last few words are fragment-like
            if len(words) > 3:
                last_few = ' '.join(words[-3:]).lower()
                # Common incomplete patterns
                incomplete_patterns = [
                    r'\b[a-z]\s[a-z]\s[a-z]$',  # Single letters
                    r'\bn\s+s\s+h\s*$',  # Fragmented characters
                    r'\b[a-z]{1,2}\s+[a-z]{1,2}\s*$'  # Very short fragments
                ]
                
                for pattern in incomplete_patterns:
                    if re.search(pattern, last_few):
                        # Remove the problematic ending
                        words = words[:-3]
                        break
            
            summary = ' '.join(words)
        
        # Remove any remaining problematic characters
        summary = re.sub(r'[^\w\s.,!?;:()\[\]"\'-]', '', summary)
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        # Ensure proper sentence ending
        if summary and not summary.endswith(('.', '!', '?')):
            summary += '.'
        
        # Capitalize first letter
        if summary:
            summary = summary[0].upper() + summary[1:]
        
        return summary
    
    def _ensure_proper_length(self, summary: str, max_length: int) -> str:
        """Ensure summary is within the specified length while preserving meaning"""
        if len(summary) <= max_length:
            return summary
            
        # Find the last complete sentence within the limit
        truncation_point = max_length - 3  # Leave room for ellipsis if needed
        
        # Look for sentence endings
        for i in range(truncation_point, max(0, truncation_point - 100), -1):
            if summary[i] in '.!?' and i < len(summary) - 1 and (i == len(summary) - 1 or summary[i + 1] == ' '):
                return summary[:i + 1]
        
        # If no sentence boundary found, truncate at word boundary
        for i in range(truncation_point, max(0, truncation_point - 50), -1):
            if summary[i] == ' ':
                return summary[:i] + "."
        
        # Last resort: hard truncate with proper ending
        return summary[:truncation_point] + "."
    
    def _mock_summarize(self, text: str, max_length: int = 150) -> str:
        """Mock summarization for development/demo purposes"""
        sentences = text.split('. ')
        
        # Take first few sentences as a simple summary
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences)
        
        # Ensure proper sentence ending
        if summary and not summary.endswith('.'):
            summary += '.'
        
        # Truncate if too long, but preserve sentence boundaries
        if len(summary) > max_length:
            # Find the last complete sentence within the limit
            truncation_point = max_length - 3
            for i in range(truncation_point, max(0, truncation_point - 100), -1):
                if summary[i] == '.' and i < len(summary) - 1:
                    summary = summary[:i + 1]
                    break
            else:
                # If no sentence boundary found, truncate at word boundary
                for i in range(truncation_point, max(0, truncation_point - 50), -1):
                    if summary[i] == ' ':
                        summary = summary[:i] + "."
                        break
                else:
                    summary = summary[:truncation_point] + "."
        
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
