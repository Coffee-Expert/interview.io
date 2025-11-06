"""Enhanced InterviewerAgent with user profile, scoring, and info collection"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import config_mvp as config

class InterviewerAgent:
    def __init__(self, domain: str, google_api_key: str):
        self.domain = domain
        self.domain_info = config.DOMAIN_TEMPLATES[domain]
        self.user_profiles = {}  # Store profiles keyed by user ID or session
        self.scores = {}  # Store scores keyed by user ID or session
        self.responses = {}  # Store responses keyed by user ID or session

        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=google_api_key,
            temperature=0.7
        )

        self.chain = self._create_chain()

    def _create_chain(self):
        """Create the interview chain with persona"""
        template = """{persona}
        You are asking question #{question_number} out of {total_questions}.
        Interview context so far:
        {conversation_history}
        Your next question from the template: "{question}"
        Ask this question in a conversational way and wait for the candidate's response.
        Make it sound natural, not robotic. Add a bit of context or follow-up if relevant."""
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        return chain

    def initialize_user(self, user_id: str):
        """Initialize profile, responses, and score for a new user session"""
        self.user_profiles[user_id] = {}
        self.responses[user_id] = []
        self.scores[user_id] = 0

    def update_user_profile(self, user_id: str, profile_data: dict):
        """Update user profile with new data"""
        if user_id not in self.user_profiles:
            self.initialize_user(user_id)
        self.user_profiles[user_id].update(profile_data)

    def get_user_profile(self, user_id: str):
        """Retrieve user profile"""
        return self.user_profiles.get(user_id, {})

    def record_response(self, user_id: str, question: str, answer: str):
        """Record user's answer and update responses"""
        if user_id not in self.responses:
            self.initialize_user(user_id)
        self.responses[user_id].append({'question': question, 'answer': answer})

    def score_response(self, user_id: str, answer: str):
        """Simple scoring logic based on answer content (placeholder)"""
        # Placeholder: increase score if answer contains certain keywords
        score_increment = 1 if len(answer) > 0 else 0
        self.scores[user_id] = self.scores.get(user_id, 0) + score_increment

    def get_user_score(self, user_id: str):
        """Retrieve user's total score"""
        return self.scores.get(user_id, 0)

    def collect_user_info(self, user_id: str, info: dict):
        """Collect additional user info"""
        self.update_user_profile(user_id, info)

    def generate_question(self, user_id: str, question_num: int, conversation: str, resume_text: str = "", jobdesc_text: str = "") -> str:
        """
        Generate the next interview question, building on user's responses, resume, and job description.
        The agent can choose to use a template question or generate a dynamic follow-up.
        """
        user_profile = self.get_user_profile(user_id)
        profile_context = ""
        if user_profile:
            profile_context = (
                f"User Info: Name: {user_profile.get('name', '')}, "
                f"Background: {user_profile.get('background', '')}, "
                f"Goals: {user_profile.get('goals', '')}.\n"
            )
        resume_context = f"\nResume:\n{resume_text[:1000]}" if resume_text else ""
        jobdesc_context = f"\nJob Description:\n{jobdesc_text[:1000]}" if jobdesc_text else ""
        # Use the template question as a suggestion, but allow the LLM to build on the conversation
        template_question = self.domain_info["questions"][question_num - 1] if question_num - 1 < len(self.domain_info["questions"]) else ""
        dynamic_prompt = f"""{self.domain_info['persona']}
{profile_context}{resume_context}{jobdesc_context}
You are conducting an interview. Here is the conversation so far:
{conversation if conversation else "Interview just started."}

Suggested question from the template (optional): "{template_question}"

Based on the user's previous answers, resume, and job description, ask the next most relevant interview question.
You may use the template question, rephrase it, or ask a follow-up that builds on the user's last answer.
Make the interview feel natural and adaptive. Only output the next question, nothing else.
"""
        response = self.llm.invoke(dynamic_prompt)
        return response.content if hasattr(response, "content") else response

    def generate_summary(self, user_id: str, all_qa: list) -> str:
        """Generate interview summary and include user profile info"""
        qa_text = "\n\n".join([
            f"Q: {item['q']}\nA: {item['a']}"
            for item in all_qa
        ])
        summary_prompt = f"""Based on this {self.domain_info['name']} interview, provide a concise professional summary:
{qa_text}
Generate a personal bulletted, organized summary with:
1. Overall Assessment (2-3 sentences)
2. Key Strengths (3-4 bullet points)
3. Areas for Development (2-3 bullet points)
4. Pitfalls (and websites/sources/links to study from, for better performance)
5. Recommendation (Hire/Prepare and try again/Maybe with brief reason)
and give an interview score out of 100
User Profile: {self.get_user_profile(user_id)}
User Score: {self.get_user_score(user_id)}"""
        summary = self.llm.invoke(summary_prompt)
        return summary.content