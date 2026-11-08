"""Nyaya Saathi: an AI legal-help assistant for everyday problems in India (Streamlit UI)."""
from __future__ import annotations

import json

import streamlit as st

from core.documents import build_notice
from core.engine import Conversation
from core.llm import LLM, load_config

st.set_page_config(page_title="Nyaya Saathi: AI legal help", page_icon="⚖️", layout="centered")

cfg = load_config()

# ------------------------------------------------------------------ sidebar: model swap + case view
with st.sidebar:
    st.header("⚙️ Model")
    providers = list(cfg["providers"])
    provider = st.selectbox("Provider", providers, index=providers.index(cfg["provider"]))
    default_model = LLM.from_config(provider).model
    model = st.text_input("Model", value=default_model)
    if st.button("🔄 New conversation", use_container_width=True) or "conv" not in st.session_state \
            or st.session_state.get("model_key") != (provider, model):
        st.session_state.conv = Conversation(LLM.from_config(provider, model))
        st.session_state.model_key = (provider, model)
        st.session_state.doc = None

    conv: Conversation = st.session_state.conv
    st.divider()
    st.header("📋 Your case")
    st.caption(f"Issue: **{conv.issue or '-'}** · Language: **{conv.lang or '-'}** · Stage: **{conv.stage}**")
    if conv.case:
        st.json(conv.case, expanded=True)
    if conv.validation_log:
        with st.expander(f"🛡️ Safety check log ({sum(len(x['removed']) for x in conv.validation_log)} removed)"):
            st.json(conv.validation_log)
    if conv.llm.log:
        calls = conv.llm.log
        st.caption(f"{len(calls)} LLM calls · {sum(c.prompt_tokens + c.completion_tokens for c in calls):,} tokens")
    st.download_button("⬇️ Download transcript (JSON)", json.dumps(conv.to_dict(), ensure_ascii=False, indent=2, default=str),
                       file_name="conversation.json", use_container_width=True)

# ------------------------------------------------------------------ main
st.title("⚖️ Nyaya Saathi")
st.caption("Free legal information for everyday problems: **deposit not returned · refund / defective product · "
           "unpaid salary · a notice you don't understand**. English, हिंदी, or Hinglish, by text or voice. "
           "Not a lawyer; it tells you when you need one.")

if not conv.history:
    with st.chat_message("assistant"):
        st.markdown("Namaste! Tell me what happened, in any language you like. Who, what, when, and how much money is involved?\n\n"
                    "_Example: \"Mere landlord ne 40,000 ka deposit wapas nahi kiya, maine March mein flat khali kiya tha.\"_")

for m in conv.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ------------------------------------------------------------------ actions after advice
if conv.issue and conv.stage == "advised" and conv.practice is None:
    c1, c2 = st.columns(2)
    if c1.button("📝 Draft legal notice", use_container_width=True):
        with st.spinner("Drafting notice..."):
            st.session_state.doc = build_notice(conv)
    if c2.button("🎭 Practise with the other side", use_container_width=True):
        conv.start_practice()
        st.rerun()

doc = st.session_state.get("doc")
if doc:
    with st.expander("📝 Legal notice draft", expanded=True):
        if doc["placeholders"]:
            st.warning("Fill these before sending: " + "; ".join(doc["placeholders"]))
        st.markdown(doc["markdown"])
        st.download_button("⬇️ Download .docx", doc["docx"], file_name="legal_notice.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        st.caption("Format and legal basis come from fixed templates; only the facts paragraphs are AI-written and checked. "
                   "Read it fully before sending. For large amounts, have a lawyer review it.")


def run(text: str):
    try:
        with st.spinner("Thinking..."):
            conv.handle(text)
    except Exception as e:  # show errors plainly instead of a stack trace
        conv.history.append({"role": "assistant", "content": f"⚠️ Something went wrong talking to the model: `{e}`. "
                             "Check the API key in `.env` or switch provider in the sidebar.", "kind": "error"})
    st.rerun()


audio = st.audio_input("🎙️ Or speak (Hindi / English / Hinglish)")
if audio is not None and st.session_state.get("last_audio") != audio.getvalue()[:64]:
    st.session_state.last_audio = audio.getvalue()[:64]
    try:
        with st.spinner("Transcribing..."):
            heard = conv.llm.transcribe(audio.getvalue(), "voice.wav")
        st.info(f"🎙️ Heard: {heard}")
        run(heard)
    except Exception as e:
        st.error(f"Voice transcription failed: {e}. Voice uses Groq Whisper (needs GROQ_API_KEY); you can type instead.")

if prompt := st.chat_input("Describe your problem, ask a question, or paste a notice..."):
    run(prompt)
