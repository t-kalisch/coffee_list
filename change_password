import streamlit as st
import coffee_list


PAGES = {
    "App1": app1,
    "App2": app2
}st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()
