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

# Version number
version_number = "1.3.0"

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

# Countdown function for the next run
def update_countdown():
    global last_wait_time

    if last_wait_time > 0:
        minutes, seconds = divmod(last_wait_time, 60)
        countdown_label.config(text=f"Next Run Time: {minutes}m {seconds}s")
        last_wait_time -= 1
        global countdown_task
        countdown_task = root.after(1000, update_countdown)  # Schedule next countdown update
    else:
        # Perform the next action once the countdown ends
        perform_random_key_action()
        last_wait_time = random.randint(2, 7) * 60  # Random interval between 2 and 7 minutes
        update_countdown()

# Kill function to cancel any running tasks or countdowns
def kill():
    global running, last_wait_time
    running = False
    last_wait_time = 0  # Reset the countdown to prevent it from continuing
    countdown_label.config(text="Next Run Time: Not yet scheduled")
    last_run_label.config(text="Last Run Time: Not yet run")
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

    # If there's any scheduled function, cancel it
    root.after_cancel(countdown_task)  # This will cancel the scheduled countdown task

# Main thread to control the actions
def main():
    global running, last_wait_time

    last_wait_time = 7  # Initial countdown for 7 seconds
    update_countdown()

# Start the program
def start():
    global running
    if not running:
        running = True
        threading.Thread(target=main, daemon=True).start()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)

# Stop the program
def stop():
    global running
    if running:
        kill()  # Call the kill function to stop everything
        messagebox.showinfo("Info", "Program stopped")

# Open the Help window
def open_info_window():
    info_window = tk.Toplevel(root)
    info_window.title("Help")
    
    info_window.geometry("300x230")
    info_window.pack_propagate(False)
    info_window.resizable(False, False)

    tk.Label(info_window, text="Roblox AFK Mover", font=("Helvetica", 12, 'bold')).pack(pady=10)
    tk.Label(info_window, text="Helpful Information:", font=("Helvetica", 8, 'bold')).pack(pady=2)

    help_frame = tk.Frame(info_window, bg="lightgrey", bd=1, relief=tk.SOLID)
    help_frame.pack(pady=10, padx=10, fill=tk.X)

    help_text = """- Ensure Roblox is open before starting.
- Roblox must be selected for the program to work.
- The program will perform random key presses every
   few minutes to keep your Roblox game active.
- Roblox may close or restart the server you are in.
  This is out of our control."""
    
    tk.Label(help_frame, text=help_text, justify='left', anchor='w', bg="lightgrey", font=("Helvetica", 8)).pack(pady=1, padx=5)
    tk.Button(info_window, text="Close", command=info_window.destroy).pack(pady=10)

# Open the Version window
def open_version_window():
    version_window = tk.Toplevel(root)
    version_window.title("Version")
    
    version_window.geometry("300x250")
    version_window.pack_propagate(False)
    version_window.resizable(False, False)

    tk.Label(version_window, text=f"Roblox AFK Mover v{version_number}", font=("Helvetica", 12, 'bold')).pack(pady=10)
    tk.Label(version_window, text="Patch Notes:", font=("Helvetica", 8, 'bold')).pack(pady=2)

    patch_notes_frame = tk.Frame(version_window, bg="lightgrey", bd=1, relief=tk.SOLID)
    patch_notes_frame.pack(pady=10, padx=10, fill=tk.X)

    tk.Label(patch_notes_frame, text="""- Added Help and Version windows
- Added Next Run Time
- Added 7 second delay when starting
- Separated information into menus
- Changed the way logs are saved
- Logs now help determine unique key patterns
- Visual changes for better readability""", justify='left', anchor='w', bg="lightgrey", font=("Helvetica", 8)).pack(pady=3, padx=5)

    tk.Button(version_window, text="Close", command=version_window.destroy).pack(pady=10)

# GUI setup
root = tk.Tk()
root.title("Roblox AFK Mover")
root.geometry("300x170")
root.resizable(False, False)

menu_bar = tk.Menu(root)
menu_bar.add_command(label="Help", command=open_info_window)
menu_bar.add_command(label="Version", command=open_version_window)
root.config(menu=menu_bar)

hello_world_label = tk.Label(root, text="Click Help for instructions", font=("Helvetica", 12, 'bold'))
hello_world_label.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Start", command=start, bg="#009900", fg="white", padx=25, pady=5)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="Stop", command=stop, bg="#cc0000", fg="white", state=tk.DISABLED, padx=25, pady=5)
stop_button.pack(side=tk.LEFT, padx=5)

run_info_frame = tk.Frame(root, bg="lightgrey", bd=1, relief=tk.SOLID)
run_info_frame.pack(pady=10, padx=10, fill=tk.X)

last_run_label = tk.Label(run_info_frame, text="Last Run Time: Not yet run", font=("Helvetica", 8), bg="lightgrey")
last_run_label.pack(pady=2, padx=5)

countdown_label = tk.Label(run_info_frame, text="Next Run Time: Not yet scheduled", font=("Helvetica", 8), bg="lightgrey")
countdown_label.pack(pady=2, padx=5)

root.mainloop()
