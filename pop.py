import os
import subprocess
import pyautogui
import time
import asyncio
import pygetwindow as gw
import logging
import pyperclip
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
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
import psutil
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
            stop_tasks(*tasks)
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

async def open_exam_url_in_lockdown_browser_async(url):
    window.webview.load(QUrl(url))
    logging.info("Opened exam URL in lockdown browser")

async def enter_full_screen_async():
    pyautogui.press("f11")
    logging.info("Entered full-screen mode")

async def prevent_task_switching_and_log_async():
    global exit_tasks
    while not exit_tasks:
        try:
            browser_name = "Lockdown Browser"
            browser = gw.getWindowsWithTitle(browser_name)
            if not browser:
                logging.error("Lockdown Browser window not found!")
            else:
                other_apps = gw.getAllTitles()
                other_apps.remove(browser[0].title)
                if other_apps:
                    logging.warning(
                        f"User attempted to open other applications: {', '.join(other_apps)}"
                    )

        except Exception as e:
            logging.error(f"Error: {e}")
        await asyncio.sleep(1)

async def monitor_clipboard_async():
    global exit_tasks
    clipboard_data = ""
    while not exit_tasks:
        current_clipboard = pyperclip.paste()
        if current_clipboard != clipboard_data:
            clipboard_data = current_clipboard
            logging.warning(
                "Copy-paste action detected. Copy-paste is disabled during the exam."
            )
            pyperclip.copy("")
        await asyncio.sleep(1)

async def detect_all_audio_devices_async():
    global exit_tasks
    while not exit_tasks:
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
        await asyncio.sleep(10)

async def check_for_screen_sharing_apps_async():
    global exit_tasks
    while not exit_tasks:
        try:
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
        await asyncio.sleep(10)

async def offline_mode_async():
    global exit_tasks
    while not exit_tasks:
        logging.info("Entering offline mode...")
        logging.info("Simulating offline activities...")
        await asyncio.sleep(5)  # Simulate offline activities for 5 seconds
        logging.info("Exiting offline mode...")
        logging.info("Resuming exam...")


# ... (previous code remains unchanged)

# Define the 'stop_tasks' function
async def stop_tasks(*tasks):
    global exit_tasks
    exit_tasks = True
    for task in tasks:
        task.cancel()
        try:
            await asyncio.gather(task)
        except asyncio.CancelledError:
            pass

async def main():
    app = QApplication(sys.argv)
    window = LockdownBrowserWindow()
    window.show()

    # Declare the 'tasks' variable
    tasks = [
        prevent_task_switching_and_log_async(),
        monitor_clipboard_async(),
        detect_all_audio_devices_async(),
        check_for_screen_sharing_apps_async(),
        offline_mode_async(),
    ]

    # Use asyncio.gather to run tasks concurrently and await it
    await asyncio.gather(
        open_exam_url_in_lockdown_browser_async(exam_url),
        enter_full_screen_async(),
        stop_tasks(*tasks),
    )

    # Define the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    asyncio.run(main())
