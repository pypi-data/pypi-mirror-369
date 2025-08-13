import sys
import urllib
import zipfile

import cv2
import numpy as np
from mss import mss
from .globals import SETTINGS
import subprocess
import pywinctl as pwc
import subprocess
import tempfile
import os
from PIL import Image
import numpy as np
import re

def ensure_capture2text_installed():
    """
    Checks if Capture2Text.exe is installed in install_dir or default path.
    If not, downloads and extracts it.

    Returns the full path to Capture2Text.exe.

    Parameters:
        install_dir (str): Optional directory to install/extract Capture2Text.
                           Defaults to a folder in user's AppData\\Local\\Capture2Text
    """
    install_dir = os.getenv("LOCALAPPDATA")

    exe_path = os.path.join(install_dir, "Capture2Text", "Capture2Text.exe")

    if os.path.isfile(exe_path):
        return exe_path

    # If not present, download and extract
    print("Capture2Text.exe not found. Downloading...")

    url = "https://sourceforge.net/projects/capture2text/files/latest/download"  # redirects to latest zip

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "capture2text.zip")
        try:
            urllib.request.urlretrieve(url, zip_path)
        except Exception as e:
            raise RuntimeError(f"Failed to download Capture2Text: {e}")

        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all contents to install_dir
            if not os.path.exists(install_dir):
                os.makedirs(install_dir)
            zip_ref.extractall(install_dir)

    if os.path.isfile(exe_path):
        print(f"Capture2Text downloaded and extracted to {exe_path}")
        return exe_path
    else:
        raise FileNotFoundError("Capture2Text.exe not found after extraction.")

def Capture2Text(frame,
                 numeric_only=False,
                 numeric_only_include_positive_minus=False,
                 one_word=False):
    """
    Run Capture2Text OCR on a given image frame and return the extracted text.

    Parameters:
        frame (numpy.ndarray or PIL.Image.Image): The image to OCR.
        capture2text_path (str): Path to Capture2Text executable.
        numeric_only (bool): If True, filter output to digits only.
        numeric_only_include_positive_minus (bool): If True and numeric_only,
            also allow '+' and '-' characters.
        one_word (bool): If True, return only first word from the output.

    Returns:
        str: The OCR extracted and post-processed text.
    """
    # Convert numpy array to PIL image if necessary
    exe_dir = ensure_capture2text_installed()

    if isinstance(frame, np.ndarray):
        frame = Image.fromarray(frame)

    with tempfile.TemporaryDirectory() as temp_dir:
        image_path = os.path.join(temp_dir, "temp_capture.png")
        output_path = os.path.join(temp_dir, "output.txt")

        frame.save(image_path)

        cmd = [
            exe_dir,
            "-i", image_path,
            "-o", output_path
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Capture2Text failed: {e.stderr.decode(errors='ignore')}")

        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
        else:
            text = ""

    # Post-process text filters
    if numeric_only:
        if numeric_only_include_positive_minus:
            # Keep digits, plus and minus signs only
            text = re.sub(r"[^0-9+\-]", "", text)
        else:
            # Keep digits only
            text = re.sub(r"[^0-9]", "", text)

    if one_word:
        # Keep only the first word (split by whitespace)
        text = text.split()[0] if text else ""

    return text

def AdjustCoordinatesBasedOnResolution(x1, y1, x2, y2, monitor=0):
    screen_width, screen_height = GetScreenResolution(monitor)
    return int(x1 * screen_width / 1920), int(y1 * screen_height / 1080), int(x2 * screen_width / 1920), int(y2 * screen_height / 1080)

def GetWindowByName(window_name):
    window = pwc.getWindowsWithTitle(window_name)
    if window:
        window = window[0]
        window.activate(True)
        return window
    return None

def GetWindowCoordinatesFromScreenCoordinates(window_name, x, y):
    window = GetWindowByName(window_name)
    window_rect = window.rect
    return max(x - window_rect[0], 0), max(y - window_rect[1], 0)

def GetScreenCoordinatesFromWindowCoordinates(window_name, x, y):
    window = GetWindowByName(window_name)
    window_rect = window.rect
    return max(window_rect[0] + x, 0), max(window_rect[1] + y, 0)

def ConvertBoundingWidthHeight_ScreenToWindow(window_name, screen_width, screen_height):
    window = GetWindowByName(window_name)
    if window:
        window_left, window_top = window.left, window.top
        window_x = screen_width - window_left
        window_y = screen_height - window_top
        return window_x, window_y
    else:
        return None, None

def ConvertBoundingWidthHeight_WindowToScreen(window_name, window_width, window_height):
    window = GetWindowByName(window_name)
    if window:
        window_left, window_top = window.left, window.top
        screen_x = window_width + window_left
        screen_y = window_height + window_top
        return screen_x, screen_y
    else:
        return None, None

def GetScreenResolution(monitor=0):
    with mss() as sct:
        return sct.monitors[monitor]["width"], sct.monitors[monitor]["height"]

def GetWindowBounds(window_name):
    return cv2.getWindowImageRect(window_name)

def TakeRegionScreenshot(x, y, width, height, grayscale=False, monitor=0):
    """
    Gets a screenshot of a region of the window or screen.

    :param x1: The top left x coordinate of the region to take the screenshot from.
    :param y1: The top left y coordinate of the region to take the screenshot from.
    :param x2: The bottom right x coordinates of the region to take the screenshot from.
    :param y2: The bottom right y coordinates of the region to take the screenshot from.
    :param grayscale: Whether to convert the image to grayscale.
    :param monitor: The monitor to take the screenshot from.
    :return:
    """
    with mss() as sct:
        if SETTINGS.window_name is not None:
            x, y = GetScreenCoordinatesFromWindowCoordinates(SETTINGS.window_name, x, y)
            region = sct.grab({
                "top": y,
                "left": x,
                "width": width,
                "height": height,
            })
        else:
            mon = sct.monitors[monitor]
            region = sct.grab({
                "top": mon["top"] + y,
                "left": mon["left"] + x,
                "width": width,
                "height": height,
                "mon": monitor,
            })
        region = cv2.cvtColor(np.array(region), cv2.COLOR_RGBA2GRAY if grayscale else cv2.COLOR_RGBA2BGR)
        return region

def ConvertToGrayScale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def ConvertToThreshold(frame, threshold=128, max_value=255, threshold_type=cv2.THRESH_BINARY):
    _, frame = cv2.threshold(frame, threshold, max_value, threshold_type)
    return frame

def LoadFrameFromPath(path, grayscale=False):
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR)

def DebugRectangle(frame, x, y, width, height, color=(0, 255, 0), thickness=2):
    if SETTINGS.window_name is not None:
        x, y = GetWindowCoordinatesFromScreenCoordinates(SETTINGS.window_name, x, y)
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, thickness)
    return frame

def DebugText(frame, text, x, y, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(0, 255, 0), thickness=2):
    if SETTINGS.window_name is not None:
        x, y = GetWindowCoordinatesFromScreenCoordinates(SETTINGS.window_name, x, y)
    cv2.putText(frame, str(text), (x, y), font, font_scale, color, thickness)
    return frame

def DisplayDebugFrame(frame, pause=True, destroy=False, title="DebugFrame", x=0, y=0):
    temp_frame = cv2.resize(frame, fx=0.5, fy=0.5, dsize=(0, 0))
    cv2.imshow(title, temp_frame)
    cv2.moveWindow(title, x, y)
    cv2.waitKey(0 if pause else 1)
    if destroy:
        cv2.destroyAllWindows()

def DestroyAllDebugFrames():
    cv2.destroyAllWindows()