class Globals():
    def __init__(self, window_name=None, monitor=0, debug=False):
        self.window_name = window_name
        self.monitor = monitor
        self.debug = debug

SETTINGS = Globals()

def AdjustCoordinatesBasedOnResolution(x1, y1, x2, y2, monitor=0):
    pass

def GetWindowCoordinatesFromScreenCoordinates(window_name, x, y):
    pass

def GetScreenCoordinatesFromWindowCoordinates(window_name, x, y):
    pass

def GetScreenResolution(monitor=0):
    pass

def GetWindowBounds(window_name):
    pass

def TakeRegionScreenshot(x, y, width, height, grayscale=False, monitor=0):
    pass

def ConvertToGrayScale(frame):
    pass

def ConvertToThreshold(frame, threshold=128, max_value=255, threshold_type=cv2.THRESH_BINARY):
    pass

def LoadFrameFromPath(path, grayscale=False):
    pass

def DebugRectangle(frame, x, y, width, height, color=(0, 255, 0), thickness=2):
    pass

def DebugText(frame, text, x, y, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(0, 255, 0), thickness=2):
    pass

def DisplayDebugFrame(frame, pause=True, destroy=False, title="DebugFrame", x=0, y=0):
    pass

def DestroyAllDebugFrames():
    pass

def RunWait(exe_path, args=[]):
    pass

def ImageMagick(command):
    pass

def Capture2Text(frame, numeric_only=False, numeric_only_include_positive_minus=False, one_word=False):
    pass

def ParseInt(text: str):
    pass

def GetPixelColour(x, y):
    pass

def FindImageInRegion(x, y, width, height, template_path, threshold=0.8, grayscale=True, monitor=SETTINGS.monitor, return_first_on_threshold=True, min_scale=0.5, max_scale=1.5, scale_step=0.05):
    pass

def GetBar(x1, y1, x2, y2, threshold=128, max_value=255, monitor=SETTINGS.monitor):
    pass

def GetBarByColour(x1, y1, x2, y2, color, tolerance=30, monitor=SETTINGS.monitor):
    pass

def GetValue(x1, y1, x2, y2, threshold=128, max_value=255, monitor=SETTINGS.monitor):
    pass

def GetText(x1, y1, x2, y2, one_word=False, threshold=128, max_value=255, monitor=SETTINGS.monitor):
    pass

def Click(x, y, delay=100):
    pass

def MouseMove(x, y, delay=100):
    pass

def FocusedClick(x, y, focusDelay=100, delay=100):
    pass

def SaveObject(fileName, obj):
    pass

def LoadObject(fileName):
    pass

def SetRegions():
    pass
