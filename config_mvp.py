"""
Simple MVP Config
"""
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# Domain Q&A Templates
DOMAIN_TEMPLATES = {
    "engineering": {
        "name": "Software Engineering",
        "persona": "You are an experienced senior software engineer conducting a technical interview. Ask questions about coding, system design, and technical problem-solving.",
        "questions": [
            "Tell me about your experience with system design. Walk me through a complex system you've architected.",
            "How do you approach debugging a production issue? Can you share a specific example?",
            "Explain the difference between SQL and NoSQL databases and when you'd use each.",
            "What's your experience with microservices architecture? What are the trade-offs?",
            "Describe your approach to writing clean, maintainable code. What practices do you follow?",
            "How do you handle technical debt in your projects?",
            "Tell me about a time you optimized code for performance. What was the problem and solution?",
            "What's your experience with CI/CD pipelines and DevOps?",
            "How do you approach learning new technologies or frameworks?",
            "Describe a challenging technical problem you solved and how you approached it.",
        ]
    },
    "management": {
        "name": "Management",
        "persona": "You are a senior manager conducting a leadership interview. Ask questions about team management, decision-making, and leadership style.",
        "questions": [
            "Tell me about a team you've led. How large was it and what were your responsibilities?",
            "Describe your management style. How do you motivate your team?",
            "Share an example of a difficult decision you made as a manager and how you handled it.",
            "How do you handle conflict within your team? Give me a specific example.",
            "What's your approach to performance management and giving feedback?",
            "Tell me about a time you had to manage up - dealing with difficult stakeholders or executives.",
            "How do you develop and grow talent in your team?",
            "Describe a situation where you had to make a tough call between business needs and team wellbeing.",
            "What metrics do you use to measure team performance and success?",
            "Tell me about your experience with cross-functional collaboration and coordination.",
        ]
    },
    "hr": {
        "name": "Human Resources",
        "persona": "You are an HR professional conducting an interview focused on people, culture, and organizational development.",
        "questions": [
            "Tell me about your experience in HR. What areas have you worked in?",
            "Describe your approach to recruitment and building a strong team.",
            "How do you foster a positive company culture? Give me a specific example.",
            "Share an experience where you resolved a complex employee relations issue.",
            "What's your approach to employee development and career growth?",
            "Tell me about your experience with compensation and benefits strategy.",
            "How do you handle performance issues and difficult conversations with employees?",
            "Describe your approach to diversity, equity, and inclusion initiatives.",
            "What's your experience with organizational change management?",
            "Tell me about a time you improved an HR process or policy. What was the outcome?",
        ]
    }
}

NUM_QUESTIONS = 10
