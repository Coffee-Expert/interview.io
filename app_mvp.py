"""
Simple Interview Chatbot - MVP
"""
import streamlit as st

import os
import tempfile
import sys
import chromadb
from agent_mvp import InterviewerAgent
import pdfplumber
import logging

logging.basicConfig(level=logging.DEBUG)

# Page config
st.set_page_config(page_title="Interview.io", page_icon="🎤", layout="wide")

# --- Futuristic Apple-like Design ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'SF Pro Display', 'Inter', 'Segoe UI', Arial, sans-serif !important;
        background: linear-gradient(135deg, #181c24 0%, #232a36 100%);
        color: #f5f6fa;
    }
    .block-container {
        background: rgba(30,32,40,0.92);
        border-radius: 24px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
        padding: 2rem 2.5rem;
        margin-top: 2rem;
    }
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(90deg, #1e90ff 0%, #007aff 100%);
        color: #fff;
        border-radius: 12px;
        border: none;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,122,255,0.12);
        transition: 0.2s;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: linear-gradient(90deg, #007aff 0%, #1e90ff 100%);
        color: #fff;
        box-shadow: 0 4px 16px rgba(0,122,255,0.18);
    }
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        background: rgba(40,44,54,0.85);
        border-radius: 8px;
        border: 1px solid #232a36;
        color: #f5f6fa;
        padding: 0.5rem 1rem;
        font-size: 1rem;
    }
    .stSidebar {
        background: rgba(24, 28, 36, 0.98);
        border-radius: 24px 0 0 24px;
        box-shadow: 2px 0 24px 0 rgba(31, 38, 135, 0.12);
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .stMarkdown h1 {
        font-size: 2.5rem;
        color: #1e90ff;
        margin-bottom: 0.2em;
    }
    .stMarkdown h2 {
        color: #f5f6fa;
    }
    .stMarkdown h3 {
        color: #1e90ff;
    }
    .stExpanderHeader {
        font-weight: 600;
        color: #1e90ff;
    }
    .stProgress>div>div>div>div {
        background: linear-gradient(90deg, #1e90ff 0%, #007aff 100%);
    }
    </style>
""", unsafe_allow_html=True)


try:
    """importing transformer library"""
    from sentence_transformers import SentenceTransformer
    logging.debug("SentenceTransformer imported successfully")
except ImportError as e:
    logging.error(f"ImportError: {e}")
print(f"Python interpreter used: {sys.executable}")
import config_mvp as config

# Utility: Extract text from PDF or TXT file
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    if uploaded_file.type == "application/pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        with pdfplumber.open(tmp_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        os.remove(tmp_path)
        return text
    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    else:
        return ""

# Utility: Vectorize text
def get_vectorizer():
    if "vectorizer" not in st.session_state:
        st.session_state.vectorizer = SentenceTransformer("all-MiniLM-L6-v2")
    return st.session_state.vectorizer

# Utility: Initialize ChromaDB collection
def get_chromadb_collection():
    if "chroma_client" not in st.session_state:
        st.session_state.chroma_client = chromadb.Client()
    if "chroma_collection" not in st.session_state:
        st.session_state.chroma_collection = st.session_state.chroma_client.create_collection("user_docs")
    return st.session_state.chroma_collection

# Store uploaded files and user profile in ChromaDB
def store_user_docs_and_vectors(user_id, resume_file, jobdesc_file, user_profile):
    collection = get_chromadb_collection()
    vectorizer = get_vectorizer()
    # Extract text
    resume_text = extract_text_from_file(resume_file)
    jobdesc_text = extract_text_from_file(jobdesc_file)
    profile_text = f"Name: {user_profile.get('name', '')}\nBackground: {user_profile.get('background', '')}\nGoals: {user_profile.get('goals', '')}"
    # Vectorize
    docs = []
    metadatas = []
    ids = []
    if resume_text:
        docs.append(resume_text)
        metadatas.append({"type": "resume", "user_id": user_id})
        ids.append(f"{user_id}_resume")
    if jobdesc_text:
        docs.append(jobdesc_text)
        metadatas.append({"type": "jobdesc", "user_id": user_id})
        ids.append(f"{user_id}_jobdesc")
    if profile_text.strip():
        docs.append(profile_text)
        metadatas.append({"type": "profile", "user_id": user_id})
        ids.append(f"{user_id}_profile")
    if docs:
        embeddings = vectorizer.encode(docs).tolist()
        collection.upsert(
            embeddings=embeddings,
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )
    return resume_text, jobdesc_text, profile_text


# --- SIDEBAR ---
with st.sidebar:
    # --- Avatar/Profile Picture ---
    st.markdown("## User Profile")
    if 'avatar_image' not in st.session_state:
        st.session_state.avatar_image = None
    avatar_file = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"], key="avatar_upload")
    if avatar_file is not None:
        st.session_state.avatar_image = avatar_file.getvalue()
    if st.session_state.avatar_image:
        st.image(st.session_state.avatar_image, width=100, caption="Profile Picture")

    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    user_profile = st.session_state.user_profile

    # Editable fields
    user_profile['name'] = st.text_input("Name", value=user_profile.get('name', ''), key="sidebar_name")
    user_profile['background'] = st.text_area("Background", value=user_profile.get('background', ''), height=60, key="sidebar_background")
    user_profile['goals'] = st.text_area("Goals", value=user_profile.get('goals', ''), height=40, key="sidebar_goals")
    st.session_state.user_profile = user_profile

    st.markdown("---")

    # --- Theme Switcher ---
    st.markdown("### 🎨 Theme")
    theme = st.selectbox("Choose Theme", ["Dark", "Dark"], key="theme_switcher")
    st.session_state.theme = theme
    st.markdown("---")

    # --- Navigation ---
    st.markdown("## Navigation")
    if st.button("Home", key="sidebar_home"):
        st.session_state.page = 'domain'
        st.session_state.question_num = 1
        st.session_state.qa_list = []
        st.session_state.conversation = ""
        st.session_state.current_question = None
        st.rerun()
    if st.button("Restart Interview", key="sidebar_restart"):
        st.session_state.page = 'interview'
        st.session_state.question_num = 1
        st.session_state.qa_list = []
        st.session_state.conversation = ""
        st.session_state.current_question = None
        st.rerun()

    st.markdown("---")

    # --- Progress ---
    st.markdown("## Progress")
    if 'question_num' in st.session_state and 'domain' in st.session_state:
        st.write(f"Question: {st.session_state.question_num} / {getattr(config, 'NUM_QUESTIONS', 1)}")
    if st.session_state.get('page') == 'summary':
        # Show score if available
        agent = InterviewerAgent(st.session_state.domain, config.GOOGLE_API_KEY)
        user_id = "default_user"
        if 'user_profile' in st.session_state:
            agent.update_user_profile(user_id, st.session_state.user_profile)
        for qa in st.session_state.qa_list:
            agent.record_response(user_id, qa['q'], qa['a'])
            agent.score_response(user_id, qa['a'])
        # Use LLM-based score from summary if available
        import re
        summary = agent.generate_summary(user_id, st.session_state.qa_list)
        llm_score = None
        score_match = re.search(r"score\s*[:\-]?\s*(\d{1,3})\s*/\s*100", summary, re.IGNORECASE)
        if score_match:
            llm_score = int(score_match.group(1))
        if llm_score is not None:
            st.write(f"Score: {llm_score} / 100")
        else:
            st.write("Score: _(Not found in summary)_")
        # --- Download Report Button ---
        import base64
        summary_text = f"Interview.io Summary\n\nScore: {llm_score if llm_score is not None else '?'} / 100\n\n"
        for i, qa in enumerate(st.session_state.qa_list, 1):
            summary_text += f"Q{i}: {qa['q']}\nA{i}: {qa['a']}\n\n"
        b64 = base64.b64encode(summary_text.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="interview_report.txt">📥 Download Report</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.markdown("---")

    # --- Conversation History ---
    st.markdown("## Conversation History")
    if 'qa_list' in st.session_state and st.session_state.qa_list:
        for i, qa in enumerate(st.session_state.qa_list, 1):
            st.markdown(f"**Q{i}:** {qa['q']}")
            st.markdown(f"**A{i}:** {qa['a']}")
            st.markdown("---")

    # --- Help & Tips Section ---
    st.markdown("---")
    with st.expander("Help & Tips"):
        st.markdown("""
        - Make sure to fill out your profile for a personalized interview.
        - You can upload your resume and job description for more tailored questions.
        - Use the 'Restart Interview' button to try again with new answers.
        - Download your interview report after completion for your records.
        - For best results, answer questions thoughtfully and in detail.
        """)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'domain'  # domain, interview, summary
if 'domain' not in st.session_state:
    st.session_state.domain = None
if 'question_num' not in st.session_state:
    st.session_state.question_num = 1
if 'qa_list' not in st.session_state:
    st.session_state.qa_list = []
if 'conversation' not in st.session_state:
    st.session_state.conversation = ""
if 'current_question' not in st.session_state:
    st.session_state.current_question = None

# Check API key
if not config.GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env")
    st.stop()

# PAGE 1: Domain Selection
if st.session_state.page == 'domain':
    st.markdown("# Interview.io")
    st.markdown("#### *just a few questions away from acing your interviews*")
    st.markdown("Select your interview domain")

    st.markdown("### Tell us a bit about yourself (this will help personalize your interview):")
    user_name = st.text_input("Your Name", key="user_name")
    user_background = st.text_area("Background / Experience", key="user_background", height=80)
    user_goals = st.text_area("Career Goals / Interests", key="user_goals", height=60)

    st.markdown("### (Optional) Upload your Resume and Job Description")
    resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"], key="resume_file")
    jobdesc_file = st.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"], key="jobdesc_file")

    if not resume_file:
        st.info("You have not uploaded a resume. The interview will proceed using only your profile information.")
    if not jobdesc_file:
        st.info("You have not uploaded a job description. The interview will proceed using only your profile information.")

    # Store user info in session state
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    st.session_state.user_profile['name'] = user_name
    st.session_state.user_profile['background'] = user_background
    st.session_state.user_profile['goals'] = user_goals

    col1, col2, col3 = st.columns(3)

    def can_start_interview():
        return user_name.strip() != "" and user_background.strip() != ""

    with col1:
        if st.button("Engineering", use_container_width=True, disabled=not can_start_interview()):
            st.session_state.domain = 'engineering'
            st.session_state.page = 'interview'
            st.session_state.question_num = 1
            st.session_state.qa_list = []
            st.session_state.conversation = ""
            # Vectorize and store docs
            user_id = "default_user"
            from streamlit.runtime.uploaded_file_manager import UploadedFile
            user_profile = st.session_state.user_profile
            resume_text, jobdesc_text, profile_text = store_user_docs_and_vectors(
                user_id,
                resume_file,
                jobdesc_file,
                user_profile
            )
            st.session_state.resume_text = resume_text if resume_text is not None else ""
            st.session_state.jobdesc_text = jobdesc_text if jobdesc_text is not None else ""
            st.session_state.profile_text = profile_text if profile_text is not None else ""
            st.rerun()

    with col2:
        if st.button("Management", use_container_width=True, disabled=not can_start_interview()):
            st.session_state.domain = 'management'
            st.session_state.page = 'interview'
            st.session_state.question_num = 1
            st.session_state.qa_list = []
            st.session_state.conversation = ""
            user_id = "default_user"
            user_profile = st.session_state.user_profile
            resume_text, jobdesc_text, profile_text = store_user_docs_and_vectors(
                user_id,
                resume_file,
                jobdesc_file,
                user_profile
            )
            st.session_state.resume_text = resume_text if resume_text is not None else ""
            st.session_state.jobdesc_text = jobdesc_text if jobdesc_text is not None else ""
            st.session_state.profile_text = profile_text if profile_text is not None else ""
            st.rerun()

    with col3:
        if st.button("HR", use_container_width=True, disabled=not can_start_interview()):
            st.session_state.domain = 'hr'
            st.session_state.page = 'interview'
            st.session_state.question_num = 1
            st.session_state.qa_list = []
            st.session_state.conversation = ""
            user_id = "default_user"
            user_profile = st.session_state.user_profile
            resume_text, jobdesc_text, profile_text = store_user_docs_and_vectors(
                user_id,
                resume_file,
                jobdesc_file,
                user_profile
            )
            st.session_state.resume_text = resume_text if resume_text is not None else ""
            st.session_state.jobdesc_text = jobdesc_text if jobdesc_text is not None else ""
            st.session_state.profile_text = profile_text if profile_text is not None else ""
            st.rerun()

# PAGE 2: Interview
elif st.session_state.page == 'interview':
    # Guard against missing domain (should not happen, but prevents KeyError)
    if st.session_state.domain not in config.DOMAIN_TEMPLATES:
        st.error("Interview domain not set. Please return to the home page and select a domain.")
    else:
        domain_name = config.DOMAIN_TEMPLATES[st.session_state.domain]['name']
        st.markdown(f"# {domain_name} Interview")
        st.markdown(f"Question {st.session_state.question_num} of {config.NUM_QUESTIONS}")
        
        # Progress bar
        progress = st.session_state.question_num / config.NUM_QUESTIONS
        st.progress(progress)
        
        # Initialize agent if needed
        if st.session_state.current_question is None:
            with st.spinner("Generating question..."):
                agent = InterviewerAgent(st.session_state.domain, config.GOOGLE_API_KEY)
                # Store user profile in agent
                user_id = "default_user"  # Replace with real user/session id if available
                if 'user_profile' in st.session_state:
                    agent.update_user_profile(user_id, st.session_state.user_profile)
                question = agent.generate_question(
                    user_id,
                    st.session_state.question_num,
                    st.session_state.conversation,
                    st.session_state.get("resume_text", ""),
                    st.session_state.get("jobdesc_text", "")
                )
                st.session_state.current_question = question
        
        # Display question
        st.info(st.session_state.current_question)
        
        # User answer
        user_answer = st.text_area(
            "Your answer:",
            height=150,
            placeholder="Type your answer here...",
            key=f"answer_{st.session_state.question_num}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                if user_answer.strip():
                    # Store Q&A
                    q_text = config.DOMAIN_TEMPLATES[st.session_state.domain]['questions'][
                        st.session_state.question_num - 1
                    ]
                    st.session_state.qa_list.append({
                        'q': q_text,
                        'a': user_answer
                    })
                    
                    # Update conversation
                    st.session_state.conversation += f"\nQ: {q_text}\nA: {user_answer}"
                    
                    # Check if done
                    if st.session_state.question_num >= config.NUM_QUESTIONS:
                        st.session_state.page = 'summary'
                        st.rerun()
                    else:
                        # Next question
                        st.session_state.question_num += 1
                        st.session_state.current_question = None
                        st.rerun()
                else:
                    st.warning("Please provide an answer")
        
        with col2:
            if st.button("← Back to Domain", use_container_width=True):
                st.session_state.page = 'domain'
                st.session_state.question_num = 1
                st.session_state.qa_list = []
                st.session_state.conversation = ""
                st.session_state.current_question = None
                st.rerun()

# PAGE 3: Summary
elif st.session_state.page == 'summary':
    domain_name = config.DOMAIN_TEMPLATES[st.session_state.domain]['name']
    st.markdown(f"# Interview.io Summary - {domain_name}")
    st.markdown("#### *just a few questions away from acing your interviews*")
    
    # Generate summary
    with st.spinner("Generating summary..."):
        agent = InterviewerAgent(st.session_state.domain, config.GOOGLE_API_KEY)
        user_id = "default_user"
        if 'user_profile' in st.session_state:
            agent.update_user_profile(user_id, st.session_state.user_profile)
        # Record all Q&A in agent for scoring and summary
        for qa in st.session_state.qa_list:
            agent.record_response(user_id, qa['q'], qa['a'])
            agent.score_response(user_id, qa['a'])
        summary = agent.generate_summary(user_id, st.session_state.qa_list)

    st.markdown(summary)

    # Extract LLM-based score from summary (expects "score out of 100" in summary)
    import re
    llm_score = None
    score_match = re.search(r"score\s*[:\-]?\s*(\d{1,3})\s*/\s*100", summary, re.IGNORECASE)
    if score_match:
        llm_score = int(score_match.group(1))
    if llm_score is not None:
        st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1rem;">
                <div style="background:rgba(0,122,255,0.08);border-radius:50%;width:80px;height:80px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,122,255,0.10);">
                    <span style="font-size:2.2rem;font-weight:700;color:#007aff;">{llm_score if llm_score is not None else "?"}</span>
                </div>
                <div>
                    <span style="font-size:1.3rem;font-weight:600;color:#222;">Your Interview Score</span><br>
                    <span style="font-size:1.1rem;color:#555;">out of 100</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="display:flex;align-items:center;gap:1rem;">
                <div style="background:rgba(0,122,255,0.08);border-radius:50%;width:80px;height:80px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,122,255,0.10);">
                    <span style="font-size:2.2rem;font-weight:700;color:#007aff;">?</span>
                </div>
                <div>
                    <span style="font-size:1.3rem;font-weight:600;color:#222;">Your Interview Score</span><br>
                    <span style="font-size:1.1rem;color:#555;">out of 100</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Q&A recap
    with st.expander("📋 Full Q&A Recap"):
        for i, qa in enumerate(st.session_state.qa_list, 1):
            st.markdown(f"### Question {i}")
            st.write(f"**Q:** {qa['q']}")
            st.write(f"**A:** {qa['a']}")
            st.divider()
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("New Interview", use_container_width=True, type="primary"):
            st.session_state.page = 'domain'
            st.session_state.question_num = 1
            st.session_state.qa_list = []
            st.session_state.conversation = ""
            st.session_state.current_question = None
            st.rerun()
    
    with col2:
        if st.button("Home", use_container_width=True):
            st.session_state.page = 'domain'
            st.session_state.question_num = 1
            st.session_state.qa_list = []
            st.session_state.conversation = ""
            st.session_state.current_question = None
            st.rerun()