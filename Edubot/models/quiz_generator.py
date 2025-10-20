from openai import OpenAI
import json
import streamlit as st
from config.settings import GPT_CONFIG, get_openai_api_key, is_openai_mock_enabled
from typing import List, Dict, Any
from utils.question_history import get_question_history_manager

class QuizGenerator:
    """GPT-3.5 based quiz generation model"""
    
    def __init__(self):
        self.config = GPT_CONFIG
        self.api_key = get_openai_api_key()
        
        if self.api_key:
            # Initialize OpenAI client with new API syntax
            self.client = OpenAI(api_key=self.api_key)
        else:
            st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
            self.client = None
    
    def generate_quiz_questions(self, topic: str, content: str = None, 
                              num_questions: int = 5, 
                              question_type: str = "multiple_choice") -> List[Dict[str, Any]]:
        """Generate quiz questions based on topic and content with history tracking"""
        
        # Get question history manager
        history_manager = get_question_history_manager()
        
        # Validate inputs
        if not topic or not topic.strip():
            return [{"error": "Topic is required"}]
        
        num_questions = max(1, min(int(num_questions), 10))
        
        try:
            # Generate initial questions
            if is_openai_mock_enabled():
                questions = self._mock_quiz(topic, content, num_questions, question_type)
            else:
                if not self.api_key or not self.client:
                    st.error("OpenAI API key not found. Please configure it in .env or Streamlit secrets.")
                    return [{"error": "OpenAI API key not configured"}]
                
                # Usage optimization: cap tokens
                max_tokens = max(128, min(int(self.config['max_tokens']), 800))

                # Generate multiple choice questions only
                prompt = self._create_multiple_choice_prompt(topic, content, num_questions)
                
                # Generate questions using GPT-3.5 with retry logic
                retries = 2
                for attempt in range(retries + 1):
                    try:
                        response = self.client.chat.completions.create(
                            model=self.config['model'],
                            messages=[
                                {"role": "system", "content": "You are an expert educational content creator. Generate high-quality quiz questions."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=max_tokens,
                            temperature=self.config['temperature']
                        )
                        break
                    except Exception as e:
                        message = str(e)
                        if "429" in message or "rate limit" in message.lower() or "quota" in message.lower():
                            import time
                            if attempt < retries:
                                time.sleep(1.5 * (attempt + 1))
                                continue
                        raise
                
                # Parse response
                questions_text = response.choices[0].message.content
                questions = self._parse_questions(questions_text, question_type)
            
            # Allow unlimited quiz generation - no uniqueness filtering
            # Students can take as many quizzes as they want on any topic
            final_questions = questions[:num_questions] if len(questions) >= num_questions else questions
            
            # If we don't have enough questions, generate more
            if len(final_questions) < num_questions:
                needed_questions = num_questions - len(final_questions)
                
                if is_openai_mock_enabled():
                    # For mock mode, create additional questions
                    additional_questions = self._generate_additional_mock_questions(topic, needed_questions, question_type)
                else:
                    # For real API, generate additional questions
                    additional_prompt = self._create_additional_questions_prompt(topic, content, needed_questions, question_type)
                    response = self.client.chat.completions.create(
                        model=self.config['model'],
                        messages=[
                            {"role": "system", "content": "You are an expert educational content creator. Generate high-quality quiz questions."},
                            {"role": "user", "content": additional_prompt}
                        ],
                        max_tokens=min(300, needed_questions * 80),
                        temperature=0.8  # Higher temperature for variety
                    )
                    additional_questions = self._parse_questions(response.choices[0].message.content, question_type)
                
                # Add the additional questions
                final_questions.extend(additional_questions[:needed_questions])
            
            # Take exactly the requested number of questions
            final_questions = final_questions[:num_questions]
            
            # Add questions to history for statistics (but don't limit future generation)
            history_manager.add_questions(topic, final_questions)
            
            # Add question numbers
            for i, question in enumerate(final_questions, 1):
                question['question_number'] = i
            
            return final_questions
            
        except Exception as e:
            # Handle common auth errors clearly
            message = str(e)
            if "invalid_api_key" in message or "Incorrect API key" in message:
                st.error("Invalid OpenAI API key. Please check OPENAI_API_KEY in .env or Streamlit secrets.")
            elif "429" in message or "rate limit" in message.lower() or "quota" in message.lower():
                st.warning("OpenAI rate limit or quota exceeded. Try again later, reduce question count, or enable mock mode by setting OPENAI_MOCK=1 in .env during development.")
            else:
                st.error(f"Error generating quiz questions: {e}")
            return [{"error": message}]

    def _mock_quiz(self, topic: str, content: str, num_questions: int, question_type: str = "multiple_choice") -> List[Dict[str, Any]]:
        """Return deterministic mock data for local testing without an API key."""
        questions: List[Dict[str, Any]] = []
        
        # Create diverse mock questions for different topics with more variety
        mock_questions = {
            "multiple_choice": [
                {
                    "question": f"What is the primary purpose of {topic}?",
                    "options": {
                        "A": f"To provide fundamental understanding of {topic} concepts",
                        "B": f"To implement advanced algorithms in {topic}",
                        "C": f"To solve complex problems using {topic}",
                        "D": f"To optimize performance in {topic} systems"
                    },
                    "correct_answer": "A",
                    "explanation": f"The primary purpose of {topic} is to provide fundamental understanding of its core concepts and principles."
                },
                {
                    "question": f"Which of the following is a key characteristic of {topic}?",
                    "options": {
                        "A": f"Scalability in {topic} applications",
                        "B": f"Efficiency in {topic} processing",
                        "C": f"Reliability in {topic} systems",
                        "D": f"All of the above are key characteristics"
                    },
                    "correct_answer": "D",
                    "explanation": f"All these characteristics - scalability, efficiency, and reliability - are essential in {topic} systems."
                },
                {
                    "question": f"What is the main advantage of using {topic}?",
                    "options": {
                        "A": f"Improved performance in {topic} operations",
                        "B": f"Better resource management in {topic}",
                        "C": f"Enhanced security in {topic} applications",
                        "D": f"All of the above advantages"
                    },
                    "correct_answer": "D",
                    "explanation": f"{topic} provides multiple advantages including improved performance, better resource management, and enhanced security."
                },
                {
                    "question": f"How does {topic} contribute to modern technology?",
                    "options": {
                        "A": f"By providing innovative solutions in {topic}",
                        "B": f"Through automation and efficiency in {topic}",
                        "C": f"By enabling data-driven decisions in {topic}",
                        "D": f"All of the above contributions"
                    },
                    "correct_answer": "D",
                    "explanation": f"{topic} contributes to modern technology through innovation, automation, and data-driven approaches."
                },
                {
                    "question": f"What are the core principles underlying {topic}?",
                    "options": {
                        "A": f"Modularity and reusability in {topic}",
                        "B": f"Scalability and performance in {topic}",
                        "C": f"Security and reliability in {topic}",
                        "D": f"All of the above principles"
                    },
                    "correct_answer": "D",
                    "explanation": f"The core principles of {topic} include modularity, scalability, security, and reliability."
                },
                {
                    "question": f"Which approach is most effective for learning {topic}?",
                    "options": {
                        "A": f"Hands-on practice with {topic}",
                        "B": f"Theoretical study of {topic} concepts",
                        "C": f"Combination of theory and practice",
                        "D": f"Memorization of {topic} facts"
                    },
                    "correct_answer": "C",
                    "explanation": f"Learning {topic} effectively requires both theoretical understanding and practical application."
                },
                {
                    "question": f"What challenges are commonly faced in {topic} implementation?",
                    "options": {
                        "A": f"Complexity and integration issues",
                        "B": f"Performance and scalability concerns",
                        "C": f"Security and maintenance challenges",
                        "D": f"All of the above challenges"
                    },
                    "correct_answer": "D",
                    "explanation": f"Common challenges in {topic} include complexity, performance, security, and maintenance issues."
                },
                {
                    "question": f"How has {topic} evolved in recent years?",
                    "options": {
                        "A": f"Through technological advancements",
                        "B": f"By adopting new methodologies",
                        "C": f"Through increased automation",
                        "D": f"All of the above developments"
                    },
                    "correct_answer": "D",
                    "explanation": f"{topic} has evolved through technological advancements, new methodologies, and increased automation."
                },
                {
                    "question": f"What role does {topic} play in industry applications?",
                    "options": {
                        "A": f"Enabling digital transformation",
                        "B": f"Improving operational efficiency",
                        "C": f"Supporting innovation and growth",
                        "D": f"All of the above roles"
                    },
                    "correct_answer": "D",
                    "explanation": f"{topic} plays a crucial role in digital transformation, efficiency improvement, and innovation support."
                },
                {
                    "question": f"What future trends are expected in {topic}?",
                    "options": {
                        "A": f"Artificial intelligence integration",
                        "B": f"Cloud-native architectures",
                        "C": f"Enhanced automation capabilities",
                        "D": f"All of the above trends"
                    },
                    "correct_answer": "D",
                    "explanation": f"Future trends in {topic} include AI integration, cloud-native approaches, and enhanced automation."
                }
            ]
        }
        
        # Generate questions dynamically to avoid running out
        available_questions = mock_questions["multiple_choice"]
        
        # Create additional question templates for more variety
        additional_templates = [
            {
                "question": f"What is the most critical factor in successful {topic} deployment?",
                "options": {
                    "A": f"Proper planning and strategy for {topic}",
                    "B": f"Skilled personnel and expertise in {topic}",
                    "C": f"Adequate resources and infrastructure for {topic}",
                    "D": f"All factors are equally critical"
                },
                "correct_answer": "D",
                "explanation": f"Successful {topic} deployment requires proper planning, skilled personnel, and adequate resources."
            },
            {
                "question": f"How does {topic} compare to traditional approaches?",
                "options": {
                    "A": f"{topic} offers better efficiency than traditional methods",
                    "B": f"{topic} provides more flexibility than traditional approaches",
                    "C": f"{topic} enables better scalability than traditional systems",
                    "D": f"{topic} offers advantages in all these areas"
                },
                "correct_answer": "D",
                "explanation": f"{topic} provides significant advantages over traditional approaches in efficiency, flexibility, and scalability."
            },
            {
                "question": f"What skills are essential for working with {topic}?",
                "options": {
                    "A": f"Technical knowledge of {topic} fundamentals",
                    "B": f"Problem-solving and analytical skills",
                    "C": f"Communication and collaboration abilities",
                    "D": f"All of these skills are essential"
                },
                "correct_answer": "D",
                "explanation": f"Working with {topic} requires technical knowledge, problem-solving skills, and communication abilities."
            },
            {
                "question": f"What impact does {topic} have on organizational productivity?",
                "options": {
                    "A": f"Increased efficiency in {topic} processes",
                    "B": f"Better decision-making through {topic} insights",
                    "C": f"Enhanced collaboration in {topic} teams",
                    "D": f"All of the above impacts"
                },
                "correct_answer": "D",
                "explanation": f"{topic} enhances organizational productivity through increased efficiency, better decision-making, and enhanced collaboration."
            },
            {
                "question": f"What are the key considerations for {topic} security?",
                "options": {
                    "A": f"Data protection and privacy in {topic}",
                    "B": f"Access control and authentication for {topic}",
                    "C": f"Compliance and regulatory requirements for {topic}",
                    "D": f"All of the above considerations"
                },
                "correct_answer": "D",
                "explanation": f"{topic} security requires attention to data protection, access control, and compliance requirements."
            }
        ]
        
        # Combine original and additional templates
        all_templates = available_questions + additional_templates
        
        # Generate unlimited questions with dynamic variations
        import random
        import time
        
        # Create even more question patterns for unlimited generation
        question_patterns = [
            f"What are the key aspects of {topic}?",
            f"How does {topic} work in practice?",
            f"Which factors influence {topic} implementation?",
            f"What role does {topic} play in modern technology?",
            f"How is {topic} typically implemented?",
            f"What are the main benefits of using {topic}?",
            f"What challenges commonly arise in {topic}?",
            f"How has {topic} evolved over time?",
            f"What are the practical applications of {topic}?",
            f"How can {topic} performance be optimized?",
            f"What makes {topic} effective?",
            f"How does {topic} compare to alternatives?",
            f"What skills are needed for {topic}?",
            f"How does {topic} impact business operations?",
            f"What are the security considerations in {topic}?",
            f"How is {topic} integrated with other systems?",
            f"What tools are commonly used with {topic}?",
            f"How do you troubleshoot {topic} issues?",
            f"What are the best practices for {topic}?",
            f"How do you measure {topic} success?"
        ]
        
        option_patterns = [
            f"Core principles and fundamentals of {topic}",
            f"Advanced techniques and methodologies in {topic}",
            f"Practical applications and real-world uses of {topic}",
            f"Industry standards and best practices for {topic}",
            f"Emerging trends and future developments in {topic}",
            f"Integration and compatibility aspects of {topic}",
            f"Performance optimization strategies in {topic}",
            f"Security and reliability considerations in {topic}",
            f"Cost-effectiveness and efficiency in {topic}",
            f"Scalability and maintenance of {topic} systems",
            f"Quality assurance and testing in {topic}",
            f"Documentation and training for {topic}",
            f"Monitoring and analytics for {topic}",
            f"Automation and workflow optimization in {topic}",
            f"Compliance and regulatory aspects of {topic}"
        ]
        
        for i in range(1, num_questions + 1):
            # Use time-based seed for more randomness across different generations
            random_seed = int(time.time() * 1000) + i
            random.seed(random_seed)
            
            base_index = (i - 1) % len(all_templates)
            
            # Create dynamic variations for unlimited generation
            if i > len(all_templates) or random.random() > 0.7:  # 30% chance to use template, 70% to create new
                # Generate completely new questions
                question_text = random.choice(question_patterns)
                
                # Create unique option sets
                available_options = option_patterns.copy()
                random.shuffle(available_options)
                
                unique_options = {
                    "A": available_options[0] if len(available_options) > 0 else f"Basic concepts of {topic}",
                    "B": available_options[1] if len(available_options) > 1 else f"Advanced techniques in {topic}",
                    "C": available_options[2] if len(available_options) > 2 else f"Practical applications of {topic}",
                    "D": f"All of the above aspects of {topic}"
                }
                
                variation_number = ((i - 1) // len(all_templates)) + 1
                mock_q = {
                    "question": f"{question_text} (Variation {variation_number})",
                    "options": unique_options,
                    "correct_answer": "D",
                    "explanation": f"This question covers multiple important aspects of {topic} including various concepts, techniques, and applications."
                }
            else:
                # Use base template
                base_q = all_templates[base_index]
                
                mock_q = base_q
                
            
            # Add multiple choice question
            questions.append({
                "question_number": i,
                "question_type": "multiple_choice",
                "question": mock_q["question"],
                "options": mock_q["options"],
                "correct_answer": mock_q["correct_answer"],
                "explanation": mock_q["explanation"]
            })
        return questions
    
    def _generate_additional_mock_questions(self, topic: str, num_questions: int, question_type: str = "multiple_choice") -> List[Dict[str, Any]]:
        """Generate additional mock questions with variations"""
        questions = []
        
        # Create more diverse variations
        variations = [
            f"Advanced {topic} Concepts",
            f"Practical {topic} Applications", 
            f"Industry {topic} Standards",
            f"Modern {topic} Trends",
            f"Real-world {topic} Scenarios",
            f"Emerging {topic} Technologies",
            f"Best Practices in {topic}",
            f"Common Pitfalls in {topic}",
            f"Future of {topic}",
            f"Integration of {topic} with Other Technologies"
        ]
        
        for i in range(num_questions):
            variation = variations[i % len(variations)]
            
            # Create unique questions for each variation
            question_templates = [
                f"What are the key aspects of {variation.lower()}?",
                f"How does {variation.lower()} impact modern technology?",
                f"What challenges are associated with {variation.lower()}?",
                f"What benefits does {variation.lower()} provide?",
                f"How is {variation.lower()} implemented in practice?"
            ]
            
            question_text = question_templates[i % len(question_templates)]
            

            
            questions.append({
                "question": f"{question_text}",
                "options": {
                    "A": f"Fundamental principles of {variation.lower()}",
                    "B": f"Advanced techniques in {variation.lower()}",
                    "C": f"Common challenges in {variation.lower()}",
                    "D": f"All of the above aspects"
                },
                "correct_answer": "D",
                "explanation": f"{variation} encompasses fundamental principles, advanced techniques, and common challenges."
            })
        
        return questions
    
    def _create_additional_questions_prompt(self, topic: str, content: str, num_questions: int, question_type: str = "multiple_choice") -> str:
        """Create prompt for generating additional unique questions"""
        prompt = f"""
        Generate {num_questions} ADDITIONAL, UNIQUE multiple choice questions about {topic}.
        
        {f'Use the following content as reference: {content[:1000]}' if content else ''}
        
        CRITICAL: These questions must be COMPLETELY DIFFERENT from any previous questions about {topic}.
        Focus on different aspects, subtopics, or perspectives of {topic}.
        
        IMPORTANT: Each question must follow this EXACT format:
        
        Q1. [Write a unique question about a different aspect of {topic}]
        A) [Complete, meaningful answer option]
        B) [Complete, meaningful answer option]
        C) [Complete, meaningful answer option]
        D) [Complete, meaningful answer option]
        Correct Answer: [Write the letter A, B, C, or D]
        Explanation: [Provide a clear explanation of why this answer is correct]
        
        Requirements:
        - Questions must be about DIFFERENT aspects of {topic} than previous questions
        - All 4 options must be complete sentences/phrases, NOT placeholders
        - Options should be plausible but clearly distinguishable
        - Only one option should be correct
        - Explanations should help students understand the concept
        - Vary difficulty and focus areas within {topic}
        """
        
        return prompt
    
    def _create_multiple_choice_prompt(self, topic: str, content: str, num_questions: int) -> str:
        """Create prompt for multiple choice questions"""
        prompt = f"""
        Generate {num_questions} UNIQUE, high-quality multiple choice questions specifically about {topic}.
        
        {f'Use the following content as reference: {content[:1000]}' if content else ''}
        
        CRITICAL REQUIREMENTS:
        - Each question must be UNIQUE and test different aspects of {topic}
        - NO duplicate questions or similar question patterns
        - Each question must be specifically relevant to {topic}
        - Cover different subtopics, concepts, and difficulty levels within {topic}
        
        IMPORTANT: Each question must follow this EXACT format:
        
        Q1. [Write a clear, specific question about {topic} - make it unique from other questions]
        A) [Write a complete, meaningful answer option - NOT a placeholder]
        B) [Write a complete, meaningful answer option - NOT a placeholder]
        C) [Write a complete, meaningful answer option - NOT a placeholder]
        D) [Write a complete, meaningful answer option - NOT a placeholder]
        Correct Answer: [Write the letter A, B, C, or D]
        Explanation: [Provide a clear explanation of why this answer is correct]
        
        Requirements:
        - Questions must be specific and test understanding of {topic}
        - All 4 options (A, B, C, D) must be complete sentences/phrases, NOT placeholders
        - Options should be plausible but clearly distinguishable
        - Only one option should be correct
        - Explanations should help students understand the concept
        - Vary difficulty from basic to advanced
        - Each question should test different knowledge areas within {topic}
        - NO repetition of question patterns or similar wording
        """
        return prompt
    
    def _create_short_answer_prompt(self, topic: str, content: str, num_questions: int) -> str:
        """Create prompt for short answer questions"""
        prompt = f"""
        Generate {num_questions} UNIQUE, high-quality short answer questions specifically about {topic}.
        
        {f'Use the following content as reference: {content[:1000]}' if content else ''}
        
        CRITICAL REQUIREMENTS:
        - Each question must be UNIQUE and test different aspects of {topic}
        - NO duplicate questions or similar question patterns
        - Each question must be specifically relevant to {topic}
        - Cover different subtopics, concepts, and difficulty levels within {topic}
        
        IMPORTANT: Each question must follow this EXACT format:
        
        Q1. [Write a clear, specific question that tests understanding of {topic} - make it unique from other questions]
        Expected Answer: [Provide a comprehensive, detailed answer]
        Key Points: [List 3-5 specific points that should be present in a good answer]
        
        Requirements:
        - Questions should test conceptual understanding, not just memorization
        - Expected answers should be detailed and educational
        - Key points should be specific and measurable
        - Questions should vary in complexity
        - Each question should test different knowledge areas within {topic}
        - NO repetition of question patterns or similar wording
        """
        return prompt
    
    def _parse_questions(self, questions_text: str, question_type: str = "multiple_choice") -> List[Dict[str, Any]]:
        """Parse generated questions into structured format (multiple choice only)"""
        questions = []
        
        try:
            # Split by question number
            question_blocks = questions_text.split('\nQ')
            
            for i, block in enumerate(question_blocks[1:], 1):  # Skip first empty block
                question_data = self._parse_multiple_choice_block(block.strip().split('\n'), i)
                if question_data:
                    questions.append(question_data)
            
        except Exception as e:
            st.error(f"Error parsing questions: {e}")
            questions.append({"error": f"Parsing error: {str(e)}"})
        
        return questions
    
    def _parse_multiple_choice_block(self, lines: List[str], question_num: int) -> Dict[str, Any]:
        """Parse multiple choice question block"""
        question_data = {
            "question_number": question_num,
            "question_type": "multiple_choice",
            "question": "",
            "options": {},
            "correct_answer": "",
            "explanation": ""
        }
        
        current_section = "question"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('A)') or line.startswith('A.'):
                current_section = "options"
                question_data["options"]["A"] = line[2:].strip()
            elif line.startswith('B)') or line.startswith('B.'):
                question_data["options"]["B"] = line[2:].strip()
            elif line.startswith('C)') or line.startswith('C.'):
                question_data["options"]["C"] = line[2:].strip()
            elif line.startswith('D)') or line.startswith('D.'):
                question_data["options"]["D"] = line[2:].strip()
            elif line.startswith('Correct Answer:') or line.startswith('Correct Answer'):
                answer_part = line.split(':', 1)[1] if ':' in line else line.split('Correct Answer', 1)[1]
                question_data["correct_answer"] = answer_part.strip()
            elif line.startswith('Explanation:') or line.startswith('Explanation'):
                explanation_part = line.split(':', 1)[1] if ':' in line else line.split('Explanation', 1)[1]
                question_data["explanation"] = explanation_part.strip()
            elif current_section == "question":
                question_data["question"] += line + " "
        
        question_data["question"] = question_data["question"].strip()
        
        # Validate that we have complete data
        if not question_data["question"]:
            question_data["error"] = f"Question {question_num}: Missing question text"
        elif len(question_data["options"]) < 4:
            question_data["error"] = f"Question {question_num}: Missing options (found {len(question_data['options'])}/4)"
        elif not question_data["correct_answer"]:
            question_data["error"] = f"Question {question_num}: Missing correct answer"
        elif not question_data["explanation"]:
            question_data["error"] = f"Question {question_num}: Missing explanation"
        
        return question_data
    
    def validate_quiz(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate generated quiz questions"""
        validation = {
            "total_questions": len(questions),
            "valid_questions": 0,
            "errors": [],
            "warnings": []
        }
        
        # Track questions for uniqueness validation
        question_texts = []
        option_sets = []
        
        for question in questions:
            if "error" in question:
                validation["errors"].append(question["error"])
                continue
            
            validation["valid_questions"] += 1
            
            # Check for missing fields
            if question.get("question_type") == "multiple_choice":
                if not question.get("options") or len(question["options"]) < 4:
                    validation["warnings"].append(f"Question {question['question_number']}: Missing options")
                if not question.get("correct_answer"):
                    validation["warnings"].append(f"Question {question['question_number']}: Missing correct answer")
                
                # Check for duplicate option sets
                options_text = "|".join(sorted(question.get("options", {}).values()))
                if options_text in option_sets:
                    validation["warnings"].append(f"Question {question['question_number']}: Duplicate option set detected")
                else:
                    option_sets.append(options_text)
            
            # Check for duplicate questions
            question_text = question.get("question", "").strip().lower()
            if question_text in question_texts:
                validation["warnings"].append(f"Question {question['question_number']}: Duplicate question detected")
            else:
                question_texts.append(question_text)
        
        return validation
    
    def ensure_question_uniqueness(self, questions: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Ensure all questions are unique by adding topic-specific variations"""
        import time
        import hashlib
        import random
        
        unique_questions = []
        seen_questions = set()
        variation_count = 0
        
        for i, question in enumerate(questions):
            # Create a unique identifier for the question
            question_text = question.get("question", "").strip().lower()
            
            # If we've seen this question before, add a variation
            if question_text in seen_questions:
                variation_count += 1
                
                # Add a variation to make it unique
                if question.get("question_type") == "multiple_choice":
                    # Create different variations
                    variations = [
                        f" (Advanced {topic} Concepts)",
                        f" (Practical {topic} Applications)",
                        f" (Industry {topic} Standards)",
                        f" (Modern {topic} Trends)",
                        f" (Real-world {topic} Scenarios)"
                    ]
                    
                    variation = variations[variation_count % len(variations)]
                    original_question = question["question"]
                    question["question"] = f"{original_question}{variation}"
                    
                    # Modify options to be more specific
                    new_options = {}
                    for key, value in question["options"].items():
                        new_options[key] = f"{value} in {topic} context"
                    question["options"] = new_options
                    
                    # Update explanation
                    question["explanation"] = f"{question['explanation']} This is particularly relevant in {topic} applications."
                else:
                    # For short answer questions
                    variation = f" (Advanced {topic} Concepts)"
                    question["question"] = f"{question['question']}{variation}"
                    question["expected_answer"] = f"{question['expected_answer']} Advanced applications include more sophisticated implementations."
                    question["key_points"] = f"{question['key_points']}; Advanced concepts; Complex implementations"
            
            seen_questions.add(question_text)
            unique_questions.append(question)
        
        return unique_questions
    
    def get_question_history_stats(self, topic: str = None) -> Dict[str, Any]:
        """Get question history statistics"""
        history_manager = get_question_history_manager()
        
        if topic:
            return history_manager.get_topic_stats(topic)
        else:
            all_topics = history_manager.get_all_topics()
            total_questions = sum(history_manager.get_topic_stats(t)['total_questions_served'] for t in all_topics)
            return {
                "total_topics": len(all_topics),
                "total_questions_served": total_questions,
                "topics": all_topics
            }
    
    def clear_question_history(self, topic: str = None):
        """Clear question history for a topic or all topics"""
        history_manager = get_question_history_manager()
        
        if topic:
            history_manager.clear_topic_history(topic)
        else:
            history_manager.clear_all_history()
    
    def reset_topic_limits(self, topic: str = None):
        """Reset any topic limits to allow unlimited quiz generation"""
        # This function ensures unlimited quiz generation
        # by clearing any restrictions that might prevent quiz generation
        if topic:
            self.clear_question_history(topic)
        else:
            self.clear_question_history()
        
        # Note: With the new unlimited generation system,
        # this function is mainly for backwards compatibility
    
    def score_quiz(self, questions: List[Dict[str, Any]], user_answers: Dict[int, str], topic: str = None) -> Dict[str, Any]:
        """Score a quiz based on user answers"""
        total_questions = len(questions)
        correct_answers = 0
        results = []
        
        for question in questions:
            question_num = question.get("question_number", 0)
            user_answer = user_answers.get(question_num, "")
            correct_answer = question.get("correct_answer", "")
            
            is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
            if is_correct:
                correct_answers += 1
            
            results.append({
                "question_number": question_num,
                "question": question.get("question", ""),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", "")
            })
        
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        score_result = {
            "score": correct_answers,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "incorrect_answers": total_questions - correct_answers,
            "percentage": round(percentage, 1),
            "results": results,
            "quiz_type": questions[0].get('question_type', 'unknown') if questions else 'unknown'
        }
        
        # Add quiz result to history if topic is provided
        if topic:
            history_manager = get_question_history_manager()
            history_manager.add_quiz_result(topic, score_result)
        
        return score_result

# Global quiz generator instance
@st.cache_resource
def get_quiz_generator(_version: int = 8):
    """Get cached quiz generator instance. _version bumps invalidate old cache."""
    return QuizGenerator()

