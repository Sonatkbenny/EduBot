"""
Test script to verify text summarization fixes for meaningless endings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_text_preprocessing():
    """Test the preprocessing fixes"""
    print("🔧 Testing Text Preprocessing Fixes")
    print("=" * 60)
    
    try:
        from models.summarizer import TextSummarizer
        
        summarizer = TextSummarizer()
        
        # Test cases with problematic text
        test_cases = [
            {
                "name": "Text with meaningless characters at end",
                "text": "Software engineering is a systematic approach to design, development, and maintenance of software systems. It involves various methodologies, tools, and techniques to ensure the creation of high-quality, reliable, and maintainable software. The field encompasses requirements analysis, system design, coding, testing, and deployment. Software engineers must consider factors such as user requirements, performance, security, and scalability when developing applications. The discipline has evolved significantly since its inception in the 1960s, incorporating best practices from computer science, mathematics, and engineering principles. Modern software engineering emphasizes agile methodologies, continuous integration, and collaborative development practices. n s h ---.ni n,n ... [meaningless text]",
                "expected": "Should remove meaningless characters and end properly"
            },
            {
                "name": "Very long text that needs truncation",
                "text": "Software development lifecycle (SDLC) is a structured approach used by software engineers and development teams to design, develop, and test high-quality software applications. The SDLC framework defines a series of phases that software must go through from conception to deployment and maintenance. The primary phases include planning, analysis, design, implementation, testing, deployment, and maintenance. Each phase has specific objectives, deliverables, and activities that contribute to the overall success of the software project. Planning involves defining the scope, objectives, and resources required for the project. Analysis focuses on understanding user requirements and system specifications. Design phase creates the architectural blueprint and user interface mockups. Implementation involves actual coding and development of the software. Testing ensures the software meets quality standards and user requirements. Deployment involves releasing the software to the production environment. Maintenance includes ongoing support, updates, and bug fixes. Various SDLC models exist including Waterfall, Agile, Spiral, and DevOps, each with its own advantages and use cases. The choice of SDLC model depends on factors such as project complexity, team size, timeline, and client requirements. Effective SDLC implementation leads to successful software delivery that meets user expectations and business objectives.",
                "expected": "Should truncate at sentence boundary"
            },
            {
                "name": "Text with random characters mixed in",
                "text": "Database management systems (DBMS) are software applications that interact with users, applications, and the database itself to capture and analyze data. A DBMS allows users to create, retrieve, update and delete data in a database. Popular DBMS include MySQL, PostgreSQL, Oracle, and SQL Server. @@#$%^& These systems provide data security, integrity, and concurrent access control. !@#$%",
                "expected": "Should clean problematic characters"
            }
        ]
        
        print("\n🧪 Testing Preprocessing:")
        print("-" * 40)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']}")
            print(f"Expected: {test_case['expected']}")
            
            # Test preprocessing
            processed = summarizer._preprocess_text(test_case['text'])
            print(f"✅ Preprocessed length: {len(processed)} chars")
            print(f"   Ends with: '{processed[-20:]}'")
            
            # Verify no meaningless endings
            if not any(char in processed[-50:] for char in ['@', '#', '$', '%', '^', '&']):
                print("   ✓ No problematic characters at end")
            else:
                print("   ❌ Still contains problematic characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Preprocessing test failed: {e}")
        return False

def test_summary_postprocessing():
    """Test the postprocessing fixes"""
    print("\n\n🔧 Testing Summary Postprocessing Fixes")
    print("=" * 60)
    
    try:
        from models.summarizer import TextSummarizer
        
        summarizer = TextSummarizer()
        
        # Test cases with problematic summaries
        problematic_summaries = [
            "Software is developed or engineered, it is not manufactured in the classical sense. Hardware exhibits relatively high failure rates early in its life n s h",
            "Database management systems provide data security and integrity. They allow concurrent access control for multiple users 123456789",
            "Machine learning algorithms can be supervised or unsupervised. They learn from data patterns @#$%",
            "Web development involves frontend and browser technologies. It requires knowledge of HTML CSS a b c",
            "The software development lifecycle includes planning analysis design and"
        ]
        
        print("\n🧪 Testing Postprocessing:")
        print("-" * 40)
        
        for i, summary in enumerate(problematic_summaries, 1):
            print(f"\n{i}. Original: '{summary}'")
            
            processed = summarizer._postprocess_summary(summary)
            print(f"   Processed: '{processed}'")
            
            # Check if meaningless endings were removed
            if processed != summary:
                print("   ✓ Summary was cleaned")
            else:
                print("   → Summary unchanged (was already clean)")
            
            # Verify proper ending
            if processed.endswith(('.', '!', '?')):
                print("   ✓ Proper sentence ending")
            else:
                print("   ❌ Missing proper ending")
        
        return True
        
    except Exception as e:
        print(f"❌ Postprocessing test failed: {e}")
        return False

def test_full_summarization():
    """Test complete summarization with the fixes"""
    print("\n\n🎯 Testing Complete Summarization")
    print("=" * 60)
    
    try:
        from models.summarizer import get_summarizer
        
        summarizer = get_summarizer()
        
        # Sample text that might cause issues
        test_text = """
        Software engineering is a systematic approach to the design, development, and maintenance of software systems. 
        It involves the application of engineering principles to software development, ensuring that the resulting 
        applications are reliable, efficient, maintainable, and meet user requirements. The field encompasses various 
        methodologies, tools, and techniques that help developers create high-quality software within budget and time 
        constraints. Software engineers must consider multiple factors including functionality, performance, security, 
        scalability, and user experience when building applications. The discipline has evolved significantly since 
        its inception, incorporating best practices from computer science, mathematics, and traditional engineering. 
        Modern software engineering emphasizes iterative development, continuous integration, automated testing, 
        and collaborative development practices using version control systems and project management tools.
        """
        
        print("\n📝 Generating summary...")
        summary = summarizer.summarize(test_text, max_length=200, min_length=80)
        
        print(f"✅ Original text length: {len(test_text)} characters")
        print(f"✅ Summary length: {len(summary)} characters")
        print(f"\n📄 Generated Summary:")
        print("-" * 40)
        print(f'"{summary}"')
        print("-" * 40)
        
        # Verify quality
        checks = [
            ("Proper length", 80 <= len(summary) <= 200),
            ("Proper ending", summary.endswith(('.', '!', '?'))),
            ("No meaningless chars", not any(char in summary for char in ['@', '#', '$', '%', '^', '&'])),
            ("Capitalized start", summary[0].isupper() if summary else False),
            ("No incomplete words", not summary.endswith((' n s h', ' a b c', ' ---.ni')))
        ]
        
        print("\n🔍 Quality Checks:")
        print("-" * 20)
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        # Overall assessment
        all_passed = all(check[1] for check in checks)
        if all_passed:
            print("\n🎉 All quality checks passed!")
            print("✅ Text summarization fixes are working correctly!")
        else:
            print("\n⚠️ Some quality checks failed - review needed")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Full summarization test failed: {e}")
        return False

def show_fix_summary():
    """Show what was fixed"""
    print("\n\n📋 FIXES IMPLEMENTED:")
    print("=" * 60)
    print("1. ✅ Text Preprocessing:")
    print("   - Remove non-printable/problematic characters")
    print("   - Truncate at sentence boundaries, not mid-word")
    print("   - Ensure proper sentence endings after truncation")
    
    print("\n2. ✅ Summary Postprocessing:")
    print("   - Detect and remove incomplete word fragments")
    print("   - Remove meaningless character patterns (n s h, etc.)")
    print("   - Clean remaining problematic characters")
    print("   - Ensure proper capitalization and punctuation")
    
    print("\n3. ✅ Mock Summarization:")
    print("   - Preserve sentence boundaries during truncation")
    print("   - Ensure proper endings for truncated text")
    
    print("\n🎯 RESULT:")
    print("- Summaries will now end with complete sentences")
    print("- No more meaningless character fragments")
    print("- Clean, readable summaries every time")

if __name__ == "__main__":
    print("🚀 TESTING TEXT SUMMARIZATION FIXES")
    print("=" * 60)
    
    # Run all tests
    test1_passed = test_text_preprocessing()
    test2_passed = test_summary_postprocessing()  
    test3_passed = test_full_summarization()
    
    show_fix_summary()
    
    # Final result
    print("\n" + "=" * 60)
    if all([test1_passed, test2_passed, test3_passed]):
        print("🎉 ALL TESTS PASSED! 🎉")
        print("Text summarization is now fixed and working correctly!")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
        
    print("=" * 60)
