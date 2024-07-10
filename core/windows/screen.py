import ctypes
import ctypes.wintypes


user32 = ctypes.windll.user32
MONITOR_DEFAULTTONEAREST = 2


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_long),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", ctypes.c_long)
    ]


def get_window_rect(hwnd):
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect


def find_window_by_title(window_title):
    hwnd = user32.FindWindowW(None, window_title)
    if hwnd == 0:
        print(f"{window_title} not found")
        return None
    return hwnd


def get_screen_of_window(rect):
    monitor = user32.MonitorFromRect(ctypes.byref(rect), MONITOR_DEFAULTTONEAREST)
    monitor_info = MONITORINFO()
    monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info))
    return (monitor_info.rcMonitor.left,
            monitor_info.rcMonitor.top,
            monitor_info.rcMonitor.right - monitor_info.rcMonitor.left,
            monitor_info.rcMonitor.bottom - monitor_info.rcMonitor.top)


def get_screen_by_window_title(window_title):
    hwnd = find_window_by_title(window_title)
    rect = get_window_rect(hwnd)

    return get_screen_of_window(rect)


if __name__ == "__main__":
    from core.constants import GW2_WINDOW_TITLE

    screen_width, screen_height, screen_left, screen_top = get_screen_by_window_title(GW2_WINDOW_TITLE)
    screen_resolution = (screen_width, screen_height)
    print(f"Screen Resolution: {screen_resolution}")
