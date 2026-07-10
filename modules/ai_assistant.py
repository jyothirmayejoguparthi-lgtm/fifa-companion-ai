import streamlit as st
from utils.llm_client import ask_assistant
from utils.i18n import t
from utils.error_handling import safe_render


@safe_render("AI Assistant")
def render(role: str, lang: str, lang_name: str):
    st.markdown(f"### 🤖 {t('nav_ai_assistant', lang)}")
    st.info(
        "Helping FIFA World Cup 2026 fans, volunteers, organizers and staff "
        "navigate stadiums, transportation, accessibility, crowd management "
        "and emergency services."
    )

    question = st.text_input(
        t("ask_placeholder", lang),
        key="ai_question_input",
        help="Ask about washrooms, gates, medical help, transport, or accessibility.",
    )

    ask_clicked = st.button(t("ask_button", lang), key="ask_ai_btn")

    if ask_clicked and question.strip():
        with st.spinner(t("loading", lang)):
            try:
                answer = ask_assistant(question, role=role, lang_name=lang_name)
            except Exception as e:
                answer = f"Sorry, something went wrong answering that. ({e})"

        st.session_state.chat_history.append((question, answer))

    # Render chat history, most recent first
    for q, a in reversed(st.session_state.chat_history[-5:]):
        st.markdown(f"**You:** {q}")
        st.success(a)

        if st.session_state.get("read_aloud"):
            _render_tts(a)


def _render_tts(text: str):
    """Browser-native text-to-speech using the Web Speech API (no external deps)."""
    safe_text = text.replace('"', '\\"').replace("\n", " ")
    st.components.v1.html(
        f"""
        <script>
        const msg = new SpeechSynthesisUtterance("{safe_text}");
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
        </script>
        """,
        height=0,
    )
