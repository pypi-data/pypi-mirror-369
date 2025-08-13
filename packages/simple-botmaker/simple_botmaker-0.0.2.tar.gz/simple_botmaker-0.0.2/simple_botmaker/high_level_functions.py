import datetime
import os
import pywinctl as pwc
import time
import pickle
import cv2
import numpy as np
import pyautogui
import tkinter as tk
from tkinter import simpledialog
from mss import mss
from .low_level_functions import TakeRegionScreenshot, ConvertToThreshold, Capture2Text, LoadFrameFromPath, \
    GetScreenResolution, GetWindowCoordinatesFromScreenCoordinates, \
    ConvertBoundingWidthHeight_ScreenToWindow, GetWindowByName, \
    ConvertBoundingWidthHeight_WindowToScreen, GetScreenCoordinatesFromWindowCoordinates
from .globals import SETTINGS

def GetPixelColour(x, y):
    with mss() as sct:
        image = sct.grab({"top": y, "left": x, "width": 1, "height": 1})
        return image.pixel(0, 0)

def FindImageInRegion(x, y, width, height, template_path, threshold=0.8, grayscale=True, monitor=SETTINGS.monitor, return_first_on_threshold=True, min_scale=0.5, max_scale=1.5, scale_step=0.05):
    region = TakeRegionScreenshot(x, y, width, height, grayscale=grayscale, monitor=monitor)
    template_orig = LoadFrameFromPath(template_path, grayscale=grayscale)
    best_val = -1
    best_match = None
    best_scale = None
    scales = [min_scale + i * scale_step for i in range(int((max_scale - min_scale) / scale_step) + 1)]
    for scale in scales:
        template = cv2.resize(template_orig, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        result = cv2.matchTemplate(region, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > best_val:
            best_val = max_val
            best_match = (max_loc, template)
            best_scale = scale
            if return_first_on_threshold and max_val >= threshold:
                max_loc, template = best_match
                return { "x": max_loc[0], "y": max_loc[1],
                         "width": template.shape[1], "height": template.shape[0],
                         "scale": best_scale, "match": best_val }
    if best_val >= threshold:
        max_loc, template = best_match
        return { "x": max_loc[0], "y": max_loc[1],
                 "width": template.shape[1], "height": template.shape[0],
                 "scale": best_scale, "match": best_val }
    else:
        return None

def GetBar(x1, y1, x2, y2, threshold=128, max_value=255, monitor=SETTINGS.monitor):
    region = TakeRegionScreenshot(x1, y1, x2, y2, True, monitor)
    thresh = ConvertToThreshold(region, threshold, max_value, cv2.THRESH_BINARY)
    pixels = cv2.countNonZero(thresh)
    total_pixels = thresh.shape[0] * thresh.shape[1]
    return (pixels / total_pixels) * 100

def GetBarByColour(x1, y1, x2, y2, color, tolerance=30, monitor=SETTINGS.monitor):
    color_map = {
        'red': np.array([0, 0, 255]),
        'green': np.array([0, 255, 0]),
        'blue': np.array([255, 0, 0]),
        'white': np.array([255, 255, 255]),
        'black': np.array([0, 0, 0]),
        'yellow': np.array([0, 255, 255])
    }
    target = color_map.get(color.lower())
    if target is None:
        raise ValueError("Unsupported color")
    region = TakeRegionScreenshot(x1, y1, x2, y2, False, monitor=monitor)
    diff = np.linalg.norm(region.astype(np.int32) - target, axis=2)
    matching_pixels = np.sum(diff <= tolerance)
    total_pixels = region.shape[0] * region.shape[1]
    return (matching_pixels / total_pixels) * 100

def GetValue(x1, y1, x2, y2, threshold=128, max_value=255, monitor=SETTINGS.monitor):
    region = TakeRegionScreenshot(x1, y1, x2, y2, True, monitor)
    thresh = ConvertToThreshold(region, threshold, max_value, cv2.THRESH_BINARY)
    return Capture2Text(thresh, True, True, True)

def GetText(x1, y1, x2, y2, one_word=False, threshold=128, max_value=255, monitor=SETTINGS.monitor):
    region = TakeRegionScreenshot(x1, y1, x2, y2, True, monitor)
    thresh = ConvertToThreshold(region, threshold, max_value, cv2.THRESH_BINARY)
    return Capture2Text(thresh, False, False, one_word)

def Click(x, y, delay=100):
    pyautogui.click(x, y)
    time.sleep(delay / 1000)

def MouseMove(x, y, delay=100):
    pyautogui.moveTo(x, y)
    time.sleep(delay / 1000)

def FocusedClick(x, y, focusDelay=100, delay=100):
    pyautogui.moveTo(x, y)
    time.sleep(focusDelay / 1000)
    pyautogui.click()
    time.sleep(delay / 1000)

def SaveObject(fileName, obj):
    with open(fileName, 'wb') as f:
        pickle.dump(obj, f)

def LoadObject(fileName):
    with open(fileName, 'rb') as f:
        return pickle.load(f)

def SetRegions():
    root = tk.Tk()
    root.withdraw()
    objects = {}
    image = None
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    path = os.path.join(os.getcwd(), "Custom Regions", current_time)
    if not os.path.exists(path):
        os.makedirs(path)
    window = None
    window_width, window_height = None, None
    while True:
        windows = pwc.getAllWindows()
        windows_string = ""
        title_count = 0
        for w in windows:
            title = w.title.strip()
            if title:
                title_count += 1
                if title_count % 4 == 0:
                    windows_string += "\n"
                windows_string += title + ", "
        win_name = simpledialog.askstring("Window Name", "Type window title, possible choices:\n" + windows_string)
        if win_name and not GetWindowByName(win_name):
            continue
        else:
            window = GetWindowByName(win_name)
            break
    while True:
        cv2.destroyAllWindows()
        time.sleep(0.5)
        x, y, width, height = window.box
        image = TakeRegionScreenshot(x, y, width, height)
        image = cv2.resize(image, fx=0.75, fy=0.75, dsize=(0, 0))
        cv2.imshow("Screenshot", image)
        sel_type = simpledialog.askstring("Selection", "Enter selection type: region, pixel, screenshot, exit")
        selected = None
        window_width, window_height = window.width, window.height
        if sel_type is None:
            continue
        if sel_type.lower() in ["exit", "e"]:
            break
        x, y, w, h = 0, 0, 0, 0
        if sel_type.lower() in ["region", "r", "c"]:
            r = cv2.selectROI("Screenshot", image, False, False)
            x, y, w, h = r
            selected = {"x": x, "y": y, "width": w, "height": h, "window_width": window_width, "window_height": window_height}
            cv2.imshow("Selected", image[y:y+h, x:x+w])
            cv2.waitKey(1)
        elif sel_type.lower() in ["pixel", "p"]:
            coord = []
            def click_event(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    coord[:] = [x, y]
            cv2.setMouseCallback("Screenshot", click_event)
            while not coord:
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    break
            if coord:
                x, y = coord
                selected = {"x": x, "y": y, "colour": image[y, x], "window_width": window_width, "window_height": window_height}
        elif sel_type.lower() in ["screenshot", "full"]:
            r = cv2.selectROI("Screenshot", image, False, False)
            x, y, w, h = r
            selected = {"x": x, "y": y, "width": w, "height": h, "image": image[y:y+h, x:x+w], "window_width": window_width, "window_height": window_height}
            cv2.imshow("Selected", selected["image"])
            cv2.waitKey(1)
        else:
            continue
        name = simpledialog.askstring("Input", "Enter name for region:")
        if name:
            objects[name] = selected

    cv2.destroyAllWindows()
    with open(os.path.join(path, "regions.txt"), "w") as f:
        for key, value in objects.items():
            f.write(key + "\n")
            window_width, window_height = value["width"] * 1.25, value["height"] * 1.25
            window_x, window_y = value["x"] * 1.25, value["y"] * 1.25
            screen_x, screen_y = GetScreenCoordinatesFromWindowCoordinates(win_name, window_x, window_y)
            screen_width, screen_height = ConvertBoundingWidthHeight_WindowToScreen(win_name, window_width, window_height)
            if "width" not in value:
                f.write("Name: " + key +
                        "\nScreen x: " + str(screen_x) +
                        "\nScreen y: " + str(screen_y) +
                        "\nWindow x: " + str(window_x) +
                        "\nWindow y: " + str(window_y) +
                        "\nColour: " + str(value["colour"]) +
                        "\n\n")
            else:
                f.write("Name: " + key +
                        "\n(Screen) x: " + str(screen_x) +
                        "\n(Screen) y: " + str(screen_y) +
                        "\n(Screen) width: " + str(screen_width) +
                        "\n(Screen) height: " + str(screen_height) +
                        "\n(Window) x: " + str(window_x) +
                        "\n(Window) y: " + str(window_y) +
                        "\n(Window) width: " + str(window_width) +
                        "\n(Window) height: " + str(window_height) +
                        "\n\n")
            if "image" in value:
                cv2.imwrite(os.path.join(path, key + ".png"), value["image"])
    for key, value in objects.items():
        cv2.putText(image, key, (value["x"], value["y"] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        if "colour" in value:
            value["width"], value["height"] = 4, 4
            value["x"] -= 2
            value["y"] -= 2
            cv2.putText(image, str(value["colour"]), (value["x"], value["y"] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 255, 0), 1)
        cv2.rectangle(image, (value["x"], value["y"]), (value["x"] + value["width"], value["y"] + value["height"]), (0, 255, 0), 2)
        if "image" in value:
            cv2.imshow(key, value["image"])

    cv2.imwrite(os.path.join(path, "FinalRegions.png"), image)
    cv2.imshow("Final", image)
    cv2.waitKey(0)