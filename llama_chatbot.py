import streamlit as st
from llama_cpp import Llama

# Load the model using from_pretrained (based on your provided method)
@st.cache_resource
def load_llama_model():
    llm = Llama.from_pretrained(
        repo_id="monal04/llama-2-7b-chat.Q4_0.gguf-GGML",
        filename="llama-2-7b-chat.Q2_K.gguf",  # Ensure this file exists locally
        n_ctx=2048,
        n_threads=8
    )
    return llm

llm = load_llama_model()

# System prompt to prime the model
SYSTEM_PROMPT = """You are a helpful ERP consultant, trained in SAP, Microsoft Dynamics, and Oracle NetSuite.
You assist users by answering ERP-related queries clearly and professionally."""

# Store conversation history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Streamlit UI
st.set_page_config(page_title="ERP Chatbot", page_icon="🧠")
st.title("🤖 ERP Chatbot (LLaMA 2 Local)")

st.markdown("Ask me anything about **ERP systems** like SAP, Oracle NetSuite, or Microsoft Dynamics.")

# User input field
user_input = st.text_input("💬 Your question:", placeholder="e.g., What is SAP RISE?", key="user_input")

if st.button("Ask") and user_input:
    st.session_state["history"].append(("user", user_input))

    # Format messages as expected by llama-cpp chat completion
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for role, content in st.session_state["history"]:
        messages.append({"role": role, "content": content})

    # LLaMA chat completion
    response = llm.create_chat_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=512
    )

    # Extract and save assistant reply
    reply = response['choices'][0]['message']['content']
    st.session_state["history"].append(("assistant", reply))

# Display chat history
st.markdown("---")
for role, content in reversed(st.session_state["history"]):
    if role == "user":
        st.markdown(f"**🧑‍💼 You:** {content}")
    else:
        st.markdown(f"**🤖 ERP Bot:** {content}")
