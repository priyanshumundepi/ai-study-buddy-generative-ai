import os
import json
import re
import streamlit as st
from google import genai

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020, #151b35, #202044);
    color: #f8fafc;
}
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 35px 25px;
    border-radius: 24px;
    text-align: center;
    background: linear-gradient(120deg, #312e81, #6d28d9, #1d4ed8);
    margin-bottom: 25px;
    border: 1px solid #818cf8;
}
.hero h1 { color: white; font-size: 2.8rem; }
.hero p { color: #e0e7ff; font-size: 1.1rem; }
.feature-card {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid #475569;
    padding: 20px;
    border-radius: 18px;
    min-height: 130px;
    margin-bottom: 12px;
}
.feature-card h3 { color: #c4b5fd; }
.feature-card p { color: #e2e8f0; }
.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white;
    border-radius: 12px;
    min-height: 45px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📚 AI Study Buddy</h1>
    <p>Your Personal AI Learning Assistant</p>
    <p>Learn smarter. Practice better. Achieve more. 🚀</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### ✨ Explore Your Learning Tools")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📚 AI Study Notes</h3>
        <p>Generate organized notes and important concepts.</p>
    </div>
    <div class="feature-card">
        <h3>💡 Topic Explainer</h3>
        <p>Understand difficult topics in simple English.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>📝 MCQ Quiz</h3>
        <p>Practice questions and check your score.</p>
    </div>
    <div class="feature-card">
        <h3>🗂️ AI Flashcards</h3>
        <p>Revise important questions and answers.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()



st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020 0%, #151b35 55%, #202044 100%);
    color: #f8fafc;
}

.block-container {
    max-width: 1050px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

h1 {
    color: #ffffff !important;
    font-size: 2.7rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #c4b5fd !important;
}

p, label, .stMarkdown {
    color: #e2e8f0;
}

div[data-testid="stTextInput"] input {
    background: #1e293b;
    color: white;
    border: 1px solid #475569;
    border-radius: 12px;
    padding: 12px;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #1e293b;
    color: white;
    border-radius: 12px;
    border-color: #475569;
}

.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.4rem;
    font-weight: 700;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #6d28d9, #1d4ed8);
    border: none;
    transform: translateY(-2px);
}

div[data-testid="stExpander"] {
    background: rgba(30, 41, 59, 0.75);
    border: 1px solid #475569;
    border-radius: 14px;
    margin-bottom: 10px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: #475569;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 AI Study Buddy")
st.subheader("Your Personal AI Learning Assistant")
st.write("Learn smarter with your personal AI study partner!")

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API key nahi mili. Colab mein API key wala cell dobara run karo.")
    st.stop()

client = genai.Client(api_key=api_key)

if "study_material" not in st.session_state:
    st.session_state.study_material = None

if "flashcards_data" not in st.session_state:
    st.session_state.flashcards_data = None

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

if "quiz_version" not in st.session_state:
    st.session_state.quiz_version = 0

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

topic = st.text_input(
    "📖 Enter your study topic",
    placeholder="Example: Python Programming"
)

feature = st.selectbox(
    "Choose your study tool",
    ["Study Notes", "MCQ Quiz", "Topic Explainer", "AI Flashcards"]
)

if st.button("✨ Start Learning"):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        st.session_state.study_material = None
        st.session_state.quiz_data = None
        st.session_state.quiz_submitted = False

        with st.spinner("🤖 AI is preparing your study material..."):
            try:
                if feature == "MCQ Quiz":
                    prompt = f"""
                    Create exactly 5 multiple-choice questions about {topic}.
                    Return ONLY valid JSON, without markdown fences.
                    Use this exact structure:
                    {{
                      "questions": [
                        {{
                          "question": "Question text",
                          "options": [
                            "Option A",
                            "Option B",
                            "Option C",
                            "Option D"
                          ],
                          "answer": 0,
                          "explanation": "Short explanation"
                        }}
                      ]
                    }}
                    The answer must be an integer from 0 to 3,
                    representing the correct option's index.
                    Include exactly 4 options per question.
                    """
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )

                    raw_text = response.text.strip()
                    raw_text = re.sub(
                        r"^```(?:json)?\s*|\s*```$",
                        "",
                        raw_text
                    )

                    quiz = json.loads(raw_text)

                    if len(quiz["questions"]) != 5:
                        raise ValueError("AI did not generate 5 questions.")

                    for q in quiz["questions"]:
                        if (
                            len(q["options"]) != 4
                            or not isinstance(q["answer"], int)
                            or q["answer"] not in range(4)
                        ):
                            raise ValueError("Quiz format is invalid.")

                    st.session_state.quiz_data = quiz
                    st.session_state.quiz_version += 1

                elif feature == "AI Flashcards":
                    prompt = f"""
                    Create 8 useful study flashcards about {topic}.
                    Return ONLY valid JSON without markdown fences.
                    Use this structure:
                    {{
                      "flashcards": [
                        {{
                          "question": "A short question",
                          "answer": "A clear and simple answer"
                        }}
                      ]
                    }}
                    Keep answers beginner-friendly and accurate.
                    """

                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )

                    raw_text = response.text.strip()
                    raw_text = re.sub(
                        r"^```(?:json)?\s*|\s*```$",
                        "",
                        raw_text
                    )

                    cards = json.loads(raw_text)["flashcards"]

                    if not cards:
                        raise ValueError("No flashcards were generated.")

                    st.session_state.flashcards_data = cards

                else:
                    if feature == "Study Notes":
                        prompt = (
                            f"Create clear, well-organized study notes on "
                            f"{topic}. Include headings, key points and examples."
                        )
                    else:
                        prompt = (
                            f"Explain {topic} in simple English for a beginner. "
                            "Include examples and a short summary."
                        )

                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )
                    st.session_state.study_material = response.text

            except Exception as e:
                st.error(f"AI request failed: {e}")

if st.session_state.study_material:
    st.markdown("## 📚 Your Study Material")
    st.markdown(st.session_state.study_material)

if st.session_state.quiz_data:
    st.markdown("## 📝 Test Your Knowledge")
    st.write("Choose one answer for each question, then submit your quiz.")

    questions = st.session_state.quiz_data["questions"]
    version = st.session_state.quiz_version

    for i, q in enumerate(questions):
        st.markdown(f"**Q{i + 1}. {q['question']}**")
        st.radio(
            "Choose your answer:",
            q["options"],
            key=f"quiz_{version}_{i}",
            index=None,
            disabled=st.session_state.quiz_submitted
        )

    if not st.session_state.quiz_submitted:
        if st.button("✅ Submit Quiz"):
            answers = [
                st.session_state.get(f"quiz_{version}_{i}")
                for i in range(len(questions))
            ]

            if any(answer is None for answer in answers):
                st.warning("Please answer all 5 questions first.")
            else:
                score = sum(
                    answers[i] == q["options"][q["answer"]]
                    for i, q in enumerate(questions)
                )
                st.session_state.quiz_score = score
                st.session_state.quiz_answers = answers
                st.session_state.quiz_submitted = True
                st.rerun()

    if st.session_state.quiz_submitted:
        score = st.session_state.quiz_score
        st.success(f"🎉 Your Score: {score}/{len(questions)}")

        for i, q in enumerate(questions):
            selected = st.session_state.quiz_answers[i]
            correct = q["options"][q["answer"]]

            if selected == correct:
                st.markdown(f"**Q{i + 1}: Correct! ✅**")
            else:
                st.markdown(f"**Q{i + 1}: Incorrect ❌**")

            st.write(f"Your answer: {selected}")
            st.write(f"Correct answer: {correct}")
            st.info(f"Explanation: {q['explanation']}")

        if st.button("🔄 Generate New Quiz"):
            st.session_state.quiz_data = None
            st.session_state.quiz_submitted = False
            st.rerun()

if st.session_state.flashcards_data:
    st.markdown("## 🗂️ Your AI Flashcards")
    st.write("Revise your topic using these question-and-answer cards.")

    for i, card in enumerate(st.session_state.flashcards_data):
        with st.expander(f"📝 Flashcard {i + 1}: {card['question']}"):
            st.markdown("**Answer:**")
            st.write(card["answer"])

st.divider()
st.caption("AI Study Buddy | Built with Python, Streamlit & Gemini AI")
