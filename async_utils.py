import logging
import pyperclip
import pyaudio
import time
import psutil
import asyncio
import pygetwindow as gw




async def prevent_task_switching_and_log(window):
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

        except Exception as e:
            logging.error(f"Error: {e}")
        await asyncio.sleep(1)

import pyautogui

async def monitor_clipboard(window):
    global exit_threads
    last_clipboard_data = pyperclip.paste()
    while not exit_threads:
        current_clipboard = pyperclip.paste()
        if current_clipboard != last_clipboard_data:
                logging.warning("Copy-paste action detected. Copy-paste is disabled during the exam.")
                # Clear the clipboard to prevent pasting using pyperclip
                pyperclip.copy("")

                # Disable paste shortcut (Ctrl+V)
                pyautogui.hotkey("ctrl", "v")

        last_clipboard_data = current_clipboard
        await asyncio.sleep(1)


async def detect_all_audio_devices(window):
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
        await asyncio.sleep(10)


async def check_for_screen_sharing_apps(window):
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
        await asyncio.sleep(10)


async def offline_mode(window):
    while not exit_threads:
        logging.info("Entering offline mode...")
        logging.info("Simulating offline activities...")
        await asyncio.sleep(5)  # Simulate offline activities for 5 seconds
        logging.info("Exiting offline mode...")
        logging.info("Resuming exam...")


async def run_background_tasks(window):
    await asyncio.gather(
        prevent_task_switching_and_log(window),
        monitor_clipboard(window),
        detect_all_audio_devices(window),
        check_for_screen_sharing_apps(window),
        offline_mode(window),
    )
