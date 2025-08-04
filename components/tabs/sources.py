import streamlit as st

from components.tabs.local_files import local_files
from components.tabs.github_repo import github_repo
from components.tabs.website import website

def sources():
    st.title("Directly import your data")
    st.caption("Convert your data into embeddings for utilization during chat")
    st.write("")

    with st.expander("💻 &nbsp; **Local Files**", expanded=False):
        local_files()

    with st.expander("🗂️ &nbsp;**GitHub Repo**", expanded=False):
        github_repo()

    with st.expander("🌐 &nbsp; **Website**", expanded=False):
        website()

    if st.button("🧹 Clear Session"):
        st.session_state.clear()
        # st.success("Session cleared! Please reload the page.")
        # st.stop()
        st.rerun()
