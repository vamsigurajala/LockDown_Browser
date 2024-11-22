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
import multiprocessing

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

# Function to open the exam URL in lockdown browser
def open_exam_url_in_lockdown_browser(url, exit_flag):
    while not exit_flag.is_set():
        window.webview.load(QUrl(url))
        logging.info("Opened exam URL in lockdown browser")
        time.sleep(1)

# Function to enter full-screen mode (F11)
def enter_full_screen(exit_flag):
    while not exit_flag.is_set():
        pyautogui.press("f11")
        logging.info("Entered full-screen mode")
        time.sleep(1)

# Function to prevent browser task switching and log attempts to switch
def prevent_task_switching_and_log(exit_flag):
    while not exit_flag.is_set():
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

        except Exception as e:
            logging.error(f"Error: {e}")
        time.sleep(1)

# Function to monitor clipboard changes
def monitor_clipboard(exit_flag):
    clipboard_data = ""
    while not exit_flag.is_set():
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
def detect_all_audio_devices(exit_flag):
    while not exit_flag.is_set():
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
def check_for_screen_sharing_apps(exit_flag):
    while not exit_flag.is_set():
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
def offline_mode(exit_flag):
    while not exit_flag.is_set():
        logging.info("Entering offline mode...")
        logging.info("Simulating offline activities...")
        time.sleep(5)  # Simulate offline activities for 5 seconds
        logging.info("Exiting offline mode...")
        logging.info("Resuming exam...")


class LockdownBrowserWindow(QMainWindow):
    def __init__(self, exit_flags):
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
        self.enter_full_screen(exit_flags[0])

        # Disable/Intercept the right-click context menu
        self.webview.setPage(
            self.webview.page()
        )  # Set the web view's page for the context menu changes
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)

    def enter_full_screen(self, exit_flag):
        while not exit_flag.is_set():
            # Set the window to be frameless and transparent
            # self.setWindowFlags(Qt.FramelessWindowHint)
            # self.setAttribute(Qt.WA_TranslucentBackground)
            self.showFullScreen()
            time.sleep(1)

    def keyPressEvent(self, event, exit_flag):
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
            for flag in exit_flags:
                flag.set()
            QCoreApplication.quit()
        elif event.key() in blocked_keys:
            blocked_key = blocked_keys[event.key()]
            self.show_warning(f"{blocked_key} actions are disabled during the exam.")
        else:
            super().keyPressEvent(event)

    def show_warning(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Warning")
        msg_box.setText(message)
        msg_box.exec_()

def stop_processes(exit_flags, *processes):
    for flag in exit_flags:
        flag.set()
    for process in processes:
        process.join()


powershell_command = f"powershell -ExecutionPolicy Bypass -Command \"python 'C:/Users/Krishnavamsi_Gurajal/Desktop/Browser/ids-ldb/app.py' -lockdown_browser_launcher\""
subprocess.Popen(powershell_command, shell=True)
os.system("taskkill /f /im explorer.exe")


# Function to close all unnecessary processes
def close_all_processes(exit_flag):
    current_pid = os.getpid()  # Get the current process ID

    # Get the process names to keep
    processes_to_keep = {"Code.exe", "Teams.exe", "chrome.exe", "powershell.exe", "cmd.exe"}

    # Get the unique argument used to identify the running process
    unique_argument = "-lockdown_browser_launcher"

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # Skip the current process and specified processes to keep
            if proc.info["pid"] == current_pid or proc.info["name"] in processes_to_keep:
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

# ... (your existing functions)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create multiprocessing events to signal exit
    exit_flags = [multiprocessing.Event() for _ in range(7)]

    window = LockdownBrowserWindow(exit_flags)
    window.show()

    # Create and start the processes
    processes = [
        multiprocessing.Process(target=prevent_task_switching_and_log, args=(exit_flags[1],)),
        multiprocessing.Process(target=monitor_clipboard, args=(exit_flags[2],)),
        multiprocessing.Process(target=detect_all_audio_devices, args=(exit_flags[3],)),
        multiprocessing.Process(target=check_for_screen_sharing_apps, args=(exit_flags[4],)),
        multiprocessing.Process(target=offline_mode, args=(exit_flags[5],)),
        multiprocessing.Process(target=close_all_processes, args=(exit_flags[6],)),
    ]

    for process in processes:
        process.start()

    open_exam_url_in_lockdown_browser(exam_url, exit_flags[0])
    close_all_processes()
    #list_running_processes()
    powershell_command = "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"C:/Users/Krishnavamsi_Gurajal/Desktop/Browser/ids-ldb/app.py\" -lockdown_browser_launcher' -WindowStyle Hidden"
    subprocess.Popen(["powershell", powershell_command])


    # Wait for the processes to finish before exiting
    stop_processes(exit_flags, *processes)

    sys.exit(app.exec_())