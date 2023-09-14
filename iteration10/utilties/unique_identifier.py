import platform
import uuid
import hashlib
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from datetime import datetime

def gen_id_by_time():
    '''Generates a unique session id based on time... There's an extremely slim chance two sessions could get the same id if two sessions join the server at the same time'''
    
    # Converting the system information to string
    system_info = platform.uname()

    current_time = datetime.now()

    # Converting the system information and current time to string
    info_str = str(system_info) + str(current_time)

    # Generate a UUID using the string
    unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, info_str)

    # Converting the UUID to a SHA256 hash
    unique_key = hashlib.sha256(str(unique_id).encode()).hexdigest()

    return unique_key

def gen_id():
    '''Generates a unique session id based on time... There's an extremely slim chance two sessions could get the same id if two sessions join the server at the same time'''
    
    # Converting the system information to string
    system_info = platform.uname()

    # Converting the system information to string
    info_str = str(system_info)

    # Generate a UUID using the string
    unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, info_str)

    # Converting the UUID to a SHA256 hash
    unique_key = hashlib.sha256(str(unique_id).encode()).hexdigest()

    return unique_key

def get_session_id() -> str:
    '''Obtains the id of that session directly from streamlit. This method is the safer of the two, but/as it uses internal functions from streamlit itself'''
    ctx = get_script_run_ctx()
    return ctx.session_id