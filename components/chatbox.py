import streamlit as st

from utils.ollama import chat, context_chat

from deep_translator import GoogleTranslator
translator = GoogleTranslator(source='auto', target='ja')
def chatbox():
    if prompt := st.chat_input("How can I help?"):
        # Prevent submission if Ollama endpoint is not set
        translated = translator.translate(prompt)
        if not st.session_state["query_engine"]:
            st.warning("Please confirm settings and upload files before proceeding.")
            st.stop()

        # Add the user input to messages state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate llama-index stream with user input
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response = st.write_stream(
                    # chat(
                    #     prompt=prompt
                    # )
                    context_chat(
                        prompt=translated, query_engine=st.session_state["query_engine"]
                    )
                )

        # Add the final response to messages state
        st.session_state["messages"].append({"role": "assistant", "content": translator.translate(response)})
