import streamlit as st

from utils.ollama import chat, context_chat

from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='auto', target='ja')

def custom_tooltip(text, tooltip_text, position="top"):
    return f"""
    <style>
    .tooltip {{
        position: relative;
        display: inline-block;
        padding: 1px;  /* Thêm padding để tạo vùng đệm */
        cursor: pointer;
    }}
    
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: {'125%' if position == 'top' else 'auto'};
        top: {'125%' if position == 'bottom' else 'auto'};
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s, visibility 0.3s;  /* Thêm transition cho visibility */
        font-size: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        pointer-events: auto;  /* Cho phép tương tác với tooltiptext */
    }}
    
    .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
    }}
    
    /* Tạo một pseudo-element để mở rộng vùng hover */
    .tooltip::after {{
        content: '';
        position: absolute;
        width: 100%;
        height: 20px;
        bottom: {'-20px' if position == 'top' else 'auto'};
        top: {'-20px' if position == 'bottom' else 'auto'};
        left: 0;
    }}
    </style>
    
    <div class="tooltip">{text}
        <span class="tooltiptext">{tooltip_text}</span>
    </div>
    """

def chatbox():
    if prompt := st.chat_input("How can I help?"):
        translated = translator.translate(prompt)
        if (not st.session_state["query_engine"]) and (not st.session_state["use_uploaded_vectordb"]):
            st.warning("Please confirm settings and upload files before proceeding.")
            st.stop()

        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                response, source = context_chat(
                        prompt=translated, query_engine=st.session_state["query_engine"]
                    )
                st.write(response)
                st.markdown(custom_tooltip("1", f"{source[0].node.text}"), unsafe_allow_html=True)

        st.session_state["messages"].append({"role": "assistant", "content": "".join(response)})
