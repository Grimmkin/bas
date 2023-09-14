import streamlit as st
import serial, threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit_server_state import server_state, server_state_lock

def initialize_device():
    #validation can be done here
    try:
        server_state.device = serial.Serial("COM5", 9600)
        st.toast("Device connected successfully", icon="🔗")
        #st.toast(st.session_state.device.readline().decode().strip(), icon="🎉")
    except:
        server_state.device = None
        st.toast("Device failed to connect", icon="🚫")

def check_thread_status():
    if server_state.thread:
        if server_state.thread.is_alive():
            st.toast("Thread is alive", icon="💗")
        else:
            st.toast("Thread terminated", icon="💀")

# threading functions responsible for enrol-------------------------------------------------------------------------------------------------------------
def enrol():
    server_state.device.write(b"#")
    while True:
        try:
            result = server_state.device.readline().decode().strip()
            break
        except:
            st.toast("Device disconnected, terminating", icon="💀")
            return
        
    #lots of error handling to be done here
    with server_state_lock.rerun:
        server_state.rerun = False
    
    with server_state_lock.device_id:
        server_state.device_id = result
    return

def start_enrol():
    if server_state.thread is None or not server_state.thread.is_alive():
        if server_state.device != None:
            if server_state.thread is None or not server_state.thread.is_alive():
                server_state.thread = threading.Thread(target=enrol)
                add_script_run_ctx(server_state.thread)
                server_state.thread.start()
        else:
            st.toast("Device is not connected", icon="🚫")
            return
    
    # if thread is alive ===========================================================

    # stop burst mode on device
    print("stopping burst mode...enrol")
    server_state.device.write(b"!")
    
# threading functions responsible for burst mode-------------------------------------------------------------------------------------------------------------
def burst_mode():

    check_thread_status()

    print("starting burst mode...")
    server_state.device.write(b"_")

    # lots of error handling to be done here
    while server_state.thread_key == True:
        if server_state.device:
            result = server_state.device.readline()
            with server_state_lock.event:
                server_state.event.check_in(result.decode().strip())
        else:
            pass
    
def toggle_burst_mode():
    # toggle burst mode
    if server_state.thread is None or not server_state.thread.is_alive(): 
        if server_state.device:
            with server_state_lock.thread_key:
                server_state.thread_key = True

            server_state.thread = threading.Thread(target=burst_mode)
            add_script_run_ctx(server_state.thread)
            with server_state_lock.thread:
                server_state.thread.start()
            return
        else:
            st.toast("Device is not connected", icon="🚫")
            return
    
    # if thread is alive ===========================================================

    # stop burst mode on device
    print("stopping burst mode...")
    server_state.device.write(b"!")

    # terminate thread
    with server_state_lock.thread_key:
        server_state.thread_key = False