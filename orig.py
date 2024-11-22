import os
import subprocess
import pyautogui
import time
import threading
import pygetwindow as gw
import logging
import pyperclip
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QAction,
    QToolBar,
    QStyle,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, QCoreApplication
import sys
import datetime
import pyaudio
import psutil  # Import the psutil library for process checking
import keyboard
from PIL import Image, ImageDraw
import keyboard




# Configure logging
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_file = f"lockdown_browser_{current_date}.log"
logging.basicConfig(
    filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s"
)

# Suppress console output for the root logger
logging.getLogger().setLevel(logging.WARNING)

# Define the URL of the GeeksforGeeks exam page
exam_url = "https://www.google.com/search?q=python+online+compiler&rlz=1C1RXQR_enIN1040IN1040&oq=python+on&gs_lcrp=EgZjaHJvbWUqCQgAECMYJxiKBTIJCAAQIxgnGIoFMgYIARBFGEAyBggCEEUYOTIKCAMQABixAxiABDIHCAQQABiABDIGCAUQRRg8MgYIBhBFGDwyBggHEEUYPNIBCDMyMTNqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8"

# Flag to signal threads to exit
exit_threads = False
block_keys = True
threads = []


def open_exam_url_in_lockdown_browser(url):
    window.webview.load(QUrl(url))
    logging.info("Opened exam URL in lockdown browser")


# Function to enter full-screen mode (F11)
def enter_full_screen():
    pyautogui.press("f11")
    logging.info("Entered full-screen mode")

"""
import ctypes

def lock_screen():
    try:
        # Lock the screen using the Windows API
        ctypes.windll.user32.LockWorkStation()
        logging.info("Screen locked successfully.")
    except Exception as e:
        logging.error(f"Error locking screen: {e}")
"""

import keyboard

# Function to prevent browser task switching and log attempts to switch
def prevent_task_switching_and_log():
    global exit_threads
    while not exit_threads:
        try:
            browser_name = "Lockdown Browser"
            browser = gw.getWindowsWithTitle(browser_name)
            if not browser:
                logging.error("Lockdown Browser window not found!")
            else:
                # Check for other applications and log attempts to open them
                other_apps = gw.getAllTitles()
                other_apps.remove(browser[0].title)
                if other_apps:
                    logging.warning(
                        f"User attempted to open other applications: {', '.join(other_apps)}"
                    )

                    # Lock the screen when other applications are detected
                    #lock_screen()

                # Suppress key events to block tab switching
                #pyautogui.hotkey('ctrl', 'alt', 'tab')
                #pyautogui.hotkey('alt','tab')

                #pyautogui.moveTo(1, 1)


        except Exception as e:
            logging.error(f"Error: {e}")
        time.sleep(1)




def monitor_clipboard():
    global exit_threads
    clipboard_data = ""
    while not exit_threads:
        current_clipboard = pyperclip.paste()
        if current_clipboard != clipboard_data:
            clipboard_data = current_clipboard
            logging.warning(
                "Copy-paste action detected. Copy-paste is disabled during the exam."
            )
            # Clear the clipboard to prevent pasting
            pyperclip.copy("")
        time.sleep(1)


# Function to detect and log all connected audio devices
def detect_all_audio_devices():
    global exit_threads
    while not exit_threads:
        try:
            p = pyaudio.PyAudio()
            input_devices = [
                p.get_device_info_by_index(i)
                for i in range(p.get_device_count())
                if p.get_device_info_by_index(i)["maxInputChannels"] > 0
            ]
            output_devices = [
                p.get_device_info_by_index(i)
                for i in range(p.get_device_count())
                if p.get_device_info_by_index(i)["maxOutputChannels"] > 0
            ]
            if input_devices:
                input_device_names = [device["name"] for device in input_devices]
                logging.warning(
                    f"Connected audio input devices: {', '.join(input_device_names)}"
                )
            if output_devices:
                output_device_names = [device["name"] for device in output_devices]
                logging.warning(
                    f"Connected audio output devices: {', '.join(output_device_names)}"
                )
        except Exception as e:
            logging.error(f"Error: {e}")
        time.sleep(10)


# Function to check for common screen sharing applications
def check_for_screen_sharing_apps():
    global exit_threads
    while not exit_threads:
        try:
            # Check for common screen sharing applications (candidates should avoid these)
            common_screen_sharing_apps = [
                "TeamViewer",
                "AnyDesk",
                "Zoom",
                "Skype",
                "Chrome Remote Desktop",
                "teams",
            ]

            for app in common_screen_sharing_apps:
                for process in psutil.process_iter(attrs=["pid", "name"]):
                    if app.lower() in process.info["name"].lower():
                        logging.warning(
                            f"Screen sharing application detected: {app}. Candidate must avoid cheating."
                        )

        except Exception as e:
            logging.error(f"Error: {e}")
        time.sleep(10)  # Check every 10 seconds


# Function to support offline mode (simplified example)
def offline_mode():
    while not exit_threads:
        logging.info("Entering offline mode...")
        logging.info("Simulating offline activities...")
        time.sleep(5)  # Simulate offline activities for 5 seconds
        logging.info("Exiting offline mode...")
        logging.info("Resuming exam...")



class LockdownBrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # # Create a QWebEngineView to display the exam URL
        self.webview = QWebEngineView(self)

        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        back_action = QAction("Back", self)
        back_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_action.triggered.connect(self.webview.back)
        toolbar.addAction(back_action)

        forward_action = QAction("Forward", self)
        forward_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        forward_action.triggered.connect(self.webview.forward)
        toolbar.addAction(forward_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_action.triggered.connect(self.webview.reload)
        toolbar.addAction(refresh_action)

        # Configure web settings to suppress JavaScript error messages
        web_settings = self.webview.settings()
        web_settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        web_settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)

        self.webview.setUrl(QUrl(exam_url))
        layout.addWidget(self.webview)

        # Set up the main window
        self.setWindowTitle("Lockdown Browser")
        self.setGeometry(100, 100, 800, 600)

        # Enter full-screen mode automatically
        self.enter_full_screen()

        # Disable/Intercept the right-click context menu
        self.webview.setPage(
            self.webview.page()
        )  # Set the web view's page for the context menu changes
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)

    def enter_full_screen(self):
        # Set the window to be frameless and transparent
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def keyPressEvent(self, event):
        global block_keys
        blocked_keys = {
            Qt.Key_C: "C key",
            Qt.Key_V: "V key",
            Qt.Key_M: "M key",
            Qt.Key_Alt: "Alt key",
            Qt.Key_Meta: "Windows/Command key",
            Qt.Key_Tab: "Tab key",
            Qt.Key_Print: "Print Screen key",
            Qt.Key_SysReq: "System Request key",
        }
        if event.key() == Qt.Key_Q:
            exit_threads = True
            QCoreApplication.quit()
        elif event.key() in blocked_keys:
            blocked_key = blocked_keys[event.key()]
            self.show_warning(f"{blocked_key} actions are disabled during the exam.")
        elif block_keys and event.key() == Qt.Key_Print:
            # If Print Screen key is pressed, capture the screen and make it blank
            self.capture_and_blank_screen()
        else:
            super().keyPressEvent(event)

    def show_warning(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Warning")
        msg_box.setText(message)
        msg_box.exec_()
    
''' 
   def capture_and_blank_screen(self):
        # Capture the screen
        screenshot = pyautogui.screenshot()

        # Get the size of the captured screen
        width, height = screenshot.size

        # Create a blank image with the same size
        blank_image = Image.new("RGB", (width, height), (255, 255, 255))

        # Save or display the blank image as needed
        blank_image.save(save_path) 
        '''




powershell_command = f"powershell -ExecutionPolicy Bypass -Command \"python 'C:/Users/Krishnavamsi_Gurajal/Desktop/Browser/ids-ldb/app.py' -lockdown_browser_launcher\""
subprocess.Popen(powershell_command, shell=True)
os.system("taskkill /f /im explorer.exe")


def close_all_processes():
    current_pid = os.getpid()  # Get the current process ID

    # Get the process names to keep
    processes_to_keep = {"Code.exe", "Teams.exe", "chrome.exe", "powershell.exe", "cmd.exe",}

    # Get the unique argument used to identify the running process
    unique_argument = "-lockdown_browser_launcher"

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # Skip the current process and specified processes to keep
            if (
                proc.info["pid"] == current_pid
                or proc.info["name"] in processes_to_keep
            ):
                continue

            # Skip processes with NoneType cmdline
            if proc.info["cmdline"] is None:
                continue

            # Check if the unique argument is not in the cmdline
            if unique_argument not in proc.info["cmdline"]:
                try:
                    # Terminate the process
                    proc.terminate()
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ) as e:
                    logging.info(f"Error terminating process {proc.info['name']}: {e}")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logging.info(f"Error processing process {proc.info['name']}: {e}")

#def list_running_processes():
#   for proc in psutil.process_iter(["pid", "name"]):
#        print(f"Process ID: {proc.info['pid']}, Name: {proc.info['name']}")


#Call the function to list running processes
#list_running_processes()


# Function to stop threads gracefully
def stop_threads(*threads):
    global exit_threads
    exit_threads = True
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LockdownBrowserWindow()
    window.show()

    # Create and start the threads
    threads.append(threading.Thread(target=prevent_task_switching_and_log))
    threads.append(threading.Thread(target=monitor_clipboard))
    threads.append(threading.Thread(target=detect_all_audio_devices))
    threads.append(threading.Thread(target=check_for_screen_sharing_apps))
    threads.append(threading.Thread(target=offline_mode))

    for thread in threads:
        thread.start()

    open_exam_url_in_lockdown_browser(exam_url)
    close_all_processes()
    #list_running_processes()
    powershell_command = "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"C:/Users/Krishnavamsi_Gurajal/Desktop/Browser/ids-ldb/app.py\" -lockdown_browser_launcher' -WindowStyle Hidden"
    subprocess.Popen(["powershell", powershell_command])

    #save_path = r"C:\\Users\\vamsi\\Pictures\\Screenshots.png"
    #window.capture_and_blank_screen(save_path)

    # Wait for the threads to finish before exiting
    app.aboutToQuit.connect(lambda: stop_threads(*threads))

    sys.exit(app.exec_())