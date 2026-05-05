"""
app.py – Streamlit UI (alternative to React frontend).
Run with: streamlit run app.py
"""

import streamlit as st
import requests
import json

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="ConvoLens",
    page_icon="🔍",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background-color: #0a0f1e; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return None


def api_post(endpoint, data):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🔍 ConvoLens")
    st.markdown("---")

    # Upload CSV
    uploaded = st.file_uploader("Upload Conversation CSV", type=["csv"])
    if uploaded:
        files = {"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
        try:
            r = requests.post(f"{API_BASE}/upload", files=files, timeout=120)
            if r.ok:
                result = r.json()
                st.success(f"✓ {result['total_messages']} messages, {result['total_topics']} topics")
            else:
                st.error(f"Upload failed: {r.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")

    st.markdown("---")

    # Persona
    st.markdown("### 👤 Persona")
    persona = api_get("/persona")
    if persona:
        for key, values in persona.items():
            if values:
                st.markdown(f"**{key.replace('_', ' ').title()}**")
                for v in values:
                    st.markdown(f"- {v}")
    else:
        st.info("Upload a CSV to see persona data")

    st.markdown("---")

    # Topics
    st.markdown("### 📑 Topics")
    topics = api_get("/topics")
    if topics:
        for t in topics:
            with st.expander(f"Topic {t['topic_id']} (#{t['start_index']}–{t['end_index']})"):
                st.write(t.get("summary", "No summary"))
    else:
        st.info("Upload a CSV to see topics")


# --- Main Chat ---
st.markdown("# 💬 Conversation Analyst")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about the conversation..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = api_post("/chat", {"query": prompt})
            if result:
                response = result["response"]
            else:
                response = "Error: Could not get a response. Is the backend running?"
            st.markdown(response)

    st.session_state.chat_history.append({"role": "assistant", "content": response})
