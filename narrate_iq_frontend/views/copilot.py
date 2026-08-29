"""
views/copilot.py
-----------------
The AI Copilot: a conversational front door onto the same analysis
shown everywhere else in the app. This is intentionally NOT a general
chatbot - every answer is expected to be grounded in the current
Narrate IQ decision, root-cause graph, experiments, and learning data
your backend already computes.

Data source / mutation (unchanged): POST /chat {question, conversation}
using your existing Groq-backed implementation. This file only changes
presentation and never alters the request/response contract.
"""

import requests
import streamlit as st

from api_client import post_json

SUGGESTED_QUESTIONS = [
    "Why did revenue decline?",
    "Why not marketing?",
    "Did the experiment work?",
]


def render() -> None:
    header_l, header_r = st.columns([3, 1])
    with header_l:
        st.markdown('<div class="niq-eyebrow">AI COPILOT</div>', unsafe_allow_html=True)
        st.markdown("## Ask Narrate IQ")
        st.caption("Answers are grounded in your current decision, evidence, and experiment data — not a general model.")
    with header_r:
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # suggested questions
    # --------------------------------------------------------

    cols = st.columns(len(SUGGESTED_QUESTIONS))
    selected = None
    for col, question in zip(cols, SUGGESTED_QUESTIONS):
        with col:
            if st.button(question, use_container_width=True, key=f"suggest_{question}"):
                selected = question

    if selected:
        _ask(selected)
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # conversation history
    # --------------------------------------------------------

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --------------------------------------------------------
    # free-form input
    # --------------------------------------------------------

    question = st.chat_input("Ask Narrate IQ anything about the current analysis...")

    if question:
        history_payload = [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages
        ]
        st.session_state.chat_messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing evidence..."):
                try:
                    result = post_json("/chat", {"question": question, "conversation": history_payload})
                    answer = result["answer"]
                    st.markdown(answer)
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                except requests.RequestException as exc:
                    st.error(str(exc))


def _ask(question: str) -> None:
    history_payload = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages
    ]
    st.session_state.chat_messages.append({"role": "user", "content": question})

    try:
        result = post_json("/chat", {"question": question, "conversation": history_payload})
        st.session_state.chat_messages.append({"role": "assistant", "content": result["answer"]})
    except requests.RequestException as exc:
        st.error(str(exc))
