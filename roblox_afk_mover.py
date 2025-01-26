import os
import pyautogui
import random
import time
import logging
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import platform
import sys
import requests  # Added to check for updates

# Version number
version_number = "1.3.0"

# Function to check for updates
def check_for_updates():
    repo_url = "https://raw.githubusercontent.com/nickstar14/Roblox-AFK-Mover/master/version.txt"
    try:
        response = requests.get(repo_url, timeout=5)
        response.raise_for_status()
        latest_version = response.text.strip()

        if latest_version != version_number:
            messagebox.showinfo(
                "Update Available",
                f"A new version ({latest_version}) is available! Please update your program."
            )
        else:
            print("You're using the latest version.")
    except requests.ConnectionError:
        print("No internet connection. Unable to check for updates.")
    except requests.exceptions.RequestException as e:
        print(f"Error checking for updates: {e}")

# Call the update check before anything else
check_for_updates()

# Determine the OS and set the Documents folder path
if platform.system() == "Windows":
    documents_path = Path.home() / 'Documents' / 'Roblox AFK Mover'
elif platform.system() == "Darwin":  # macOS
    documents_path = Path.home() / 'Documents' / 'Roblox AFK Mover'
else:
    raise OSError("Unsupported operating system")

# Create the folder if it doesn't exist
documents_path.mkdir(parents=True, exist_ok=True)

# Generate a log file name based on the current start time
log_file_name = datetime.now().strftime("log_%Y-%m-%d_%H-%M-%S.txt")
log_file_path = documents_path / log_file_name

# Configure logging to create a new log file each time
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

running = False
last_wait_time = 0
countdown_task = None

# List to store the last 10 unique patterns
pattern_log = []

# Function to generate a random key press pattern
def generate_key_pattern():
    keys = ['w', 'a', 's', 'd', 'space']
    num_presses = random.randint(2, 7)  # Random number of key presses between 2 and 7
    pattern = []

    for _ in range(num_presses):
        key = random.choice(keys)
        duration = random.uniform(0.1, 0.5) if random.random() < 0.7 else random.uniform(0.5, 1.5)  # 70% short, 30% long
        pattern.append((key, duration))

    return pattern

# Function to perform the key presses based on the pattern
def perform_key_pattern(pattern):
    pressed_keys = []

    for key, duration in pattern:
        pressed_keys.append(key)
        if key == 'space':
            pyautogui.press('space')
        else:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)

    return pressed_keys

# Main function for random key actions
def perform_random_key_action():
    global pattern_log

    pattern = generate_key_pattern()
    pressed_keys = perform_key_pattern(pattern)

    # Ensure unique patterns are logged
    while pattern in pattern_log:
        pattern = generate_key_pattern()

    pattern_log.append(pattern)
    if len(pattern_log) > 10:
        pattern_log.pop(0)

    # Log pattern with timestamp and key details
    with open(log_file_path, 'a') as f:
        f.write(f'Pattern: {pressed_keys} - Duration: {", ".join([str(dur) for key, dur in pattern])}\n')

    logging.info(f'Keys pressed: {pressed_keys} - Pattern Duration: {", ".join([str(dur) for key, dur in pattern])}')

    # Update last run time
    last_run_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')  # Updated format
    last_run_label.config(text=f"Last Run Time: {last_run_time}")

# (The rest of your code remains unchanged.)
