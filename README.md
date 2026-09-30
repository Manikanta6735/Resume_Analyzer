# 📄 AI Resume Analyzer

An easy-to-use **Streamlit-based AI Resume Analyzer** that evaluates a resume, identifies skills, highlights strengths and weaknesses, and provides actionable improvement suggestions. It can also compare a resume against a specific job description.

## 🚀 Features

- Upload resumes in **PDF, DOCX, or TXT** format
- Optional **job description matching**
- Overall resume/job-match score
- ATS compatibility score
- Matched skills detection
- Missing skills detection
- Resume strengths and weaknesses
- Top-priority improvement recommendation
- Actionable resume suggestions
- Suggested keywords to add
- Estimated experience level
- Extracted resume text preview
- Download analysis results as JSON
- Works with an **offline keyword/heuristic analyzer**

## 🛠️ Technologies Used

- Python
- Streamlit
- Plotly
- PDF/DOCX/TXT resume parsing
- Keyword and heuristic analysis
- Optional AI analysis support

## 📁 Project Structure

```text
AI-Resume-Analyzer/
│
├── app.py
├── resume_parser.py
├── analyzer.py
├── offline_analyzer.py
├── requirements-offline.txt
└── README.md
```

## ⚙️ How It Works

1. Upload your resume.
2. Optionally paste the job description.
3. Click **Analyze Resume**.
4. The application extracts the resume text.
5. The analyzer evaluates the resume and job requirements.
6. Results are displayed through scores, skill analysis, strengths, weaknesses, and suggestions.
7. The analysis can be downloaded as a JSON file.

The current `app.py` uses the offline keyword/heuristic analyzer by default. The application also contains support for an AI analysis path through `analyzer.py`.

## 💻 Installation

### 1. Clone or download the project

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd AI-Resume-Analyzer
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements-offline.txt
```

If you do not have a `requirements-offline.txt`, install the main packages:

```bash
pip install streamlit plotly
```

Also install any additional packages required by `resume_parser.py`, `analyzer.py`, and `offline_analyzer.py`.

## ▶️ Run the Application

From the project folder, run:

```bash
streamlit run app.py
```

The Streamlit application will open in your browser.

## 📄 Supported Resume Formats

- `.pdf`
- `.docx`
- `.txt`

## 📊 Results Provided

### Overall Score
Measures the resume's overall match/quality according to the selected analysis method.

### ATS Compatibility
Provides an ATS-oriented compatibility score.

### Matched Skills
Shows skills detected in the resume that match the analysis requirements.

### Missing Skills
Shows potentially relevant skills that are not detected.

### Strengths
Highlights positive aspects identified in the resume.

### Weaknesses
Shows areas that may need improvement.

### Actionable Suggestions
Provides practical recommendations for improving the resume.

### Keywords to Add
Lists useful keywords that may improve matching with a job description.

## 🧪 Example Workflow

```text
Upload Resume
      ↓
Extract Resume Text
      ↓
Optional Job Description
      ↓
Analyze Resume
      ↓
Calculate Scores
      ↓
Identify Skills & Gaps
      ↓
Generate Suggestions
      ↓
Display Results
      ↓
Download JSON
```

## 🔒 Privacy Note

Resume files may contain personal information such as names, phone numbers, email addresses, education, and employment history. Avoid uploading sensitive resumes to services or repositories where you do not intend to share that information.

## 🎯 Future Improvements

- Advanced LLM-powered resume analysis
- Better ATS scoring
- Resume section detection
- Job-specific resume recommendations
- Resume rewriting
- Cover letter generation
- Multiple job-description comparison
- Resume version management
- Interactive analytics dashboard
- User authentication
- Database storage
- Cloud deployment

## 👨‍💻 Project Purpose

This project is designed as a portfolio application demonstrating skills in:

- Python development
- Streamlit application development
- Natural language/text processing
- Resume parsing
- Data analysis
- ATS-oriented analysis
- Interactive dashboard development

## 📜 License

This project is intended for educational and portfolio purposes. Add an appropriate open-source license if you plan to distribute it publicly.
