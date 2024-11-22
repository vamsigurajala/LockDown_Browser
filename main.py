import logging
import os
import asyncio
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStyle, QToolBar, QAction, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, QCoreApplication
import sys
import datetime
from PIL import Image
import pygetwindow as gw
import pyautogui
import psutil
import time
# Import functions from async_utils
from async_utils import run_background_tasks

# Configure logging
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_file = f"lockdown_browser_{current_date}.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

# Suppress console output for the root logger
logging.getLogger().setLevel(logging.WARNING)

# Define the URL of the GeeksforGeeks exam page
exam_url = "https://www.google.com/search?q=python+online+compiler&rlz=1C1RXQR_enIN1040IN1040&oq=python+on&gs_lcrp=EgZjaHJvbWUqCQgAECMYJxiKBTIJCAAQIxgnGIoFMgYIARBFGEAyBggCEEUYOTIKCAMQABixAxiABDIHCAQQABiABDIGCAUQRRg8MgYIBhBFGDwyBggHEEUYPNIBCDMyMTNqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8"

# Set the path for saving the blank screen image
save_path = "C:\\Users\\vamsi\\Pictures\\Screenshots.png"

# Global variable to control the exit of background tasks
exit_threads = False


class LockdownBrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create a QWebEngineView to display the exam URL
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

        # Show the window
        self.show()

    def enter_full_screen(self):
        # Set the window to be frameless and transparent
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def keyPressEvent(self, event):
        global exit_threads
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
        elif event.key() == Qt.Key_Print:
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

    



# Function to close all processes not needed for the exam
def close_all_processes():
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
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    logging.info(f"Error terminating process {proc.info['name']}: {e}")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logging.info(f"Error processing process {proc.info['name']}: {e}")


import pyperclip


async def monitor_clipboard():
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
        await asyncio.sleep(1)

async def run_background_tasks():
    await asyncio.gather(
        monitor_clipboard(),
        # Add other async tasks here as needed
    )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LockdownBrowserWindow()

    # Create and start the event loop
    loop = asyncio.get_event_loop()
    exit_threads = False

    # Run the background tasks
    loop.create_task(run_background_tasks())

    # Open the PowerShell command to launch the script
    powershell_command = (
        f"powershell -ExecutionPolicy Bypass -Command \"python 'C:/Users/vamsi/Desktop/Browser/ids-ldb/app.py' -lockdown_browser_launcher\""
    )
    subprocess.Popen(powershell_command, shell=True)
    os.system("taskkill /f /im explorer.exe")


    # Close unnecessary processes
    close_all_processes()

    sys.exit(app.exec_())
