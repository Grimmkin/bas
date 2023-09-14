from plyer import notification
import serial.tools.list_ports
import dearpygui.dearpygui as dpg
import time

def scanner_sentry(state):
    while True:
        ports = serial.tools.list_ports.comports()
        arduino_ports = [port.device for port in ports if 'Arduino' in port.description]
        if arduino_ports and state.scanner is None:
            try:
                state.scanner = serial.Serial(arduino_ports[0], 9600)
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
        elif not arduino_ports and state.scanner is not None:
            state.scanner = None
            notification.notify(
                title = '❌ Device Disconnected',
                app_name = "Attendance System",
                message = " ",
                app_icon = None,
                timeout = 0,
            )
            dpg.configure_item("Connected", default_value=False)  # direct update to the UI
        time.sleep(1)