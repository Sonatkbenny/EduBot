import PyPDF2
import streamlit as st
from typing import List, Dict, Any
import io
import re

class FileProcessor:
    """Process uploaded PDF and TXT files"""
    
    def __init__(self):
        self.supported_formats = ['pdf', 'txt']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def process_uploaded_file(self, uploaded_file) -> Dict[str, Any]:
        """Process a single uploaded file"""
        
        if uploaded_file is None:
            return {"error": "No file uploaded"}
        
        try:
            # Check file size
            if uploaded_file.size > self.max_file_size:
                return {"error": f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"}
            
            # Get file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension not in self.supported_formats:
                return {"error": f"Unsupported file format. Supported formats: {', '.join(self.supported_formats)}"}
            
            # Process based on file type
            if file_extension == 'pdf':
                return self._process_pdf_file(uploaded_file)
            elif file_extension == 'txt':
                return self._process_txt_file(uploaded_file)
            
        except Exception as e:
            return {"error": f"Error processing file: {str(e)}"}
    
    def _process_pdf_file(self, uploaded_file) -> Dict[str, Any]:
        """Extract text from PDF file"""
        try:
            # Read PDF file
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            
            # Extract text from all pages
            text_content = ""
            total_pages = len(pdf_reader.pages)
            
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            # Clean and process text
            cleaned_text = self._clean_text(text_content)
            
            return {
                "filename": uploaded_file.name,
                "file_type": "pdf",
                "total_pages": total_pages,
                "raw_text": text_content,
                "cleaned_text": cleaned_text,
                "word_count": len(cleaned_text.split()),
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Error processing PDF: {str(e)}"}
    
    def _process_txt_file(self, uploaded_file) -> Dict[str, Any]:
        """Process TXT file"""
        try:
            # Read text content
            text_content = uploaded_file.read().decode('utf-8')
            
            # Clean and process text
            cleaned_text = self._clean_text(text_content)
            
            return {
                "filename": uploaded_file.name,
                "file_type": "txt",
                "total_pages": 1,
                "raw_text": text_content,
                "cleaned_text": cleaned_text,
                "word_count": len(cleaned_text.split()),
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Error processing TXT file: {str(e)}"}
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_sections(self, text: str, max_section_length: int = 1000) -> List[str]:
        """Split text into manageable sections for processing"""
        if not text:
            return []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        sections = []
        current_section = ""
        
        for paragraph in paragraphs:
            if len(current_section) + len(paragraph) < max_section_length:
                current_section += paragraph + "\n\n"
            else:
                if current_section:
                    sections.append(current_section.strip())
                current_section = paragraph + "\n\n"
        
        # Add the last section
        if current_section:
            sections.append(current_section.strip())
        
        return sections
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract key terms from text"""
        if not text:
            return []
        
        # Simple keyword extraction (can be enhanced with NLP libraries)
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]
    
    def validate_file_content(self, text: str) -> Dict[str, Any]:
        """Validate file content for processing"""
        validation = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        if not text:
            validation["is_valid"] = False
            validation["errors"].append("File is empty")
            return validation
        
        # Check minimum content length
        if len(text.split()) < 10:
            validation["warnings"].append("File content seems too short for meaningful analysis")
        
        # Check for common issues
        if len(text) > 50000:
            validation["warnings"].append("File is very large and may take time to process")
        
        # Check for non-English content (simple heuristic)
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[a-zA-Z0-9]', text))
        
        if total_chars > 0 and english_chars / total_chars < 0.5:
            validation["warnings"].append("File may contain non-English content")
        
        return validation
    
    def get_file_statistics(self, processed_file: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about processed file"""
        if not processed_file.get("success"):
            return {"error": "File not processed successfully"}
        
        text = processed_file.get("cleaned_text", "")
        
        stats = {
            "filename": processed_file.get("filename", ""),
            "file_type": processed_file.get("file_type", ""),
            "total_pages": processed_file.get("total_pages", 0),
            "word_count": len(text.split()),
            "character_count": len(text),
            "paragraph_count": len(text.split('\n\n')),
            "sentence_count": len(text.split('.')),
            "average_words_per_sentence": len(text.split()) / max(len(text.split('.')), 1),
            "keywords": self.extract_keywords(text, top_n=5)
        }
        
        return stats

# Global file processor instance
@st.cache_resource
def get_file_processor():
    """Get cached file processor instance"""
    return FileProcessor()






