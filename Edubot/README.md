# EduBot - Personalized AI Learning Assistant

A comprehensive AI-powered learning assistant that provides personalized educational support through text summarization, quiz generation, performance analysis, and resource recommendations.

## Features

- **Text Summarization**: Uses T5 model to generate concise summaries from uploaded PDF/TXT notes
- **Quiz Generation**: Leverages GPT-3.5 to create contextually relevant questions based on weak topics
- **Performance Analysis**: Predictive models to classify student strengths/weaknesses
- **Resource Recommendations**: TF-IDF based recommendations for educational content and YouTube videos
- **Modular Architecture**: Easy model upgrades and replacements

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: PostgreSQL
- **AI Models**: 
  - T5 (Text Summarization)
  - GPT-3.5 (Quiz Generation)
  - TF-IDF (Recommendations)
  - Logistic Regression/Decision Trees (Performance Analysis)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file
4. Configure PostgreSQL database
5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
edubot/
├── app.py                 # Main Streamlit application
├── config/
│   ├── __init__.py
│   ├── database.py        # Database configuration
│   └── settings.py        # Application settings
├── models/
│   ├── __init__.py
│   ├── summarizer.py      # T5 text summarization
│   ├── quiz_generator.py  # GPT-3.5 quiz generation
│   ├── recommender.py     # TF-IDF recommendations
│   └── performance.py     # Performance analysis models
├── utils/
│   ├── __init__.py
│   ├── file_processor.py  # PDF/TXT processing
│   └── data_processor.py  # Data preprocessing
├── database/
│   ├── __init__.py
│   ├── models.py          # Database models
│   └── operations.py      # Database operations
└── frontend/
    ├── __init__.py
    ├── components.py      # Reusable UI components
    └── pages.py           # Page layouts
```

## Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/edubot
MODEL_CACHE_DIR=./models_cache
```

## Usage

1. Upload PDF/TXT notes for summarization
2. Generate quizzes based on weak topics
3. Analyze performance patterns
4. Get personalized resource recommendations

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


