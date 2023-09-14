import streamlit as st
from utilties.page_changer import changePageToLast

def UI_back_button(function = None):
    '''
    Imitates flutter's navigation style by using a stack.
    It also takes a function argument that it runs right before popping
    the current page off the stack. This function could be a problem if someone modifies the navigation stack inside of it.
    A potential fix would be to implement the navigation stack as a class and have it verify a key before allowing a stack modification.
    '''
    if function:
        function()
    st.button("**↩**", on_click=changePageToLast, help="Go back")