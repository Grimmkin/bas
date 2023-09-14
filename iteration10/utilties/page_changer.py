import streamlit as st
from streamlit_server_state import server_state, server_state_lock

# these need to be triggered
def changePageToCourse(called_by_self = False):
    key = "New Course"

    # store last page on stack
    if called_by_self:
        st.session_state.NavigationStack.append("Home")
    else:
        st.session_state.NavigationStack.append(st.session_state.view)
    st.session_state.view = key

def changePageToDatabase(called_by_self = False):
    key = "New Database"

    # store last page on stack
    if called_by_self:
        st.session_state.NavigationStack.append("Home")
    else:
        st.session_state.NavigationStack.append(st.session_state.view)
    st.session_state.view = key

def changePageToHome(called_by_self = False):
    key = "Home"

    # store last page on stack
    if called_by_self:
        st.session_state.NavigationStack.append("Home")
    else:
        st.session_state.NavigationStack.append(st.session_state.view)
    st.session_state.view = key

def changePageToHistory(called_by_self = False):
    key = "History"

    # store last page on stack
    if called_by_self:
        st.session_state.NavigationStack.append("Home")
    else:
        st.session_state.NavigationStack.append(st.session_state.view)
    st.session_state.view = key

def changePageToStudents(called_by_self = False):
    key = "Students"

    # store last page on stack
    if called_by_self:
        st.session_state.NavigationStack.append("Home")
    else:
        st.session_state.NavigationStack.append(st.session_state.view)
    st.session_state.view = key

def changePageToEvent(called_by_self = False):
    key = "Event"

    # store last page on stack
    if called_by_self:
        st.session_state.NavigationStack.append("Home")
    else:
        st.session_state.NavigationStack.append(st.session_state.view)
    st.session_state.view = key

def changePageToEnrolStudent(called_by_self = False):
    key = "New Student"

    with server_state_lock["rerun"]:
        server_state.rerun = True
    # store last page on stack
    if called_by_self:
        st.session_state.NavigationStack.append("Home")
    else:
        st.session_state.NavigationStack.append(st.session_state.view)
    st.session_state.view = key

def changePageToEventPage(called_by_self = False):
    key = "Event Page"

    if not server_state.event.event_running:
        server_state.event.start_event()

    # store last page on stack
    if called_by_self:
        st.session_state.NavigationStack.append("Home")
    else:
        st.session_state.NavigationStack.append(st.session_state.view)
    st.session_state.view = key

# special functions - forces the UI to return to previous screen
def changePageToLast():
    if len(st.session_state.NavigationStack) > 0:
        st.session_state.view = st.session_state.NavigationStack.pop()
    else:
        changePageToHome()

# these run automatically
def changePageToCourseAuto(called_by_self = False):
    changePageToCourse(called_by_self)
    st.experimental_rerun()

def changePageToDatabaseAuto(called_by_self = False):
    changePageToDatabase(called_by_self)
    st.experimental_rerun()

def changePageToHomeAuto(called_by_self = False):
    changePageToHome(called_by_self)
    st.experimental_rerun()

def changePageToHistoryAuto(called_by_self = False):
    changePageToHistory(called_by_self)
    st.experimental_rerun()

def changePageToStudentsAuto(called_by_self = False):
    changePageToStudents(called_by_self)
    st.experimental_rerun()

def changePageToEventAuto(called_by_self = False):
    changePageToEvent(called_by_self)
    st.experimental_rerun()

def changePageToEnrolStudentAuto(called_by_self = False):
    changePageToEnrolStudent(called_by_self)
    st.experimental_rerun()

def changePageToEventPageAuto(called_by_self = False):
    changePageToEventPage(called_by_self)
    st.experimental_rerun()