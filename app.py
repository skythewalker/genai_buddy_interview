import streamlit as st
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate


load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(groq_api_key="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", model_name="llama-3.1-8b-instant")

st.set_page_config(page_title="Interview buddy", page_icon="🤖", layout="centered")

st.title("🤖 Interview Buddy")
st.write("Practice mock interviews with instant feedback. Get your feedback history after 5 questions.")

role = st.selectbox(
    "Choose your interview role: ",
    ["Fullstack developer", "Frontend developer", "Backend developer", "QA enginner", "Data scientist"]
)
# session state for memory chat
if "history" not in st.session_state:
    st.session_state.history = []
    
if "question" not in st.session_state:
    st.session_state.question = None
    
if "answer" not in st.session_state:
    st.session_state.answer = ""
    
# New session state variable to track the number of questions answered
if "questions_answered" not in st.session_state:
    st.session_state.questions_answered = 0
    
    

# generate an interview
if st.session_state.questions_answered < 5:
    if st.button("Get Question"):
        st.session_state.answer = ""
        prompt = ChatPromptTemplate.from_template(
            "You are an interviewer hiring for a {role}. "
            "Ask one interview question (technical or behavioral).."
        )
        chain = prompt | llm
        st.session_state.question = chain.invoke({"role": role}).content
        st.write("## Question: ")
        st.write(st.session_state.question)

# answer box
if st.session_state.question:
    answer = st.text_area("Your answer: ", height=250, key="answer")

    if st.button("Submit answer"):
        answer = st.session_state.answer
        feedback_prompt = ChatPromptTemplate.from_template(
            "You are an expert interviewer.\n\n"
            "The interview question was:\n{question}\n\n"
            "The candidate's answer was:\n{answer}\n\n"
            "Evaluate the answer using these rules:\n"
            "- If the candidate says 'I don’t know', gives no answer, or writes irrelevant text → Score = 1 or 2.\n"
            "- If the candidate gives a partially correct or incomplete answer → Score = 3-5.\n"
            "- If the candidate gives a mostly correct but not fully detailed answer → Score = 6-8.\n"
            "- If the candidate gives a clear, complete, and correct answer with strong reasoning/code → Score = 9-10.\n\n"
            "Your response must be in this exact format:\n"
            "Score (1-10): <score>\n"
            "Strengths: <bullet points>\n"
            "Improvements: <bullet points>\n"
            "Make sure the score follows the rules strictly."
        )
        print("answer ==>", answer)
        chain = feedback_prompt | llm
        feedback = chain.invoke({"question": st.session_state.question, "answer": answer}).content

        # save to history and increment the counter
        st.session_state.history.append({"q": st.session_state.question, "a": answer, "f": feedback})
        st.session_state.questions_answered += 1

        st.write("### Feedback: ")
        st.success(feedback)



# show history only after 10 questions are completed
if st.session_state.questions_answered >= 5:
    st.write("## 📜 Interview History")
    for i, h in enumerate(st.session_state.history):
        st.write(f"**Q{i+1}:** {h['q']}")
        st.write(f"**Your Answer:** {h['a']}")
        st.write(f"**Feedback:** {h['f']}")
        st.write("---")