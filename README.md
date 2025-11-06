# Interview Bot MVP - Project Overview

## Problem Statement

Traditional interview preparation is time-consuming, generic, and often lacks personalization. Candidates struggle to get targeted practice, actionable feedback, and domain-specific mock interviews tailored to their background, resume, and job description.

## Problem Solutions

- **Personalized Interview Simulation:** The bot generates interview questions based on the user's resume, job description, and career goals.
- **Domain-Specific Practice:** Supports multiple domains (Engineering, Management, HR) with relevant question sets.
- **Automated Feedback & Scoring:** Provides instant feedback and scoring to help users identify strengths and weaknesses.
- **No Resume/JD Required:** Can function with just user profile information, making it accessible to all users.

## Project Explanations

The Interview Bot MVP is a Streamlit-based web application that simulates real interview scenarios. Users can upload their resume and job description (optional), fill in their profile, and select a domain for the interview. The bot generates questions, collects answers, and provides feedback and a summary at the end.

## Tech Stack

- **Frontend/UI:** Streamlit
- **Backend/Logic:** Python
- **Vector Embeddings:** sentence-transformers (MiniLM)
- **Database:** ChromaDB (for document and vector storage)
- **PDF Parsing:** pdfplumber
- **Environment Management:** python-dotenv
- **Other:** langchain, Google GenAI, pandas, numpy

## Architecture Design

```
[User] 
   |
   v
[Streamlit UI] <--> [Session State]
   |
   v
[InterviewerAgent] <--> [ChromaDB] <--> [SentenceTransformer]
   |
   v
[Feedback & Scoring]
```

- **User** interacts with the Streamlit UI.
- **Session State** manages user data, uploaded files, and interview progress.
- **InterviewerAgent** generates questions and feedback using user data and embeddings.
- **ChromaDB** stores user documents and their vector representations.
- **SentenceTransformer** encodes text for semantic search and question generation.

## How It Works

1. User enters profile info and (optionally) uploads resume/JD.
2. User selects a domain and starts the interview.
3. The bot generates questions using the InterviewerAgent, leveraging user data and embeddings.
4. User answers questions; responses are stored and scored.
5. At the end, the bot provides a summary and a score, with a full Q&A recap.

##Live Demo


https://github.com/user-attachments/assets/6f1c12ee-2e6e-4e56-8acb-6088cc74a30d



## Impacted Use Cases

- Job seekers preparing for interviews in specific domains.
- Students practicing for campus placements.
- Professionals seeking targeted feedback for career transitions.
- Recruiters or trainers simulating interview scenarios for candidates.

## Future Scope

- Add support for more domains and question templates.
- Integrate with external job boards and resume parsers.
- Enable voice-based Q&A and feedback.
- Advanced analytics and progress tracking.
- Multi-language support.
- Team/enterprise features for group training.

## Team Members

- Abhishek Kevin Gomes
- Ankur Singh
