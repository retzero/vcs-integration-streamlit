import streamlit as st
from page.login_page import login_page
from page.signup_page import signup_page
from page.app import app_page
from utils.init_session import init_session, reset_session

init_session()

st.session_state['extra_input_params'] = {
}

for input_param in st.session_state['extra_input_params'].keys():
    if input_param not in st.session_state:
        st.session_state[input_param] = None

if st.session_state['authenticated']:
    app_page()
else:
    #FIXME:
    if True:
        st.session_state['guest_mode'] = True
        st.session_state['authenticated'] = True
        st.session_state['page'] = 'app'
        st.rerun()
    elif st.session_state['page'] == 'login':
        reset_session()
        login_page(guest_mode=True)
    elif st.session_state['page'] == 'signup':
        signup_page(
            extra_input_params=False,
            confirmPass = True
        )
