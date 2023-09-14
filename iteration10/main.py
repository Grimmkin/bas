import dearpygui.dearpygui as dpg
from utils.window_functions import calculate_window_position_dimensions

from plyer import notification
from pickle import load
from glob import glob
from threading import Thread
from requests import post, get, exceptions
from json import dumps

from classes.event import Event
from classes.course import Course
from classes.schedule import Schedule
from classes.student import StudentModel
from classes.department import Department
from classes.validation import ValidationError

from utils.date_and_time_funcs import get_current_time
from utilties.unique_identifier import gen_id
from utils.get__ip_address import get_ip
from utils.data import random_student

import server
import uvicorn
import websocket
import json

import socket as sckt

import time, serial, threading
from serial.tools import list_ports

# ========================================================================== INITIALIZATIONS ==================================================================================================
thread_server = None
server_thread = None
scanner = None
thread_flag = False
burst_thread = None

socket = None
signature = gen_id()
socket_thread = None

active = "default"
sockets = {
    "default": None,
    "external": None,
}

event = {
    "event_title":"",
    "event_code": ""
}

# ========================================================================== DATA ======================================================================================================
# load schedule
try:
    with open("./data/schedule.obas", 'rb') as f:
        schedule = load(f)
except FileNotFoundError:
    schedule = Schedule()

departments = glob("./data/departments/*.dpt")
if len(departments) > 0:
    try:
        with open(departments[0], 'rb') as dpt:
            department = load(dpt)
            notification.notify(
                title = f"{department.database} loaded",
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )       
    except Exception as e:
        print(Exception)
        department = None
        notification.notify(
            title = "Failed to load department",
            app_name = "Attendance System",
            message = " ",
            app_icon = None,
            timeout = 0,
        )   
else:
    department = None
    notification.notify(
        title = "No Departments found",
        app_name = "Attendance System",
        message = " ",
        app_icon = None,
        timeout = 0,
    )

# ========================================================================== EVENTS ====================================================================================================
class Events:
    def __init__(self):
        with dpg.tab(label = "Events", tag = "events_tab"):
            dpg.add_spacer(height=10)
            with dpg.group(horizontal = True):
                with dpg.child_window(border = False, width = 450, show = True, no_scrollbar = True):
                    with dpg.child_window(border = True, width = -1, height = 178, show = True, no_scrollbar = True):
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "?".rjust(12),
                            )
                            dpg.add_button(label = "Create/Join Event", width = -1, callback = summon_create_event_window)

                        dpg.add_separator()

                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "Event Title".rjust(12),
                            )
                            events_held = dpg.add_input_text(default_value="", tag="event_title", width=-1)
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "Event Code".rjust(12),
                            )
                            events_on_network = dpg.add_input_text(default_value="", tag="event_code", width=-1)
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "Present".rjust(12),
                            )
                            events_held = dpg.add_input_text(default_value="", tag="present", width=-1)

                        dpg.add_separator()

                        dpg.add_checkbox(
                            label="Allow check in for students",
                            default_value=True,
                            tag="student_check_in",
                        )

                        dpg.add_checkbox(
                            label="Allow check in for staff",
                            default_value=False,
                            tag="staff_check_in",
                        )

                        dpg.add_checkbox(
                            label="Allow participants to check out",
                            default_value=False,
                            tag="sign_out",
                        )
                    with dpg.child_window(tag="servers_table", border = False, width = 450, show = True, no_scrollbar = True):
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "Active Server".rjust(16),
                            )
                            dpg.add_input_text(default_value="", tag="active_server", width=-1)
                        self.load_servers()
                        

                with dpg.child_window(border = False, width = -1, show = True, no_scrollbar = True):
                    with dpg.child_window(border = True, width = -1, height = 104, show = True, no_scrollbar = True):
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "Last Checked In".rjust(16),
                            )
                            events_held = dpg.add_input_text(default_value="", tag="last_checked_in", width=-1)
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "Check In Time".rjust(16),
                            )
                            events_held = dpg.add_input_text(default_value="", tag="check_in_time", width=-1)
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "S/ID".rjust(16),
                            )
                            events_on_network = dpg.add_input_text(default_value="", tag="scanner_id", width=-1)

                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "?".rjust(16),
                            )
                            dpg.add_button(label = "Start Check in", width = -1, tag="burst_mode_button", callback=self.check_in)
                    with dpg.child_window(border = False, width = -1, height = -1, show = True, tag="attendance"):
                        Events.populate_event()

    def check_in(self):
        student = random_student()

        msg = {"action":"check_in", "checkin_data":student}
        try:
            sockets[active].send(json.dumps(msg))
        except Exception as e:
            print(str(e))

    @staticmethod
    def populate_event(data = None):
        if dpg.does_item_exist("attendance_table"):
            dpg.delete_item("attendance_table")

        with dpg.table(
            parent="attendance",
            borders_outerV=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_innerH=True,
            scrollY=True,
            freeze_rows=1,
            tag="attendance_table",
        ):
            dpg.add_table_column(
                label="First Name",
            )
            dpg.add_table_column(
                label="Last Name",
            )
            dpg.add_table_column(
                label="S/ID",
                width_fixed=True,
            )
            dpg.add_table_column(
                label="Department",
            )
            dpg.add_table_column(
                label="Staff/Student",
                width_fixed=True,
            )
            dpg.add_table_column(
                label="Check In",
                width_fixed=True,
            )
            dpg.add_table_column(
                label="Check out",
                width_fixed=True,
            )
        try:
            event_state = get_event(raw=True)
        except:
            pass

        if data:
            dpg.configure_item("event_title", default_value = data["event_title"])
            dpg.configure_item("event_code", default_value = data["event_code"])

        if event_state:
            print(f"Attendance Table: {event_state}")
            for person in event_state:
                Events.add_person(person)

    def connect(self, disconnect = False):
        global sockets, active
        ip = dpg.get_value("external_ip_address")
        uri = f"ws://{ip}/ws"
        
        try:
            if disconnect:
                raise Exception
            socket = websocket.create_connection(uri)
            # assign default key to socket
            sockets["external"] = socket
            # set active socket to default
            active = "external"
            print("switched")
        except Exception as e:
            print(str(e))
            sockets["external"] = None
            active = "default"

        Events.load_servers()

    @staticmethod
    def add_person(data):
        with dpg.table_row(parent="attendance_table"):
            dpg.add_selectable(label=data["first_name"])
            dpg.add_selectable(label=data["last_name"])
            dpg.add_selectable(label=data["id"])
            dpg.add_selectable(label=data["check in"])
            dpg.add_selectable(label=data["check out"])

    @staticmethod
    def switch_server(sender):
        label = dpg.get_item_label(sender)
        if sockets[label]:
            active = label
            Events.populate_event()

    @staticmethod
    def load_servers():
        dpg.configure_item("active_server", default_value=active.capitalize())
        if dpg.does_item_exist("servers"):
            dpg.delete_item("servers")

        with dpg.table(
            parent="servers_table",
            borders_outerV=True,
            borders_outerH=True,
            borders_innerV=True,
            borders_innerH=True,
            header_row=True,
            tag="servers",
        ):
            dpg.add_table_column(label="Server")
            dpg.add_table_column(label="Status")
            dpg.add_table_column(label="Connection")
            # Add new row to table in the UI
        
        # Default server
        with dpg.table_row(parent="servers"):
            dpg.add_selectable(label="default", callback=Events.switch_server)
            dpg.add_selectable(label="Active" if sockets["default"] else "Inactive")
            dpg.add_selectable(label=get_ip())

        # External server
        with dpg.table_row(parent="servers"):
            dpg.add_selectable(label="external", callback=Events.switch_server)
            dpg.add_input_text(default_value="Active" if sockets["external"] else "", tag="external_ip_address", width=-1, before="http://")
            dpg.add_button(label="Disconnect" if sockets["external"] else "Connect", width=-1, callback=Events.connect, user_data = (False if sockets["external"] else True,),)

# ========================================================================== STUDENTS ==================================================================================================
class Students:
    def __init__(self):
        self.edit = False if department else True
        self.justify = 24
        with dpg.tab(label = "Students/Staff", tag = "students_tab"):
            dpg.add_spacer(height=10)
            with dpg.group(horizontal = True):
                with dpg.child_window(border = False, width = 600, show = True, no_scrollbar = True):
                    with dpg.child_window(border = True, width = 600, height = 82, show = True, no_scrollbar = True):
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "Number of registered students".rjust(32),
                            )
                            number_of_registered_students = dpg.add_input_text(default_value="", tag="number_of_registered_students", width=-1)

                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "Number of registered staff".rjust(32),
                            )
                            number_of_registered_staff = dpg.add_input_text(default_value="", tag="number_of_registered_staff", width=-1)

                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                "?".rjust(32),
                            )
                            dpg.add_button(label = "Register Student", width = -1)

                    # dpg.add_separator()
                    with dpg.child_window(border = False, width = 600, height = -1, show = True,):
                        with dpg.table(
                            borders_outerV=True,
                            borders_outerH=True,
                            borders_innerV=True,
                            borders_innerH=True,
                            scrollY=True,
                            freeze_rows=1,
                            tag="students_table",
                        ):
                            
                            dpg.add_table_column(
                                label="S/ID",
                                width_fixed=True,
                            )
                            dpg.add_table_column(
                                label="First Name",
                            )
                            dpg.add_table_column(
                                label="Last Name",
                            )
                            dpg.add_table_column(
                                label="D/ID",
                                width_fixed=True,
                            )
                            dpg.add_table_column(
                                label="Sex",
                                width_fixed=True,
                            )
                        load_students()

                dpg.add_spacer(width=5)
                with dpg.child_window(width=-1,tag="control_panel", border=True, height=-1):

                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            "DEPARTMENT CODE".rjust(self.justify),
                        )
                        dpg.add_input_text(default_value=department.code if department else "", tag="department_code", width=-1)

                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            "DEPARTMENT NAME".rjust(self.justify),
                        )
                        dpg.add_input_text(default_value=department.name if department else "", tag="department_name", width=-1)

                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            "DEPARTMENT FACULTY".rjust(self.justify),
                        )
                        dpg.add_input_text(default_value=department.faculty if department else "", tag="department_faculty", width=-1)

                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            "DEPARTMENT LEVEL".rjust(self.justify),
                        )
                        dpg.add_combo(
                            default_value=department.level if department else "100",
                            items=["100", "200", "300", "400", "500", "600"],
                            width=-1,
                            tag='department_level'
                        )

                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            "?".rjust(self.justify),
                        )
                        dpg.add_button(tag="create_department", label = "Edit Info" if department else "Create Department", width = -1, callback=edit_department if department else create_department)

                    dpg.add_spacer(height=5)

                    dpg.add_separator()

                    dpg.add_spacer(height=5)
                                   
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            "NUMBER OF COURSES".rjust(self.justify),
                        )
                        dpg.add_input_text(default_value="0", tag="department_no_of_courses", width=-1)
                        
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            "?".rjust(self.justify),
                        )
                        dpg.add_button(label = "Add Course", width = -1, callback=summon_add_course_window)

                    dpg.add_spacer(height=10)

                    with dpg.child_window(border = False, width = -1, height = -1, show = True,):
                        with dpg.group(horizontal=True, tag="courses_table_group"):
                            dpg.add_text(
                                "...".rjust(self.justify),
                            )
                            load_courses()
# ========================================================================== REGISTER STUDENT ==========================================================================================
class RegisterStudent:
    def __init__(self):
        self.tag = "register_student"
        self.justify = 14
        if department:
            x, y, w, h = calculate_window_position_dimensions(500, 220)
            with dpg.window(
                label="Register Student/Staff",
                modal=True,
                pos=(x, y),
                width=w,
                height=h,
                no_move=False,
                no_resize=True,
                on_close=self.close,
                tag=self.tag,
            ):
                with dpg.tab_bar():
                    self.register_student()
                    self.register_staff()
        else:
            notification.notify(
                title = "❌ A department hasn't been created",
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            

    def register_student(self):
        with dpg.tab(label = "Register Student", tag = "register_student_tab"):
            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Device ID".rjust(self.justify)
                ),
                dpg.add_checkbox(tag="device_id_check", default_value=False, enabled=False)
                dpg.add_input_text(tag="device_id", default_value="?", enabled=False, width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "?".rjust(self.justify),
                )
                dpg.add_button(label="Enrol Fingerprint", width=-1, callback=enrol)

            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "First Name".rjust(self.justify),
                )
                first_name = dpg.add_input_text(default_value="", tag="first_name", width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Last Name".rjust(self.justify),
                )
                last_name = dpg.add_input_text(default_value="", tag="last_name", width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Matric ID".rjust(self.justify),
                )
                id = dpg.add_input_int(default_value=0, tag="id", width=-1)
                
            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Gender".rjust(self.justify),
                    tag=dpg.generate_uuid()
                )
                gender = dpg.add_combo(
                    default_value="Male",
                    items=["Male", "Female"],
                    width=-1,
                    tag='student_gender'
                )

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "?".rjust(self.justify),
                )
                dpg.add_button(tag="register_student_button", label="Submit", width=-1, callback=self.create_student)

    def register_staff(self):
        with dpg.tab(label = "Register Staff", tag = "register_staff_tab"):
            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Device ID".rjust(self.justify)
                ),
                dpg.add_checkbox(tag="staff_device_id_check", default_value=False, enabled=False)
                dpg.add_input_text(tag="staff_device_id", default_value="?", enabled=False, width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "?".rjust(self.justify),
                )
                dpg.add_button(label="Enrol Fingerprint", width=-1)

            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "First Name".rjust(self.justify),
                )
                first_name = dpg.add_input_text(default_value="", tag="staff_first_name", width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Last Name".rjust(self.justify),
                )
                last_name = dpg.add_input_text(default_value="", tag="staff_last_name", width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Gender".rjust(self.justify),
                    tag=dpg.generate_uuid()
                )
                gender = dpg.add_combo(
                    default_value="Male",
                    items=["Male", "Female"],
                    width=-1,
                    tag='staff_gender'
                )

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Email".rjust(self.justify),
                )
                email = dpg.add_input_text(tag="email", width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "?".rjust(self.justify),
                )
                dpg.add_button(label="Submit", width=-1, )

    def close(self):
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)

    
    def create_student(self):
        # Try to create the StudentModel
        dpg.configure_item("register_student_button", enabled=False)
        try:
            student = StudentModel(
                first_name=dpg.get_value("first_name"),
                last_name=dpg.get_value("last_name"),
                id=dpg.get_value("id"),
                device_id=dpg.get_value("device_id"),
                sex=dpg.get_value("student_gender"),
            )

            department.add_student(student.__dict__)
            notification.notify(
                title = '🎉 Student registered successfully',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )

            dpg.configure_item("first_name", default_value="")
            dpg.configure_item("last_name", default_value="")
            dpg.configure_item("id", default_value=0)
            dpg.configure_item("device_id", default_value="?")
            dpg.configure_item("student_gender", default_value="Male")
            dpg.configure_item("device_id_check", default_value="False")

            load_students()

            return
        
        except ValidationError as e:
            notification.notify(
                title = f'❌ {e.message}',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
        finally:
            dpg.configure_item("register_student_button", enabled=True)
# ========================================================================== CREATE EVENT ==============================================================================================
class CreateEvent:
    def __init__(self):
        self.tag = "create_event"
        self.justify = 14
        x, y, w, h = calculate_window_position_dimensions(500, 127)
        with dpg.window(
            label="Create/Join Event",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            no_move=False,
            no_resize=True,
            on_close=self.close,
            tag=self.tag,
        ):
            self.create_native_event()

    def create_native_event(self):
        with dpg.group(horizontal=True):
            dpg.add_text(
                "Event Code".rjust(self.justify),
            )
            dpg.add_combo(
                items = [i["course_code"] for i in schedule.get_courses()] + ["MISCELLANOUS"],
                width=-1,
                tag='event_code_registration',
                callback=self.populate_event_title
            )

        with dpg.group(horizontal=True):
            dpg.add_text(
                "Event Title".rjust(self.justify),
            )
            dpg.add_input_text(default_value="", tag="event_title_registration", width=-1)

        with dpg.group(horizontal=True):
            dpg.add_text(
                "?".rjust(self.justify),
            )
            dpg.add_button(label="Create Event", tag="send_event_to_server", width=-1, callback=self.create_event_via_socket)

    def event_join(self):
        dpg.configure_item("event_join", label = "...")
        dpg.configure_item("send_event_to_server", enabled = False)
        event = get_event()
        if event:
            notification.notify(
                title = f'🎉 Found Event',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            dpg.configure_item("event_code_join", default_value = event["event_code"])
            dpg.configure_item("event_title_join", default_value = event["event_title"])

            dpg.configure_item("event_join", label = "Confirm Event", callback = self.confirm_event)
            # dpg.configure_item("event_join", callback = self.confirm_event)
            return

        notification.notify(
            title = f'❌ Unable to connect to server',
            app_name = "Attendance System",
            message = " ",
            app_icon = None,
            timeout = 0,
        )
        dpg.configure_item("event_join", label = "Join Event")

    def create_server(self):
        global thread_server, socket
        if socket:
            try:
                server_signature = socket.send({"action":"signature"})
                if server_signature == signature:
                    # a server by this client already exists
                    return True
            except:
                # whatever the error
                pass

        try:
            # Getting here means an error either happened or a server doesn't exist
            thread_server = uvicorn.run(server.app, host='0.0.0.0', port=5000)

            # connect the client to the server
            self.join_server()
            return True
        except:
            socket = None
            return False
    
    def join_server(self):
        global socket
        try:
            uri = "ws://localhost:8000/ws"
            socket = websocket.create_connection(uri)
            return True
        except Exception as e:
            notification.notify(
                title = f'{e}',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            return False
    
    # def join_event(self):
    #     if not socket:
    #         if self.join_server() == False:
    #             return
    #     socket_thread = threading.Thread(target=socket_func, daemon=True)
    #     socket_thread.start()
    #     try:
    #         socket.send(json.dumps({"action":"get_event"}))
    #     except Exception as e:   
    #         notification.notify(
    #             title = f"{e}",
    #             app_name = "Attendance System",
    #             message = " ",
    #             app_icon = None,
    #             timeout = 0,
    #         )

    def create_event_via_socket(self):
        try:
            event = Event(
                event_code=dpg.get_value("event_code_registration"),
                event_title=dpg.get_value("event_title_registration"),
            )

            msg = {"action": "create_event", "event":event.__dict__}
            sockets[active].send(json.dumps(msg))
            time.sleep(0.1)
            listener_updates = eval(dpg.get_value("server_updates_event_creation"))
            if listener_updates['message'] == "Event created successfully" and listener_updates['uid'] == signature:
                notification.notify(
                    title = "🎉 Event created!",
                    app_name = "Attendance System",
                    message = " ",
                    app_icon = None,
                    timeout = 0,
                )
                self.close()
                pull_event_info_from_server()
            else:
                notification.notify(
                    title = "❌ Unable to create event!",
                    app_name = "Attendance System",
                    message = " ",
                    app_icon = None,
                    timeout = 0,
                )
            dpg.configure_item("server_updates_event_creation", default_value = "...")
        except ValidationError as e:
            notification.notify(
                title = f'{e}',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )

    def create_event(self):
        global socket
        if not socket:
            if self.create_server() == False:
                notification.notify(
                    title = "Unable to create server. Please restart application",
                    app_name = "Attendance System",
                    message = " ",
                    app_icon = None,
                    timeout = 0,
                )
                return
            
        try:
            server_signature = socket.send(json.dumps({"action":"get_signature"}))
            if server_signature == signature:
                event = Event(
                    event_code=dpg.get_value("event_code_registration"),
                    event_title=dpg.get_value("event_title_registration"),
                )

                event = {"action": "create_event", "event":event.__dict__}
                
                socket.send(json.dumps(event))
                notification.notify(
                    title = f'{e}',
                    app_name = "Attendance System",
                    message = " ",
                    app_icon = None,
                    timeout = 0,
                )
                return
            
        except ValidationError:
            notification

        except Exception as e:
            notification.notify(
                title = f'{e}',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
        
    def populate_event_title(self):
        if dpg.get_value("event_code_registration") != "MISCELLANOUS":
            dpg.configure_item("event_title_registration", default_value = [i["course_title"] for i in schedule.get_courses() if i["course_code"] == dpg.get_value("event_code_registration")][0])
        else:
            dpg.configure_item("event_title_registration", default_value = "")

    def close(self):
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
# ========================================================================== ADD COURSE ================================================================================================
class AddCourse:
    def __init__(self):
        self.days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        self.tag = "add_course"
        self.justify = 14
        x, y, w, h = calculate_window_position_dimensions(500, 290)
        with dpg.window(
            label="Add New Course",
            modal=True,
            pos=(x, y),
            width=w,
            height=h,
            no_move=False,
            no_resize=True,
            on_close=self.close,
            tag=self.tag,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Course Code".rjust(self.justify),
                )
                event_code = dpg.add_input_text(default_value="", tag="course_code_creation", width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "Course Title".rjust(self.justify),
                )
                event_title = dpg.add_input_text(default_value="", tag="course_title_creation", width=-1)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "...".rjust(self.justify),
                )
                dpg.add_text(
                    "Days this course will hold".rjust(self.justify),
                )

            for i in self.days:
                with dpg.group(horizontal=True):
                    dpg.add_text(
                        "...".rjust(self.justify),
                    )
                    dpg.add_checkbox(label=i.capitalize(), tag=i, default_value=False)

            with dpg.group(horizontal=True):
                dpg.add_text(
                    "?".rjust(self.justify),
                )
                dpg.add_button(label="Add Course", width=-1, callback=self.create_course)

    def create_course(self):
        try:
            course = Course(
                course_code=dpg.get_value("course_code_creation"),
                course_title=dpg.get_value("course_title_creation"),
                days= [i for i in self.days if dpg.get_value(i)]
            )

            schedule.add_to_schedule(course=course)
            load_courses()
            notification.notify(
                title = f'Event created successfully!🎉',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            self.close()
            return

        except ValidationError as e:
            notification.notify(
                title = f'❌ {e.message}',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            return
        
    def close(self):
        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
# ========================================================================== FUNCTIONS =================================================================================================

def summon_register_student_window():
    RegisterStudent()

def summon_create_event_window():
    CreateEvent()

def summon_add_course_window():
    AddCourse()

def add_course(courses):
    with dpg.table_row(parent="courses"):
        for course in courses:
            with dpg.child_window(border=True, height=59):
                with dpg.group(horizontal=True):
                    dpg.add_text(
                        "Course Code".rjust(12),
                    )
                    
                    with dpg.theme() as theme:
                        with dpg.theme_component(0):
                            dpg.add_theme_color(dpg.mvThemeCol_Text, (47, 129, 247), category=dpg.mvThemeCat_Core)
                    dpg.add_input_text(default_value=course["course_code"], width=-1, enabled=False)
                    dpg.bind_item_theme(dpg.last_item(), theme)

                with dpg.group(horizontal=True):
                    dpg.add_text(
                        "Course Title".rjust(12),
                    )
                    
                    with dpg.theme() as theme:
                        with dpg.theme_component(0):
                            dpg.add_theme_color(dpg.mvThemeCol_Text, (63, 185, 80), category=dpg.mvThemeCat_Core)
                    dpg.add_input_text(default_value=course["course_title"], width=-1, enabled=False)
                    dpg.bind_item_theme(dpg.last_item(), theme)

def split_into_threes(lis):
    start = 0
    end = 3
    main = []
    runs = int(len(lis)/3 +1 if len(lis)%3 != 0 else len(lis)/3)
    for i in range(runs):
        main.append(lis[start:end])
        start+=3
        end+=3
    return main


def load_courses():
    if dpg.does_item_exist("courses"):
        dpg.delete_item("courses")

    with dpg.table(
        parent="courses_table_group",
        borders_outerV=False,
        borders_outerH=False,
        borders_innerV=False,
        borders_innerH=False,
        scrollY=True,
        header_row=False,
        tag="courses",
    ):
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()

    courses = schedule.get_courses()
    dpg.configure_item("department_no_of_courses", default_value=len(courses))
    courses = split_into_threes(courses)
    if courses:
        for course in courses:
            add_course(course)

def edit_department():
    if department:
        if department.update_info(
            {
                "name":dpg.get_value("department_name"),
                "code":dpg.get_value("department_code"),
                "level":dpg.get_value("department_level"),
                "faculty":dpg.get_value("department_faculty"),
            }
        ):
          notification.notify(
            title = f"DEPARTMENT INFO UPDATED!",
            app_name = "Attendance System",
            message = " ",
            app_icon = None,
            timeout = 0,
        )
        else:
            dpg.configure_item("department_name", default_value = department.name)
            dpg.configure_item("department_code", default_value = department.code)
            dpg.configure_item("department_level", default_value = department.level)
            dpg.configure_item("department_faculty", default_value = department.faculty)

def create_department():
    global department
    try:
        department = Department(
            name = dpg.get_value("department_name"),
            code = dpg.get_value("department_code"),
            level = dpg.get_value("department_level"),
            faculty= dpg.get_value("department_faculty"),
        )
        dpg.configure_item("create_department", callback = edit_department)
        dpg.configure_item("create_department", label = "Edit Info")
        notification.notify(
            title = f"DEPARTMENT CREATED!",
            app_name = "Attendance System",
            message = " ",
            app_icon = None,
            timeout = 0,
        )
        return
    except ValidationError as e:
        department = None
        dpg.configure_item("create_department", enabled = True)
        notification.notify(
            title = f"{e.message}",
            app_name = "Attendance System",
            message = " ",
            app_icon = None,
            timeout = 0,
        )

def clb_selectable(sender, user_data):
    print(f"Content:{dpg.get_item_label(sender)}, Row and column: {user_data}")

def add_student(row):
    # Add new row to table in the UI
    with dpg.table_row(parent="students_table"):
        dpg.add_selectable(label=row["device_id"], callback=clb_selectable, user_data=(row))
        dpg.add_selectable(label=row["first_name"], callback=clb_selectable, user_data=(row))
        dpg.add_selectable(label=row["last_name"], callback=clb_selectable, user_data=(row))
        dpg.add_selectable(label=str(row["id"]), callback=clb_selectable, user_data=(row))
        dpg.add_selectable(label="M" if row["sex"] == "Male" else "F", callback=clb_selectable, user_data=(row))

def load_students():
    if department:
        for student in department.students.values():
            add_student(student)

# server functions
def event_connect():
    if thread_server is None:
        event = get_event()
    # pull_info_from_server()
        
def burst_mode():
    global scanner
    global event
    global thread_flag
    # print("starting burst mode...")
    # scanner.write(b"Stop\n")
    # time.sleep(0.5)
    scanner.write(b"BurstVerify\n")
    # lots of error handling to be done here
    while thread_flag:
        try:
            result = scanner.readline().decode().strip()
            print(result)
            try:
                result = int(result)
                print(result)
                check_in(result)
            except ValueError:
                pass

        except serial.serialutil.SerialException:
            # terminate thread
            thread_flag = False
            thread = None
            dpg.configure_item("burst_mode_button", label="Start Check In")
    
def toggle_burst_mode():
    global burst_thread
    global thread_flag

    # toggle burst mode
    if burst_thread is None or not burst_thread.is_alive():
        if scanner:
            thread_flag = True
            burst_thread = threading.Thread(target=burst_mode, daemon=True)
            burst_thread.start()
            dpg.configure_item("burst_mode_button", label="Stop Check In...")
            return
        else:
            notification.notify(
                title = '❌ Scanner is not connected',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            dpg.configure_item("burst_mode_button", label="Start Check In")
            return
        
    print(burst_thread)
    print(f"burst_thread is alone: {burst_thread.is_alive}")
        
    # if thread is alive ===========================================================
    print("Killing thread")
    # stop burst mode on device
    print("stopping burst mode...")
    scanner.write(b"!")

    # terminate thread
    thread_flag = False
    burst_thread = None
    dpg.configure_item("burst_mode_button", label="Start Check In")

def get_event(raw=False):
    if raw:
        url = 'http://localhost:10000/get_event_raw'
    else:    
        url = 'http://localhost:10000/get_event'

    try:
        response = get(url)
        response.raise_for_status()
        event = response.json()
        return event
    except exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
def pull_event_info_from_server():
    point = "server_updates_event_info"
    sockets[active].send(json.dumps({"action":"get_event"}))
    time.sleep(0.1)
    info = eval(dpg.get_value(point))
    dpg.configure_item("event_title", default_value = info["event_title"])
    dpg.configure_item("event_code", default_value = info["event_code"])
    dpg.configure_item(point, default_value = "...")

def create_event_http():
    try:
        event = Event(
            event_code=dpg.get_value("event_code_registration"),
            event_title=dpg.get_value("event_title_registration"),
        )

        url = "http://localhost:5000/create_event"
        data = event.__dict__
        headers = {'Content-type': 'application/json'}

        response = post(url, data=dumps(data), headers=headers)
        return True
    except ValidationError as e:
        notification.notify(
            title = f'❌ {e.message}',
            app_name = "Attendance System",
            message = " ",
            app_icon = None,
            timeout = 0,
        )

def check_in(id):
    print(id)
    if burst_thread.is_alive() and id == 0:
        toggle_burst_mode()
        notification.notify(
            title = "❌ An error occurred",
            app_name = "Attendance System",
            message = " ",
            app_icon = None,
            timeout = 0,
        )
        return
    
    if department:
        print(department.students)
        data = department.students[str(id)]
        dpg.configure_item("last_checked_in", default_value = f"{data['first_name']} {data['last_name']}")
        dpg.configure_item("check_in_time", default_value = get_current_time())
        dpg.configure_item("scanner_id", default_value = id)

        if server_thread and get_event():
            url = "http://localhost:5000/check_in"

            data.update({"department":department.name})

            # update UI

            # send update to server
            headers = {'Content-type': 'application/json'}

            response = post(url, data=dumps(data), headers=headers)
            if response.status_code == 400:
                return False
            return True
      
def enrol():
    if scanner:
        try:
            scanner.write(b"Enroll\n")
            while True:
                result = scanner.readline().decode().strip()
                try:
                    result = int(result)
                    break
                except ValueError:
                    if result == "" or result == " ":
                        break
                    dpg.configure_item("device_id", default_value = result)
        except Exception as e:
            # dpg.configure_item("exception_popup", show=True)
            return
        if result == 0 or result == "" or result == " ":
            notification.notify(
                title = "❌ Unable to enrol fingerprint",
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            return
        else:
            dpg.configure_item("device_id", default_value=result)  # direct update to the UI
            dpg.configure_item("device_id_check", default_value=True)
            notification.notify(
                title = "🎉 Fingerprint Enrolled!",
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
        return
    
# scanner funcs
def scanner_sentry():
    global scanner
    while True:
        ports = list_ports.comports()
        arduino_ports = [port.device for port in ports if 'Arduino' in port.description]
        if arduino_ports and scanner is None:
            try:
                scanner = serial.Serial(arduino_ports[0], 9600)
                notification.notify(
                    title = '🎉 Connected to Device',
                    app_name = "Attendance System",
                    message = " ",
                    app_icon = None,
                    timeout = 0,
                )
                dpg.configure_item("Connected", default_value=True)  # direct update to the UI
            except Exception as e:
                pass
        elif not arduino_ports and scanner is not None:
            scanner = None
            notification.notify(
                title = '❌ Device Disconnected',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            dpg.configure_item("Connected", default_value=False)  # direct update to the UI
        time.sleep(1)  # check every second
        
# server funcs
def start_server():
    uvicorn.run(server.app, host='0.0.0.0', port=10000)

def listener():
    while True:
        try:
            event = sockets[active].recv()
            dpg.configure_item(eval(event)["point"], default_value = event)
            if eval(event)["point"] == "server_updates_checkin":
                Events.add_person(eval(event)["data"])
        except :
            active = "default"

def pinger():
    # prevents socket from being terminated
    while True:
        try:
            if active != "default":
                sockets["default"].send(json.dumps({"action":"ping"}))    
            sockets[active].send(json.dumps({"action":"ping"}))
        except Exception as e:
            print(str(e))
        time.sleep(5)

def connect_client():
    global sockets, active
    uri = "ws://localhost:10000/ws"
    socket = websocket.create_connection(uri)

    # assign default key to socket
    sockets["default"] = socket

    # set active socket to default
    active = "default"
# ========================================================================== MAIN =====================================================================================================
dpg.create_context()

with dpg.window(tag="main_window",) as main_window:

    # Add a menu bar
    with dpg.menu_bar():
        with dpg.menu(label="Menu"):
            dpg.add_menu_item(label="Register Student", callback=summon_register_student_window)
            dpg.add_menu_item(label="Add Course", callback=summon_add_course_window)
            dpg.add_menu_item(label="Create/join Event", callback=summon_create_event_window)
            dpg.add_menu_item(label="Analytics")
        with dpg.menu(label="Settings"):
            dpg.add_menu_item(label="Connected", check=True, tag="Connected", default_value=False, enabled=False)
        with dpg.menu(label="Server", enabled=True):
            dpg.add_text(tag="server_updates_event_creation", default_value="...")
            dpg.add_text(tag="server_updates_event_info", default_value="...")
            dpg.add_text(tag="server_updates_checkin", default_value="...")
            dpg.add_text(tag="server_updates_event_delete", default_value="...")
            dpg.add_text(tag="server_updates_error", default_value="...")
            dpg.add_text(tag="server_updates_ping", default_value="...")

    with dpg.tab_bar():
        Students()
        Events()


dpg.set_primary_window(main_window, True)

# start scanner sentry
threading.Thread(target=scanner_sentry, daemon=True).start()

# start server
threading.Thread(target=start_server, daemon=True).start()

# connect client to server
connect_client()

# start receiving thread
threading.Thread(target=listener, daemon=True).start()

# start pinging thread
threading.Thread(target=pinger, daemon=True).start()

Events.load_servers()

dpg.create_viewport(title="Attendance System")
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.maximize_viewport()
#dpg.show_style_editor()
dpg.start_dearpygui()
dpg.destroy_context()


