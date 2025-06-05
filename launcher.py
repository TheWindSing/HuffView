import subprocess
import time
import os
import sys
import webbrowser
import socket

import subprocess
import os
import sys
import socket
import webbrowser
import time

def is_port_in_use(port):
    s = socket.socket()
    try:
        s.connect(('127.0.0.1', port))
        s.close()
        return True
    except:
        return False

def launch_app():
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    app_path = os.path.join(base_dir, 'app.py')
    subprocess.Popen(['python', app_path], shell=True)

def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000/")

if not is_port_in_use(5000):
    launch_app()
    open_browser()
else:
    webbrowser.open("http://127.0.0.1:5000/")
