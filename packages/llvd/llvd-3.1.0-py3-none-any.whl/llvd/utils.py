import os
import re
from random import randint
from time import sleep
import random


def subtitles_time_format(ms):
    """
    Formats subtitles time
    """
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:02}'


def clean_name(name):
    digit_removed = re.sub(r'^\d+\.', "", name)
    chars_removed = re.sub(r'[\\:<>"/|?*’.\')(,]', "", digit_removed).replace("«", " ")\
        .replace("-»", " ").replace("»", " ").strip()
    extra_space_removed = re.sub(r'(\s+)', " ", chars_removed)
    return extra_space_removed.strip()


def clean_dir(course_name):
    course = course_name.lower().replace("c#", "c-sharp").replace(".net", "-dot-net")
    without_chars = re.sub(r'[\':)(,>.’/]', " ", course.strip()).replace("«", " ")\
        .replace("-»", " ").replace("»", " ").strip()
    return re.sub(r'(\s+)', "-", without_chars).replace("--", "-")


def throttle(wait_time=None):
    esc: str = '\x1b['
    clear_line = f'{esc}2K'
    cursor_home = f'{esc}0G'
    cursor_up = f'{esc}1A'
    if wait_time is None:
        print('utils.py#throttle - Error: missing throttle wait time.')
        return
    if len(wait_time) > 1:
        min_delay = wait_time[0]
        max_delay = wait_time[1]
        delay = randint(min_delay, max_delay)
    else:
        delay = wait_time[0]  # in case only one parameter passed
    print(f'Delaying for {delay} seconds.')
    sleep(delay)
    # clean up delay message
    print(f'{cursor_up}{clear_line}{cursor_up}{cursor_home}')


def cleanup_empty_directories(path, errors=None):
    """Recursively remove empty directories. Returns the number of removed directories."""
    if not os.path.isdir(path):
        return 0

    removed = 0
    try:
        # Recursively process subdirectories
        entries = os.listdir(path)
        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                removed += cleanup_empty_directories(full_path, errors)
        # Check if directory is empty after processing subdirectories
        entries = os.listdir(path)
        if not entries:
            os.rmdir(path)
            removed += 1
    except (OSError, PermissionError) as e:
        if errors is not None:
            errors.append(f"Failed to clean up directory {path}: {str(e)}")
    return removed


def load_proxies(proxy_file_path):
    """Load proxies from a file, return a list of proxy URLs."""
    with open(proxy_file_path, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies


def get_random_proxy(proxies):
    """Return a random proxy from the list."""
    return random.choice(proxies) if proxies else None
